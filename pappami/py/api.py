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


from py.base import *

import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import webapp2 as webapp


from google.appengine.ext.ndb import model
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.modelMsg import *
from py.form import IspezioneForm, NonconformitaForm
from py.base import BasePage, CMMenuHandler, config, handle_404, handle_500

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class UserApiHandler(BasePage):
  
  @reguser_required
  def get(self): 
    co = self.getCommissario()
    user_schools = list()
    for cm in co.commissioni():
      user_schools.append({'id': str(cm.key.id()),
                        'name': cm.desc()})
    user_api = {'id': str(co.usera.id()),
                'fullname': str(co.nomecompleto(None,True)),
                'schools': user_schools}
    self.output_as_json(user_api)

class MenuApiHandler(CMMenuHandler):
      
  @reguser_required
  def get(self): 

    menu_api = []
    data = datetime.strptime(self.request.get("date"),Const.DATE_FORMAT).date()
    c = model.Key("Commissione", int(self.request.get("school"))).get()
    menus = self.getMenu(data, c)      
    if len(menus):
      menu = self.getMenu(data, c)[0]
      menu_api = [
        { 'id': menu.primo.key.id(),
          'desc1': menu.primo.nome,
          'desc2': 'primo'},
        { 'id': menu.secondo.key.id(),
          'desc1': menu.secondo.nome,
          'desc2': 'secondo' },
        { 'id': menu.contorno.key.id(),
          'desc1': menu.contorno.nome,
          'desc2': 'contorno' },
        { 'id': menu.dessert.key.id(),
          'desc1': menu.dessert.nome,
          'desc2': 'dessert' }];

    self.output_as_json(menu_api)

 
    
app = webapp.WSGIApplication([
    ('/api/getuser', UserApiHandler),
    ('/api/getmenu', MenuApiHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()