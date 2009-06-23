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
from py.main import BasePage


TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class CMAdminMenuHandler(BasePage):

  def get(self):    

    template_values = {
      'content_left': 'admin/leftbar.html',
      'content': 'admin/menu.html'
    }

    if( self.request.get("data") ):
      data = datetime.datetime.strptime(self.request.get("data"),DATE_FORMAT).date()
      menu = Menu.all().filter("validitaA >=", data).order("-validitaA").order("settimana").order("giorno")
      template_values['data'] = data
      template_values['menu'] = menu

    self.getBase(template_values)

  def post(self):    
    if( self.request.get("cmd") == "list" ):

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      template_values = {
        'content_left': 'admin/leftbar.html',
        'content': 'admin/menu.html'
      }

      if self.request.get("data") :
        data = datetime.datetime.strptime(self.request.get("data"),DATE_FORMAT).date()
        menu = Menu.all().filter("validitaA >=", data).order("-validitaA").order("settimana").order("giorno")
        template_values['data'] = data
        template_values['menu'] = menu

      self.getBase(template_values)


class CMAdminCommissioneHandler(BasePage):

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
        'content_left': 'admin/leftbar.html',
        'content': 'admin/commissione.html',
        'commissione': commissione,
        'key': key,
        'offset': self.request.get("offset"),
        'tipoScuola': self.request.get("tipoScuola"),
        'centroCucina': self.request.get("centroCucina"),
        'zona': self.request.get("zona"),
        'distretto': self.request.get("distretto"),
        'centriCucina': CentroCucina.all().order("nome")
      }
    
      self.getBase(template_values)

    else:
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()
      if self.request.get("offset"):
        offset = int(self.request.get("offset"))
      else:
        offset = 0
        
      if offset > 0:
        prev = offset - 10
      else:
        prev = None
      next = offset + 10
      
      # Creating the data
      description = {"nome": ("string", "Commissione"),
                     "nomeScuola": ("string", "Scuola"),
                     "tipo": ("string", "Tipo"),
                     "indirizzo": ("string", "Indirizzo"),
                     "distretto": ("string", "Dist."),
                     "zona": ("string", "Zona"),
                     "geo": ("string", "Geo"),
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
      try:
        for commissione in commissioni.order("nome").fetch(10, offset):
          data.append({"nome": commissione.nome, "nomeScuola": commissione.nomeScuola, "tipo": commissione.tipoScuola, "indirizzo": commissione.strada + ", " + commissione.civico + ", " + commissione.cap + " " + commissione.citta, "distretto": commissione.distretto, "zona": commissione.zona, "geo": str(commissione.geo != None), "comando":"<a href='/admin/commissione?cmd=open&key="+str(commissione.key())+"&offset="+str(offset)+ "&tipoScuola=" + self.request.get("tipoScuola") + "&centroCucina=" + self.request.get("centroCucina") + "&zona="+ self.request.get("zona") + "&distretto=" + self.request.get("distretto")+"'>Apri</a>"})
      except db.Timeout:
        errmsg = "Timeout"
        
      # Loading it into gviz_api.DataTable
      data_table = DataTable(description)
      data_table.LoadData(data)

      # Creating a JSon string
      gvizdata = data_table.ToJSon(columns_order=("nome", "nomeScuola", "tipo", "indirizzo", "distretto", "zona", "geo", "comando"))

      centriCucina = CentroCucina.all().order("nome")

      template_values = {
        'content_left': 'admin/leftbar.html',
        'content': 'admin/commissioni.html',
        'centriCucina': centriCucina,
        'gvizdata': gvizdata,
        'prev': prev,
        'next': next,
        'tipoScuola': self.request.get("tipoScuola"),
        'centroCucina': self.request.get("centroCucina"),
        'zona': self.request.get("zona"),
        'distretto': self.request.get("distretto"),
        'nome': self.request.get("nome")
      }
      self.getBase(template_values)

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

      self.redirect("/admin/commissione?offset=" + self.request.get("offset") + "&tipoScuola=" + self.request.get("q_tipoScuola") + "&centroCucina=" + self.request.get("q_centroCucina") + "&zona="+ self.request.get("q_zona") + "&distretto=" + self.request.get("q_distretto") )
      
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
        'content_left': 'admin/leftbar.html',
        'content': 'admin/commissioni.html',
        'commissioni': commissioni,
        'centriCucina': centriCucina,
        'tipoScuola': self.request.get("tipoScuola"),
        'centroCucina': self.request.get("centroCucina"),
        'prev': self.requst.get("prev"),
        'next': self.requst.get("next"),
        'nome': self.request.get("nome")
      }
      self.getBase(template_values)

class CMAdminHandler(BasePage):

  def get(self):    
    if self.request.get("cmd") == "flush":
      memcache.flush_all()
      
    template_values = {
      'content_left': 'admin/leftbar.html',
      'content': ''
    }
    self.getBase(template_values)

class CMAdminCommissarioHandler(BasePage):

  def get(self):    

    if( self.request.get("cmd") == "enable" or
        self.request.get("cmd") == "disable" ):
      
      commissario = Commissario.get(self.request.get("key"))

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()
              
      if self.request.get("cmd") == "enable" :
        commissario.stato = 1
        for c in commissario.commissioni():
          c.numCommissari = c.numCommissari + 1
          c.put() 
      elif self.request.get("cmd") == "disable" :
        commissario.stato = 0 
        for c in commissario.commissioni():
          c.numCommissari = c.numCommissari - 1
          c.put() 
        
      commissario.put()
      
      if commissario.stato == 1:
        if self.request.url.find("test") != -1:
          url = "test-pappa-mi.appspot.com"
        else:
          url = "pappa-mi.appspot.com"

        message = mail.EmailMessage()
        message.sender = "aiuto.pappami@gmail.com"
        message.to = commissario.user.email()
        message.bcc = "aiuto.pappami@gmail.com"
        message.subject = "Benvenuto in Pappa-Mi"
        message.body = """ La tua richiesta di registrazione come Commissario e' stata confermata.
        
        Ora puoi accedere all'applicazione utilizzando il seguente link:
        
        http://"""  + url + """/commissario
        
        e iniziare a inserire le schede di valutazione e di non conformita'
        
        Ciao
        Pappa-Mi staff
        
        """
          
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
        'content_left': 'admin/leftbar.html',
        'content': 'admin/commissari.html',
        'json': json
      }
      self.getBase(template_values)
    
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
