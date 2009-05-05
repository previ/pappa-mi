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
from datetime import datetime, date, time
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.model import *
from py.form import CommissioneForm
from py.gviz_api import *


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
      data = datetime.datetime.strptime(self.request.get("data"),DATE_FORMAT).date()
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

      if self.request.get("data") :
        data = datetime.datetime.strptime(self.request.get("data"),DATE_FORMAT).date()
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
        'test': self.request.url.find("test") != -1,
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

      # Creating the data
      description = {"nome": ("string", "Commissione"),
                     "nomeScuola": ("string", "Scuola"),
                     "tipo": ("string", "Tipo"),
                     "indirizzo": ("string", "Indirizzo"),
                     "centroCucina": ("string", "Centro Cucina"),
                     "distretto": ("string", "Dist."),
                     "zona": ("string", "Zona"),
                     "comando": ("string", "")}
      
      commissioni = Commissione.all()
      if self.request.get("tipoScuola") :
        commissioni = commissioni.filter("tipoScuola", self.request.get("tipoScuola"))
      if self.request.get("centroCucina") :
        commissioni = commissioni.filter("centroCucina", CentroCucina.get(self.request.get("centroCucina")))
      if self.request.get("nome") :
        commissioni = commissioni.filter("nome>=", self.request.get("nome"))
        commissioni = commissioni.filter("nome<", self.request.get("nome") + u'\ufffd')

      data = list()
      for commissione in commissioni.order("nome"):
        data.append({"nome": commissione.nome, "nomeScuola": commissione.nomeScuola, "tipo": commissione.tipoScuola, "indirizzo": commissione.strada + ", " + commissione.civico + ", " + commissione.cap + " " + commissione.citta, "centroCucina": commissione.centroCucina.nome, "distretto": commissione.distretto, "zona": commissione.zona, "comando":"<a href='/admin/commissione?cmd=open&key="+str(commissione.key())+"'>Apri</a>"})

      # Loading it into gviz_api.DataTable
      data_table = DataTable(description)
      data_table.LoadData(data)

      # Creating a JSon string
      gvizdata = data_table.ToJSon(columns_order=("nome", "nomeScuola", "tipo", "indirizzo", "centroCucina", "distretto", "zona", "comando"), order_by="nome")

      centriCucina = CentroCucina.all().order("nome")

      template_values = {
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'centriCucina': centriCucina,
        'gvizdata': gvizdata,
        'tipoScuola': self.request.get("tipoScuola"),
        'centroCucina': self.request.get("centroCucina"),
        'nome': self.request.get("nome"),
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

      self.redirect("/admin/commissione")
      
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
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      stato = False
      commissario = Commissario.all().filter("user", user).get()
      if commissario :
        stato = commissario.stato
        
      template_values = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'commissario': stato == 1,
        'url': url,
        'url_linktext': url_linktext
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/admin.html')
      self.response.out.write(template.render(path, template_values))

class CMAdminCommissarioHandler(webapp.RequestHandler):

  def get(self):    

    if( self.request.get("cmd") == "enable" or
        self.request.get("cmd") == "disable" ):
      
      commissario = Commissario.get(self.request.get("key"))

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()
              
      if self.request.get("cmd") == "enable" :
        commissario.stato = 1 
      elif self.request.get("cmd") == "disable" :
        commissario.stato = 0 
        
      commissario.put()
      
      if commissario.stato == 1:

        message = mail.EmailMessage()
        message.sender = "aiuto.pappami@gmail.com"
        message.to = commissario.user.email()
        message.subject = "Pappa-Mi Registrazione confermata"
        message.body = """ Benvenuto in commissione mensa !"""
          
        message.send()

      
      self.redirect("/admin/commissario")
    
    else:
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      # Creating the data
      description = {"nome": ("string", "Nome"),
                     "cognome": ("string", "Cognome"),
                     "email": ("string", "Email"),
                     "commissioni": ("string", "Commissioni"),
                     "stato": ("string", "Stato"),
                     "comando": ("string", "Azione")}
      
      data = list()
      for commissario in Commissario.all():
        if commissario.stato == 1:
          stato = "Attivo"
          cmd = "disable"
          comando = "Disabilita"
        else:
          stato = "Richiesta"
          cmd = "enable"
          comando = "Attiva"
        
        commissioni = ""
        for c in commissario.commissioni():
          commissioni = commissioni + c.nome + "<br/>"
        data.append({"nome": commissario.nome, "cognome": commissario.cognome, "email": commissario.user.email(), "commissioni": commissioni, "stato":stato, "comando":"<a href='/admin/commissario?cmd=" + cmd + "&key="+str(commissario.key())+"'>"+comando+"</a>"})

      # Loading it into gviz_api.DataTable
      data_table = DataTable(description)
      data_table.LoadData(data)

      # Creating a JSon string
      json = data_table.ToJSon(columns_order=("nome", "cognome", "email", "commissioni", "stato", "comando"), order_by="cognome")

 
      template_values = {
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'json': json,
        'url': url,
        'url_linktext': url_linktext,
        'user': user
      }
      path = os.path.join(os.path.dirname(__file__), '../templates/admin/commissari.html')
      self.response.out.write(template.render(path, template_values))
    
    
application = webapp.WSGIApplication([
  ('/admin/commissione', CMAdminCommissioneHandler),
  ('/admin/menu', CMAdminMenuHandler),
  ('/admin/commissario', CMAdminCommissarioHandler),
  ('/admin', CMAdminHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
