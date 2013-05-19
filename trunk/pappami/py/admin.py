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
from google.appengine.api import urlfetch
from datetime import datetime, date, time
import wsgiref.handlers
import random

from google.appengine.ext.ndb import model, toplevel
from google.appengine.api import search
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from engineauth import models

from model import *
from modelMsg import *
from form import CommissioneForm
from gviz_api import *
from base import BasePage, config
#from gcalendar import *
from stream import *

TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class AdminMenuHandler(BasePage):

  @reguser_required
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
          menu.validitaDa = datetime.strptime(fields[1],Const.ACTIVITY_DATE_FORMAT).date()
          menu.validitaA = datetime.strptime(fields[2],Const.ACTIVITY_DATE_FORMAT).date()
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
            p_i = PiattoIngrediente.query().filter(PiattoIngrediente.piatto==piatto.key).filter(PiattoIngrediente.ingrediente==ing.key).get()
            if not p_i:
              logging.info("fields[2]: " + fields[2])
              p_i = PiattoIngrediente()
              p_i.piatto = piatto.key
              p_i.ingrediente = ing.key
              p_i.quantita = float(fields[2])
              p_i.put()
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
        commissione = model.Key("Commissione", self.request.get("key")).get()
        key = commissione.key

      template_values = {
        'content': 'admin/commissione.html',
        'commissione': commissione,
        'key': key,
        'offset': self.request.get("offset"),
        'tipoScuola': self.request.get("tipoScuola"),
        'centroCucina': self.request.get("centroCucina"),
        'zona': self.request.get("zona"),
        'distretto': self.request.get("distretto"),
        'centriCucina': CentroCucina.query().order(CentroCucina.nome)
      }

      self.getBase(template_values)

    else:
      centriCucina = CentroCucina.query().order(CentroCucina.nome)

      template_values = {
        'content': 'admin/commissioni.html',
        'centriCucina': centriCucina,
      }
      self.getBase(template_values)


  def post(self):
    if( self.request.get("cmd") == "save" ):
      if self.request.get("key"):
        commissione = model.Key("Commissione", self.request.get("key")).get()
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

      centriCucina = CentroCucina.query().order(CentroCucina.nome)

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

  @toplevel
  def post(self):
    return self.get()

  @toplevel
  def get(self):

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
      dataInizio = datetime.strptime(self.request.get("offset"),Const.DATE_FORMAT).date()
      
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
        isp_str += str(isp.numeroPastiTotale) + "\t"
        isp_str += "\n"
        self.response.out.write(isp_str)
          
      return
  
    if self.request.get("cmd") == "getNonconf":
      dataInizio = datetime.strptime(self.request.get("offset"),Const.DATE_FORMAT).date()
      
      for nc in Nonconformita.query().filter(Nonconformita.dataNonconf > dataInizio).order(Nonconformita.dataNonconf):
        nc_str = ""
        nc_str += ((nc.commissione.get().nome + " - " + nc.commissione.get().tipoScuola) if nc.commissione else "") + "\t"
        nc_str += (nc.commissario.get().usera.get().email if nc.commissario.get().usera else "") + "\t"
        nc_str += str(nc.dataNonconf) + "\t"
        nc_str += str(nc.tipo) + "\t"
        nc_str += str(nc.richiestaCampionatura) + "\n"
        self.response.out.write(nc_str)
        
      return

    if self.request.get("cmd") == "fixnodeperm":
      what = self.request.get("kind")
      if what == "node":
        for n in SocialNode.query():
          if n.default_admin == True or n.default_comment == False:
            n.default_admin = False
            n.default_comment = True
            n.put()

      if what == "sub":
        limit = int(self.request.get("limit"))
        offset = int(self.request.get("offset"))
            
        for ns in SocialNodeSubscription.query().fetch(limit=limit, offset=offset):
          if ns.can_admin == True or ns.can_comment == False:
            ns.can_admin = False
            ns.can_comment = True
            ns.put_async()
          
    if self.request.get("cmd") == "upCommissioni":
      data = self.request.get("rawdata")
      for line in data.split("\n"):
        logging.info(line)
        field = line.split("\t")
        if len(field) > 14:
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

    if self.request.get("cmd") == "migSocial":
      #SocialUtils.msg_to_post()
      self.response.out.write("migSocial Ok")
      return

    if self.request.get("cmd") == "flush":
      memcache.flush_query()
      self.response.out.write("flush Ok")
      return

    if self.request.get("cmd") == "flushnews":
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

    if self.request.get("cmd") == "dncmzona":
      for cm in Commissione.query():
        self.response.out.write(str(cm.key.id()) + "\t" + cm.desc() + "\t" + cm.strada + "\t" + str(cm.zona) + "\n")
      return

    if self.request.get("cmd") == "upcmzona":
      data = self.request.get("rawdata")
      for line in data.split("\n"):
        logging.info(line)
        fields = line.split("\t")
        if len(fields) > 2:
          cm = model.Key("Commissione", int(fields[0])).get()
          cm.zona = str(int(fields[3]))
          cm.put_async()
      self.response.out.write("upcmzona Ok")
      return

    if self.request.get("cmd") == "upcmzona":
      data = self.request.get("rawdata")
      for line in data.split("\n"):
        logging.info(line)
        fields = line.split("\t")
        if len(fields) > 2:
          cm = model.Key("Commissione", int(field[0])).get()
          cm.zona = fields[3]
          cm.put_async()

    if self.request.get("cmd") == "migrate":
      what = self.request.get("kind")
      limit = int(self.request.get("limit"))
      offset = int(self.request.get("offset"))
      SocialAdmin.migrate(what, offset, limit)

    if self.request.get("cmd") == "init_last_ntfy":
      limit = int(self.request.get("limit"))
      s_futures = list()
      for s in SocialNodeSubscription.query().filter(SocialNodeSubscription.last_ntfy_sent==None).fetch(limit):
        s.last_ntfy_sent = datetime(s.starting_date.year, s.starting_date.month, s.starting_date.day)
        s_futures.append(s.put_async())
      Future.wait_all(s_futures)
      
    if self.request.get("cmd") == "vacuum_node_index":
      index = search.Index(name="index-nodes")
      while True:
        doc_ids = [doc.doc_id for doc in index.get_range(ids_only=True)]
        if not doc_ids:
          break
        index.delete(doc_ids)

    if self.request.get("cmd") == "vacuum_post_index":
      index = search.Index(name="index-posts")
      while True:
        doc_ids = [doc.doc_id for doc in index.get_range(ids_only=True)]
        if not doc_ids:
          break
        index.delete(doc_ids)

    if self.request.get("cmd") == "prune_index":
      index = search.Index(name="index-nodes")
      for doc in index.get_range(ids_only=True):
        try:
          item = model.Key(urlsafe=doc.doc_id[5:]).get()
        except:
          index.delete(doc_ids)

      index = search.Index(name="index-posts")
      for doc in index.get_range(ids_only=True):
        try:
          item = model.Key(urlsafe=doc.doc_id[5:]).get()
        except:
          index.delete(doc_ids)

    if self.request.get("cmd") == "refresh_index":
      for node in SocialNode.query():
        fields = [search.TextField(name='name', value=node.name),
         search.HtmlField(name='description', value=node.description)]
        if node.geo:
          fields.append(search.GeoField(name='geo', value=search.GeoPoint(node.geo.lat, node.geo.lon)))

        doc=search.Document(
                        doc_id='node-'+str(node.key.id()),
                        fields=fields,
                        language='it')


        index = search.Index(name='index-nodes')
        try:
            index.put(doc)

        except search.Error, e:
            pass
      for post in SocialPost.query():
        resource = ""
        for r in post.resource:
          resource += r.get().restype + " "

        #logging.info(resource)
        ref_date = post.created
        if len(post.resource) > 0:
          if post.resource[0].kind() in ["Ispezione","Dieta"]:
            ref_date = post.resource[0].get().dataIspezione
          elif post.resource[0].kind() == ["Nonconformita"]:
            ref_date = post.resource[0].get().dataNonconf
          elif post.resource[0].kind() == ["Nota"]:
            ref_date = post.resource[0].get().dataNota

        doc=search.Document(
                        doc_id='post-'+post.key.urlsafe(),
                        fields=[search.TextField(name='node', value=post.key.parent().get().name),
                                search.TextField(name='author', value=post.commissario.nomecompleto(cmsro=None, myself=True)),
                                search.TextField(name='title', value=post.title),
                                search.HtmlField(name='content', value=post.content),
                                search.HtmlField(name='comments', value=post.get_comments_text()),
                                search.TextField(name='resources', value=resource),
                                search.TextField(name='attach', value=str(len(post.attachments)>0)),
                                search.DateField(name='date', value=ref_date)
                                ],
                        language='it')


        index = search.Index(name='index-posts')
        try:
            index.put(doc)

        except search.Error, e:
            pass

    if self.request.get("cmd") == "deact_profile":
      data = self.request.get("rawdata")
      for email in data.splitlines():
        logging.info("deactivating: " + email)
        commissario = Commissario.get_by_email_lower(email)
        
        if commissario:
          for commissione in commissario.commissioni():
            commissario.unregister(commissione)
        
          #unsubscribe nodes
          for sn in SocialNodeSubscription.get_by_user(commissario.usera.get()):
            sn.key.delete()
  
          for sp in SocialPostSubscription.get_by_user(commissario.usera.get()):
            sp.key.delete()
        
          commissario.stato = 99
          commissario.put()
          commissario.set_cache()
        
          for ue in models.UserEmail.get_by_user(commissario.usera.id()):
            ue.key.delete()
          
          logging.info("deactivated: " + email)

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

  def delete_all_in_index(self, index_name):
      """Delete all the docs in the given index."""
      doc_index = search.Index(name=index_name)

      while True:
          # Get a list of documents populating only the doc_id field and extract the ids.
          document_ids = [document.doc_id
                          for document in doc_index.list_documents(ids_only=True)]
          if not document_ids:
              break
          # Remove the documents for the given ids from the Index.
          doc_index.remove(document_ids)

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


class SocialAdmin(object):
  @classmethod
  def migrate(cls, what, offset, limit):
      if what == "nodes":
        logging.info("generate_nodes.city")
        citta=Citta.get_all()
        for i in citta:
          node=SocialNode(name=i.nome,description="Gruppo di discussione sulla citta di "+i.nome,resource=[i.key])
          node.init_rank()
          node.put()
  
        logging.info("generate_nodes.cm")

        commissioni=Commissione.query().fetch()
        for i in commissioni:
          logging.info("node: " + i.nome)
          c = i.citta.get()
          node = SocialNode(name = i.nome + " " + i.tipoScuola,
                          description="Gruppo di discussione per la scuola " + i.tipoScuola + " " + i.nome + " di " + c.nome, resource=[i.key])
          node.init_rank()
          node.put()

        logging.info("generate_nodes.tag")
      tags_mapping = {"salute": "Salute",
                      "educazione alimentare": "Educazione alimentare",
                      "commissioni mensa": "Commissioni Mensa",
                      "dieta": "Diete speciali",
                      "nutrizione": "Nutrizione",
                      "milano ristorazione": "Milano",
                      "eventi": "Eventi",
                      "assemblea cittadina": "Commissioni Mensa",
                      "mozzarella blu": "Commissioni Mensa",
                      "dieta mediterranea": "Nutrizione",
                      "commercio equo e solidale": "Generale",
                      "celiaci": "Diete speciali",
                      "centro cucina": "Commissioni Mensa",
                      "tip of the week": "Commissioni Mensa",
                      "rassegna stampa": "Generale",
                      "": "Generale",
                      }
      for tag in tags_mapping:
        logging.info("tag: " + tag)
        node = SocialNode.query().filter(SocialNode.name==tags_mapping[tag]).get()
        if not node:
            node = SocialNode(name = tags_mapping[tag],
                        description="Gruppo di discussione su " + tags_mapping[tag] )
            node.init_rank()
            node.put()
        tags_mapping[tag] = node
  
      node_default = tags_mapping["rassegna stampa"]

      if what == "subscriptions":
        #subscriptions
        logging.info("subscriptions.city")
        for co in Commissario.get_all(limit=limit, offset=offset):
          Cache.clear_all_caches()
          logging.info("subscriptions: " + co.user_email_lower)
          logging.info("subscriptions.city")
          node_citta = SocialNode.get_by_resource(co.citta)[0]
          node_citta.subscribe_user(co.usera.get(), ntfy_period=1)

          logging.info("subscriptions.tags")
          for tag in tags_mapping:
            node_tag = tags_mapping[tag]
            node_tag.subscribe_user(co.usera.get(), ntfy_period=1)

          logging.info("subscriptions.cm")
          for cm in co.commissioni():
            logging.info("subscriptions.cm: " + cm.nome)
            cms = SocialNode.get_by_resource(cm.key)
            if len(cms) > 0:
              node_cm = SocialNode.get_by_resource(cm.key)[0]
              node_cm.subscribe_user(co.usera.get(), ntfy_period=1)
            else:
              logging.info(cm.name + " not found")
            #zone
            if cm.zona:
              nodes = SocialNode.get_by_name(cm.citta.get().nome + " - Zona " + str(cm.zona))
              if len(nodes) > 0:
                nodes[0].subscribe_user(co.usera.get(), 1)


      if what == "messages":
        for m in Messaggio.query().filter(Messaggio.livello == 0).filter().order(Messaggio.creato_il).fetch(limit=limit, offset=offset):
          logging.info("msg: " + m.title)
          post = None
          if m.tipo in [101,102,103,104]:
            #dati: get node by cm (resource)
            node = SocialNode.get_by_resource(m.grp)[0]
            post=node.create_open_post(author=m.c_ua.get(), title=m.title, content=m.body, resources=[m.par]).get()
            #allegati a ispezioni e note
            for a in m.par.get().get_allegati:
              logging.info("msg.par.allegati")
              a.obj = post.key
              a.put()

          elif m.tipo == 201:
            #messaggi
            node = None
            if len(m.tags) > 0:
                node = tags_mapping[m.tags[0].nome]
            if not node:
                node = node_default
            post=node.create_open_post(m.c_ua.get(), m.title, m.body, []).get()
            #allegati a messaggi
            for a in m.get_allegati:
              logging.info("msg.allegati")
              a.obj = post.key
              a.put()


          post.created = m.creato_il
          init_rank = post.created - Const.BASE_RANK
          post.rank = init_rank.seconds + (init_rank.days*Const.DAY_SECONDS)
          post.put()

          #commenti
          if m.commenti:
            logging.info("msg.commenti")
            for mc in Messaggio.get_by_parent(m.key):
              comment = post.create_comment(mc.body, mc.c_ua.get())
              comment.created = mc.creato_il
              comment.put()
              for v in mc.votes:
                logging.info("msg.voti")
                vote = Vote(c_u = v.c_ua, c_d = v.creato_il, ref=comment.key, vote = v.voto)
                vote.put()

          #voti
          for v in m.votes:
            logging.info("msg.voti")
            vote = Vote(c_u = v.c_ua, c_d = m.creato_il, ref=post.key, vote = v.voto)
            vote.put()

      logging.info("migrate.end")

app = webapp.WSGIApplication([
  ('/admin/commissione', CMAdminCommissioneHandler),
  ('/admin/commissione/getdata', CMAdminCommissioneDataHandler),
  ('/admin/menu', AdminMenuHandler),
  ('/admin/commissario', CMAdminCommissarioHandler),
  ('/admin', CMAdminHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

def main():
  app.run();

if __name__ == "__main__":
  main()
