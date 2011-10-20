#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from py.base import *

import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.form import CommissarioForm
from py.base import BasePage, roleCommissario, CMCommissioniDataHandler
from py.calendar import *

class CMProfiloHandler(BasePage):
  
  @login_required
  def get(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    template_values = {
      'content': 'profilo.html',
      'cmsro': commissario,
      'citta': Citta.all().order("nome")      
    }
    self.getBase(template_values)
    
  def post(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario):
      form = CommissarioForm(self.request.POST, commissario)
      form.populate_obj(commissario)
      
      #commissario.nome = self.request.get("nome")
      #commissario.cognome = self.request.get("cognome")
      #commissario.citta = db.Key(self.request.get("citta"))
      #commissario.emailComunicazioni = self.request.get("emailalert")
      commissario.put()

      old = list()
      for cc in CommissioneCommissario.all().filter("commissario",commissario):
        old.append(str(cc.commissione.key()))
        #logging.info("old " + cc.commissione.nome)
      old = set(old)

      new = list()
      for c_key in self.request.get_all("commissione"):
        new.append(c_key)
        logging.info("new " + Commissione.get(db.Key(c_key)).nome)
      new = set(new)

      todel = old - new
      toadd = new - old

      for cm in todel:
        cmd = Commissione.get(db.Key(cm))
        logging.info("delete " + cmd.nome)
        
        cc = CommissioneCommissario.all().filter("commissario",commissario).filter("commissione",cmd).get()
        """if cc.commissione.calendario :
          calendario = Calendario();        
          calendario.logon(user=Configurazione.all().filter("nome","calendar_user").get().valore, password=Configurazione.all().filter("nome", "calendar_password").get().valore)
          calendario.load(cc.commissione.calendario)
          calendario.unShare(commissario.user.email())"""
        cc.delete()
        cmd.numCommissari -= 1
        cmd.put()                
        
      for cm in toadd:
        cma = Commissione.get(db.Key(cm))
        logging.info("add " + cma.nome)

        cc = CommissioneCommissario(commissione = cma, commissario = commissario)
        cc.put()
        cma.numCommissari += 1
        cma.put()
        if cc.commissione.calendario :
          calendario = Calendario();        
          calendario.logon(user=Configurazione.all().filter("nome","calendar_user").get().valore, password=Configurazione.all().filter("nome", "calendar_password").get().valore)
          calendario.load(cc.commissione.calendario)
          calendario.share(commissario.user.email())

      commissario.setCMDefault()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
        
    self.response.out.write("Dati salvati.")

class CMAvatarHandler(BasePage):
      
  def post(self):
    cmd = self.request.get("cmd")
    logging.info("cmd:" + cmd)
    if cmd == "upload":
      commissario = self.getCommissario(users.get_current_user())
      avatar_file = self.request.get("avatar_file")
      logging.info("1")
      if avatar_file:
        if len(avatar_file) < 1000000 :
          logging.info("2")
          avatar = images.resize(self.request.get("avatar_file"), 128,128)
          commissario.avatar_data = avatar
          commissario.avatar_url = "/public/avatar?key=" + str(commissario.key())
          commissario.put()
          self.response.out.write(commissario.avatar()+"&size=big");
        else:
          logging.info("attachment is too big.")
    if cmd == "saveurl":
      commissario = self.getCommissario(users.get_current_user())
      commissario.avatar_url = self.request.get("picture")
      commissario.put()
    
app = webapp.WSGIApplication([
    ('/profilo', CMProfiloHandler),
    ('/profilo/avatar', CMAvatarHandler),
    ('/profilo/getcm', CMCommissioniDataHandler)],
    debug = os.environ['HTTP_HOST'].startswith('localhost'))

def main():
  app.run();

if __name__ == "__main__":
  main()