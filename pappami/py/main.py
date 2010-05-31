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
      url_linktext = 'Logout'
    else:
      url = "/login"
      url_linktext = 'Login'
    if self.request.url.find("test") != -1 :
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
      
    
    template_values["user"] = user
    template_values["admin"] = users.is_current_user_admin()
    template_values["url"] = url
    template_values["url_linktext"] = url_linktext
    template_values["version"] = "0.6.1.16 - 2010.05.16"

    path = os.path.join(os.path.dirname(__file__), '../templates/main.html')
    self.response.out.write(template.render(path, template_values))

  def getCommissario(self,user):
    return Commissario.all().filter("user", user).get()
  
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
  
  def get(self):
    template_values = dict()
    template_values["content"] = "public.html"
    template_values["billboard"] = "billboard.html"
    #template_values["content_left"] = "leftbar.html"
    template_values["content_right"] = "rightbar.html"
    template_values["content_extra"] = "extra.html"

    news = memcache.get("news")
    i = 0
    if news is None:
      #news_all = py.feedparser.parse(self.request.url + "/js/atom_v1_0_msgs.xml")
      news_all = py.feedparser.parse("http://blog.pappa-mi.it/feeds/posts/default")
      logging.debug(news_all)
      news = []
      for n in news_all.entries:
        #logging.debug(n)
        if i >= 2 :
          break
        i = i + 1
        news.append(n)
        
      memcache.add("news",news)
      
    stats = self.getStats()
    template_values["stats"] = stats
    template_values["news"] = news

    if(len(news)>0):
      template_values["newsMsg"] = news[0].content[0]
    
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

class CMCommissioneHandler(BasePage):
    
  @login_required
  def get(self):
    template_values = dict()
    template_values["content"] = "map.html"
    template_values["centriCucina"] = CentroCucina.all().order("nome")
    self.getBase(template_values)

class CMSupportoHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "supporto.html"
    self.getBase(template_values)
    
class CMCondizioniHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "condizioni.inc"
    self.getBase(template_values)
    
class CMMenuHandler(webapp.RequestHandler):
  
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
        
class CMMapHandler(webapp.RequestHandler):
  
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

def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
  ('/', MainPage),
  #('/fb', FbPage),
  ('/docs', DocPage),
  #('/blog', BlogPage),
  ('/map', CMMapHandler),
  ('/menu', CMMenuHandler),
  ('/commissioni', CMCommissioneHandler),
  ('/supporto', CMSupportoHandler),
  ('/condizioni', CMCondizioniHandler)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
