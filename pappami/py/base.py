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


from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
#from webapp2_extras import jinja2
import jinja2
from webapp2_extras import sessions
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import images

import py.feedparser

from py.gviz_api import *
from py.model import *
from py.modelMsg import *

class Const:
  TIME_FORMAT = "T%H:%M:%S"
  DATE_FORMAT = "%Y-%m-%d"
  ACTIVITY_FETCH_LIMIT = 5

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

  def dispatch(self):
    # Get a session store for this request.
    sessions.default_config['secret_key'] = "secretsecretsecret" 
    self.session_store = sessions.get_store(request=self.request)

    try:
        # Dispatch the request.
        webapp.RequestHandler.dispatch(self)
    finally:
        # Save all sessions.
        self.session_store.save_sessions(self.response)

  @webapp.cached_property
  def session(self):
      # Returns a session using the default cookie key.
      return self.session_store.get_session()      

  def getBase(self, template_values):
    
    if self.request.url.find("appspot.com") != -1 and self.request.url.find("test") == -1 and self.request.url.find("-hr") == -1:
      self.redirect("http://www.pappa-mi.it")
        
    user = users.get_current_user()
    if user:
      url = users.create_logout_url("/")
      url_linktext = 'Esci'
    else:
      url = "/login"
      template_values["login_url"] = users.create_login_url(self.request.uri)
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
        memcache.set("commissario" + str(user.user_id()), commissario, 600)
      template_values["commissario"] = commissario.isCommissario() or commissario.isRegCommissario()
      template_values["genitore"] = commissario.isGenitore()
      user.fullname = commissario.nomecompleto()
      user.title = commissario.titolo()
      user.avatar = commissario.avatar()
     
       
      #logging.info("commissario: " + str(commissario.isCommissario()))
      #logging.info("genitore: " + str(commissario.isGenitore()))

    if "main" not in template_values:
      template_values["main"] = 'main.html'
    template_values["user"] = user
    template_values["admin"] = users.is_current_user_admin()
    template_values["url"] = url
    template_values["shownote"] = True
    #template_values["comments"] = False   
    template_values["url_linktext"] = url_linktext
    template_values["host"] = self.getHost()
    template_values["version"] = "1.4.0.36 - 2011.04.30"
    
    #logging.info("content: " + template_values["content"])
    #self.response.write(self.jinja2.render_template(template_values["main"], context=template_values))
    
    template = jinja_environment.get_template(template_values["main"])
    self.response.write(template.render(template_values))
    
  def getCommissario(self,user):
    commissario = None
    if(user):
      commissario = memcache.get("user" + str(user.user_id()))
      if not commissario:
        logging.info(user.email())
      #commissario = db.GqlQuery("SELECT * FROM Commissario where user = USER('" + user.email() + "')").get()
      commissario = Commissario.all().filter("user", user).get()
      memcache.add("user" + str(user.user_id()), commissario, 600)
    return commissario

  def getCommissioni(self):
    commissioni = memcache.get("commissioni")
    if commissioni == None:
      commissioni = Commissione.all().order("nome");
      memcache.add("commissioni", commissioni)
    return commissioni

  def getTopTags(self):
    tags = memcache.get("toptags")
    if not tags:
      tags = list()
      for tag in Tag.all().order("-numRef").fetch(40):
        tags.append(tag)
      memcache.add("toptags", tags, 60)      
    return tags
    
  def getActivities(self, tagname = ""):
    activities = None
    if tagname != "":
      activities = memcache.get("public_activities_" + tagname)
      if activities == None:
        activities = list()
        tag = Tag.all().filter("nome", tagname).get()
        if tag:
          for tagobj in tag.tagobj_reference_set:
            activities.append(tagobj.obj)
          activities = sorted(activities, key=lambda student: student.creato_il, reverse=True)
        memcache.add("public_activities_" + tagname, activities, 60)
      
    else:
      activities = memcache.get("public_activities")
      if not activities:
        activities = list()
        for msg in Messaggio.all().filter("livello", 0).order("-creato_il").fetch(50):
          #logging.info("tags: " + msg.tags())
          activities.append(msg)
        memcache.add("public_activities", activities, 60)
    return activities

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
    logging.info("get_activities")
    
    activities = None
    logging.info("tag: " + self.request.get("tag"))
    
    tag = self.request.get("tag")
      
    if tag != "":
      tag = self.session['tag'] = tag
    
    tag = self.session.get('tag')

    if tag != "!" and tag != "":
      activities = self.get_activities_by_tagname(tag,offset)
    elif self.request.get("msgtype") != "":
      activities = self.get_activities_by_msgtype(int(self.request.get("msgtype")),offset)
    elif self.request.get("user") != "":
      activities = self.get_activities_by_user(self.request.get("user"),offset)
    else:
      activities = self.get_activities_all(offset)
    
    return activities
  
  def get_activities_by_filter(self, activity_filter):
    activities = list()    
    for tagname in activity_filter.tagnames:
      activities.extend(self.get_activities_by_tagname(tagname))
    for msgtype in activity_filter.msgtypes:
      activities.extend(self.get_activities_by_msgtype(msgtype))
    for user in activity_filter.users:
      activities.extend(self.get_activities_by_user(user))
    for group in activity_filter.groups:
      activities.extend(self.get_activities_by_group(group))

    activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      
    return activities

  def get_activities_by_tagname(self,tagname,offset=0):
    logging.info("get_activities_by_tagname")
    activities = memcache.get("public_activities_tag_" + tagname + "_" + str(offset))
    if activities == None:
      activities = list()
      tag = Tag.all().filter("nome", tagname).get()
      if tag:
        count = 0
        for tagobj in tag.tagobj_reference_set[offset*Const.ACTIVITY_FETCH_LIMIT:(offset+1)*Const.ACTIVITY_FETCH_LIMIT]:
          count += 1
          if count > Const.ACTIVITY_FETCH_LIMIT:
            break
          activities.append(tagobj.obj)
      activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      memcache.add("public_activities_tag_" + tagname + "_" + str(offset/Const.ACTIVITY_FETCH_LIMIT), activities, 60)
    return activities

  def get_activities_by_msgtype(self, msgtype, offset=0):
    logging.info("get_activities_by_msgtype")
    activities = memcache.get("public_activities_type_" + str(msgtype) + "_" + str(offset))
    if activities == None:
      activities = list()
      logging.info("get_activities_by_msgtype: " + str(msgtype))
      for msg in Messaggio.all().filter("tipo", msgtype).order("-creato_il").fetch(Const.ACTIVITY_FETCH_LIMIT, offset*Const.ACTIVITY_FETCH_LIMIT):
        logging.info("get_activities_by_msgtype: " + str(msg.tipo))
        activities.append(msg)
      memcache.add("public_activities_type_" + str(msgtype) + "_" + str(offset), activities, 60)
    return activities

  def get_activities_by_user(self, user_email, offset=0):
    activities = memcache.get("public_activities_user_" + user_email + "_" + str(offset))
    if activities == None:
      activities = list()
      for msg in Messaggio.all().filter("creato_da", users.User(user_email)).order("-creato_il").fetch(Const.ACTIVITY_FETCH_LIMIT, offset*Const.ACTIVITY_FETCH_LIMIT):
        activities.append(msg)
      memcache.add("public_activities_user_" + user_email + "_" + str(offset), activities, 60)
    return activities

  def get_activities_by_group(self, user):
    return list()

  def get_activities_all(self, offset=0):
    logging.info('get_activities_all')
    activities = memcache.get("activities_all_" + str(offset))
    if not activities:
      activities = list()
      for msg in Messaggio.all().filter("livello", 0).order("-creato_il").fetch(Const.ACTIVITY_FETCH_LIMIT, offset*Const.ACTIVITY_FETCH_LIMIT):
        activities.append(msg)
        
      activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      memcache.add("public_activities_" + str(offset), activities, 60)
    return activities
  
  def getHost(self):
    host = self.request.url[len("http://"):]
    host = host[:host.find("/")]
    #logging.info("host: " + host)
    return host

  _news = {"news_pappami":"http://blog.pappa-mi.it/feeds/posts/default",
          "news_web": "http://www.google.com/reader/public/atom/user%2F14946287599631859889%2Fstate%2Fcom.google%2Fbroadcast",
          "news_cal": "http://www.google.com/calendar/feeds/aiuto%40pappa-mi.it/public/basic"}
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
    user = users.get_current_user()
    city = self.request.get("city")
    if city == "" and self.getCommissario(user):
      city = self.getCommissario(user).citta.key()
    else:
      city = db.Key(city)      

    buff = ""
    if city:
      buff = memcache.get("cmall"+str(city))
      if(buff is None):
        cmlist = list()  
        cms = Commissione.all().filter("citta", city).order("nome")
        for cm in cms:
          cmlist.append({'value': str(cm.key()), 'label':cm.nome + ' - ' + cm.tipoScuola})
          #cmlist.append({'key': str(cm.key()), 'nome':cm.nome + ' - ' + cm.tipoScuola})
        
        #buff = json.JSONEncoder().encode({'label':'nome', 'identifier':'key', 'items': cmlist})      
        buff = json.JSONEncoder().encode(cmlist)      
          
        memcache.add("cmall"+str(city), buff)
          
    expires_date = datetime.utcnow() + timedelta(20)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)

class CMCommissioniHandler(BasePage):
      
  def getBase(self,template_values):
    template_values["content"] = "map.html"
    template_values["limit"] = 100
    template_values["centriCucina"] = CentroCucina.all().order("nome")
    template_values['action'] = self.request.path
    template_values['geo'] = self.getCommissario(users.get_current_user()).citta.geo
    super(CMCommissioniHandler,self).getBase(template_values)

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
    citta = Citta.all().get()
    if c and c.getCentroCucina(data).getMenuOffset(data) is not None:
      offset = c.getCentroCucina(data).getMenuOffset(data)
      citta = c.citta

    if data >= date(2010,6,14) and data < date(2010,8,31):
      offset = 0
      
    menu = memcache.get("menu-" + str(offset) + "-" + str(data))
    if not menu:
      menu = list()
      
      self.getMenuHelper(menu,data,offset,citta)
      if offset >= 0:
        self.getMenuHelper(menu,self.workingDay(data+timedelta(1)),offset,citta)
              
      memcache.set("menu-" + str(offset) + "-" + str(data), menu, 60)
    return menu

  def getMenuHelper(self, menu, data, offset, citta):
    mn = MenuNew.all().filter("citta",citta).filter("validitaDa <=", data).order("-validitaDa").get()
    
    piatti = dict()
    if offset > 0:
      for pg in PiattoGiorno.all().filter("giorno", data.isoweekday()).filter("settimana", (((((data-mn.validitaDa).days) / 7)+offset)%4 + 1) ):
        piatti[pg.tipo] = pg.piatto    
      mh = MenuHelper()
      mh.data = data + timedelta(data.isoweekday()-1)      
      mh.giorno = data.isoweekday()
      mh.primo = piatti["p"]
      mh.secondo = piatti["s"]
      mh.contorno = piatti["c"]
      mh.dessert = piatti["d"]
      menu.append(mh)
    else:
      settimane = dict()
      for pg in PiattoGiorno.all().filter("giorno", data.isoweekday()):
        if not pg.settimana in settimane:
          settimane[pg.settimana] = dict()
        settimane[pg.settimana][pg.tipo] = pg.piatto
    
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
    menu = list();

    #logging.info("data: %s", data)

    offset = cm.getCentroCucina(data).getMenuOffset(data)

    if offset == None:
      offset = 0

    if data >= date(2010,6,14) and data < date(2010,8,31):
      offset = 0
      
    # settimana corrente
    menu = MenuNew.all().filter("citta",cm.citta).filter("validitaDa <=", data).order("-validitaDa").get()

    giorni = dict()
    for pg in PiattoGiorno.all().filter("settimana", (((((data-menu.validitaDa).days) / 7)+offset)%4 + 1) ):
      if not pg.giorno in giorni:
        giorni[pg.giorno] = dict()
      giorni[pg.giorno][pg.tipo] = pg.piatto

    mlist = list()
    for i in range(1,6):
      piatti = giorni[i]
      mh = MenuHelper()
      mh.data = data + timedelta(data.isoweekday()-1)      
      mh.giorno = i
      mh.primo = piatti["p"]
      mh.secondo = piatti["s"]
      mh.contorno = piatti["c"]
      mh.dessert = piatti["d"]
      mlist.append(mh)
      
    return mlist
      
  def getBase(self,template_values):
    cm = None
    commissario = self.getCommissario(users.get_current_user())
    if self.request.get("cm") != "":
      cm = Commissione.get(self.request.get("cm"))
    elif commissario and commissario.commissione() :
      cm = commissario.commissione()
    else:
      cm = Commissione.all().get()
    date = self.request.get("data")
    if date:
      date = datetime.strptime(date,Const.DATE_FORMAT).date()
    else:
      date = datetime.now().date()
    
    date1 = date - timedelta(date.isoweekday() - 1)
    date2 = date1 + timedelta(7)
    template_values['content'] = 'menu.html'
    template_values['menu1'] = self.getMenuWeek(date1, cm )
    template_values['menu2'] = self.getMenuWeek(date2, cm )
    template_values['data'] = date
    template_values['data1'] = date1
    template_values['data2'] = date2
    template_values['cm'] = cm
    template_values['action'] = self.request.path
    #logging.info("CMMenuHandler.type: " + str(type(self)))
    super(CMMenuHandler,self).getBase(template_values)    
    
class CMMenuHandlerOld(BasePage):

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
    tipoScuola = "Materna"
    if c and c.getCentroCucina(data).getMenuOffset(data) is not None:
      offset = c.getCentroCucina(data).getMenuOffset(data)
      tipoScuola = c.tipoScuola

    if data >= date(2010,6,14) and data < date(2010,8,31):
      offset = 0
      
    menu = memcache.get("menu-" + str(offset) + "-" + str(data))
    if not menu:
      logging.info("cache miss: " + "menu-" + str(offset) + "-" + str(data))
      menu = list()

      self.getMenuHelper(menu,data,offset,tipoScuola)
      if offset >= 0:
        self.getMenuHelper(menu,data+timedelta(1),offset,tipoScuola)
      
      if offset < 0:
        menu = sorted(menu, key=lambda menu: menu.settimana)
        
      memcache.set("menu-" + str(offset) + "-" + str(data), menu, 60)
    return menu

  def getMenuHelper(self, menu, data, offset, tipoScuola):
    menus = Menu.all().filter("validitaDa <=", data).filter("giorno", data.isoweekday()).filter("tipoScuola", tipoScuola).order("-validitaDa")

    for m in menus:
      #logging.info("s %d g %d, sc: %d, gc: %d", m.settimana, m.giorno, ((((data-m.validitaDa).days) / 7)%4)+1, data.isoweekday())
      if((((((data-m.validitaDa).days) / 7)+offset)%4 + 1) == m.settimana or offset == -1):
        m.data = data
        menu.append(m)
        if((offset == -1 and len(menu) >=4) or (offset >=0 )):
          break

  def getMenuWeek(self, data, cm): 
    menu = list();

    #logging.info("data: %s", data)

    offset = cm.getCentroCucina(data).getMenuOffset(data)

    if offset == None:
      offset = 0

    if data >= date(2010,6,14) and data < date(2010,8,31):
      offset = 0
      
    # settimana corrente
    menus = Menu.all().filter("validitaDa <=", data).filter("tipoScuola", cm.tipoScuola).order("-validitaDa")
    #logging.info("len %d" , menus.count())

    count = 0
    for m in menus:
      if((((((data-m.validitaDa).days) / 7)+offset)%4 + 1) == m.settimana):
        m.data = data + timedelta(m.giorno-1)      
        menu.append(m)        
        #logging.info("m" + m.primo)
        count += 1
        if count >=5 :
          break

    return sorted(menu, key=lambda menu: menu.giorno)
      
  def getBase(self,template_values):
    cm = None
    commissario = self.getCommissario(users.get_current_user())
    if self.request.get("cm") != "":
      cm = Commissione.get(self.request.get("cm"))
    elif commissario and commissario.commissione() :
      cm = commissario.commissione()
    else:
      cm = Commissione.all().get()
    date = self.request.get("data")
    if date:
      date = datetime.strptime(date,Const.DATE_FORMAT).date()
    else:
      date = datetime.now().date()
    
    date1 = date - timedelta(date.isoweekday() - 1)
    date2 = date1 + timedelta(7)
    template_values['content'] = 'menu.html'
    template_values['menu1'] = self.getMenuWeek(date1, cm )
    template_values['menu2'] = self.getMenuWeek(date2, cm )
    template_values['data'] = date
    template_values['data1'] = date1
    template_values['data2'] = date2
    template_values['cm'] = cm
    template_values['action'] = self.request.path
    #logging.info("CMMenuHandler.type: " + str(type(self)))
    super(CMMenuHandler,self).getBase(template_values)    

class CMCittaHandler(webapp.RequestHandler):
  def get(self):        
    citta = Citta.all()
    citlist = list()
    for c in citta:
      citlist.append({'key': str(c.key()), 'nome':c.nome, 'codice':c.codice, 'provincia':c.provincia, 'lat':c.geo.lat, 'lon':c.geo.lon})
      
    self.response.out.write(json.JSONEncoder().encode({'label':'nome', 'identifier':'key', 'items': citlist}))
    
    
    
def roleCommissario(func):
  def callf(basePage, *args, **kwargs):
    commissario = basePage.getCommissario(users.get_current_user())
    if commissario == None or commissario.isCommissario() == False:
      basePage.redirect("/")
    else:
      return func(basePage, *args, **kwargs)
  return callf    