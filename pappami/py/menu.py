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

from py.base import BasePage, CMMenuHandler, Const, ActivityFilter, commissario_required, user_required, config
import cgi, logging, os
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import fixpath

from google.appengine.ext.ndb import model
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache

from py.model import *
from py.modelMsg import *
from py.comments import *

class CMMenuDataHandler(CMMenuHandler):
  
  def get(self): 
    if( self.request.get("cmd") == "getbydate" ):
      menu = Menu();
      data = datetime.strptime(self.request.get("data"),Const.DATE_FORMAT).date()
      c = model.Key("Commissione", int(self.request.get("commissione"))).get()
      menus = self.getMenu(data, c)      
      if len(menus):
        menu = self.getMenu(data, c)[0]
      
      json.dump(menu.to_dict(), self.response.out)

    else:
      template_values = dict()
      template_values['content'] = 'menu.html'      
      template_values["todayofweek"] = self.get_next_working_day(datetime.now().date()).isoweekday()
      template_values["citta"] = Citta.get_all()
      self.getBase(template_values)

  def post(self):
    cm_key = self.get_context().get("cm_key")
    cm = None
    if cm_key:
      cm = model.Key("Commissione", cm_key).get()
    if self.request.get("cm"):
      logging.info(self.request.get("cm"))
      cm = model.Key("Commissione", int(self.request.get("cm"))).get()
    
    template_values = dict()
    template_values['content'] = 'menu.html'      
    template_values["citta"] = Citta.get_all()
    template_values["todayofweek"] = self.get_next_working_day(datetime.now().date()).isoweekday()

    if cm:
      self.get_context()["citta_key"] = cm.citta.id()
      self.get_context()["cm_key"] = cm.key.id()
      self.get_context()["cm_name"] = cm.desc()    
      
    self.getBase(template_values)
    
      

class CMMenuSlideHandler(CMMenuHandler):
  
  def get(self): 
    template_values = dict()
    template_values['main'] = 'menu_slides.html'    
    self.getBase(template_values)

app = webapp.WSGIApplication([
  ('/menu', CMMenuDataHandler),
  ('/menuslide', CMMenuSlideHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

def main():
  app.run();

if __name__ == "__main__":
  main()
    