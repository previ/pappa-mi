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

from py.gviz_api import *
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
      if( commissario.ultimo_accesso_il is None or datetime.now() - commissario.ultimo_accesso_il > timedelta(minutes=60) ):
        commissario.ultimo_accesso_il = datetime.now()
        commissario.put()
        memcache.set("commissario" + str(user.user_id()), commissario, 600)
      template_values["commissario"] = commissario.isCommissario()
      template_values["genitore"] = commissario.isGenitore()
      #logging.info("commissario: " + str(commissario.isCommissario()))
      #logging.info("genitore: " + str(commissario.isGenitore()))
    
    template_values["user"] = user
    template_values["admin"] = users.is_current_user_admin()
    template_values["url"] = url
    template_values["url_linktext"] = url_linktext
    template_values["version"] = "1.0.0.21 - 2010.06.22"

    path = os.path.join(os.path.dirname(__file__), '../templates/main.html')
    self.response.out.write(template.render(path, template_values))

  def getCommissario(self,user):
    commissario = None
    if(user):
      #commissario = memcache.get("user" + str(user.user_id()))
      #if not commissario:
        commissario = Commissario.all().filter("user = ", user).get()
        #memcache.add("user" + str(user.user_id()), commissario, 600)
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

class CMCommissioniDataHandler(BasePage):

  def get(self): 
    user = users.get_current_user()
    buff = memcache.get("cmall")
    if(buff is None):
  
      description = {"nome": ("string", "Nome"), 
                     "key": ("string", "Key")}
      data_table = DataTable(description)
      
      cms = Commissione.all().order("nome")
      buff = ""
      buff = '{"label": "nome", "identifier": "key", "items": ['
      buff = buff + '{ "nome": "", "key": ""},'
  
      
      notfirst = False
      for cm in cms.order("nome"):
        if(notfirst) :
          buff = buff + ','
        notfirst = True
        buff = buff + '{ "nome": "' + cm.nome + ' - ' + cm.tipoScuola + '", "key": "' + str(cm.key()) + '"}'
        
      buff = buff + ']}'
      memcache.add("cmall", buff)
        
    expires_date = datetime.utcnow() + timedelta(20)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)

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
    #logging.info("len %d" , menus.count())

    count = 0
    for m in menus:
      if((((((data-m.validitaDa).days) / 7)+offset)%4 + 1) == m.settimana):
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
    #logging.info("CMMenuHandler.type: " + str(type(self)))
    super(CMMenuHandler,self).getBase(template_values)    
    