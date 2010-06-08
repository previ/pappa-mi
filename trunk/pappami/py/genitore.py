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
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.form import IspezioneForm, NonconformitaForm
from py.main import BasePage
from py.commissario import CMCommissioniDataHandler
from py.commissario import CMCommissarioDataHandler

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMGenitoreHandler(BasePage):

  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isGenitore() :
      self.redirect("/genitore/registrazione")
    else:
      tab=self.request.get("tab")
      template_values = {
        'content_left': 'genitore/leftbar.html',
        'tab': tab
        }
      if tab == "nc" :
        template_values['content'] = 'genitore/nonconfs.html'
      elif tab == "ud" :
        template_values['content'] = 'genitore/profilo.html'
        template_values['cmsro'] = commissario
      else:
        template_values['content'] = 'genitore/ispezioni.html'
      
      #logging.info("OK")
      self.getBase(template_values)
    
class CMGenitoreDataHandler(CMCommissarioDataHandler):
  def dummy(self):
    self
      
class CMRegistrazioneGenitoreHandler(BasePage):
  
  def get(self): 
    commissioni = self.getCommissioni()

    template_values = dict()
      
    commissario = self.getCommissario(users.get_current_user())
    if commissario is not None:
      template_values["content"] = "genitore/registrazione_ok.html"
      template_values["cmsro"] = commissario
    else:
      template_values["content"] = "genitore/registrazione.html"
      
    self.getBase(template_values)
  
  def post(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario == None):
      commissario = Commissario(nome = self.request.get("nome"), cognome = self.request.get("cognome"), user = user, stato = 11)
      commissario.put()
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()

      self.sendRegistrationRequestMail(commissario)
    
    template_values = {
      'content': 'genitore/registrazione_ok.html',
      'cmsro': commissario
    }
    self.getBase(template_values)

  def sendRegistrationRequestMail(self, commissario) :

    host = self.getHost()
       
    message = mail.EmailMessage()
    message.sender = "aiuto@pappa-mi.it"
    message.to = commissario.user.email()
    message.bcc = "aiuto@pappa-mi.it"
    message.subject = "Benvenuto in Pappa-Mi"
    message.body = """ La tua richiesta di registrazione come Genitore e' stata confermata.
    
    Ora puoi accedere all'area a te riservata:
    
    Schede Ispezione e Non Conformita'
    http://"""  + host + """/genitore

    Dati statistici di tutte le Commissioni
    http://"""  + host + """/stats

    Documenti
    http://"""  + host + """/docs
    
    Ciao |
    Pappa-Mi staff
    
    """
      
    message.send()
      
class CMIspezioneGenitoreHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isGenitore() :
      self.redirect("/genitore/registrazione")
      return

    isp = Ispezione.get(self.request.get("key"))

    cancopy = None;
    if( isp.commissario.key() == commissario.key()):
      cancopy = True
    
    template_values = {
      'content': 'genitore/ispezione_read.html',
      'content_left': 'genitore/leftbar.html',
      'isp': isp,
      'cancopy': cancopy
      }

    self.getBase(template_values)

        

class CMNonconfGenitoreHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isGenitore() :
      self.redirect("/genitore/registrazione")
      return

    nc = Nonconformita.get(self.request.get("key"))


    template_values = {
      'content': 'genitore/nonconf_read.html',
      'content_left': 'genitore/leftbar.html',
      'nc': nc
      }

    self.getBase(template_values)

def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
    ('/genitore/ispezione', CMIspezioneGenitoreHandler),
    ('/genitore/nonconf', CMNonconfGenitoreHandler),
    ('/genitore/registrazione', CMRegistrazioneGenitoreHandler),
    ('/genitore', CMGenitoreHandler),
    ('/genitore/getcm', CMCommissioniDataHandler),
    ('/genitore/getdata', CMGenitoreDataHandler)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)
      
if __name__ == "__main__":
  main()
