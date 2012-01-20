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
from py.base import BasePage, roleCommissario, CMCommissioniDataHandler, commissario_required, user_required
from py.calendar import *
from py.form import CommissarioForm

class CMSignupHandler(BasePage):
  
  @login_required
  def get(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario:
      self.redirect("/")
    else:
      commissario = CommissarioForm()
      
    template_values = {
      'content': 'signup.html',
      'citta': Citta.all().order("nome"),
      'default_avatar': '/img/avatar/default_avatar.gif'
    }
    self.getBase(template_values)
    
  @login_required
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

class CMSignupHandlerOld(BasePage):
  
  def get(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario == None):
      stato = 11
      if self.request.get("iscm") == "S":
        stato = 0
      
      commissario = Commissario(nome = self.request.get("nome"), cognome = self.request.get("cognome"), user = user, stato = stato)
      if self.request.get("citta"):
        commissario.citta = db.Key(self.request.get("citta"))
      commissario.emailComunicazioni = "S"
      commissario.put()
          
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()

      commissario.setCMDefault()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
        
      self.sendRegistrationRequestMail(commissario)
    template_values = dict()
    template_values['cmsro'] = commissario
    if commissario.isRegCommissario():
      template_values['content'] = 'commissario/registrazione_ok.html'
      self.getBase(template_values)
    else:
      self.redirect("/genitore")

  def sendRegistrationRequestMail(self, commissario):
    if commissario.isGenitore():
      self.sendRegistrationGenitoreRequestMail(commissario)
    else:
      self.sendRegistrationCommissarioRequestMail(commissario)      

  def sendRegistrationGenitoreRequestMail(self, commissario) :

    host = self.getHost()

    sender = "Pappa-Mi <aiuto@pappa-mi.it>"
    
    message = mail.EmailMessage()
    message.sender = sender
    message.to = commissario.user.email()
    message.bcc = sender
    message.subject = "Benvenuto in Pappa-Mi"
    message.body = """ La tua richiesta di registrazione come Genitore e' stata confermata.
    
    Ora puoi accedere all'area a te riservata:
    http://"""  + host + """/genitore

    PappaPedia (documenti):
    http://pappapedia.pappa-mi.it
    
    Ciao !
    Pappa-Mi staff
    
    """
      
    message.send()

  def sendRegistrationCommissarioRequestMail(self, commissario) :

    host = self.getHost()
    
    sender = "Pappa-Mi <aiuto@pappa-mi.it>"
    
    message = mail.EmailMessage()
    message.sender = sender
    message.to = sender
    message.subject = "Richiesta di Registrazione da " + commissario.nome + " " + commissario.cognome
    message.body = commissario.nome + " " + commissario.cognome + " " + commissario.user.email() + """ ha inviato una richiesta di registrazione come Commissario. 
    
    Per abilitarlo usare il seguente link:
    
    """ + "http://" + host + "/admin/commissario?cmd=enable&key="+str(commissario.key())

    message.send()
    
app = webapp.WSGIApplication([
  ('/signup', CMSignupHandler),
  ('/profilo/getcm', CMCommissioniDataHandler)], 
  debug=os.environ['HTTP_HOST'].startswith('localhost'))

def main():
  app.run();

if __name__ == "__main__":
  main()