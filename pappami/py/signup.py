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
from py.base import BasePage, roleCommissario, CMCommissioniDataHandler
from py.calendar import *
from py.form import CommissarioForm

class CMSignupHandler(BasePage):
  
  def get(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario:
      self.redirect("/login")
    else:
      commissario = CommissarioForm()
      
    template_values = {
      'content': 'signup.html',
      'citta': Citta.all().order("nome"),
      'default_avatar': '/img/avatar/default_avatar.gif'
    }
    self.getBase(template_values)
    
  def post(self):
    user = users.get_current_user()
    form = CommissarioForm(self.request)

    commissario = Commissario()

    form.populate_obj(commissario)
    commissario.user = user
    #commissario.nome = self.request.get("nome")
    #commissario.cognome = self.request.get("cognome")
    #commissario.citta = db.Key(self.request.get("citta"))
    #commissario.stato = int(self.request.get("tipo"))
    #commissario.emailComunicazioni = self.request.get("emailalert")
    commissario.put()
    commissario.user_email_lower = commissario.user.email().lower()
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
      
    message = "Registrazione completata."
    if commissario.isRegCommissario():
      message = "Grazie per esserti registrato, riceverai una mail quando il tuo profilo sarà stato attivato."
      
    self.response.out.write(message)
    
app = webapp.WSGIApplication([
  ('/signup', CMSignupHandler),
  ('/profilo/getcm', CMCommissioniDataHandler)], 
  debug=os.environ['HTTP_HOST'].startswith('localhost'))

def main():
  app.run();

if __name__ == "__main__":
  main()