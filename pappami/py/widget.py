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
    c = Commissione.get(self.request.get("cm"))
    if(c is not None):
          
      data = datetime.now().date()
      
      template_values = dict()
      template_values["data1"] = data
      template_values["menu1"] = self.getMenu(self.nextWorkingDay(data - timedelta(1)), c)
      template_values["data2"] = self.nextWorkingDay(data) + timedelta(1)
      template_values["menu2"] = self.getMenu(self.nextWorkingDay(data)+ timedelta(1), c)
      template_values["bgcolor"] = bgcolor
      template_values["fcolor"] = fcolor
      
      
      path = os.path.join(os.path.dirname(__file__), '../templates/widget/menu.html')
      self.response.out.write(template.render(path, template_values))

  def nextWorkingDay(self, data):
    if(data.isoweekday() < 6):
      data = data + timedelta(1)
    if(data.isoweekday() < 6):
      data = data + timedelta(1)
    return data
    
  def getMenu(self, data, c):
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
    return menu
      
class CMStatWidgetHandler(webapp.RequestHandler):
  
  def get(self): 

    bgcolor = self.request.get("bc")
    if(bgcolor is None): 
      bgcolor = "eeeeff"
    fcolor = self.request.get("fc")
    if(fcolor is None): 
      fcolor = "000000"
    c = Commissione.get(self.request.get("cm"))
    if(c is not None):
      
      stats = StatisticheIspezioni.all().filter("commissione",None).filter("centroCucina",None).order("-dataFine").get()
      statCC = StatisticheIspezioni.all().filter("centroCucina",c.centroCucina).order("-dataFine").get()
      statCM = StatisticheIspezioni.all().filter("commissione",c).order("-dataFine").get()
      
      template_values = dict()
      template_values["stats"] = stats
      template_values["statCC"] = statCC
      template_values["statCM"] = statCM
      template_values["bgcolor"] = bgcolor
      template_values["fcolor"] = fcolor
      
      path = os.path.join(os.path.dirname(__file__), '../templates/widget/stat.html')
      self.response.out.write(template.render(path, template_values))

def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
  ('/widget/menu', CMMenuWidgetHandler),
  ('/widget/stat', CMStatWidgetHandler)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
    