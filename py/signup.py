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
import random


from google.appengine.ext.ndb import model
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.api import mail
from engineauth import models

from gviz_api import *
from model import *
from base import BasePage, CMCommissioniDataHandler, commissario_required, user_required, reguser_required, config, handle_404, handle_500
#from gcalendar import *
from form import CommissarioForm

class SignupPreHandler(BasePage):

  @user_required
  def get(self):
    if self.getCommissario() and self.getCommissario().is_active():
      self.redirect("/")
    form = CommissarioForm()
    form.nome.data=""
    form.cognome.data=""
    user = self.request.user
    if len(user.auth_ids) == 1: #ensure this is for first registration only
      user_info = models.UserProfile.get_by_id(user.auth_ids[0]).user_info.get("info")
      #logging.info("userinfo: " + str(user_info))
      if user_info.get("name"):
        if user_info.get("name").get("givenName"):
          form.nome.data=user_info.get("name").get("givenName")
        if user_info.get("name").get("familyName"):
          form.cognome.data=user_info.get("name").get("familyName")
      if user_info.get("image"):
        form.avatar_url.data=user_info.get("image").get("url")
    if not form.avatar_url.data:
      form.avatar_url.data = "/img/default_avatar_" + str(random.randint(0, 7)) + ".png"

    form.privacy = [[0,1,1],[1,1,1],[0,1,1],[1,1,1],[0,1,1]]
    form.notify = [1,2,0]
    if user.email:
      form.email = user.email
    else:
      form.email = ""
    template_values = {
      'content': 'signup.html',
      'citta': Citta.get_all(),
      'form': form,
      'default_avatar': "/img/default_avatar_" + str(random.randint(0, 7)) + ".png"
    }
    self.getBase(template_values)

  @user_required
  def post(self):
    return self.get()

class SignupHandler(BasePage):

  @user_required
  def post(self):
    user = self.request.user
    #logging.info(user)
    form = CommissarioForm(self.request.POST)

    if not user.email:
      user.email = self.request.get("email")
      user.put()
      models.UserEmail.create(user.email, user.get_id())

    #SocialProfile.create(user.key)
    commissario = self.getCommissario()
    if not commissario:
      commissario = Commissario()

    form.populate_obj(commissario)
    commissario.usera = user.key
    commissario.citta = model.Key("Citta", int(self.request.get("citta")))
    commissario.user_email_lower = user.email.lower()

    privacy = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    for what in range(0,len(privacy)):
      for who in range(0,len(privacy[0])):
        if self.request.get("p_"+str(what)+"_"+str(who)):
          privacy[what][who] = int(self.request.get("p_"+str(what)+"_"+str(who)))

    notify = [0,0,0]
    for what in range(0,len(notify)):
      if self.request.get("n_"+str(what)):
        notify[what] = int(self.request.get("n_"+str(what)))

    commissario.privacy = privacy
    commissario.notify = notify

    commissario.put()
    commissario.set_cache()


    new = list()
    for c_key in self.request.get_all("commissione"):
      new.append(int(c_key))
      #logging.info("new " + c_key)
    new = set(new)

    for cm in new:
      commissione = model.Key("Commissione", cm).get()
      commissario.register(commissione)
      node = SocialNode.get_by_resource(commissione.key)[0]
      if node:
        node.subscribe_user(commissario.usera.get())
      if commissione.zona:
        nodes = SocialNode.get_by_name(commissione.citta.get().nome + " - Zona " + str(commissione.zona))
        if len(nodes) > 0:
          nodes[0].subscribe_user(commissario.usera.get())


    #default nodes
    def_nodes = ["Salute",
                 "Educazione alimentare",
                 "Commissioni Mensa",
                 "Nutrizione",
                 "Eventi",
                 "Generale"]
    for node_name in def_nodes:
      nodes = SocialNode.get_by_name(node_name)
      if len(nodes) > 0:
        nodes[0].subscribe_user(commissario.usera.get())

    commissario.setCMDefault()
    #logging.info(commissario.usera)
    commissario.set_cache()

    self.sendRegistrationRequestMail(commissario)

    message = "Registrazione completata."
    if commissario.isRegCommissario():
      message = "Grazie per esserti registrato, riceverai una mail quando il tuo profilo sarà stato attivato."

    self.response.out.write(message)


  def sendRegistrationRequestMail(self, commissario):
    if commissario.isGenitore():
      self.sendRegistrationConfirmGenitoreMail(commissario)
    else:
      self.sendRegistrationConfirmCommissarioMail(commissario)

  def sendRegistrationConfirmGenitoreMail(self, commissario) :

    host = self.getHost()

    sender = "Pappa-Mi <aiuto@pappa-mi.it>"

    message = mail.EmailMessage()
    message.sender = sender
    message.to = commissario.usera.get().email
    message.bcc = sender
    message.subject = "Benvenuto in Pappa-Mi"
    message.body = """ La tua richiesta di registrazione come Genitore e' stata confermata.

    Clicca qui per accedere a Pappa-Mi:
    http://"""  + host + """/


    Ti rocordo anche il sito PappaPedia (documenti):
    http://pappapedia.pappa-mi.it

    Ciao !
    Pappa-Mi staff

    """

    message.send()

  def sendRegistrationConfirmCommissarioMail(self, commissario) :

    host = self.getHost()

    sender = "Pappa-Mi <aiuto@pappa-mi.it>"

    message = mail.EmailMessage()
    message.sender = sender
    message.to = commissario.usera.get().email
    message.bcc = sender
    message.subject = "Benvenuto in Pappa-Mi"
    message.body = """ La tua richiesta di registrazione come Commissione Mensa e' stata confermata.

    Clicca qui per accedere a Pappa-Mi:
    http://"""  + host + """/


    Ti rocordo anche il sito PappaPedia (documenti):
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
    message.body = commissario.nome + " " + commissario.cognome + " " + commissario.usera.get().email + """ ha inviato una richiesta di registrazione come Commissario.

    Per abilitarlo usare il seguente link:

    """ + "http://" + host + "/admin/commissario?cmd=enable&key="+str(commissario.key.id())

    message.send()

app = webapp.WSGIApplication([
  ('/signup', SignupPreHandler),
  ('/signup2', SignupHandler),
  ('/profilo/getcm', CMCommissioniDataHandler)],
  debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()
