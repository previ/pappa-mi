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

from google.appengine.ext.ndb import model
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.api import mail
from engineauth import models

from gviz_api import *
from model import *
from base import BasePage, CMCommissioniDataHandler, commissario_required, user_required, reguser_required
from gcalendar import *
from form import CommissarioForm

class SignupPreHandler(BasePage):
  
  @user_required
  def get(self):   
    form = CommissarioForm()
    form.nome.data=""
    form.cognome.data=""
    user = self.request.user
    if len(user.auth_ids) == 1: #ensure this is for first registration only
      user_info = models.UserProfile.get_by_id(user.auth_ids[0]).user_info.get("info")
      logging.info("userinfo: " + str(user_info))
      if user_info.get("name"):
        if user_info.get("name").get("givenName"):
          form.nome.data=user_info.get("name").get("givenName")
        if user_info.get("name").get("familyName"):
          form.cognome.data=user_info.get("name").get("familyName")
      if user_info.get("image"):
        form.avatar_url.data=user_info.get("image").get("url")
    if not form.avatar_url.data:
      form.avatar_url.data = "/img/avatar/default_avatar.gif"
      
    form.privacy = [[0,1,1],[1,1,1],[0,1,1],[1,1,1],[0,1,1]]
    if user.email:
      form.email = user.email
    else:
      form.email = ""
    template_values = {
      'content': 'signup.html',
      'citta': Citta.get_all(),
      'form': form,
      'default_avatar': '/img/avatar/default_avatar.gif'
    }
    self.getBase(template_values)
    
  @user_required
  def post(self):
    return self.get()

class SignupHandler(BasePage):
  
    
  @user_required
  def post(self):
    user = self.request.user
    form = CommissarioForm(self.request.POST)

    if not user.email:
      user.email = self.request.get("email")      
      user.put()
      models.UserEmail.create(user.email, user.get_id())
    commissario = Commissario()

    form.populate_obj(commissario)
    commissario.usera = user.key
    commissario.citta = model.Key("Citta", int(self.request.get("citta")))
    commissario.user_email_lower = user.email.lower()
    commissario.put()


    new = list()
    for c_key in self.request.get_all("commissione"):
      new.append(int(c_key))
      logging.info("new " + c_key)
    new = set(new)
      
    for cm in new:
      commissione = model.Key("Commissione", cm).get()
      commissario.register(commissione)
      if commissione.calendario :
        calendario = Calendario();        
        #calendario.logon(user=Configurazione.get_value_by_name("calendar_user"), password=Configurazione.get_value_by_name("calendar_password"))
        #calendario.load(commissione.calendario)
        #calendario.share(commissario.usera.get().email)

    commissario.setCMDefault()
    memcache.set("commissario" + str(user.get_id()), commissario, 600)
      
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
    message.to = commissario.usera.get().email
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
  ('/signup', SignupPreHandler),
  ('/signup2', SignupHandler),
  ('/profilo/getcm', CMCommissioniDataHandler)], 
  debug=os.environ['HTTP_HOST'].startswith('localhost'))

def main():
  app.run();

if __name__ == "__main__":
  main()