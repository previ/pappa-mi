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

class CMMenuWidgetHandler(webapp.RequestHandler):
  
  def get(self): 
    menu = Menu();

    bgcolor = self.request.get("bc")
    if(bgcolor is None): 
      bgcolor = "eeeeff"
    fcolor = self.request.get("fc")
    if(fcolor is None): 
      fcolor = "000000"

    template_values = dict()
    template_values["bgcolor"] = bgcolor
    template_values["fcolor"] = fcolor

    c = None
    if self.request.get("cm"):
      c = Commissione.get(self.request.get("cm"))
    
    self.createMenu(self.request,c,template_values)
    
    path = os.path.join(os.path.dirname(__file__), '../templates/widget/menu2.html')
    self.response.out.write(template.render(path, template_values))

  def createMenu(self,request,c,template_values):
    menu = Menu();
       
    data = self.workingDay(datetime.now().date())
    
    template_values["data"] = data
    template_values["menu"] = self.getMenu(data, c)
    
  def workingDay(self, data):
    while data.isoweekday() > 5:
      data += timedelta(1)      
    return data
    
  def getMenu(self, data, c):
    offset = -1
    if c and c.centroCucina.menuOffset is not None:
      offset = c.centroCucina.menuOffset      

    menu = memcache.get("menu" + str(offset))
    if not menu:
      #logging.info(offset)
      menus = Menu.all().filter("validitaDa <=", data).filter("giorno", data.isoweekday()).order("-validitaDa")
      #logging.info("len %d" , menus.count())
  
      menu = list()
      for m in menus:
        #logging.info("s %d g %d, sc: %d, gc: %d", m.settimana, m.giorno, ((((data-m.validitaDa).days) / 7)%4)+1, data.isoweekday())
        if((((((data-m.validitaDa).days) / 7)+offset)%4 + 1) == m.settimana or offset == -1):
          menu.append(m)
          if((offset == -1 and len(menu) >=4) or (offset >=0 )):
            break
  
      menu = sorted(menu, key=lambda menu: menu.settimana)
      memcache.set("menu" + str(offset), menu, 60)
    return menu
  
class CMStatWidgetHandler(webapp.RequestHandler):
  
  def get(self): 

    bgcolor = self.request.get("bc")
    if(bgcolor == ""): 
      bgcolor = "eeeeff"
    fcolor = self.request.get("fc")
    if(fcolor == ""): 
      fcolor = "000000"

    template_values = dict()
    template_values["bgcolor"] = bgcolor
    template_values["fcolor"] = fcolor

    c = None
    if self.request.get("cm"):
      c = Commissione.get(self.request.get("cm"))
    
    self.createStat(self.request,c,template_values)
    
    t = ""
    if self.request.get("t") == "c":
      t = "_" + self.request.get("t")

    template_values["wcontent"] = "stat" + t + ".html"
    
    path = os.path.join(os.path.dirname(__file__), '../templates/widget/wstat.html')
    self.response.out.write(template.render(path, template_values))

  def createStat(self,request,c,template_values):

    now = datetime.now().date()
    year = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1

    stats = memcache.get("statAll")
    if not stats:
      logging.info("statAll miss")
      stats = StatisticheIspezioni.all().filter("commissione",None).filter("centroCucina",None).filter("timeId", year).get()
      memcache.set("statAll", stats, 60)

    statCC = None
    statCM = None
    if c:
      statCC = memcache.get("statCC" + str(c.centroCucina.key()))
      if not statCC:
        logging.info("statCC miss")
        statCC = StatisticheIspezioni.all().filter("centroCucina",c.centroCucina).filter("timeId", year).get()
        memcache.set("statCC" + str(c.centroCucina.key()), statCC)
      statCM = memcache.get("statCM" + str(c.key()))
      if not statCM:
        logging.info("statCM miss")
        statCM = StatisticheIspezioni.all().filter("commissione",c).filter("timeId", year).get()
        memcache.set("statCM" + str(c.key()), statCM, 3600)
      
    template_values["stats"] = stats
    template_values["statCC"] = statCC
    template_values["statCM"] = statCM
    
def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
  ('/widget/menu', CMMenuWidgetHandler),
  ('/widget/stat', CMStatWidgetHandler)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
    