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

from py.base import BasePage, CMMenuHandler, Const, ActivityFilter, commissario_required, user_required, config, handle_404, handle_500
import cgi, logging, os
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import fixpath
from google.appengine.api import urlfetch
from HTMLParser import HTMLParser

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

class MenuScraper(BasePage):
  
  def get(self): 
    template_values = dict()
    
    response = urlfetch.fetch('http://www.milanoristorazione.it/cosa-si-mangia/ricerca-menu?ps=mese&codRefe=000413&x1=01&x2=05&x3=2012', deadline=60)
    p = MenuParser()
    p.text = ""
    p.feed(response.content)
    
    self.response.out.write(p.text)


# create a subclass and override the handler methods
class MenuParser(HTMLParser):    
  

  piatti = set()
  settimane = list()
  
  curr_id = ""
  def handle_starttag(self, tag, attrs):
    for attrid, attrvalue in attrs:
      if attrid == "id":
        self.curr_id=attrvalue
    
  def handle_endtag(self, tag):
    pass     

  def handle_data(self, data):
    #logging.info(data)
    if self.curr_id == "divmleftletter":
      logging.info(data)
      self.text += "\n" + data + "|"
      self.curr_id=""
    if self.curr_id == "divplatedesc":
      logging.info(data)
      self.text += data + "|"
      self.curr_id=""
    
  
app = webapp.WSGIApplication([
  ('/menu', CMMenuDataHandler),
  ('/menuslide', CMMenuSlideHandler),
  ('/menu/scrape', MenuScraper),
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()
    