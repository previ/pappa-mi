#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import random

from google.appengine.ext.ndb import model
from engineauth import models, middleware
from google.appengine.api import users
import webapp2 as webapp
from webapp2_extras import security
from google.appengine.api import memcache
from google.appengine.api import mail

from google.appengine.ext.webapp import util
from base import BasePage, config, handle_404, handle_500

class LoginPage(BasePage):
  
  def get(self):
    user = self.request.user if self.request.user else None
    profiles = None

    if not self.getCommissario(self.request.user):
      template_values = dict()
      template_values["main"] = 'eauth/main.html'
      template_values["content"] = 'eauth/login.html'

      if "_messages" in self.request.session.data:
        messages = self.request.session.data.pop("_messages")
        template_values.update({'messages': messages})

      self.getBase(template_values)
    else:
      self.redirect("/")
  def post(self):
    return self.get()

class ProtectedPage(BasePage):
  
  def get(self):
    session = self.request.session if self.request.session else None
    user = self.request.user if self.request.user else None
    profiles = None
    emails = None
    if user:
      profile_keys = [model.Key('UserProfile', p) for p in user.auth_ids]
      profiles = model.get_multi(profile_keys)
      emails = models.UserEmail.get_by_user(user.key.id())
      template_values = {
          'theuser': user,
          'session': session,
          'profiles': profiles,
          'emails': emails,
          'logout': "/eauth/logout"
      }
      template_values["content"] = 'priv.html'
      self.getBase(template_values)
    else:
      self.redirect("/eauth/login?next="+self.request.path)
      
  def post(self):
    return self.get()

class LogoutPage(BasePage):
  
  def get(self):
    self.response.delete_cookie('_eauth')
    self.redirect("/")            
      
class SignupPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["main"] = '/eauth/main.html'
    template_values["content"] = '/eauth/signup.html'

    if not self.session.get("c"):
      a = random.randint(1, 10)
      b = random.randint(1, 10)
      
      self.session["a"] = str(a)
      self.session["b"] = str(b)
      self.session["c"] = str(a + b)
      
    template_values["cap_a"] = self.session["a"]
    template_values["cap_b"] = self.session["b"]
    #logging.info("SignupPage a: " + template_values["cap_a"] + " b " + template_values["cap_b"] + " c " + self.session["c"])
      
    self.getBase(template_values)
    
  def post(self):
    error = None
    email = self.request.get('email')
    password1 = self.request.get("password")
    password2 = self.request.get("password2")
    c1 = self.session.get("c")
    c2 = self.request.get("c")
    #logging.info("c1: " + str(c1) + " c2 " + str(c2))

    self.session["a"] = None
    self.session["b"] = None
    self.session["c"] = None

    if c1 != c2:
      error = "La risposta alla domanda di controllo &egrave; sbagliata, riprova"
    elif password1 != password2:
      error = "Controllo password non corretto"
    elif email is None or email == "":
      error = "Email non valida"
    else:
      user_info = {}
      user_info['emails'] = [{'value': email, 'type': 'home', 'primary': True, 'verified': False}]
      auth_id = models.User.generate_auth_id('password', email)
      u_i = {
          'auth_id': auth_id,
          'info': user_info,
          'extra': {
              'raw_info': user_info,
              }
      }
      
      profile = models.UserProfile.get_or_create(auth_id, u_i, password=security.generate_password_hash(password1, length=12))      

      self.request = middleware.EngineAuthRequest(self.request.environ)
      self.request.load_user_by_profile(profile)
      return self.redirect("/signup")
    
    if error:
      self.handle_error(error)

  def handle_error(self, error):
    template_values = dict()
    template_values["main"] = '/eauth/main.html'
    template_values["content"] = '/eauth/signup.html'
    a = random.randint(1, 10)
    b = random.randint(1, 10)
          
    if not self.session.get("c"):
      self.session["a"] = str(a)
      self.session["b"] = str(b)
      self.session["c"] = str(a + b)

    template_values["cap_a"] = self.session["a"]
    template_values["cap_b"] = self.session["b"]
    #logging.info("SignupPage a: " + template_values["cap_a"] + " b " + template_values["cap_b"] + " c " + self.session["c"])

    template_values["messages"] = [{'message': error}]
    self.getBase(template_values)
      
    
        

class PwdRecoverRequestPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["main"] = '/eauth/main.html'
    template_values["content"] = '/eauth/pwdrec1.html'

    a = random.randint(1, 10)
    b = random.randint(1, 10)
    
    self.session["c"] = str(a + b)
    template_values["cap_a"] = a
    template_values["cap_b"] = b
    
    self.getBase(template_values)
    
  def post(self):

    error = None
    password = None
    c1 = self.session.get("c")
    c2 = self.request.get("c")
    #logging.info("c1: " + c1 + " c2 " + c2)
    if c1 != c2:
      error = "La risposta alla domanda di controllo è sbagliata, riprova"
    else:
      email = self.request.get("email")
      #logging.info(email)
      user = models.UserEmail.get_by_emails([email])
      if user is None:
        error = "Email non presente in archivio"
      else:
        self.sendPwdRecEmail(email)
        error = "Ok"
    
    self.response.out.write(error)

  def sendPwdRecEmail(self, email):

    host = self.getHost()

    sender = "Pappa-Mi <aiuto@pappa-mi.it>"

    auth_id = models.User.generate_auth_id("password", email)
    profile = models.UserProfile.get_by_id(auth_id)
    url = self.getHost() + "/eauth/pwdrecch?key="+profile.key.urlsafe()

    message = mail.EmailMessage()
    message.sender = sender
    message.to = email
    message.bcc = sender
    message.subject = "Pappa-Mi: richiesta di cambio password"
    message.body = """ Hai chiesto di cambiare la password del tuo account.
    
    Clicca sul link di seguito per continuare:
    http://"""  + url + """

        
    Ciao
    Pappa-Mi staff
    
    """
      
    message.send()

    
    #logging.info("url: " + url)
    
class PwdRecoverChangePage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["main"] = '/eauth/main.html'
    template_values["content"] = '/eauth/pwdrec2.html'

    keycripted = self.request.get("key")    
    ##TODO DECRYPT
    key = keycripted
    if key is None:
      error = "Errore, richiesta non valida"
    else:
      userprofile = model.Key(urlsafe=key).get()
      if userprofile is None:
        error = "Errore, richiesta non valida"
      else:
        template_values["key"] = keycripted
        
    self.getBase(template_values)
        
  def post(self):

    error = None
    password = None
    password1 = self.request.get("password1")
    password2 = self.request.get("password2")

    keycripted = self.request.get("key")
    ##TODO DECRYPT
    key = keycripted

    userprofile = model.Key(urlsafe=key).get()
    
    if userprofile is None:
      error = "Email non presente in archivio"
    elif password1 != password2:
      error = "Controllo password non corretto"
    else:
      userprofile.password = security.generate_password_hash(password1, length=12)     
      userprofile.put()
      error = "Ok"
    
    self.response.out.write(error)

class PwdChangePage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["main"] = '/eauth/main.html'
    template_values["content"] = '/eauth/pwdchg.html'
        
    self.getBase(template_values)
        
  def post(self):

    error = None
    password = self.request.get("password")
    password1 = self.request.get("password1")
    password2 = self.request.get("password2")

    auth_id = models.User.generate_auth_id("password", self.request.user.email)
    userprofile = models.UserProfile.get_by_id(auth_id)
    
    if userprofile is None:
      error = "Email non presente in archivio"
    elif not security.check_password_hash(password, userprofile.password):
      error = 'La password non è corretta.'
    elif password1 != password2:
      error = "Controllo password non corretto"
    else:
      userprofile.password = security.generate_password_hash(password1, length=12)     
      userprofile.put()
      error = "Ok"
    
    self.response.out.write(error)

class RemoveAuthPage(BasePage):
  
  def get(self):
    strategy = self.request.get("p")

    auth_id = self.request.user.has_auth_strategy(strategy)
    self.request.user.remove_auth_strategy(auth_id)      
    error = "Ok"
    
    self.response.out.write(error)

class OpenIdLoginHandler(webapp.RequestHandler):
    def get(self):
      login_url = users.create_login_url(self.request.get('continue'), None, "https://www.google.com/accounts/o8/id")
      self.redirect(login_url)
    
    def post(self):
      self.get()
  
app = webapp.WSGIApplication([
  ('/eauth/login', LoginPage),
  ('/eauth/logout', LogoutPage),
  ('/eauth/pwdrecrq', PwdRecoverRequestPage),
  ('/eauth/pwdrecch', PwdRecoverChangePage),
  ('/eauth/pwdchg', PwdChangePage),
  ('/eauth/priv', ProtectedPage),
  ('/eauth/signup', SignupPage),
  ('/eauth/rmauth', RemoveAuthPage),
  ('/_ah/login_required', OpenIdLoginHandler),
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()
  