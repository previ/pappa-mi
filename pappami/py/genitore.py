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

from py.base import BasePage, CMCommissioniDataHandler, CMCommissioniHandler, CMMenuHandler

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
from py.form import NotaForm
from py.stats import CMStatsHandler
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
      self.redirect("/genitore/menu")

class CMGenitoreDataHandler(CMCommissarioDataHandler):
  def dummy(self):
    a
  
class CMIspezioniGenitoreHandler(BasePage):
  def get(self):
    template_values = dict()
    template_values["content_left"] = "genitore/leftbar.html"
    template_values['content'] = 'genitore/ispezioni.html'
    self.getBase(template_values)

class CMNonconfsGenitoreHandler(BasePage):
  def get(self):
    template_values = dict()
    template_values["content_left"] = "genitore/leftbar.html"
    template_values['content'] = 'genitore/nonconfs.html'
    self.getBase(template_values)
    
class CMRegistrazioneGenitoreHandler(BasePage):
  
  def get(self): 
    commissioni = self.getCommissioni()

    template_values = dict()
      
    commissario = self.getCommissario(users.get_current_user())
    if commissario is not None and not commissario.isGenitore():
      self.redirect("/")
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
      commissario.emailComunicazioni = self.request.get("emailalert")
      commissario.put()
      
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()

      commissario.setCMDefault()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
        
      self.sendRegistrationRequestMail(commissario)
    
    template_values = {
      'content': 'genitore/registrazione_ok.html',
      'cmsro': commissario
    }
    self.getBase(template_values)

  def sendRegistrationRequestMail(self, commissario) :

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

class CMProfiloGenitoreHandler(BasePage):
  def get(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    template_values = {
      'content_left': 'genitore/leftbar.html',
      'content': 'genitore/profilo.html',
      'cmsro': commissario
    }
    self.getBase(template_values)
  
  def post(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario):
      commissario.nome = self.request.get("nome")
      commissario.cognome = self.request.get("cognome")
      commissario.emailComunicazioni = self.request.get("emailalert")
      commissario.put()      

      for cc in CommissioneCommissario.all().filter("commissario",commissario):
        cc.delete()
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()

      commissario.setCMDefault()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
        
    template_values = {
      'content_left': 'genitore/leftbar.html',
      'content': 'genitore/profilo.html',
      'saved': True,      
      'cmsro': commissario
    }
    self.getBase(template_values)

    
class CMIspezioneGenitoreHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is not None and commissario.isCommissario() :
      self.redirect("/commissario/ispezione?cmd=open&key="+self.request.get("key"))
      return
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
      'cancopy': cancopy,
      "public_url": "http://" + self.getHost() + "/public/isp?key=" + str(isp.key())
      }

    self.getBase(template_values)

        

class CMNonconfGenitoreHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is not None and commissario.isCommissario() :
      self.redirect("/commissario/nonconf?cmd=open&key="+self.request.get("key"))
      return
    if commissario is None or not commissario.isGenitore() :
      self.redirect("/genitore/registrazione")
      return

    nc = Nonconformita.get(self.request.get("key"))

    template_values = {
      'content': 'genitore/nonconf_read.html',
      'content_left': 'genitore/leftbar.html',
      'nc': nc,
      "public_url": "http://" + self.getHost() + "/public/nc?key=" + str(nc.key())
      }

    self.getBase(template_values)

class CMDieteGenitoreHandler(BasePage):
  def get(self):
    template_values = dict()
    template_values["content_left"] = "genitore/leftbar.html"
    template_values['content'] = 'genitore/diete.html'
    self.getBase(template_values)

class CMDietaGenitoreHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is not None and commissario.isCommissario() :
      self.redirect("/commissario/dieta?cmd=open&key="+self.request.get("key"))
      return
    if commissario is None or not commissario.isGenitore() :
      self.redirect("/genitore/registrazione")
      return

    dieta = Dieta.get(self.request.get("key"))

    template_values = {
      'content': 'genitore/dieta_read.html',
      'content_left': 'genitore/leftbar.html',
      'dieta': dieta,
      "public_url": "http://" + self.getHost() + "/public/dieta?key=" + str(dieta.key())
      }

    self.getBase(template_values)

class CMNoteGenitoreHandler(BasePage):
  def get(self):
    template_values = dict()
    template_values["content_left"] = "genitore/leftbar.html"
    template_values['content'] = 'genitore/note.html'
    self.getBase(template_values)

class CMNotaGenitoreHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is not None and commissario.isCommissario() :
      self.redirect("/commissario/nota?cmd=open&key="+self.request.get("key"))
      return
    if commissario is None or not commissario.isGenitore() :
      self.redirect("/genitore/registrazione")
      return
    
    if( self.request.get("cmd") == "" or self.request.get("cmd") == "open" ):
      nota = Nota.get(self.request.get("key"))
      allegati = None
      if nota.allegato_set.count():
        allegati = nota.allegato_set
  
      template_values = {
        'content': 'genitore/nota_read.html',
        'content_left': 'genitore/leftbar.html',
        'nota': nota,
        "public_url": "http://" + self.getHost() + "/public/nota?key=" + str(nota.key()),
        "allegati": allegati
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      nota = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("nota"))
    
      form = NotaForm(instance=nota)
      
      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
      
      form.data["commissione"] = nota.commissione

      template_values = {
        'content': 'genitore/nota.html',
        'content_left': 'genitore/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      nota = Nota(commissario = commissario) 
      form = NotaForm(instance=nota)

      for field in form:
        form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'content': 'genitore/nota.html',
        'content_left': 'genitore/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  def post(self):    
   
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())

    if commissario is None or not commissario.isGenitore() :
      return
    preview = self.request.get("preview")
   
    if( preview ):
      nota = memcache.get(preview)
      memcache.delete(preview)

      if nota.dataNota.month >= 9:
        nota.anno = nota.dataNota.year
      else:
        nota.anno = nota.dataNota.year - 1

      nota.put()
      memcache.delete("stats")
      memcache.delete("statsMese")
      
      self.redirect("/genitore/note")
    else:
      key = self.request.get("k")
      if( key != "" ) :
        nota = Nota.get(key)
      else:
        nota = Nota()
    
      form = NotaForm(data=self.request.POST, instance=nota)

      if form.is_valid():
        nota = form.save(commit=False)
        nota.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, nota, 3600)
    
        template_values = {
          'content': 'genitore/nota_read.html',
          'content_left': 'genitore/leftbar.html',
          'nota': nota,
          'preview': preview
        }
        
      else:
        template_values = {
          'content': 'genitore/nota.html',
          'content_left': 'genitore/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form
        }
        
      self.getBase(template_values)
    
class CMGenitoreCommissioniHandler(CMCommissioniHandler):
  def get(self):
    template_values = dict()
    template_values["content_left"] = "genitore/leftbar.html"
    self.getBase(template_values)
    
      
class CMGenitoreStatsHandler(CMStatsHandler):
  def post(self):
    return self.get()

  def get(self):
    template_values = dict()
    template_values["content_left"] = "genitore/leftbar.html"
    self.getBase(template_values)

class CMGenitoreMenuHandler(CMMenuHandler):
  def post(self):
    return self.get()

  def get(self):
    template_values = dict()
    template_values["content_left"] = "genitore/leftbar.html"
    self.getBase(template_values)
    
def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
    ('/genitore/isp', CMIspezioniGenitoreHandler),
    ('/genitore/nc', CMNonconfsGenitoreHandler),
    ('/genitore/diete', CMDieteGenitoreHandler),
    ('/genitore/note', CMNoteGenitoreHandler),
    ('/genitore/ispezione', CMIspezioneGenitoreHandler),
    ('/genitore/nonconf', CMNonconfGenitoreHandler),
    ('/genitore/dieta', CMDietaGenitoreHandler),
    ('/genitore/nota', CMNotaGenitoreHandler),
    ('/genitore/registrazione', CMRegistrazioneGenitoreHandler),
    ('/genitore/profilo', CMProfiloGenitoreHandler),
    ('/genitore/stats', CMGenitoreStatsHandler),
    ('/genitore/commissioni', CMGenitoreCommissioniHandler),
    ('/genitore/menu', CMGenitoreMenuHandler),
    ('/genitore', CMGenitoreHandler),
    ('/genitore/getcm', CMCommissioniDataHandler),
    ('/genitore/getdata', CMGenitoreDataHandler)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)
      
if __name__ == "__main__":
  main()
