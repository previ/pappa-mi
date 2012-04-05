#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#from webapp2_extras import jinja2
import jinja2
from webapp2_extras import sessions
from google.appengine.api import memcache
from webapp2_extras import sessions_memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import images

import py.feedparser

from py.gviz_api import *
from py.model import *
from py.modelMsg import *
from common import Const

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)[0:len(os.path.dirname(__file__))-3]+"/templates"))

class ActivityFilter():
  def __init__(self, tagnames = list(), msgtypes = list(), users = list(), groups = list()):
    self.tagnames=tagnames
    self.msgtypes=msgtypes
    self.users=users
    self.groups=groups    
  tagnames = None
  msgtypes = None
  users = None
  group = None
  
class BasePage(webapp.RequestHandler):  
  
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
        ctx["citta_key"] = commissario.citta.id()
        ctx["cm_key"] = commissario.commissione().key.id()
        ctx["cm_name"] = str(commissario.commissione().desc())
      else:
        ctx["citta_key"] = Citta.get_first().key.id()
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
    return self.request.user
  
  def getBase(self, template_values):
    
    if self.request.url.find("appspot.com") != -1 and self.request.url.find("test") == -1 and self.request.url.find("-hr") == -1:
      self.redirect("http://www.pappa-mi.it")
        
    user = self.get_current_user()
    url = None
    if user:
      url = "/eauth/logout"
      url_linktext = 'Esci'
    else:
      url = "/eauth/login?next=" + self.request.uri
      url_linktext = 'Entra'
    if self.request.url.find("/test") != -1 :
      template_values["test"] = "true"
    if self.request.url.find("www.pappa-mi.it") != -1 :
      template_values["pappamiit"] = "true"
      
    commissario = self.getCommissario(user)
    if( commissario is not None ) :
      if( commissario.ultimo_accesso_il is None or datetime.now() - commissario.ultimo_accesso_il > timedelta(minutes=60) ):
        commissario.ultimo_accesso_il = datetime.now()
        commissario.put()
      template_values["commissario"] = commissario.isCommissario() or commissario.isRegCommissario()
      template_values["genitore"] = commissario.isGenitore()
      #user.fullname = commissario.nomecompleto(commissario)
      #user.title = commissario.titolo(commissario)
      #user.avatar = commissario.avatar()
      #logging.info("nome:" + commissario.titolo(commissario) + " id: " + str(commissario.usera.id()))
       
      #logging.info("commissario: " + str(commissario.isCommissario()))
      #logging.info("genitore: " + str(commissario.isGenitore()))
    template_values["cmsro"] = commissario
    
    if "main" not in template_values:
      template_values["main"] = 'main.html'
    template_values["user"] = user
    template_values["admin"] = users.is_current_user_admin()
    template_values["url"] = url
    template_values["shownote"] = True
    #template_values["comments"] = False   
    template_values["url_linktext"] = url_linktext
    template_values["host"] = self.getHost()
    template_values["version"] = "2.0.0.0 - 2012.03.01"
    template_values["ctx"] = self.get_context()
    
    #logging.info("content: " + template_values["content"])
    #self.response.write(self.jinja2.render_template(template_values["main"], context=template_values))
    
    #this is to avoid that a new user click on "enter" instead of "register" => she will be redirected to "signup" path until she complete the process, or logout
    if user and not commissario and "signup" not in self.request.uri:
      self.redirect("/signup")
      return

    template = jinja_environment.get_template(template_values["main"])
    self.response.write(template.render(template_values))
  
  def getCommissario(self, user = None):
    if user is None:
      user = self.request.user
    if user :
      #logging.info("userid: " + str(user.key.id()))
      return Commissario.get_by_user(user)
    else:
      return None
  
  #def getCommissioni(self):
    #return Commissioni.get_all()

  @classmethod
  def getTopTags(cls):
    return Tag.get_top_referenced(40)
  

  """
  Algo A: 
  1.read N activities, starting from M offset
  2.cache the read
  3.filter activities by tag, type, user, group
  4.if activities < N and activities availables then loop 1
  5.return activities

  Algo B: 
  1.detect filter category
  2.read N activities, starting from M offset
  3.cache the read  
  4.return activities
  """
  
  def get_activities(self, offset=0):
    #logging.info("get_activities")
    
    activities = None

    #logging.info("tag: " + self.request.get("tag") + " type: " + self.request.get("type") + " user: " + self.request.get("user"))

    tag = self.get_or_set_ctx("tag", self.request.get("tag", None))
    msgtype = self.get_or_set_ctx("type", self.request.get("type", None))   
    user = self.get_or_set_ctx("user", self.request.get("user", None))
    cm = self.get_or_set_ctx("cm", self.request.get("cm", None))
          
    if tag:
      activities = Messaggio.get_by_tagname(tag,offset)
    elif msgtype:
      activities = Messaggio.get_by_msgtype(int(msgtype),offset)
    elif user:
      activities = Messaggio.get_by_user(int(user),offset)
    elif cm:
      activities = Messaggio.get_by_grp(model.Key("Commissione", int(cm)),offset)
    else:
      activities = Messaggio.get_all(offset)
    
    return activities
  
  #def get_activities_by_filter(self, activity_filter):
    #activities = list()    
    #for tagname in activity_filter.tagnames:
      #activities.extend(Messaggio.get_by_tagname(tagname))
    #for msgtype in activity_filter.msgtypes:
      #activities.extend(Messaggio.get_by_msgtype(msgtype))
    #for user in activity_filter.users:
      #activities.extend(Messaggio.get_by_user(user))
    #for group in activity_filter.groups:
      #activities.extend(Messaggio.get_by_group(model.Key(group)))

    #activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      
    #return activities

  def get_activities_by_group(self, user):
    return list()
  
  def getHost(self):
    host = self.request.url[len("http://"):]
    host = host[:host.find("/")]
    #logging.info("host: " + host)
    return host

  _news = {"news_pappami":"http://blog.pappa-mi.it/feeds/posts/default",
          "news_web": "http://www.google.com/reader/public/atom/user%2F14946287599631859889%2Fstate%2Fcom.google%2Fbroadcast",
          "news_cal": "http://www.google.com/calendar/feeds/aiuto%40pappa-mi.it/public/basic"}
  
  @classmethod
  def getNews(self,name):
    news = memcache.get(name)
    i = 0
    if news is None:
      news_all = py.feedparser.parse(self._news[name])
      #logging.debug(news_all)
      news = []
      for n in news_all.entries:
        #logging.debug(n)
        if i >= 4 :
          break
        i = i + 1
        news.append(n)
        
      memcache.add(name,news)
    return news
  
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

  def createMenu(self,request,c,template_values):
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
    citta = Citta.get_first()
    
    if c and not c.getCentroCucina(data):
      return list()
    
    if c and c.getCentroCucina(data).getMenuOffset(data) is not None:
      offset = c.getCentroCucina(data).getMenuOffset(data)
      citta = c.citta
      
    menu = memcache.get("menu-" + str(offset) + "-" + str(data))
    if not menu:
      menu = list()
      
      self.getMenuHelper(menu,data,offset,citta)
      if offset >= 0:
        self.getMenuHelper(menu,self.workingDay(data+timedelta(1)),offset,citta)
              
      memcache.set("menu-" + str(offset) + "-" + str(data), menu, 60)
    return menu

  def getMenuHelper(self, menu, data, offset, citta):    
    mn = MenuNew.get_by(citta, data)
    
    if mn:
      piatti = dict()
      if offset > 0:
        piatti = Piatto.get_by_menu_date_offset(mn, data, offset)
        mh = MenuHelper()
        mh.data = data + timedelta(data.isoweekday()-1)      
        mh.giorno = data.isoweekday()
        mh.primo = piatti["p"]
        mh.secondo = piatti["s"]
        mh.contorno = piatti["c"]
        mh.dessert = piatti["d"]
        menu.append(mh)
      else:
        settimane = Piatto.get_by_date(data)
      
        for i in range(1,5):
          piatti = settimane[i]
          mh = MenuHelper()
          mh.data = data + timedelta(data.isoweekday()-1)      
          mh.giorno = data.isoweekday()
          mh.settimana = i
          mh.primo = piatti["p"]
          mh.secondo = piatti["s"]
          mh.contorno = piatti["c"]
          mh.dessert = piatti["d"]
          menu.append(mh)      
    

  def getMenuWeek(self, data, cm): 

    logging.info(str(cm.key))
    logging.info(str(data))
    offset = cm.getCentroCucina(data).getMenuOffset(data)

    if offset == None:
      offset = 0
      
    # settimana corrente
    menu = MenuNew.get_by(cm.citta, data)

    mlist = list()
    if menu:
      giorni = Piatto.get_by_settimana((((((data-menu.validitaDa).days) / 7)+offset)%4 + 1))
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
        mh.primo = piatti["p"]
        mh.secondo = piatti["s"]
        mh.contorno = piatti["c"]
        mh.dessert = piatti["d"]
        mlist.append(mh)
      
    return mlist
      
  def getBase(self,template_values):
    cm = None
    commissario = self.getCommissario(self.get_current_user())
    if self.request.get("cm") != "":
      cm = model.Key("Commissione",int(self.request.get("cm"))).get()
    elif commissario and commissario.commissione() :
      cm = commissario.commissione()
    else:
      if commissario and commissario.citta:
        cm = Commissione.get_by_citta(commissario.citta).get()
      else:
        cm = Commissione.get_by_citta(Citta.get_first().key)[0]
      
    date = self.request.get("data")
    if date:
      date = datetime.strptime(date,Const.DATE_FORMAT).date()
    else:
      date = datetime.now().date()
    
    date = self.get_next_working_day(date)
    
    date1 = date - timedelta(date.isoweekday() - 1)
    datep = date1 - timedelta(7)
    daten = date1 + timedelta(7)

    template_values['menu'] = self.getMenuWeek(date1, cm)
    template_values['data'] = date
    template_values['data1'] = date1
    template_values['datap'] = datep
    template_values['datan'] = daten
    template_values['cm'] = cm
    template_values['action'] = self.request.path
    super(CMMenuHandler,self).getBase(template_values)
    

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
    commissario = basePage.getCommissario(basePage.request.user)
    if commissario == None or commissario.isCommissario() == False:
      basePage.redirect("/eauth/login?next="+basePage.request.url)
    else:
      return func(basePage, *args, **kwargs)
  return callf    

def reguser_required(func):
  def callf(basePage, *args, **kwargs):
    user = basePage.request.user if basePage.request.user else None
    commissario = basePage.getCommissario(user)
    if commissario == None:
      basePage.redirect("/eauth/login?next="+basePage.request.url)
    else:
      return func(basePage, *args, **kwargs)
  return callf    

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    }
}
