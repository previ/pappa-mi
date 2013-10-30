#!/usr/bin/env python
#
# Copyright 2010 Pappa-Mi org
# Authors: R.Previtera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cgi
import os, logging, json
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import fixpath

from google.appengine.ext.ndb import model, toplevel
from google.appengine.api import users


import webapp2 as webapp
import traceback
#from webapp2_extras import jinja2
import jinja2
from webapp2_extras import sessions
from google.appengine.api import memcache
from webapp2_extras import sessions_memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import images
from google.appengine.api import mail
from google.appengine.api.app_identity import *

import httpagentparser

from py.gviz_api import *
from py.model import *
#from py.modelMsg import *
from common import Const, Channel

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)[0:len(os.path.dirname(__file__))-3]+"/templates"))

unsupported_browsers = {"Microsoft Internet Explorer": ["5.0", "6.0"]}

class BaseHandler(webapp.RequestHandler):

  #@webapp.cached_property
  #def jinja2(self):
        #return jinja2.get_jinja2(app=self.app)

  @toplevel
  def dispatch(self):
    # Get a session store for this request.
    sessions.default_config['secret_key'] = "wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY"
    self.session_store = sessions.get_store(request=self.request)

    try:
        # Dispatch the request.
        webapp.RequestHandler.dispatch(self)
    finally:
        # Save all sessions.
        #logging.info(self.get_context())
        self.set_context()
        self.session_store.save_sessions(self.response)

  def handle_exception(self,exception,debug_mode=False):

    if type(exception).__name__== FloodControlException.__name__:
      template = jinja_environment.get_template("flooderror.html")
      template_values={
                       'flood_time':Const.SOCIAL_FLOOD_TIME,

                       }
      html=template.render(template_values)
      time=(datetime.now()-memcache.get("FloodControl-"+str(self.get_current_user().key)))

      time=Const.SOCIAL_FLOOD_TIME-time.seconds
      response = {'response':'flooderror','time':time,'html':html}

      self.output_as_json(response)
      return
    else:
      super(BaseHandler,self).handle_exception(exception,debug_mode)


  def success(self,data=None):

      response = {'response':'success'}
      if data:
        response.update(data.items())

      self.output_as_json(response)

  def error(self):
      response = {'response':'error'}
      self.output_as_json(response)


  @webapp.cached_property
  def session(self):
      # Returns a session using the default cookie key.
    return self.session_store.get_session(backend="memcache")

  def get_context(self):
    ctx = self.session.get("ctx")
    if ctx == None:
      ctx = dict()
      commissario = self.getCommissario()
      if commissario:
        ctx["node"] = "all"
        ctx["citta_key"] = commissario.citta.id()
        if commissario.commissione():
          ctx["cm_key"] = commissario.commissione().key.id()
          ctx["cm_name"] = str(commissario.commissione().desc())
      else:
        ctx["node"] = "news"
          
      anno = datetime.now().date().year
      if datetime.now().date().month <= 9: #siamo in inverno -estate, data inizio = settembre anno precedente
        anno = anno - 1
      ctx["anno"] = str(anno)
      self.session["ctx"] = ctx
    return ctx

  def set_context(self):
    ctx = self.session.get("ctx")
    if ctx:
      self.session["ctx"] = ctx

  def get_or_set_ctx(self, key, value):
    if value != None:
      self.get_context()[key] = value
      self.set_context()
    elif value == "" and key in self.get_context():
      del self.get_context()[key]
      value = None
    else:
      value = self.get_context().get(key)
    return value

  def get_current_user(self):
    user = None
    if hasattr(self.request, 'user'):
      user = self.request.user
    return user

  def getBase(self, template_values):

    if self.request.url.find("appspot.com") != -1 and self.request.url.find("test") == -1 and self.request.url.find("-hr") == -1:
      self.redirect("http://www.pappa-mi.it")

    uri = self.request.url[self.request.url.find('//')+2:]

    if ((uri.find("m.") != -1 or 
         uri.find("mobile.") != -1) and 
        uri.find("/mobile") == -1 and 
        not (("signup" in self.request.uri) or ("profilo" in self.request.uri) or ("condizioni" in self.request.uri))):
      logging.info("going mobile")
      self.redirect("/mobile")
      return

    user = self.get_current_user()

    if self.request.url.find("/test") != -1 :
      template_values["test"] = "true"
    if self.request.url.find("www.pappa-mi.it") != -1 :
      template_values["pappamiit"] = "true"

    user_agent = httpagentparser.detect(self.request.headers["User-Agent"])
    if user_agent.get("browser"):
      if user_agent.get("browser").get("name"):
        browser_name = user_agent.get("browser").get("name")
        browser_ver = user_agent.get("browser").get("version")
        #logging.info("Browser: " + browser_name + " version: " + browser_ver )

        if unsupported_browsers.get(browser_name):
          u_b = unsupported_browsers.get(browser_name)
          if browser_ver in u_b:
            template_values["main"] = 'unsupported.html'

    commissario = self.getCommissario(user)
    if( commissario and commissario.is_active()) :
      if commissario.ultimo_accesso_il is None and self.request.url.find("/stream") != -1:
        template_values["welcome"] = "new"
      if commissario.ultimo_accesso_il and commissario.ultimo_accesso_il < datetime(year=2013, month=4, day=19) and self.request.url.find("/stream") != -1:
        #logging.info(str(self.request.url.find("/stream")))
        template_values["welcome"] = "returning"
      if( commissario.ultimo_accesso_il is None or datetime.now() - commissario.ultimo_accesso_il > timedelta(minutes=60) ):
        commissario.ultimo_accesso_il = datetime.now()
        commissario.put()
        commissario.set_cache()
      template_values["commissario"] = commissario.isCommissario() or commissario.isRegCommissario()
      template_values["genitore"] = commissario.isGenitore()

      template_values["channel"] = Channel.get_by_user(user)

    template_values["cmsro"] = commissario
    url, url_linktext = self.get_login_url_text()

    if "main" not in template_values:
      template_values["main"] = 'main.html'
    template_values["user"] = user
    template_values["admin"] = users.is_current_user_admin()
    template_values["shownote"] = True
    template_values["url"] = url
    template_values["url_linktext"] = url_linktext
    template_values["host"] = self.getHost()
    template_values["version"] = "3.2.0.35 - 2013.10.25"
    template_values["ctx"] = self.get_context()
    
    #logging.info("users.is_current_user_admin(): " + str(users.is_current_user_admin()))
    #logging.info("users.current_user(): " + str(users.get_current_user()))

    if user and not commissario and not (("signup" in self.request.uri) or ("condizioni" in self.request.uri)):
      self.redirect("/signup")
      return
    
    template = jinja_environment.get_template(template_values["main"])
    self.response.write(template.render(template_values))

  def render_template(template_path, template_values):
    template = jinja_environment.get_template(template_path)
    return template.render(template_values)

  #response object dump as json string
  def output_as_json(self, obj):
    self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
    json.dump(obj, self.response.out)

  def getCommissario(self, user = None):
    if user is None:
      user = self.get_current_user()
    if user :
      #logging.info("userid: " + str(user.key.id()))
      return Commissario.get_by_user(user)
    else:
      return None

  @classmethod
  def host(cls):
    if "test" in get_application_id():
      host = "test.pappa-mi.it"
    else:
      host = "www.pappa-mi.it"
    return host

  def getHost(self):
    host = self.request.url[len("http://"):]
    host = host[:host.find("/")]
    #logging.info("host: " + host)
    return host


  def get_login_url_text(self):
    url = None
    url_linktext = None
    if self.get_current_user():
      url = "/eauth/logout"
      url_linktext = 'Esci'
    else:
      url = "/eauth/login?next=" + self.request.uri
      url_linktext = 'Entra'
    return url, url_linktext


class BasePage(BaseHandler):
  pass

class CMCommissioniDataHandler(BasePage):

  def get(self):
    user = self.get_current_user()
    city = self.request.get("city")
    if city == "" and self.getCommissario(user):
      city = self.getCommissario(user).citta
    else:
      city = model.Key("Citta", int(city))

    buff = ""
    buff = memcache.get("cm_city_json_"+str(city.id()))
    if(buff is None):
      cmlist = list()
      cms = Commissione.get_by_citta(city)
      for cm in cms:
        cmlist.append({'value': str(cm.key.id()), 'label':cm.nome + ' - ' + cm.tipoScuola})

      buff = json.JSONEncoder().encode(cmlist)

      memcache.add("cm_city_json_"+str(city.id()), buff)

    expires_date = datetime.utcnow() + timedelta(20)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)

class CMMenuHandler(BasePage):

  def createMenu(self,request, c, template_values):
    menu = Menu();

    data = self.workingDay(datetime.now().date())

    menu = self.getMenu(data, c)
    template_values["sett"] = len(menu) > 2
    template_values["menu"] = self.getMenu(data, c)

  def workingDay(self, data):
    while data.isoweekday() > 5:
      data += timedelta(1)
    return data

  def getMenu(self, data, c):
    offset = -1
    citta = None

    if c and not c.getCentroCucina(data):
      return list()

    if c and c.getCentroCucina(data).getMenuOffset(data) is not None:
      offset = c.getCentroCucina(data).getMenuOffset(data)
      citta = c.citta

    if not citta:
      citta = Citta.get_first()
      
    #menu = memcache.get("menu-" + str(offset) + "-" + str(data))
    menu_cache = Cache.get_cache("Menu")
    menu = menu_cache.get("menu-" + str(offset) + "-" + str(data))
    
    if not menu:
      menu = list()

      self.getMenuHelper(menu,data,offset,citta)
      if offset >= 0:
        self.getMenuHelper(menu,self.workingDay(data+timedelta(1)),offset,citta)

      menu_cache.put("menu-" + str(offset) + "-" + str(data), menu)
      
    return menu

  def getMenuHelper(self, menu, data, offset, citta):
    mn = MenuNew.get_by(citta, data)

    if mn:
      piatti = dict()
      if offset >= 0:
        piatti = Piatto.get_by_menu_date_offset(mn, data, offset)
        mh = MenuHelper()
        mh.data = data# + timedelta(data.isoweekday()-1)
        mh.giorno = data.isoweekday()
        mh.primo = piatti.get("p", Piatto())
        mh.secondo = piatti.get("s", Piatto())
        mh.contorno = piatti.get("c", Piatto())
        mh.dessert = piatti.get("d", Piatto())
        menu.append(mh)
      else:

        settimane = Piatto.get_by_date(data)

        for i in range(1,5):
          piatti = settimane[i]
          mh = MenuHelper()
          mh.data = data# + timedelta(data.isoweekday()-1)
          mh.giorno = data.isoweekday()
          mh.settimana = i
          mh.primo = piatti.get("p", Piatto())
          mh.secondo = piatti.get("s", Piatto())
          mh.contorno = piatti.get("c", Piatto())
          mh.dessert = piatti.get("d", Piatto())
          menu.append(mh)


  def getMenuWeek(self, data, cm):

    #logging.info(str(cm.key))
    #logging.info(str(data))
    offset = cm.getCentroCucina(data).getMenuOffset(data)

    if offset == None:
      offset = 0

    #logging.info("offset: " + str(offset))

    # settimana corrente
    menu = MenuNew.get_by(cm.citta, data)

    mlist = list()
    if menu:
      giorni = Piatto.get_by_menu_settimana(menu, (((((data-menu.validitaDa).days) / 7)+offset)%4 + 1) )
      #for pg in PiattoGiorno.all().filter("settimana", (((((data-menu.validitaDa).days) / 7)+offset)%4 + 1) ):
        #if not pg.giorno in giorni:
          #giorni[pg.giorno] = dict()
        #giorni[pg.giorno][pg.tipo] = pg.piatto

      data = data + timedelta(data.isoweekday()-1)

      for i in range(1,6):
        piatti = giorni[i]
        mh = MenuHelper()
        mh.data = data + timedelta(i - 1)
        mh.giorno = i
        mh.primo = piatti.get("p", Piatto())
        mh.secondo = piatti.get("s", Piatto())
        mh.contorno = piatti.get("c", Piatto())
        mh.dessert = piatti.get("d", Piatto())
        mlist.append(mh)

    return mlist



  def get_next_working_day(self, date):
    while date.isoweekday() > 5:
      date = date + timedelta(1)

    return date;


class CMCittaHandler(webapp.RequestHandler):
  def get(self):
    citta = Citta.get_all()
    citlist = list()
    for c in citta:
      citlist.append({'key': str(c.key), 'nome':c.nome, 'codice':c.codice, 'provincia':c.provincia, 'lat':c.geo.lat, 'lon':c.geo.lon})

    self.response.out.write(json.JSONEncoder().encode({'label':'nome', 'identifier':'key', 'items': citlist}))


def handle_404(request, response, exception):
  c = {'exception': exception.status}
  jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)[0:len(os.path.dirname(__file__))-3]+"/templates"))
  template = jinja_environment.get_template('404.html')
  t = template.render(c)
  response.write(t)
  response.set_status(exception.status_int)

def handle_500(request, response, exception):
  c = {'exception': traceback.format_exc(20)}
  logging.info(c["exception"])
  sender = "Pappa-Mi <aiuto@pappa-mi.it>"
  message = mail.EmailMessage()
  message.sender = sender
  message.to = sender
  message.subject = "Pappa-Mi - Exception"
  message.body = """Exception in Pappa-Mi.
  Request: """ + str(request.url) + """
  Exception: """ + str(exception) + """

  <Stacktrace>:
  """ + traceback.format_exc(20) + """

  <Stacktrace/>
  """

  message.send()

  jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)[0:len(os.path.dirname(__file__))-3]+"/templates"))
  template = jinja_environment.get_template('500.html')
  t = template.render(c)
  response.write(t)
  response.set_status(500)

def user_required(func):
  def callf(basePage, *args, **kwargs):
    user = basePage.request.user if basePage.request.user else None
    if user == None:
      basePage.redirect("/eauth/signup?next="+basePage.request.url)
    else:
      return func(basePage, *args, **kwargs)
  return callf

def commissario_required(func):
  def callf(basePage, *args, **kwargs):
    user = basePage.request.user if basePage.request.user else None
    commissario = basePage.getCommissario(user)
    #logging.info(commissario)
    if commissario == None or commissario.isCommissario() == False:
      basePage.redirect("/eauth/login?next="+basePage.request.url)
    else:
      return func(basePage, *args, **kwargs)
  return callf

def reguser_required(func):
  def callf(basePage, *args, **kwargs):
    user = basePage.request.user if basePage.request.user else None
    commissario = basePage.getCommissario(user)
    if commissario == None or commissario.is_deactivated():
      basePage.redirect("/eauth/login?next="+basePage.request.url)
    else:
      return func(basePage, *args, **kwargs)
  return callf

def reguser_required_mobile(func):
  def callf(basePage, *args, **kwargs):
    user = basePage.request.user if basePage.request.user else None
    commissario = basePage.getCommissario(user)
    if commissario == None:
      basePage.response.set_status(401, "Authentication required")
    else:
      return func(basePage, *args, **kwargs)
  return callf

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    }
}

class FloodControlException(Exception):
     def __init__(self):
                pass

     def __str__(self):
          return repr("Flood Control Error")
