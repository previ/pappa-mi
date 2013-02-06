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
import urllib
from google.appengine.api import urlfetch
from datetime import datetime, date, time
import wsgiref.handlers
import random

from google.appengine.ext.ndb import model
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from engineauth import models

from common import *
from model import *
from modelMsg import *
from form import CommissioneForm
from gviz_api import *
from base import BasePage, config
#from gcalendar import *

TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class AdminMenuHandler(BasePage):

  def get(self):
    template_values = {
      'content': '/admin/menu.html',
      'citta': Citta.get_all()
    }
    self.getBase(template_values)


  def post(self):    
    if self.request.get("cmd") == "upload" and self.request.get("what") == "menu":
      citta = model.Key("Citta", int(self.request.get("city")))
      data = self.request.get("data")
      for line in data.split("\n"):
        fields = line.split("\t")
        if len(fields) > 6:
          menu = Menu()
          menu.tipo = fields[0]
          menu.validitaDa = datetime.datetime.strptime(fields[1],Const.ACTIVITY_DATE_FORMAT).date()
          menu.validitaA = datetime.datetime.strptime(fields[2],Const.ACTIVITY_DATE_FORMAT).date()
          menu.settimana = int(fields[3])
          menu.giorno = int(fields[4])
          menu.primo = fields[5]
          menu.secondo = fields[6]
          menu.contorno = fields[7]
          menu.dessert = fields[8]
          
          logging.info("menu: " + str(menu.validitaA))
          nm = MenuNew.query().filter(MenuNew.citta==citta).filter(Menu.validitaA==menu.validitaA).get()
          if not nm:
            nm = MenuNew()
            nm.validitaDa = menu.validitaDa
            nm.validitaA = menu.validitaA
            nm.citta = citta
            nm.put()
          piatto = Piatto.query().filter(Piatto.nome==menu.primo).get()
          if not piatto:
            piatto = Piatto()
            piatto.nome = menu.primo
            piatto.calorie = 200
            piatto.proteine = 30
            piatto.carboidrati = 40
            piatto.grassi = 30
            piatto.gi = 10
            piatto.put()
            logging.info("piatto.primo.put: " + piatto.nome)
          piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).filter(PiattoGiorno.tipo=='p').get()
          if not piattoGiorno:
            piattoGiorno = PiattoGiorno()
            piattoGiorno.menu = nm.key
            piattoGiorno.tipo = "p"
            piattoGiorno.piatto = piatto.key
            piattoGiorno.giorno = menu.giorno
            piattoGiorno.settimana = menu.settimana
            piattoGiorno.put()
            logging.info("piattogiorno.primo.put: " + piatto.nome)
          piatto = Piatto.query().filter(Piatto.nome==menu.secondo).get()
          if not piatto:
            piatto = Piatto()
            piatto.nome = menu.secondo
            piatto.calorie = 200
            piatto.proteine = 30
            piatto.carboidrati = 40
            piatto.grassi = 30
            piatto.gi = 10
            piatto.put()
            logging.info("piatto.secondo.put: " + piatto.nome)
          piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).filter(PiattoGiorno.tipo=='s').get()
          if not piattoGiorno:
            piattoGiorno = PiattoGiorno()
            piattoGiorno.menu = nm.key
            piattoGiorno.tipo = "s"
            piattoGiorno.piatto = piatto.key
            piattoGiorno.giorno = menu.giorno
            piattoGiorno.settimana = menu.settimana
            piattoGiorno.put()
            logging.info("piattogiorno.secondo.put: " + piatto.nome)
          piatto = Piatto.query().filter(Piatto.nome==menu.contorno).get()
          if not piatto:
            piatto = Piatto()
            piatto.nome = menu.contorno
            piatto.calorie = 200
            piatto.proteine = 30
            piatto.carboidrati = 40
            piatto.grassi = 30
            piatto.gi = 10
            piatto.put()
            logging.info("piatto.contorno.put: " + piatto.nome)
          piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).filter(PiattoGiorno.tipo=='c').get()
          if not piattoGiorno:
            piattoGiorno = PiattoGiorno()
            piattoGiorno.menu = nm.key
            piattoGiorno.tipo = "c"
            piattoGiorno.piatto = piatto.key
            piattoGiorno.giorno = menu.giorno
            piattoGiorno.settimana = menu.settimana
            piattoGiorno.put()
            logging.info("piattogiorno.contorno.put: " + piatto.nome)
          piatto = Piatto.query().filter(Piatto.nome == menu.dessert).get()
          if not piatto:
            piatto = Piatto()
            piatto.nome = menu.dessert
            piatto.calorie = 200
            piatto.proteine = 30
            piatto.carboidrati = 40
            piatto.grassi = 30
            piatto.gi = 10
            piatto.put()
            logging.info("piatto.dessert.put:" + piatto.nome)
          piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).filter(PiattoGiorno.tipo=='d').get()
          if not piattoGiorno:
            piattoGiorno = PiattoGiorno()
            piattoGiorno.menu = nm.key
            piattoGiorno.tipo = "d"
            piattoGiorno.piatto = piatto.key
            piattoGiorno.giorno = menu.giorno
            piattoGiorno.settimana = menu.settimana
            piattoGiorno.put()
            logging.info("piattogiorno.dessert.put: " + piatto.nome)
      self.response.out.write("initMenu Ok")
      return      
    if self.request.get("cmd") == "upload" and self.request.get("what") == "content":
      data = self.request.get("data")
      for line in data.split("\n"):
        fields = line.split("\t")
        if len(fields) > 2:
          piatto = Piatto.query().filter(Piatto.nome == fields[0]).get()
          if piatto:
            ing = Ingrediente.query().filter(Ingrediente.nome==fields[1]).get()
            if not ing:
              ing = Ingrediente()
              ing.nome = fields[1]
              ing.put()
            ing_piatto = PiattoIngrediente.query().filter(PiattoIngrediente.piatto==piatto.key).filter(PiattoIngrediente.ingrediente==ing.key).get()
            if not ing_piatto:
              ing_piatto = PiattoIngrediente()
              ing_piatto.piatto = piatto.key
              ing_piatto.ingrediente = ing.key
              ing_piatto.quantita = float(fields[2])
              ing_piatto.put()
      self.response.out.write("initMenu Ok")
      return      
          

    
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
        'content': 'admin/commissione.html',
        'commissione': commissione,
        'key': key,
        'offset': self.request.get("offset"),
        'tipoScuola': self.request.get("tipoScuola"),
        'centroCucina': self.request.get("centroCucina"),
        'zona': self.request.get("zona"),
        'distretto': self.request.get("distretto"),
        'centriCucina': CentroCucina.query().order("nome")
      }
    
      self.getBase(template_values)

    else:
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      centriCucina = CentroCucina.query().order("nome")

      template_values = {
        'content': 'admin/commissioni.html',
        'centriCucina': centriCucina,
      }
      self.getBase(template_values)
      
      #if self.request.get("offset"):
        #offset = int(self.request.get("offset"))
      #else:
        #offset = 0
        
      #if offset > 0:
        #prev = offset - 10
      #else:
        #prev = None
      #next = offset + 10
      
      ## Creating the data
      #description = {"nome": ("string", "Commissione"),
                     #"nomeScuola": ("string", "Scuola"),
                     #"tipo": ("string", "Tipo"),
                     #"indirizzo": ("string", "Indirizzo"),
                     #"distretto": ("string", "Dist."),
                     #"zona": ("string", "Zona"),
                     #"geo": ("string", "Geo"),
                     #"comando": ("string", "")}
      
      #commissioni = Commissione.query()
      #if self.request.get("tipoScuola") :
        #commissioni = commissioni.filter("tipoScuola", self.request.get("tipoScuola"))
      #if self.request.get("centroCucina") :
        #commissioni = commissioni.filter("centroCucina", CentroCucina.get(self.request.get("centroCucina")))
      #if self.request.get("nome") :
        #commissioni = commissioni.filter("nome>=", self.request.get("nome"))
        #commissioni = commissioni.filter("nome<", self.request.get("nome") + u'\ufffd')

      #data = list()
      #try:
        #for commissione in commissioni.order("nome").fetch(10, offset):
          #data.append({"nome": commissione.nome, "nomeScuola": commissione.nomeScuola, "tipo": commissione.tipoScuola, "indirizzo": commissione.strada + ", " + commissione.civico + ", " + commissione.cap + " " + commissione.citta, "distretto": commissione.distretto, "zona": commissione.zona, "geo": str(commissione.geo != None), "comando":"<a href='/admin/commissione?cmd=open&key="+str(commissione.key())+"&offset="+str(offset)+ "&tipoScuola=" + self.request.get("tipoScuola") + "&centroCucina=" + self.request.get("centroCucina") + "&zona="+ self.request.get("zona") + "&distretto=" + self.request.get("distretto")+"'>Apri</a>"})
      #except db.Timeout:
        #errmsg = "Timeout"
        
      ## Loading it into gviz_api.DataTable
      #data_table = DataTable(description)
      #data_table.LoadData(data)

      ## Creating a JSon string
      #gvizdata = data_table.ToJSon(columns_order=("nome", "nomeScuola", "tipo", "indirizzo", "distretto", "zona", "geo", "comando"))

      #centriCucina = CentroCucina.query().order("nome")

      #template_values = {
        #'content': 'admin/commissioni.html',
        #'centriCucina': centriCucina,
        #'gvizdata': gvizdata,
        #'prev': prev,
        #'next': next,
        #'tipoScuola': self.request.get("tipoScuola"),
        #'centroCucina': self.request.get("centroCucina"),
        #'zona': self.request.get("zona"),
        #'distretto': self.request.get("distretto"),
        #'nome': self.request.get("nome")
      #}
      #self.getBase(template_values)

  def post(self):    
    if( self.request.get("cmd") == "save" ):
      if self.request.get("key"):
        commissione = Commissione.get(self.request.get("key"))
      else:
        commissione = Commissione()
        
      form = CommissioneForm(data=self.request.POST, instance=commissione)
      
      if form.is_valid():
        commissione = form.save(commit=False)
        commissione.geo = model.GeoPt(float(self.request.get("lat")), float(self.request.get("lon")))
        commissione.put()

      self.redirect("/admin/commissione?offset=" + self.request.get("offset") + "&tipoScuola=" + self.request.get("q_tipoScuola") + "&centroCucina=" + self.request.get("q_centroCucina") + "&zona="+ self.request.get("q_zona") + "&distretto=" + self.request.get("q_distretto") )
      
    elif self.request.get("cmd") == "list":
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()
 
      centriCucina = CentroCucina.query().order("nome")
      
      #if query.is_valid():
      commissioni = Commissione.query()
      if self.request.get("tipoScuola") :
        commissioni = commissioni.filter("tipoScuola", self.request.get("tipoScuola"))
      if self.request.get("centroCucina") :
        commissioni = commissioni.filter("centroCucina", CentroCucina.get(self.request.get("centroCucina")))
      if self.request.get("nome") :
        commissioni = commissioni.filter("nome>=", self.request.get("nome"))
        commissioni = commissioni.filter("nome<", self.request.get("nome") + u'\ufffd')

      template_values = {
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

class CMAdminCommissioneDataHandler(BasePage):

  def get(self):    
      tq = urllib.unquote(self.request.get("tq"))
      #logging.info(tq)
      query = tq[:tq.find("limit")]
      #logging.info(query)
      
      orderby = "nome"
      if(query.find("by") > 0):
        orderby = query[query.find("`"):query.rfind("`")].strip("` ")
      if(query.find("desc") > 0):
        orderby = "-" + orderby

      tipoScuola = None;
      if(query.find("tipoScuola") >= 0):
        tipoScuola = query[(query.find("tipoScuola ") + len("tipoScuola ")):]
        tipoScuola = tipoScuola[:tipoScuola.find(" ")]

      centroCucina = None;
      if(query.find("centroCucina") >= 0):
        centroCucina = query[(query.find("centroCucina ") + len("centroCucina ")):]
        centroCucina = centroCucina[:centroCucina.find(" ")]
      
      #logging.info(orderby)
      
      params = tq[tq.find("limit"):].split()
      #logging.info(params)
      limit = int(params[1])
      offset = int(params[3])
      
      if params[3] >= 0:
        offset = int(params[3])
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
                     "tipoScuola": ("string", "Tipo"),
                     "strada": ("string", "Indirizzo"),
                     "distretto": ("string", "Dist."),
                     "zona": ("string", "Zona"),
                     "geo": ("string", "Geo"),
                     "comando": ("string", "")}
      
      commissioni = Commissione.query()
      if tipoScuola :
        commissioni = commissioni.filter("tipoScuola", tipoScuola)
      if centroCucina :
        commissioni = commissioni.filter("centroCucina", CentroCucina.get(centroCucina))
      if self.request.get("nome") :
        commissioni = commissioni.filter("nome>=", self.request.get("nome"))
        commissioni = commissioni.filter("nome<", self.request.get("nome") + u'\ufffd')

      data = list()
      try:
        for commissione in commissioni.order(orderby).fetch(limit, offset):
          data.append({"nome": commissione.nome, "nomeScuola": commissione.nomeScuola, "tipoScuola": commissione.tipoScuola, "strada": commissione.strada + ", " + commissione.civico + ", " + commissione.cap + " " + commissione.citta.nome, "distretto": commissione.distretto, "zona": commissione.zona, "geo": str(commissione.geo != None), "comando":"<a href='/admin/commissione?cmd=open&key="+str(commissione.key())+"&offset="+str(offset)+ "&tipoScuola=" + self.request.get("tipoScuola") + "&centroCucina=" + self.request.get("centroCucina") + "&zona="+ self.request.get("zona") + "&distretto=" + self.request.get("distretto")+"'>Apri</a>"})
      except model.Timeout:
        errmsg = "Timeout"
        
      # Loading it into gviz_api.DataTable
      data_table = DataTable(description)
      data_table.LoadData(data)

      # Creating a JSon string
      self.response.out.write("google.visualization.Query.setResponse({reqId: '0',status:'ok',table:" + data_table.ToJSon(columns_order=("nome", "nomeScuola", "tipoScuola", "strada", "distretto", "zona", "geo", "comando"))+",version: '0.6'})")
  
class CMAdminHandler(BasePage):

  def get(self):    

    """
    Pappa-Mi 1 to 2.0 migration    
    1.deploy app with citta = TextProperty
    2.initCity1
    3.deploy app with citta = ReferenceProperty
    4.initCity2
    5.initAuthR
    6.initAuth
    7.initMenu
    8.initStream
    """
    
    if self.request.get("cmd") == "initConfig":
      dummy = Configurazione(nome="dummyname", valore="dummyvalue")
      dummy.put()
      return      
     
    if self.request.get("cmd") == "initMenu":
      citta = Citta.query().get()
      for menu in Menu.query().filter(Menu.tipoScuola=="Materna").filter(Menu.validitaA==datetime.datetime.strptime(self.request.get("offset"), "%Y-%m-%d")):
        logging.info("menu: " + str(menu.validitaA))
        nm = MenuNew.query().filter(Menu.validitaA==menu.validitaA).get()
        if not nm:
          nm = MenuNew()
          nm.validitaDa = menu.validitaDa
          nm.validitaA = menu.validitaA
          nm.citta = citta.key
          nm.put()
        piatto = Piatto.query().filter(Piatto.nome==menu.primo).get()
        if not piatto:
          piatto = Piatto()
          piatto.nome = menu.primo
          piatto.calorie = 200
          piatto.proteine = 30
          piatto.carboidrati = 40
          piatto.grassi = 30
          piatto.gi = 10
          piatto.put()
          logging.info("piatto.primo.put")
        piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).get()
        if not piattoGiorno:
          piattoGiorno = PiattoGiorno()
          piattoGiorno.menu = nm.key
          piattoGiorno.tipo = "p"
          piattoGiorno.piatto = piatto.key
          piattoGiorno.giorno = menu.giorno
          piattoGiorno.settimana = menu.settimana
          piattoGiorno.put()
          logging.info("piattogiorno.primo.put")
        piatto = Piatto.query().filter(Piatto.nome==menu.secondo).get()
        if not piatto:
          piatto = Piatto()
          piatto.nome = menu.secondo
          piatto.calorie = 200
          piatto.proteine = 30
          piatto.carboidrati = 40
          piatto.grassi = 30
          piatto.gi = 10
          piatto.put()
          logging.info("piatto.secondo.put")
        piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).get()
        if not piattoGiorno:
          piattoGiorno = PiattoGiorno()
          piattoGiorno.menu = nm.key
          piattoGiorno.tipo = "s"
          piattoGiorno.piatto = piatto.key
          piattoGiorno.giorno = menu.giorno
          piattoGiorno.settimana = menu.settimana
          piattoGiorno.put()
          logging.info("piattogiorno.secondo.put")
        piatto = Piatto.query().filter(Piatto.nome==menu.contorno).get()
        if not piatto:
          piatto = Piatto()
          piatto.nome = menu.contorno
          piatto.calorie = 200
          piatto.proteine = 30
          piatto.carboidrati = 40
          piatto.grassi = 30
          piatto.gi = 10
          piatto.put()
          logging.info("piatto.contorno.put")
        piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).get()
        if not piattoGiorno:
          piattoGiorno = PiattoGiorno()
          piattoGiorno.menu = nm.key
          piattoGiorno.tipo = "c"
          piattoGiorno.piatto = piatto.key
          piattoGiorno.giorno = menu.giorno
          piattoGiorno.settimana = menu.settimana
          piattoGiorno.put()
          logging.info("piattogiorno.contorno.put")
        piatto = Piatto.query().filter(Piatto.nome == menu.dessert).get()
        if not piatto:
          piatto = Piatto()
          piatto.nome = menu.dessert
          piatto.calorie = 200
          piatto.proteine = 30
          piatto.carboidrati = 40
          piatto.grassi = 30
          piatto.gi = 10
          piatto.put()
          logging.info("piatto.dessert.put")
        piattoGiorno = PiattoGiorno.query().filter(PiattoGiorno.menu==nm.key).filter(PiattoGiorno.piatto==piatto.key).filter(PiattoGiorno.giorno==menu.giorno).filter(PiattoGiorno.settimana==menu.settimana).get()
        if not piattoGiorno:
          piattoGiorno = PiattoGiorno()
          piattoGiorno.menu = nm.key
          piattoGiorno.tipo = "d"
          piattoGiorno.piatto = piatto.key
          piattoGiorno.giorno = menu.giorno
          piattoGiorno.settimana = menu.settimana
          piattoGiorno.put()
          logging.info("piattogiorno.dessert.put")
      self.response.out.write("initMenu Ok")
      return      
                
    if self.request.get("cmd") == "initCity1":
      for cm in Commissione.query().filter(Commissione.citta=="Milano"):
        cm.citta = None
        cm.put()

      for cc in CentroCucina.query():
        cc.citta = None
        cc.put()
      self.response.out.write("initCity1 Ok")
      return

    if self.request.get("cmd") == "initCity2":
      c = Citta.query().get()
      if not c:
        c = Citta()
        c.nome = "Milano"
        c.codice = "F205"
        c.provincia = "MI"
        c.geo = model.GeoPt(45.463681,9.188171)
        c.put()
      for cm in Commissione.query().filter(Commissione.citta==None):
        cm.citta = c.key
        cm.put_async()

      for cc in CentroCucina.query():
        cc.citta = c.key
        cc.put_async()

      for cs in Commissario.query():
        cs.citta = c.key
        cs.put_async()
      self.response.out.write("initCity2 Ok")
      return
        
    if self.request.get("cmd") == "initStream1":
      offset = 0
      limit = 100
      if self.request.get("offset"):
        offset = int(self.request.get("offset"))

      if self.request.get("kind") == "isp":
        for isp in Ispezione.query().fetch(offset=offset, limit=limit):
          logging.info(isp)
          messaggio = Messaggio(par = isp.key, root = isp.key, grp = isp.commissione, tipo = 101, livello = 0, c_ua = isp.commissario.get().usera, creato_il = isp.creato_il, modificato_il = isp.modificato_il)
          messaggio.put()
      elif self.request.get("kind") == "nc":
        for nc in Nonconformita.query().fetch(offset=offset, limit=limit):
          logging.info(nc)
          messaggio = Messaggio(par = nc.key, root = nc.key, grp = nc.commissione, tipo = 102, livello = 0, c_ua = nc.commissario.get().usera, creato_il = nc.creato_il, modificato_il = nc.modificato_il)
          messaggio.put()
      elif self.request.get("kind") == "dieta":
        for dieta in Dieta.query().fetch(offset=offset, limit=limit):
          logging.info(dieta)
          messaggio = Messaggio(par = dieta.key, root = dieta.key, grp = dieta.commissione, tipo = 103, livello = 0, c_ua = dieta.commissario.get().usera, creato_il = dieta.creato_il, modificato_il = dieta.creato_il)
          messaggio.put()
      elif self.request.get("kind") == "nota":
        for nota in Nota.query().fetch(offset=offset, limit=limit):
          logging.info(nota)
          messaggio = Messaggio(par = nota.key, root = nota.key, grp = nota.commissione, tipo = 104, livello = 0, c_ua = nota.commissario.get().usera, creato_il = nota.creato_il, modificato_il = nota.creato_il)
          messaggio.put()
      self.response.out.write("initStream Ok")
      return
          
    if self.request.get("cmd") == "initStream2":
      for msg in Messaggio().query():
        if msg.tipo in range(101, 104):
          msg.grp = msg.root.get().commissione
          msg.put_async()
      self.response.out.write("initStream 2 Ok")
      return
  
    if self.request.get("cmd") == "initStream3":
      for msg in Messaggio().query():
        if msg.c_ua is None:
          a_id = models.User.generate_auth_id('google', msg.creato_da.user_id(), 'legacy')
          logging.info("auth_id: " + str(a_id))
          ua = models.User.get_by_auth_id(a_id)          
          if ua:            
            logging.info("email: " + str(ua.email))
            msg.c_ua = ua.key
          msg.put()
      self.response.out.write("initStream 3 Ok")
      return

    if self.request.get("cmd") == "initStream4":
      for v in Voto().query():
        if v.c_ua is None:
          a_id = models.User.generate_auth_id('google', v.creato_da.user_id(), 'legacy')
          logging.info("auth_id: " + str(a_id))
          ua = models.User.get_by_auth_id(a_id)          
          if ua:            
            logging.info("email: " + str(ua.email))
            v.c_ua = ua.key
          v.put()
      for t in Tag().query():
        if t.c_ua is None:
          a_id = models.User.generate_auth_id('google', t.creato_da.user_id(), 'legacy')
          logging.info("auth_id: " + str(a_id))
          ua = models.User.get_by_auth_id(a_id)          
          if ua:            
            logging.info("email: " + str(ua.email))
            t.c_ua = ua.key
          t.put()
      self.response.out.write("initStream 4 Ok")
      return
    
    if self.request.get("cmd") == "fixStream":
      for isp in Ispezione().query():
        msgs = Messaggio.query().filter(Messaggio.par==isp.key).filter(Messaggio.tipo==101)
        if msgs.count() == 0:
          logging.info("Missing: " + str(isp.commissione.get().nome) + " " + str(isp.dataIspezione))
          messaggio = Messaggio(par = isp.key, root = isp.key, grp = isp.commissione, tipo = 101, livello = 0, c_ua = isp.commissario.get().usera, creato_il = isp.creato_il, modificato_il = isp.modificato_il)
          messaggio.put()
        elif msgs.count() == 2:
          logging.info("Duplicate: " + str(isp.commissione.get().nome) + " " + str(isp.dataIspezione))
          msgs.get().key.delete()
        elif msgs.count() > 2:
          logging.info("Multiple: " + str(isp.commissione.get().nome) + " " + str(isp.dataIspezione))
      self.response.out.write("fixStream 2 Ok")
      return

    if self.request.get("cmd") == "fixCreatoIl":
      for isp in Ispezione.query().filter(Ispezione.creato_il==None):
        isp.creato_il = isp.modificato_il
        isp.put()
      for nc in Nonconformita.query().filter(Nonconformita.creato_il==None):
        nc.creato_il = nc.modificato_il
        nc.put()
      for dieta in Dieta.query().filter(Dieta.creato_il==None):
        dieta.creato_il = dieta.modificato_il
        dieta.put()
      for nota in Nota.query().filter(Nota.creato_il==None):
        nota.creato_il = nota.modificato_il
        nota.put()
      self.response.out.write("fixIsp Ok")
      return

    if self.request.get("cmd") == "fixTagObj":
      for tagobj in TagObj().query():
        obj = tagobj.obj.get()
        if obj:
          tagobj.creato_il = tagobj.obj.get().creato_il
          tagobj.put()
      self.response.out.write("fixTagObj Ok")
      return
    
    if self.request.get("cmd") == "initAuthR":
      logging.info("initAuth")
      offset = int(self.request.get("offset"))
      for c in Commissario.query().filter().fetch(limit=100, offset=offset):
        c.usera = None
        c.put()
      self.response.out.write("initAuthR Ok")
      return
    
    
    if self.request.get("cmd") == "initAuth":
      logging.info("initAuth")
      offset = int(self.request.get("offset"))
      for c in Commissario.query().filter().fetch(limit=50, offset=offset):
        if c.usera is None:
          logging.info("initAuth.1: " + str(c.user.email()))
          auth_id = models.User.generate_auth_id('google', c.user.user_id(), 'legacy')
          user_info = {
              'auth_id': auth_id,
              'uid': c.user.user_id(), # Unique ID to the service provider
              'info': {
                  'id': c.user.user_id(),
                  'displayName': c.nome + " " + c.cognome,
                  'name': {
                      'formatted': c.nome + " " + c.cognome,
                      'familyName': c.cognome,
                      'givenName': c.nome,
                      },
                  'emails': [
                      {
                          'value': c.user.email(),                          
                          'verified': True                          
                      }
                  ]
              },
              'extra': {
              }
          }
          profile = models.UserProfile.get_or_create(auth_id, user_info)
          usera = models.User.get_or_create_by_profile(profile)          
          c.usera = usera.key
          c.avatar_url = "/img/default_avatar_" + str(random.randint(0, 7)) + ".png"
          c.put()
      self.response.out.write("initAuth Ok")
      return

    if self.request.get("cmd") == "resetEmailPrivacy":
      for c in Commissario.query():
        c.privacy = [[0,0,0],[1,1,1],[0,1,1],[1,1,1],[0,1,1]]
        c.put()
        
      self.response.out.write("Ok")
      return

    if self.request.get("cmd") == "initEmailLower":
      for c in Commissario.query().filter(Commissario.user_email_lower==""):
        c.user_email_lower = c.usera.get().email.lower()
        c.put()
        
      self.response.out.write("Ok")
      return

    if self.request.get("cmd") == "initNumCommissari":
      for c in Commissione.query().filter(Commissione.numCommissari==None):
        c.numCommissari = 0
        c.put()
        
      self.response.out.write("Ok")
      return
    
      
    if self.request.get("cmd") == "initAnno":
      d2008da = date(2008,9,1)
      d2008a = date(2009,7,31)
      d2009da = date(2009,9,1)
      d2009a = date(2010,7,31)
      d2010da = date(2010,9,1)
      d2010a = date(2011,7,31)
      for isp in Ispezione.query() :
        if isp.dataIspezione >= d2008da and isp.dataIspezione < d2008a :
          isp.anno = 2008
        if isp.dataIspezione >= d2009da and isp.dataIspezione < d2009a :
          isp.anno = 2009
        if isp.dataIspezione >= d2010da and isp.dataIspezione < d2010a :
          isp.anno = 2010
        isp.put()
      for nc in Nonconformita.query() :
        if nc.dataNonconf >= d2008da and nc.dataNonconf < d2008a :
          nc.anno = 2008
        if nc.dataNonconf >= d2009da and nc.dataNonconf < d2009a :
          nc.anno = 2009
        if nc.dataNonconf >= d2010da and nc.dataNonconf < d2010a :
          nc.anno = 2010
        nc.put()
      return
          
    
    if self.request.get("cmd") == "initZone":
      for cc in CentroCucina.query():
        ccZona = CentroCucinaZona(centroCucina = cc, zona = cc.menuOffset + 1, validitaDa=date(year=2008,month=3, day=1), validitaA=date(year=2010,month=10, day=31))
        ccZona.put()
      for cm in Commissione.query():
        cmCC = CommissioneCentroCucina(commissione = cm, centroCucina = cm.centroCucina, validitaDa=date(year=2008,month=3, day=1), validitaA=date(year=2099,month=12, day=31))
        cmCC.put()
      for z in range(1,5):
        zonaOld = ZonaOffset(zona = z, offset = 4-z, validitaDa=date(year=2008,month=3, day=1), validitaA=date(year=2010,month=10, day=31))
        zonaOld.put()
        zona = ZonaOffset(zona = z, offset = 4-z, validitaDa=date(year=2010,month=11, day=1), validitaA=date(year=2099,month=12, day=31))
        zona.put()
        
    if self.request.get("cmd") == "getCommissari":
      buff = "Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,E-mail 1 - Type,E-mail 1 - Value\r"
      for c in Commissario.query():
        if c.isCommissario():
          buff = buff + c.nome + " " + c.cognome + "," + c.nome + ",," + c.cognome + ",,,,,,,,,,,,,,,,,,,,,,,Commissari attivi Pappa-Mi ::: * My Contacts,* ," + c.user_email_lower + "\r"
        
      self.response.out.write(buff)        
      return

    if self.request.get("cmd") == "getGenitori":
      buff = "Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Group Membership,E-mail 1 - Type,E-mail 1 - Value\r"
      for c in Commissario.query():
        if c.isGenitore():
          buff = buff + c.nome + " " + c.cognome + "," + c.nome + ",," + c.cognome + ",,,,,,,,,,,,,,,,,,,,,,,Genitori attivi Pappa-Mi ::: * My Contacts,* ," + c.user_email_lower + "\r"
        
      self.response.out.write(buff)
      return

    if self.request.get("cmd") == "getIspezioni":
      dataInizio = datetime.datetime.strptime(self.request.get("offset"),Const.DATE_FORMAT).date()
      
      for isp in Ispezione.query().filter(Ispezione.dataIspezione>dataInizio).order(Ispezione.dataIspezione):
        isp_str = ""
        isp_str += ((isp.commissione.get().nome + " - " + isp.commissione.get().tipoScuola) if isp.commissione else "") + "\t"
        isp_str += (isp.commissario.get().usera.get().email if isp.commissario.get().usera else "") + "\t"
        isp_str += str(isp.dataIspezione) + "\t"
        isp_str += unicode(isp.primoPrevisto) + "\t"
        isp_str += unicode(isp.primoEffettivo) + "\t"
        isp_str += str(isp.primoDist) + "\t"
        isp_str += str(isp.primoCondito) + "\t"
        isp_str += str(isp.primoCottura) + "\t"
        isp_str += str(isp.primoTemperatura) + "\t"
        isp_str += str(isp.primoQuantita) + "\t"
        isp_str += str(isp.primoAssaggio) + "\t"
        isp_str += str(isp.primoGradimento) + "\t"
        isp_str += unicode(isp.secondoPrevisto) + "\t"
        isp_str += unicode(isp.secondoEffettivo) + "\t"
        isp_str += str(isp.secondoDist) + "\t"
        isp_str += str(isp.secondoCottura) + "\t"
        isp_str += str(isp.secondoTemperatura) + "\t"
        isp_str += str(isp.secondoQuantita) + "\t"
        isp_str += str(isp.secondoAssaggio) + "\t"
        isp_str += str(isp.secondoGradimento) + "\t"
        isp_str += unicode(isp.contornoPrevisto) + "\t"
        isp_str += unicode(isp.contornoEffettivo) + "\t"
        isp_str += str(isp.contornoCondito) + "\t"
        isp_str += str(isp.contornoCottura) + "\t"
        isp_str += str(isp.contornoTemperatura) + "\t"
        isp_str += str(isp.contornoQuantita) + "\t"
        isp_str += str(isp.contornoAssaggio) + "\t"
        isp_str += str(isp.contornoGradimento) + "\t"
        isp_str += unicode(isp.fruttaTipo) + "\t"
        isp_str += unicode(isp.fruttaServita) + "\t"
        isp_str += str(isp.fruttaMaturazione) + "\t"
        isp_str += str(isp.fruttaQuantita) + "\t"
        isp_str += str(isp.fruttaAssaggio) + "\t"
        isp_str += str(isp.fruttaGradimento) + "\t"
        isp_str += unicode(isp.paneTipo) + "\t"
        isp_str += str(isp.paneServito) + "\t"
        isp_str += str(isp.paneQuantita) + "\t"
        isp_str += str(isp.paneAssaggio) + "\t"
        isp_str += str(isp.paneGradimento) + "\t"
        isp_str += str(isp.giudizioGlobale) + "\t"
        isp_str += "\n"
        self.response.out.write(isp_str)
        
      return

    if self.request.get("cmd") == "getNonconf":
      dataInizio = datetime.datetime.strptime(self.request.get("offset"),Const.DATE_FORMAT).date()
      
      for nc in Nonconformita.query().filter(Nonconformita.dataNonconf > dataInizio).order(Nonconformita.dataNonconf):
        nc_str = ""
        nc_str += ((nc.commissione.get().nome + " - " + nc.commissione.get().tipoScuola) if nc.commissione else "") + "\t"
        nc_str += (nc.commissario.get().usera.get().email if nc.commissario.get().usera else "") + "\t"
        nc_str += str(nc.dataNonconf) + "\t"
        nc_str += str(nc.tipo) + "\t"
        nc_str += str(nc.richiestaCampionatura) + "\n"
        self.response.out.write(nc_str)
        
      return

    if self.request.get("cmd") == "upCommissioni":
      data = self.request.get("rawdata")
      for line in data.split("\n"):
        logging.info(line)
        fields = line.split("\t")
        if len(fields) > 14:
          cm = Commissione()
          cm.citta = model.Key(urlsafe=field[0])
          cm.codiceScuola = fields[1]
          cm.nome = fields[2]
          cm.nomeScuola = fields[3]
          cm.tipoScuola = fields[4]
          cm.strada = fields[5]
          cm.civico = fields[6]
          cm.provincia = fields[7]
          cm.cap = fields[8]
          cm.zona = fields[9]
          cm.distretto = fields[10]
          cm.email = fields[11]
          cm.telefono = fields[12]
          cm.fax = fields[13]
          geo = fields[14].split(',')
          cm.geo = model.GeoPt(lat=float(geo[0]), lon=float(geo[1]))
          cm.creato_da = users.get_current_user()
          cm.creato_il = datetime.now()
          cm.modificato_da = users.get_current_user()
          cm.modificato_il = datetime.now()
          cm.numCommissari = 0
          cm.stato = 1
          cm.put()
          
    if self.request.get("cmd") == "flush":
      memcache.flush_query()
      self.response.out.write("flush Ok")
      return

    if self.request.get("cmd") == "flushnews":
      #url = "http://groups.google.com/group/pappami-aggiornamenti/feed/atom_v1_0_msgs.xml"
      #result = urlfetch.fetch(url)
      #if result.status_code == 200:
        #logging.info("ok")
        #logging.info(result.content)
      #else:
        #logging.info("error")
        #logging.info(result.status_code)
        #logging.info(result.content)
      memcache.delete("news_pappami")
      memcache.delete("news_web")
      memcache.delete("news_cal")
      self.response.out.write("flush Ok")
      return

    if self.request.get("cmd") == "offset":
      ccs = CentroCucina.query()
      for cc in ccs:
        if cc.menuOffset == None:
          cc.menuOffset = None
          cc.put()
      
    template_values = {
      'content': 'admin/admin.html',
    }
    self.getBase(template_values)

  _users = dict()
  def get_user(self, user):
    if not self._users.get(user.email()):
      ua = UserEmail.get_by_emails([user.email()])
      self._users[user.user_id()] = ua
    return ua
    
class CMAdminCommissarioHandler(BasePage):

  def get(self):    

    if( self.request.get("cmd") == "enable" or
        self.request.get("cmd") == "disable" ):
      
      commissario = Commissario.get(self.request.get("key"))

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      user = users.get_current_user()

      calendario = Calendario()
      calendario.logon(user=Configurazione.query().filter("nome","calendar_user").get().valore, password=Configurazione.query().filter("nome", "calendar_password").get().valore)
      
      if self.request.get("cmd") == "enable":
        if commissario.isRegCommissario():
          commissario.stato = 1
          for c in commissario.commissioni():
            c.numCommissari = c.numCommissari + 1
            c.put() 

            if(c.calendario):
              calendario.load(c.calendario)
              calendario.share(commissario.user.email())
            
        else:
          commissario.stato = 11
      elif self.request.get("cmd") == "disable" : 
        if commissario.isCommissario():
          commissario.stato = 0 
          for c in commissario.commissioni():
            c.numCommissari = c.numCommissari - 1
            c.put() 
        else:
          commissario.stato = 10
        
      commissario.put()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
      
     
      if commissario.stato == 1:              
        
        host = self.getHost()
        
        sender = "Pappa-Mi <aiuto@pappa-mi.it>"
        message = mail.EmailMessage()
        message.sender = sender
        message.to = commissario.user.email()
        message.bcc = sender
        message.subject = "Benvenuto in Pappa-Mi"
        message.body = """ La tua richiesta di registrazione come Commissario e' stata confermata.
        
        Ora puoi accedere all'applicazione utilizzando il seguente link:
        
        http://"""  + host + """/commissario
        
        e iniziare a inserire le schede di valutazione e di non conformita'
        
        Ciao
        Pappa-Mi staff
        
        """
          
        message.send()
        
        memcache.delete("markers")
        memcache.delete("markers_all")
        memcache.delete("stats")
      
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
                     "ultimo_accesso_il": ("string", "Ultimo accesso"),
                     "comando": ("string", "Azione")}
      
      data = list()
      for commissario in Commissario.query():
        if commissario.isRegCommissario():
          stato = "Richiesta"
          comando = "Attiva"
          cmd = "enable"
        elif commissario.isCommissario():
          stato = "Commissario"
          comando = "Disabilita"
          cmd = "disable"
        elif commissario.isGenitore():
          stato = "Genitore"
          comando = "Disabilita"
          cmd = "disable"
        
        commissioni = ""
        for c in commissario.commissioni():
          commissioni = commissioni + c.nome + " - " + c.tipoScuola + "<br/>"

        data.append({"nome": commissario.nome, "cognome": commissario.cognome, "email": commissario.user.email(), "commissioni": commissioni, "stato":stato, "ultimo_accesso_il":commissario.ultimo_accesso_il, "comando":"<a href='/admin/commissario?cmd="+cmd+"&key="+str(commissario.key())+"'>"+comando+"</a>"})

      # Loading it into gviz_api.DataTable
      data_table = DataTable(description)
      data_table.LoadData(data)

      # Creating a JSon string
      json = data_table.ToJSon(columns_order=("nome", "cognome", "email", "commissioni", "stato", "ultimo_accesso_il", "comando"), order_by="cognome")

 
      template_values = {
        'content': 'admin/commissari.html',
        'json': json
      }
      self.getBase(template_values)
      
      
        
app = webapp.WSGIApplication([
  ('/admin/commissione', CMAdminCommissioneHandler),
  ('/admin/commissione/getdata', CMAdminCommissioneDataHandler),
  ('/adminmenu', AdminMenuHandler),
  ('/admin/commissario', CMAdminCommissarioHandler),
  ('/admin', CMAdminHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

def main():
  app.run();

if __name__ == "__main__":
  main()