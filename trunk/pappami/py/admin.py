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
from py.form import CommissioneForm


TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class CMAdminMenuHandler(webapp.RequestHandler):

  def get(self):    

    user = users.get_current_user()
    url = users.create_logout_url("/")
    url_linktext = 'Logout'

    template_values = {
      'user': user,
      'admin': users.is_current_user_admin(),
      'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
      'url': url,
      'url_linktext': url_linktext
    }

    if( self.request.get("data") ):
      data = datetime.strptime(self.request.get("data"),DATE_FORMAT).date()
      menu = Menu.all().filter("validitaA >=", data).order("-validitaA").order("settimana").order("giorno")
      template_values['data'] = data
      template_values['menu'] = menu

    path = os.path.join(os.path.dirname(__file__), '../templates/admin/menu.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):    
    if( self.request.get("cmd") == "list" ):

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      template_values = {
        'user': user,      
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext,
      }

      if( self.request.get("data") ):
        data = datetime.strptime(self.request.get("data"),DATE_FORMAT).date()
        menu = Menu.all().filter("validitaA >=", data).order("-validitaA").order("settimana").order("giorno")
        template_values['data'] = data
        template_values['menu'] = menu

      path = os.path.join(os.path.dirname(__file__), '../templates/admin/menu.html')
      self.response.out.write(template.render(path, template_values))


class CMAdminCommissioneHandler(webapp.RequestHandler):

  def get(self):    

    if self.request.get("cmd") == "open":

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      key = ""
      
      if(self.request.get("key") == ""):
        commissione = Commissione()       
      else:
        commissione = Commissione.get(self.request.get("key"))    
        key = commissione.key()
              
      template_values = {
        'commissione': commissione,
        'key': key,
        'centriCucina': CentroCucina.all().order("nome"),
        'user': user,      
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/commissione.html')
      self.response.out.write(template.render(path, template_values))
    
    else:
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      centriCucina = CentroCucina.all().order("nome")
 
      template_values = {
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'centriCucina': centriCucina,
        'url': url,
        'url_linktext': url_linktext,
        'user': user
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/commissioni.html')
      self.response.out.write(template.render(path, template_values))

  def post(self):    
    if( self.request.get("cmd") == "save" ):
      if self.request.get("key"):
        commissione = Commissione.get(self.request.get("key"))
      else:
        commissione = Commissione()
        
      form = CommissioneForm(data=self.request.POST, instance=commissione)
      
      if form.is_valid():
        commissione = form.save(commit=False)
        commissione.geo = db.GeoPt(float(self.request.get("lat")), float(self.request.get("lon")))
        commissione.put()

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()
              
      commissioni = Commissione.all().order("nome")
      template_values = {
        'commissioni': commissioni,
        'user': user,      
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/commissioni.html')
      self.response.out.write(template.render(path, template_values))

    elif self.request.get("cmd") == "list":
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()
 
      centriCucina = CentroCucina.all().order("nome")
      
      #if query.is_valid():
      commissioni = Commissione.all()
      if self.request.get("tipoScuola") :
        commissioni = commissioni.filter("tipoScuola", self.request.get("tipoScuola"))
      if self.request.get("centroCucina") :
        commissioni = commissioni.filter("centroCucina", CentroCucina.get(self.request.get("centroCucina")))
      if self.request.get("nome") :
        commissioni = commissioni.filter("nome>=", self.request.get("nome"))
        commissioni = commissioni.filter("nome<", self.request.get("nome") + u'\ufffd')

      template_values = {
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext,
        'commissioni': commissioni,
        'centriCucina': centriCucina,
        'tipoScuola': self.request.get("tipoScuola"),
        'centroCucina': self.request.get("centroCucina"),
        'nome': self.request.get("nome"),
        'user': user
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/commissioni.html')
      self.response.out.write(template.render(path, template_values))

class CMAdminHandler(webapp.RequestHandler):

  def get(self):    
    if( self.request.get("cmd") == "init" ):

      commissione = Commissione(nome="Commissione Materna Muzio", nomeScuola="Scuola Materna Muzio", strada="Via Muzio", civico="9", citta="Milano", cap="20124", telefono="0212345678", geo=db.GeoPt(45.4912543, 9.1995684))
      commissione.put()

      commissione = Commissione(nome="Commissione Elementare Muzio", nomeScuola="Scuola Elementare Muzio", strada="Via Muzio", civico="9", citta="Milano", cap="20124", telefono="0212345678", geo=db.GeoPt(45.4912543, 9.1995684))
      commissione.put()
      commissario = Commissario(user=users.User("test@example.com"), nome="Barba", cognome="Papa", commissione=commissione)
      commissario.put()
    
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 1, giorno = 1, primo="Primo 1 - 1", secondo="Secondo 1 - 1", contorno="Contorno 1 - 1")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 1, giorno = 2, primo="Primo 1 - 2", secondo="Secondo 1 - 2", contorno="Contorno 1 - 2")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 1, giorno = 3, primo="Primo 1 - 3", secondo="Secondo 1 - 3", contorno="Contorno 1 - 3")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 1, giorno = 4, primo="Primo 1 - 4", secondo="Secondo 1 - 4", contorno="Contorno 1 - 4")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 1, giorno = 5, primo="Primo 1 - 5", secondo="Secondo 1 - 5", contorno="Contorno 1 - 5")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 2, giorno = 1, primo="Primo 2 - 1", secondo="Secondo 2 - 1", contorno="Contorno 2 - 1")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 2, giorno = 2, primo="Primo 2 - 2", secondo="Secondo 2 - 2", contorno="Contorno 2 - 2")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 2, giorno = 3, primo="Primo 2 - 3", secondo="Secondo 2 - 3", contorno="Contorno 2 - 3")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 2, giorno = 4, primo="Primo 2 - 4", secondo="Secondo 2 - 4", contorno="Contorno 2 - 4")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 2, giorno = 5, primo="Primo 2 - 5", secondo="Secondo 2 - 5", contorno="Contorno 2 - 5")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 3, giorno = 1, primo="Primo 3 - 1", secondo="Secondo 3 - 1", contorno="Contorno 3 - 1")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 3, giorno = 2, primo="Primo 3 - 2", secondo="Secondo 3 - 2", contorno="Contorno 3 - 2")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 3, giorno = 3, primo="Primo 3 - 3", secondo="Secondo 3 - 3", contorno="Contorno 3 - 3")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 3, giorno = 4, primo="Primo 3 - 4", secondo="Secondo 3 - 4", contorno="Contorno 3 - 4")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 3, giorno = 5, primo="Primo 3 - 5", secondo="Secondo 3 - 5", contorno="Contorno 3 - 5")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 4, giorno = 1, primo="Primo 4 - 1", secondo="Secondo 4 - 1", contorno="Contorno 4 - 1")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 4, giorno = 2, primo="Primo 4 - 2", secondo="Secondo 4 - 2", contorno="Contorno 4 - 2")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 4, giorno = 3, primo="Primo 4 - 3", secondo="Secondo 4 - 3", contorno="Contorno 4 - 3")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 4, giorno = 4, primo="Primo 4 - 4", secondo="Secondo 4 - 4", contorno="Contorno 4 - 4")
      menu.put()
      menu = Menu(validitaDa=datetime.strptime("2008-09-01",DATE_FORMAT).date(),validitaA=datetime.strptime("2009-06-30",DATE_FORMAT).date(), settimana = 4, giorno = 5, primo="Primo 4 - 5", secondo="Secondo 4 - 5", contorno="Contorno 4 - 5")
      menu.put()
      url = users.create_logout_url("/")
      url_linktext = 'Logout'

      template_values = {
        'user': users.get_current_user(),      
        'url': url,
        'url_linktext': url_linktext
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/admin.html')
      self.response.out.write(template.render(path, template_values))

    else:
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      template_values = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/admin.html')
      self.response.out.write(template.render(path, template_values))

    
    
application = webapp.WSGIApplication([
  ('/admin/commissione', CMAdminCommissioneHandler),
  ('/admin/menu', CMAdminMenuHandler),
  ('/admin', CMAdminHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
