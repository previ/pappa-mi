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
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import random

from ndb import model
from engineauth import models
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required

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

    self.session["cap_a"] = random.randint(1, 10)
    self.session["cap_b"] = random.randint(1, 10)

    template_values["cap_a"] = self.session["cap_a"]
    template_values["cap_b"] = self.session["cap_b"]
    
    self.getBase(template_values)
    
  def post(self):
    pass
        

app = webapp.WSGIApplication([
  ('/eauth/login', LoginPage),
  ('/eauth/logout', LogoutPage),
  ('/eauth/priv', ProtectedPage),
  ('/eauth/signup', SignupPage)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'))
  
def main():
  app.run();

if __name__ == "__main__":
  main()
  