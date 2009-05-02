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

from py.model import *

TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class MainPage(webapp.RequestHandler):
  
  def get(self):
    user = users.get_current_user()
    if user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'user': user,
      'admin': users.is_current_user_admin(),
      'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
      'url': url,
      'url_linktext': url_linktext
      }

    path = os.path.join(os.path.dirname(__file__), '../templates/public.html')
    self.response.out.write(template.render(path, template_values))

class CMCommissioneHandler(webapp.RequestHandler):
  
  def get(self):
    user = users.get_current_user()
    if user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'user': user,
      'admin': users.is_current_user_admin(),
      'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
      'test': self.request.url.find("test") != -1,
      'url': url,
      'url_linktext': url_linktext
      }

    path = os.path.join(os.path.dirname(__file__), '../templates/map.html')
    self.response.out.write(template.render(path, template_values))

class CMStatsHandler(webapp.RequestHandler):

  def getStats(self):

    stats = memcache.get("stats")
    statsMese = memcache.get("statsMese")
    if(stats is None):
      stats = Statistiche()
      statsMese = Statistiche()
      
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
  
        if isp.ncPresenti() :
          stats.ncTotali = stats.ncTotali + 1
           
        if isp.ncRichiestaCampionatura:
          stats.ncRichiestaCampionatura = stats.ncRichiestaCampionatura + 1 
  
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

          if isp.ncPresenti() :
            statsMese.ncTotali = statsMese.ncTotali + 1

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
    user = users.get_current_user()
    if user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    s = self.getStats()
    
    template_values = {
      'user': user,
      'admin': users.is_current_user_admin(),
      'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
      'url': url,
      'url_linktext': url_linktext,
      'stats': s[0],
      'statsMese': s[1]
      }

    path = os.path.join(os.path.dirname(__file__), '../templates/stats.html')
    self.response.out.write(template.render(path, template_values))
    
class CMMenuHandler(webapp.RequestHandler):
  
  def get(self): 
    if( self.request.get("cmd") == "getbydate" ):
      menu = Menu();
      data = datetime.strptime(self.request.get("data"),DATE_FORMAT).date()

      menus = Menu.all().filter("validitaDa <", data).filter("giorno", data.isoweekday()).filter("centroCucina", Commissione.get(self.request.get("commissione")).centroCucina)

      logging.info("len %d" , menus.count())

      for m in menus:
        #logging.info("settimana %d giorno %d", m.settimana, m.giorno)
        if(((data-m.validitaDa).days - data.isoweekday()) / 7 % 4 == m.settimana):
          menu = m
      
      self.response.out.write(menu.primo)
      self.response.out.write("|")
      self.response.out.write(menu.secondo)
      self.response.out.write("|")
      self.response.out.write(menu.contorno)
      self.response.out.write("\n")
        
class CMMapHandler(webapp.RequestHandler):
  
  def get(self): 
    commissioni = Commissione.all().order("nome")
      
    self.response.out.write("<markers>\n")
    for c in commissioni :
      if(c.geo):
        self.response.out.write("<marker nome=\"")
        self.response.out.write(c.nome)
        self.response.out.write("\" indirizzo=\"")
        self.response.out.write(c.strada)
        self.response.out.write(", ")
        self.response.out.write(c.civico)
        self.response.out.write(", ")
        self.response.out.write(c.citta)
        self.response.out.write("\" lat=\"")
        self.response.out.write(c.geo.lat)
        self.response.out.write("\" lon=\"")
        self.response.out.write(c.geo.lon)
        self.response.out.write("\" tipo=\"school\" />\n") 

    self.response.out.write("</markers>")
    
application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/map', CMMapHandler),
  ('/stats', CMStatsHandler),
  ('/menu', CMMenuHandler),
  ('/commissione', CMCommissioneHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
