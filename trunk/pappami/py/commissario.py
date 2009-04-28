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

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required

from py.model import *
from py.form import IspezioneForm

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMCommissarioHandler(webapp.RequestHandler):

  def get(self): 
    user = users.get_current_user()
    commissario = db.GqlQuery("SELECT * FROM Commissario WHERE user = :1", user).get()
    if( commissario is None):
      self.request.redirect("/commissario/registrazione")
    else:

      url = users.create_logout_url("/")
      url_linktext = 'Logout'
      ispezioni = Ispezione.all().filter("commissario = ", commissario).order("-dataIspezione")
      template_values = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext,
        'ispezioni': ispezioni,
        }
      path = os.path.join(os.path.dirname(__file__), '../templates/commissario/commissario.html')
      self.response.out.write(template.render(path, template_values))

class CMRegistrazioneHandler(webapp.RequestHandler):
  
  def get(self): 
    commissioni = Commissione.all().order("nome")
    url = users.create_logout_url("/")
    url_linktext = 'Logout'
    user = users.get_current_user()
      
    template_values = {
      'commissioni': commissioni,     
      'user': user,
      'admin': users.is_current_user_admin(),
      'commissario': False,
      'url': url,
      'url_linktext': url_linktext
    }

    commissario = Commissario.all().filter("user", user).get()
    if commissario is not None:
      path = os.path.join(os.path.dirname(__file__), '../templates/commissario/registrazione_ok.html')
      template_values["commissario"] = commissario
    else:
      path = os.path.join(os.path.dirname(__file__), '../templates/commissario/registrazione.html')
    
    self.response.out.write(template.render(path, template_values))
  
  def post(self):
    user = users.get_current_user()
    commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
    if(commissario == None):
      commissario = Commissario(nome = self.request.get("nome"), cognome = self.request.get("cognome"), user = user, stato = 0)
      commissario.put()
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()
      
    url = users.create_logout_url("/")
    url_linktext = 'Logout'
    user = users.get_current_user()

    template_values = {
      'commissario': commissario,     
      'user': user,
      'admin': users.is_current_user_admin(),
      'url': url,
      'url_linktext': url_linktext
    }
    path = os.path.join(os.path.dirname(__file__), '../templates/commissario/registrazione_ok.html')
    self.response.out.write(template.render(path, template_values))

class CMIspezioneHandler(webapp.RequestHandler):
  
  @login_required
  def get(self): 
    if( self.request.get("cmd") == "open" ):
      isp = Ispezione.get(self.request.get("key"))
  
      url_linktext = 'Logout'
      url = users.create_logout_url("/")
      user = users.get_current_user()

      template_values = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext,
        'isp': isp,
        'key': isp.key(),
        }
      
      path = os.path.join(os.path.dirname(__file__), '../templates/commissario/ispezione_read.html')
      self.response.out.write(template.render(path, template_values))

    elif( self.request.get("cmd") == "edit" ):
   
      isp = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("preview"))
     
      form = IspezioneForm(instance=isp)
      
      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
        
      url_linktext = 'Logout'
      url = users.create_logout_url("/")
      user = users.get_current_user()

      template_values = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext,
        'form': form,
        'commissioni': Commissario.all().filter("user", user).filter("stato", 1).get().commissioni()
      }
      
      path = os.path.join(os.path.dirname(__file__), '../templates/commissario/ispezione.html')
      self.response.out.write(template.render(path, template_values))
    
    else:     
      user = users.get_current_user()
      commissario = Commissario.all().filter("user", user).filter("stato", 1).get()

      url_linktext = 'Logout'
      url = users.create_logout_url("/")
  
      isp = Ispezione(commissario = commissario) 
      form = IspezioneForm(instance=isp)

      for field in form:
        #logging.info(field.name)
        form.data[field.name] = str(form.initial[field.name])
         
      template_values = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext,
        'form': form,
        'commissioni': Commissario.all().filter("user", user).order("nome").get().commissioni()
        }

      path = os.path.join(os.path.dirname(__file__), '../templates/commissario/ispezione.html')
      self.response.out.write(template.render(path, template_values))

  def post(self):    
    user = users.get_current_user()
    commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
   
    preview = self.request.get("preview")
   
    if( preview ):
      isp = memcache.get(preview)
      memcache.delete(preview)
      isp.put()

      ispezioni = Ispezione.all().filter("commissario = ", commissario).order("-dataIspezione")    
      
      url = users.create_logout_url("/")
      url_linktext = 'Logout'
  
      template_values = {
        'user': user,
        'admin': users.is_current_user_admin(),
        'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
        'url': url,
        'url_linktext': url_linktext,
        'ispezioni': ispezioni
        }
  
      path = os.path.join(os.path.dirname(__file__), '../templates/commissario/commissario.html')
      self.response.out.write(template.render(path, template_values))
    else:
      key = self.request.get("key")
      if( key != "" ) :
        isp = Ispezione.get(key)
      else:
        isp = Ispezione()
    
      form = IspezioneForm(data=self.request.POST, instance=isp)
      
      if form.is_valid():
        isp = form.save(commit=False)
        
        isp.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        logging.info(preview)
        memcache.add(preview, isp, 3600)
  
        url_linktext = 'Logout'
        url = users.create_logout_url("/")
        user = users.get_current_user()
  
        template_values = {
          'user': user,
          'admin': users.is_current_user_admin(),
          'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
          'url': url,
          'url_linktext': url_linktext,
          'isp': isp,
          'preview': preview
        }
        
        path = os.path.join(os.path.dirname(__file__), '../templates/commissario/ispezione_read.html')
        self.response.out.write(template.render(path, template_values))
      else:
        #logging.info("data: %s", form.data)
        for e in form.errors["__all__"] :
          logging.info("errors: %s", e)

        url_linktext = 'Logout'
        url = users.create_logout_url("/")
        user = users.get_current_user()
  
        template_values = {
          'user': user,
          'admin': users.is_current_user_admin(),
          'commissario': Commissario.all().filter("user", user).filter("stato", 1).get() is not None,
          'commissioni': Commissario.all().filter("user", user).filter("stato", 1).get().commissioni(),
          'url': url,
          'url_linktext': url_linktext,
          'form': form
        }
        
        path = os.path.join(os.path.dirname(__file__), '../templates/commissario/ispezione.html')
        self.response.out.write(template.render(path, template_values))


  def saveIspezione(self, isp):
    isp.commissione = Commissione.get(db.Key(self.request.get("commissione")))

    isp.data = datetime.strptime(self.request.get("dataIspezione"),DATE_FORMAT).date()
  
    isp.ncCrudoBruciato = self.request.get("ncCrudoBruciato")
    isp.ncCorpiEstranei = self.request.get("ncCorpiEstranei")
    isp.ncCattivoOdore = self.request.get("ncCattivoOdore")
    isp.ncGustoSospetto = self.request.get("ncGustoSospetto")
    isp.ncRichiestaCampionatura = self.request.get("ncRichiestaCampionatura")

    isp.ncMenuDiverso = self.request.get("ncMenuDiverso")
 
    isp.numeroPastiTotale = int(self.request.get("numeroPastiTotale"))
    isp.numeroPastiBambini = int(self.request.get("numeroPastiBambini"))
    isp.numeroPastiSpeciali = int(self.request.get("numeroPastiSpeciali"))
    isp.numeroAddetti = int(self.request.get("numeroAddetti"))

    isp.puliziaRefettorio = int(self.request.get("puliziaRefettorio"))

    isp.ricicloStoviglie = self.request.get("ricicloStoviglie")
    isp.ricicloPosate = self.request.get("ricicloPosate")
    isp.ricicloBicchieri = self.request.get("ricicloBicchieri")

    isp.arrivoTermiche = datetime.strptime(self.request.get("arrivoTermiche"),TIME_FORMAT).time()

    isp.primoDistribuzione = datetime.strptime(self.request.get("primoDistribuzione"),TIME_FORMAT).time()
    isp.primoCottura = int(self.request.get("primoCottura"))
    isp.primoTemperatura = int(self.request.get("primoTemperatura"))
    isp.primoAssaggio = int(self.request.get("primoAssaggio"))
    isp.primoGradimento = int(self.request.get("primoGradimento"))
    isp.primoQuantita = int(self.request.get("primoQuantita"))
    #isp.primoNote = self.request.get("primoNote")

    isp.secondoDistribuzione = datetime.strptime(self.request.get("secondoDistribuzione"),TIME_FORMAT).time()
    isp.secondoCottura = int(self.request.get("secondoCottura"))
    isp.secondoTemperatura = int(self.request.get("secondoTemperatura"))
    isp.secondoAssaggio = int(self.request.get("secondoAssaggio"))
    isp.secondoGradimento = int(self.request.get("secondoGradimento"))
    isp.secondoQuantita = int(self.request.get("secondoQuantita"))
    #isp.secondoNote = self.request.get("secondoNote")

    isp.contornoCottura = int(self.request.get("contornoCottura"))
    isp.contornoTemperatura = int(self.request.get("contornoTemperatura"))
    isp.contornoAssaggio = int(self.request.get("contornoAssaggio"))
    isp.contornoGradimento = int(self.request.get("contornoGradimento"))
    isp.contornoQuantita = int(self.request.get("contornoQuantita"))
    #isp.contornoNote = self.request.get("contornoNote")

    isp.paneAssaggio = int(self.request.get("paneAssaggio"))
    isp.paneGradimento = int(self.request.get("paneGradimento"))
    isp.paneQuantita = int(self.request.get("paneQuantita"))
    #isp.paneNote = self.request.get("paneNote")

    isp.fruttaTipo = self.request.get("fruttaTipo")
    isp.fruttaAssaggio = int(self.request.get("fruttaAssaggio"))
    isp.fruttaGradimento = int(self.request.get("fruttaGradimento"))
    #isp.fruttaQuantita = int(self.request.get("fruttaQuantita"))
    #isp.fruttaNote = self.request.get("fruttaNote")

    isp.finePasto = datetime.strptime(self.request.get("finePasto"),TIME_FORMAT).time()
    
    isp.lavaggioFinale = int(self.request.get("lavaggioFinale"))
    isp.smaltimentoRifiuti = int(self.request.get("smaltimentoRifiuti"))
    isp.giudizioGlobale = int(self.request.get("giudizioGlobale"))
    isp.note = self.request.get("note")

application = webapp.WSGIApplication([
  ('/commissario/ispezione', CMIspezioneHandler),
  ('/commissario/registrazione', CMRegistrazioneHandler),
  ('/commissario', CMCommissarioHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
