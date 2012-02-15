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

from ndb import model
from engineauth import models
from google.appengine.api import users
import webapp2 as webapp
from webapp2_extras import security
from google.appengine.api import memcache

from google.appengine.ext.webapp import util
from base import BasePage

class LoginPage(BasePage):
  
  def get(self):
    user = self.request.user if self.request.user else None
    profiles = None
    if user:
      logging.info(user.to_dict())
    if not self.getCommissario(self.request.user):
      logging.info("called")
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

    a = random.randint(1, 10)
    b = random.randint(1, 10)
    
    self.session["c"] = str(a + b)
    template_values["cap_a"] = a
    template_values["cap_b"] = b
    
    self.getBase(template_values)
    
  def post(self):
    error = None
    email = self.request.get('email')
    password1 = self.request.get("password")
    password2 = self.request.get("password2")
    c1 = self.session.get("c")
    c2 = self.request.get("c")
    logging.info("c1: " + c1 + " c2 " + c2)

    if c1 != c2:
      error = "La risposta alla domanda di controllo è sbagliata, riprova"
    elif password1 != password2:
      error = "Controllo password non corretto"
    elif email is None or email == "":
      error = "Email non valida"
    else:
      user_info = {}
      user_info['emails'] = [{'value': email, 'type': 'home', 'primary': True}]
      auth_id = models.User.generate_auth_id('password', email)
      u_i = {
          'auth_id': auth_id,
          'info': user_info,
          'extra': {
              'raw_info': user_info,
              }
      }
      
      models.UserProfile.get_or_create(auth_id, u_i, password=security.generate_password_hash(password1, length=12))      

    if error:
      self.response.out.write(error)
    else:
      self.redirect("/auth/password", code=307)
    
        

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
    logging.info("c1: " + c1 + " c2 " + c2)
    if c1 != c2:
      error = "La risposta alla domanda di controllo è sbagliata, riprova"
    else:
      email = self.request.get("email")
      logging.info(email)
      user = models.UserEmail.get_by_emails([email])
      if user is None:
        error = "Email non presente in archivio"
      else:
        self.sendPwdRecEmail(email)
        error = "Ok"
    
    self.response.out.write(error)

  def sendPwdRecEmail(self, email):
    auth_id = models.User.generate_auth_id("password", email)
    profile = models.UserProfile.get_by_id(auth_id)
    url = self.getHost() + "/eauth/pwdrecch?key="+profile.key.urlsafe()
    logging.info("url: " + url)
    
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
    
  
app = webapp.WSGIApplication([
  ('/eauth/login', LoginPage),
  ('/eauth/logout', LogoutPage),
  ('/eauth/pwdrecrq', PwdRecoverRequestPage),
  ('/eauth/pwdrecch', PwdRecoverChangePage),
  ('/eauth/pwdchg', PwdChangePage),
  ('/eauth/priv', ProtectedPage),
  ('/eauth/signup', SignupPage)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'))
  
def main():
  app.run();

if __name__ == "__main__":
  main()
  