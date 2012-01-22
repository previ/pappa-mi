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
    commissario.put()
    commissario.user_email_lower = commissario.user.email().lower()
    commissario.put()

    old = list()
    for cc in CommissioneCommissario.all().filter("commissario",commissario):
      old.append(str(cc.commissione.key()))
    old = set(old)

    new = list()
    for c_key in self.request.get_all("commissione"):
      new.append(c_key)
      logging.info("new " + Commissione.get(db.Key(c_key)).nome)
    new = set(new)

    todel = old - new
    toadd = new - old

    for cm in todel:
      commissione = Commissione.get(cm)
      commissario.unregister(cm)
      if commissione.calendario :
        calendario = Calendario();        
        calendario.logon(user=Configurazione.get_value_by_name("calendar_user"), password=Configurazione.get_value_by_name("calendar_password"))
        calendario.load(commissione.calendario)
        calendario.unShare(commissario.user.email())
      
    for cm in toadd:
      commissione = Commissione.get(cm)
      commissario.register(cm)
      if cc.commissione.calendario :
        calendario = Calendario();        
        calendario.logon(user=Configurazione.get_value_by_name("calendar_user"), password=Configurazione.get_value_by_name("calendar_password"))
        calendario.load(cc.commissione.calendario)
        calendario.share(commissario.user.email())

    commissario.setCMDefault()
    memcache.set("commissario" + str(user.user_id()), commissario, 600)
      
    message = "Registrazione completata."
    if commissario.isRegCommissario():
      message = "Grazie per esserti registrato, riceverai una mail quando il tuo profilo sarà stato attivato."
      
    self.response.out.write(message)


  def sendRegistrationRequestMail(self, commissario):
    if commissario.isGenitore():
      cls.sendRegistrationGenitoreRequestMail(commissario)
    else:
      cls.sendRegistrationCommissarioRequestMail(commissario)      

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