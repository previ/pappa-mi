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
    user = users.get_current_user()
    if user:
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values["test"] = self.request.url.find("test") != -1,
    template_values["user"] = user
    template_values["admin"] = users.is_current_user_admin()
    template_values["commissario"] = Commissario.all().filter("user", user).filter("stato", 1).get() is not None
    template_values["url"] = url
    template_values["url_linktext"] = url_linktext
    template_values["version"] = "0.3.0.7 - 2009.05.28"

    path = os.path.join(os.path.dirname(__file__), '../templates/main.html')
    self.response.out.write(template.render(path, template_values))

class MainPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "public.html"
    template_values["billboard"] = "billboard.html"
    #template_values["content_left"] = "leftbar.html"
    template_values["content_right"] = "rightbar.html"
    template_values["content_extra"] = "extra.html"

    news = memcache.get("news")
    if not news:
      news = py.feedparser.parse("http://groups.google.it/group/pappami-aggiornamenti/feed/atom_v1_0_msgs.xml")
      memcache.add("news",news)
      
    stats = self.getStats()
    template_values["stats"] = stats[0]
    template_values["news"] = news.entries
    
    self.getBase(template_values)

  def getStats(self):

    stats = memcache.get("stats")
    statsMese = memcache.get("statsMese")
    if(stats is None):
      stats = Statistiche()
      statsMese = Statistiche()
      
      for c in Commissione.all() :
        if c.numCommissari > 0:
          stats.numeroCommissioni = stats.numeroCommissioni + 1

      for isp in Ispezione.all().order("-dataIspezione"):
        stats.numeroSchede = stats.numeroSchede + 1;
        
        stats.primoAssaggio = stats.primoAssaggio + isp.primoAssaggio
        stats.primoGradimento = stats.primoGradimento + isp.primoGradimento
        stats.secondoAssaggio = stats.secondoAssaggio + isp.secondoAssaggio
        stats.secondoGradimento = stats.secondoGradimento + isp.secondoGradimento
        stats.contornoAssaggio = stats.contornoAssaggio + isp.contornoAssaggio
        stats.contornoGradimento = stats.contornoGradimento + isp.contornoGradimento
  
        stats.puliziaRefettorio = stats.puliziaRefettorio + isp.puliziaRefettorio
        stats.smaltimentoRifiuti = stats.smaltimentoRifiuti + isp.smaltimentoRifiuti
        stats.giudizioGlobale = stats.giudizioGlobale + isp.giudizioGlobale
  
        #if isp.ncPresenti() :
          #stats.ncTotali = stats.ncTotali + 1
           
        #if isp.ncRichiestaCampionatura:
          #stats.ncRichiestaCampionatura = stats.ncRichiestaCampionatura + 1 
  
        if( datetime.now().date() - isp.dataIspezione < timedelta(days = 30)):
          statsMese.numeroSchede = statsMese.numeroSchede + 1;
        
          statsMese.primoAssaggio = statsMese.primoAssaggio + isp.primoAssaggio
          statsMese.primoGradimento = statsMese.primoGradimento + isp.primoGradimento
          statsMese.secondoAssaggio = statsMese.secondoAssaggio + isp.secondoAssaggio
          statsMese.secondoGradimento = statsMese.secondoGradimento + isp.secondoGradimento
          statsMese.contornoAssaggio = statsMese.contornoAssaggio + isp.contornoAssaggio
          statsMese.contornoGradimento = statsMese.contornoGradimento + isp.contornoGradimento
  
          statsMese.puliziaRefettorio = statsMese.puliziaRefettorio + isp.puliziaRefettorio
          statsMese.smaltimentoRifiuti = statsMese.smaltimentoRifiuti + isp.smaltimentoRifiuti
          statsMese.giudizioGlobale = statsMese.giudizioGlobale + isp.giudizioGlobale

          #if isp.ncPresenti() :
            #statsMese.ncTotali = statsMese.ncTotali + 1

      if stats.numeroSchede > 0 :
        stats.primoAssaggio = stats.primoAssaggio / stats.numeroSchede
        stats.primoGradimento = stats.primoGradimento / stats.numeroSchede
        stats.secondoAssaggio = stats.secondoAssaggio / stats.numeroSchede
        stats.secondoGradimento = stats.secondoGradimento / stats.numeroSchede
        stats.contornoAssaggio = stats.contornoAssaggio / stats.numeroSchede
        stats.contornoGradimento = stats.contornoGradimento / stats.numeroSchede
  
        stats.puliziaRefettorio = stats.puliziaRefettorio / stats.numeroSchede
        stats.lavaggioFinale = stats.lavaggioFinale / stats.numeroSchede
        stats.smaltimentoRifiuti = stats.smaltimentoRifiuti / stats.numeroSchede
        stats.giudizioGlobale = stats.giudizioGlobale / stats.numeroSchede
  
      if statsMese.numeroSchede > 0 :
        statsMese.primoAssaggio = statsMese.primoAssaggio / statsMese.numeroSchede
        statsMese.primoGradimento = statsMese.primoGradimento / statsMese.numeroSchede
        statsMese.secondoAssaggio = statsMese.secondoAssaggio / statsMese.numeroSchede
        statsMese.secondoGradimento = statsMese.secondoGradimento / statsMese.numeroSchede
        statsMese.contornoAssaggio = statsMese.contornoAssaggio / statsMese.numeroSchede
        statsMese.contornoGradimento = statsMese.contornoGradimento / statsMese.numeroSchede
  
        statsMese.puliziaRefettorio = statsMese.puliziaRefettorio / statsMese.numeroSchede
        statsMese.lavaggioFinale = statsMese.lavaggioFinale / statsMese.numeroSchede
        statsMese.smaltimentoRifiuti = statsMese.smaltimentoRifiuti / statsMese.numeroSchede
        statsMese.giudizioGlobale = statsMese.giudizioGlobale / statsMese.numeroSchede

      for isp in Nonconformita.all().order("-dataNonconf"):
        stats.ncTotali = stats.ncTotali + 1
          
      memcache.add("stats", stats)
      memcache.add("statsMese", statsMese)
    return [stats, statsMese]

class CMCommissioneHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "map.html"
    self.getBase(template_values)

class CMSupportoHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "supporto.html"
    self.getBase(template_values)


class CMStatsHandler(BasePage):

  def getStats(self):

    stats = memcache.get("stats")
    statsMese = memcache.get("statsMese")
    if(stats is None):
      stats = Statistiche()
      statsMese = Statistiche()

      for c in Commissione.all() :
        if c.numCommissari > 0:
          stats.numeroCommissioni = stats.numeroCommissioni + 1
          
      for isp in Ispezione.all().order("-dataIspezione"):
        stats.numeroSchede = stats.numeroSchede + 1;
        
        stats.primoAssaggio = stats.primoAssaggio + isp.primoAssaggio
        stats.primoGradimento = stats.primoGradimento + isp.primoGradimento
        stats.secondoAssaggio = stats.secondoAssaggio + isp.secondoAssaggio
        stats.secondoGradimento = stats.secondoGradimento + isp.secondoGradimento
        stats.contornoAssaggio = stats.contornoAssaggio + isp.contornoAssaggio
        stats.contornoGradimento = stats.contornoGradimento + isp.contornoGradimento
  
        stats.puliziaRefettorio = stats.puliziaRefettorio + isp.puliziaRefettorio
        stats.smaltimentoRifiuti = stats.smaltimentoRifiuti + isp.smaltimentoRifiuti
        stats.giudizioGlobale = stats.giudizioGlobale + isp.giudizioGlobale
  
        #if isp.ncPresenti() :
          #stats.ncTotali = stats.ncTotali + 1
           
        #if isp.ncRichiestaCampionatura:
          #stats.ncRichiestaCampionatura = stats.ncRichiestaCampionatura + 1 
  
        if( datetime.now().date() - isp.dataIspezione < timedelta(days = 30)):
          statsMese.numeroSchede = statsMese.numeroSchede + 1;
        
          statsMese.primoAssaggio = statsMese.primoAssaggio + isp.primoAssaggio
          statsMese.primoGradimento = statsMese.primoGradimento + isp.primoGradimento
          statsMese.secondoAssaggio = statsMese.secondoAssaggio + isp.secondoAssaggio
          statsMese.secondoGradimento = statsMese.secondoGradimento + isp.secondoGradimento
          statsMese.contornoAssaggio = statsMese.contornoAssaggio + isp.contornoAssaggio
          statsMese.contornoGradimento = statsMese.contornoGradimento + isp.contornoGradimento
  
          statsMese.puliziaRefettorio = statsMese.puliziaRefettorio + isp.puliziaRefettorio
          statsMese.smaltimentoRifiuti = statsMese.smaltimentoRifiuti + isp.smaltimentoRifiuti
          statsMese.giudizioGlobale = statsMese.giudizioGlobale + isp.giudizioGlobale

          #if isp.ncPresenti() :
            #statsMese.ncTotali = statsMese.ncTotali + 1

      if stats.numeroSchede > 0 :
        stats.primoAssaggio = stats.primoAssaggio / stats.numeroSchede
        stats.primoGradimento = stats.primoGradimento / stats.numeroSchede
        stats.secondoAssaggio = stats.secondoAssaggio / stats.numeroSchede
        stats.secondoGradimento = stats.secondoGradimento / stats.numeroSchede
        stats.contornoAssaggio = stats.contornoAssaggio / stats.numeroSchede
        stats.contornoGradimento = stats.contornoGradimento / stats.numeroSchede
  
        stats.puliziaRefettorio = stats.puliziaRefettorio / stats.numeroSchede
        stats.lavaggioFinale = stats.lavaggioFinale / stats.numeroSchede
        stats.smaltimentoRifiuti = stats.smaltimentoRifiuti / stats.numeroSchede
        stats.giudizioGlobale = stats.giudizioGlobale / stats.numeroSchede
  
      if statsMese.numeroSchede > 0 :
        statsMese.primoAssaggio = statsMese.primoAssaggio / statsMese.numeroSchede
        statsMese.primoGradimento = statsMese.primoGradimento / statsMese.numeroSchede
        statsMese.secondoAssaggio = statsMese.secondoAssaggio / statsMese.numeroSchede
        statsMese.secondoGradimento = statsMese.secondoGradimento / statsMese.numeroSchede
        statsMese.contornoAssaggio = statsMese.contornoAssaggio / statsMese.numeroSchede
        statsMese.contornoGradimento = statsMese.contornoGradimento / statsMese.numeroSchede
  
        statsMese.puliziaRefettorio = statsMese.puliziaRefettorio / statsMese.numeroSchede
        statsMese.lavaggioFinale = statsMese.lavaggioFinale / statsMese.numeroSchede
        statsMese.smaltimentoRifiuti = statsMese.smaltimentoRifiuti / statsMese.numeroSchede
        statsMese.giudizioGlobale = statsMese.giudizioGlobale / statsMese.numeroSchede
    
      memcache.add("stats", stats)
      memcache.add("statsMese", statsMese)
    
    return [stats, statsMese]
  
  def get(self):
    s = self.getStats()

    template_values = dict()
    template_values["content"] = "stats.html"
    template_values["stats"] = s[0]
    template_values["statsMese"] = s[1]
    self.getBase(template_values)

    
class CMMenuHandler(webapp.RequestHandler):
  
  def get(self): 
    if( self.request.get("cmd") == "getbydate" ):
      menu = Menu();
      data = datetime.strptime(self.request.get("data"),DATE_FORMAT).date()

      #logging.info("data: %s", data)

      menus = Menu.all().filter("validitaDa <=", data).filter("giorno", data.isoweekday()).filter("tipoScuola", Commissione.get(self.request.get("commissione")).tipoScuola).order("-validitaDa")

      #logging.info("len %d" , menus.count())

      for m in menus:
        #logging.info("s %d g %d, sc: %d, gc: %d", m.settimana, m.giorno, ((((data-m.validitaDa).days) / 7)%4)+1, data.isoweekday())
        if(((((data-m.validitaDa).days) / 7)%4+1) == m.settimana):
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
          
        commissioni = Commissione.all()
          
        markers = "<markers>\n"
        try:
          for c in commissioni :
            if c.geo:
              markers = markers + '<marker nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta + '"'
              markers = markers + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" />\n'
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
            markers = markers + '<marker nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta + '"'
            markers = markers + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" />\n'
        except db.Timeout:
          logging.error("Timeout")
          
        markers = markers + "</markers>"    
        memcache.add("markers", markers)
      
      #logging.info(markers)
      self.response.out.write(markers)

application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/map', CMMapHandler),
  ('/stats', CMStatsHandler),
  ('/menu', CMMenuHandler),
  ('/commissione', CMCommissioneHandler),
  ('/supporto', CMSupportoHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
