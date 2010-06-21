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

import os
import cgi
import logging
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
import py.feedparser
from py.widget import CMMenuWidgetHandler, CMStatWidgetHandler

from py.model import *

TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class BasePage(webapp.RequestHandler):
  def getBase(self, template_values):
    
    if self.request.url.find("appspot.com") != -1 and self.request.url.find("test") == -1:
      self.redirect("http://www.pappa-mi.it")
        
    user = users.get_current_user()
    if user:
      url = users.create_logout_url("/")
      url_linktext = 'Esci'
    else:
      url = "/login"
      url_linktext = 'Accedi'
    if self.request.url.find("/test") != -1 :
      template_values["test"] = "true"
    if self.request.url.find("www.pappa-mi.it") != -1 :
      template_values["pappamiit"] = "true"
      
    commissario = self.getCommissario(user)
    if( commissario is not None ) :
      if( commissario.ultimo_accesso_il is None or datetime.now() - commissario.ultimo_accesso_il > timedelta(minutes=1) ):
        commissario.ultimo_accesso_il = datetime.now()
        commissario.put()
      template_values["commissario"] = commissario.isCommissario()
      template_values["genitore"] = commissario.isGenitore()
      #logging.info("commissario: " + str(commissario.isCommissario()))
      #logging.info("genitore: " + str(commissario.isGenitore()))
    
    template_values["user"] = user
    template_values["admin"] = users.is_current_user_admin()
    template_values["url"] = url
    template_values["url_linktext"] = url_linktext
    template_values["version"] = "1.0.0.20 - 2010.06.21"

    path = os.path.join(os.path.dirname(__file__), '../templates/main.html')
    self.response.out.write(template.render(path, template_values))

  def getCommissario(self,user):
    commissario = None
    if(user):
      #logging.info("user email: " + user.email() + " id: " + user.user_id())
      #commissario = Commissario.all().filter("user = ", users.User(users.get_current_user().email())).get()
      commissario = Commissario.all().filter("user = ", user).get()
    #query = db.GqlQuery("SELECT * FROM Commissario WHERE user = USER(:usr)", usr = users.get_current_user().email())
    #commissario = query.get()
    #if(commissario):
      #logging.info("commissario: " + commissario.nome)
    return commissario
  
  def getCommissioni(self):
    commissioni = memcache.get("commissioni")
    if commissioni == None:
      commissioni = Commissione.all().order("nome");
      memcache.add("commissioni", commissioni)
    return commissioni
  
  def getHost(self):
    host = self.request.url[len("http://"):]
    host = host[:host.find("/")]
    #logging.info("host: " + host)
    return host
  
class MainPage(BasePage):

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
        
      memcache.add("news_pappami",news)
    return news
  
  def get(self):
    template_values = dict()
    template_values["content"] = "public.html"
    template_values["billboard"] = "billboard.html"
    template_values["content_left"] = "leftbar.html"
    template_values["content_right"] = "rightbar.html"
    template_values["content_extra"] = "extra.html"
    template_values["host"] = self.getHost()
  
    stats = self.getStats()

    c = None
    if self.getCommissario(users.get_current_user()):
      if len(self.getCommissario(users.get_current_user()).commissioni()) > 0:
        c = self.getCommissario(users.get_current_user()).commissioni()[0]        
    
    CMMenuWidgetHandler().createMenu(self.request,c,template_values)
    CMStatWidgetHandler().createStat(self.request,c,template_values)
    template_values["bgcolor"] = "eeeeff"
    template_values["fgcolor"] = "000000"
    
    template_values["stat"] = stats
    template_values["news_pappami"] = self.getNews("news_pappami")
    template_values["news_pappami_alt"] = "http://blog.pappa-mi.it/"
    template_values["news_web"] = self.getNews("news_web")
    template_values["news_cal"] = self.getNews("news_cal")

    #if(len(self.getNews("news_pappami"))>0):
    #  template_values["newsMsg"] = self.getNews("news_pappami")[0].content[0]

    self.getBase(template_values)

  def getStats(self):
    stats = memcache.get("stats")
    if(stats is None):
      stats = Statistiche()
      stats.numeroCommissioni = Commissione.all().filter("numCommissari >",0).count()
      stats.numeroSchede = Ispezione.all().count()      
      stats.ncTotali = Nonconformita.all().count()
      memcache.add("stats", stats)
      
    return stats

class CMCommissioniHandler(BasePage):
      
  def getBase(self,template_values):
    template_values["content"] = "map.html"
    template_values["limit"] = 500
    template_values["centriCucina"] = CentroCucina.all().order("nome")
    template_values['action'] = self.request.path
    super(CMCommissioniHandler,self).getBase(template_values)

class CMMenuHandler(BasePage):
  def getMenu(self, data, cm): 
    menu = list();

    #logging.info("data: %s", data)

    cc = cm.centroCucina
    offset = cc.menuOffset
    if offset == None:
      offset = 0
      
    # settimana corrente
    menus = Menu.all().filter("validitaDa <=", data).filter("tipoScuola", cm.tipoScuola).order("-validitaDa")
    logging.info("len %d" , menus.count())

    count = 0
    for m in menus:
      if((((((data-m.validitaDa).days) / 7)+offset)%4 + 1) == m.settimana):
        menu.append(m)
        logging.info("m" + m.primo)
        count += 1
        if count >=5 :
          break

    return sorted(menu, key=lambda menu: menu.giorno)
      
  def getBase(self,template_values):
    cm = None
    commissario = self.getCommissario(users.get_current_user())
    if self.request.get("cm") != "":
      cm = Commissione.get(self.request.get("cm"))
    elif commissario and len(commissario.commissioni()) :
      cm = commissario.commissioni()[0]
    else:
      cm = Commissione.all().get()
    date = self.request.get("data")
    if date:
      date = datetime.strptime(date,DATE_FORMAT).date()
    else:
      date = datetime.now().date()
    
    date1 = date - timedelta(datetime.now().isoweekday() - 1)
    date2 = date1 + timedelta(7)
    template_values['content'] = 'menu.html'
    template_values['menu1'] = self.getMenu(date1, cm )
    template_values['menu2'] = self.getMenu(date2, cm )
    template_values['data'] = date
    template_values['data1'] = date1
    template_values['data2'] = date2
    template_values['cm'] = cm
    template_values['action'] = self.request.path
    super(CMMenuHandler,self).getBase(template_values)    
    
class CMSupportoHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "supporto.html"
    self.getBase(template_values)
    
class CMCondizioniHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "condizioni.html"
    self.getBase(template_values)

class CMRegistrazioneHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "registrazione.html"
    self.getBase(template_values)
    
class CMMenuDataHandler(webapp.RequestHandler):
  
  def get(self): 
    if( self.request.get("cmd") == "getbydate" ):
      menu = Menu();
      data = datetime.strptime(self.request.get("data"),DATE_FORMAT).date()

      #logging.info("data: %s", data)

      c = Commissione.get(self.request.get("commissione"))
      cc = c.centroCucina
      offset = cc.menuOffset
      if offset == None:
        offset = 0
        
      menus = Menu.all().filter("validitaDa <=", data).filter("giorno", data.isoweekday()).filter("tipoScuola", c.tipoScuola).order("-validitaDa")
      #logging.info("len %d" , menus.count())

      for m in menus:
        #logging.info("s %d g %d, sc: %d, gc: %d", m.settimana, m.giorno, ((((data-m.validitaDa).days) / 7)%4)+1, data.isoweekday())
        if((((((data-m.validitaDa).days) / 7)+offset)%4 + 1) == m.settimana):
          menu = m
          break
      
      self.response.out.write(menu.primo)
      self.response.out.write("|")
      self.response.out.write(menu.secondo)
      self.response.out.write("|")
      self.response.out.write(menu.contorno)
      self.response.out.write("\n")
        
class CMMapDataHandler(webapp.RequestHandler):
  
  def get(self): 
    if self.request.get("cmd") == "all":
      markers = memcache.get("markers_all")
      if(markers == None):
          
        commissioni = Commissione.all().order("nome");
          
        markers = "<markers>\n"
        try:
          for c in commissioni :
            if c.geo:
              markers = markers + '<marker nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta + '"'
              markers = markers + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" cc="' + c.centroCucina.key().name() + '" />\n'
        except db.Timeout:
          logging.error("Timeout")
          
        markers = markers + "</markers>"    
        memcache.add("markers_all", markers)
      
      #logging.info(markers)
      self.response.out.write(markers)      
    else:
      markers = memcache.get("markers")
      if(markers == None):
          
        commissioni = Commissione.all().filter("numCommissari >", 0)
          
        markers = "<markers>\n"
        try:
          for c in commissioni :
            if c.geo :
              markers = markers + '<marker nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta + '"'
              markers = markers + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" cc="' + c.centroCucina.key().name() + '" />\n'
        except db.Timeout:
          logging.error("Timeout")
          
        markers = markers + "</markers>"    
        memcache.add("markers", markers)
      
      #logging.info(markers)
      self.response.out.write(markers)

class DocPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "docs.html"
    template_values["iframesrc"] = "http://docs.pappa-mi.it/allegati"
    self.getBase(template_values)

class BlogPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "docs.html"
    template_values["iframesrc"] = "http://blog.pappa-mi.it/"
    self.getBase(template_values)

class FbPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "fb.html"
    self.getBase(template_values)

class ChiSiamoPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "chi.html"
    self.getBase(template_values)

class CMWidgetHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "widget/widgetindex.html"
    template_values["host"] = self.getHost()
    self.getBase(template_values)
    
def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
  ('/', MainPage),
  #('/fb', FbPage),
  ('/docs', DocPage),
  #('/blog', BlogPage),
  ('/chi', ChiSiamoPage),
  ('/map', CMMapDataHandler),
  ('/menu', CMMenuDataHandler),
  ('/supporto', CMSupportoHandler),
  ('/condizioni', CMCondizioniHandler),
  ('/registrazione', CMRegistrazioneHandler),
  ('/getwidget', CMWidgetHandler)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
