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
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.form import IspezioneForm, NonconformitaForm
from py.main import BasePage

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMCommissarioHandler(BasePage):

  def get(self): 
    user = users.get_current_user()
    commissario = db.GqlQuery("SELECT * FROM Commissario WHERE user = :1", user).get()
    if( commissario is None):
      self.redirect("/commissario/registrazione")
    else:
      tab=self.request.get("tab")
      template_values = {
        'content_left': 'commissario/leftbar.html',
        'tab': tab
        }
      if tab == "nc":
        
        # Creating the data
        description_nc = {"commissione": ("string", "Commissione"), 
                       "dataNonconf": ("date", "Data"),
                       "turno": ("string", "Turno"),
                       "tipo": ("string", "Tipo"),
                       "key": ("string", "")}
        
        data_nc = list()
        for nc in Nonconformita.all().filter("commissario",commissario).order("-dataNonconf"):
          data_nc.append({"commissione": str(nc.commissione.nome), "dataNonconf": nc.dataNonconf, "turno": str(nc.turno), "tipo": nc.tipoNome(), 
                       "key":"<a class='btn' href='/commissario/nonconf?cmd=open&key="+str(nc.key())+"'>Apri</a>"})
  
        # Loading it into gviz_api.DataTable
        data_table_nc = DataTable(description_nc)
        data_table_nc.LoadData(data_nc)
  
        # Creating a JSon string
        nonconf = data_table_nc.ToJSon(columns_order=("commissione", "dataNonconf", "turno", "tipo", "key"), order_by="dataNonconf")
        template_values['content'] = 'commissario/nonconfs.html'
        template_values['nonconf'] = nonconf

      else:

        # Creating the data
        description = {"commissione": ("string", "Commissione"),
                       "dataIspezione": ("date", "Data"),
                       "turno": ("string", "Turno"),
                       "primo": ("string", "Primo"),
                       "secondo": ("string", "Secondo"),
                       "contorno": ("string", "Contorno"),
                       "frutta": ("string", "Frutta"),
                       "pasti": ("string", "Pasti serviti"),
                       "key": ("string", "")}
        
        data = list()
        for ispezione in Ispezione.all().filter("commissario",commissario).order("-dataIspezione"):
          data.append({"commissione": str(ispezione.commissione.nome), "dataIspezione": ispezione.dataIspezione, "turno": ispezione.turno, "primo": str(ispezione.primoAssaggio) + " " + str(ispezione.primoGradimento), "secondo": str(ispezione.secondoAssaggio) + " " + str(ispezione.secondoGradimento), "contorno":str(ispezione.contornoAssaggio) + " " + str(ispezione.contornoGradimento), "frutta":str(ispezione.fruttaAssaggio) + " " + str(ispezione.fruttaGradimento), "pasti":str(ispezione.numeroPastiTotale) + " " + str(ispezione.numeroPastiBambini), "key":"<a class='btn' href='/commissario/ispezione?cmd=open&key="+str(ispezione.key())+"'>Apri</a>"})
  
        # Loading it into gviz_api.DataTable
        data_table = DataTable(description)
        data_table.LoadData(data)
  
        # Creating a JSon string
        ispezioni = data_table.ToJSon(columns_order=("commissione", "dataIspezione", "turno", "primo", "secondo", "contorno", "frutta", "pasti", "key"), order_by="dataIspezione")
      
        template_values['content'] = 'commissario/ispezioni.html'
        template_values['ispezioni'] = ispezioni

      self.getBase(template_values)
      
class CMRegistrazioneHandler(BasePage):
  
  def get(self): 
    commissioni = Commissione.all().order("nome")

    template_values = {
      'commissioni': commissioni,     
    }
      
    commissario = Commissario.all().filter("user", users.get_current_user()).get()
    if commissario is not None:
      template_values["content"] = "commissario/registrazione_ok.html"
      template_values["cmsro"] = commissario
    else:
      template_values["content"] = "commissario/registrazione.html"
      
    self.getBase(template_values)
  
  def post(self):
    user = users.get_current_user()
    commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
    if(commissario == None):
      commissario = Commissario(nome = self.request.get("nome"), cognome = self.request.get("cognome"), user = user, stato = 0)
      commissario.put()
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()

      self.sendRegistrationRequestMail(commissario)
    
    template_values = {
      'content': 'commissario/registrazione_ok.html',
      'cmsro': commissario
    }
    self.getBase(template_values)

  def sendRegistrationRequestMail(self, commissario) :

    if self.request.url.find("test") != -1:
      url = "test-pappa-mi.appspot.com"
    else:
      url = "pappa-mi.appspot.com"
    
    message = mail.EmailMessage()
    message.sender = "aiuto.pappami@gmail.com"
    message.to = "aiuto.pappami@gmail.com"
    message.subject = "Richiesta di Registrazione da " + commissario.nome + " " + commissario.cognome
    message.body = commissario.nome + " " + commissario.cognome + " " + commissario.user.email() + """ ha inviato una richiesta di registrazione come Commissario. 
    
    Per abilitarlo usare il seguente link:
    
    """ + "http://" + url + "/admin/commissario?cmd=enable&key="+str(commissario.key())

    message.send()
      
class CMIspezioneHandler(BasePage):
  
  def get(self): 
    if( self.request.get("cmd") == "open" ):
      isp = Ispezione.get(self.request.get("key"))
  

      template_values = {
        'content': 'commissario/ispezione_read.html',
        'content_left': 'commissario/leftbar.html',
        'isp': isp
        }
      
    elif( self.request.get("cmd") == "edit" ):
   
      isp = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("preview"))
     
      form = IspezioneForm(instance=isp)
      
      user = users.get_current_user()
      commissario = Commissario.all().filter("user", user).filter("stato", 1).get()

      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
      
      form.data["commissione"] = isp.commissione

      template_values = {
        'content': 'commissario/ispezione.html',
        'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }
          
    else:       
      user = users.get_current_user()
      commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
      isp = Ispezione(commissario = commissario) 
      form = IspezioneForm(instance=isp)

      for field in form:
        #logging.info(field.name)
        form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'content': 'commissario/ispezione.html',
        'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }


    self.getBase(template_values)

  def post(self):    
   
    preview = self.request.get("preview")
   
    if( preview ):
      isp = memcache.get(preview)
      memcache.delete(preview)
      isp.put()
      memcache.delete("stats")
      memcache.delete("statsMese")
      
      self.redirect("/commissario")
    else:
      key = self.request.get("key")
      if( key != "" ) :
        isp = Ispezione.get(key)
      else:
        isp = Ispezione()
    
      user = users.get_current_user()
      commissario = Commissario.all().filter("user", user).filter("stato", 1).get()

      form = IspezioneForm(data=self.request.POST, instance=isp)
      
      if form.is_valid():
        isp = form.save(commit=False)
        
        isp.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        logging.info(preview)
        memcache.add(preview, isp, 3600)
    
        template_values = {
          'content': 'commissario/ispezione_read.html',
          'content_left': 'commissario/leftbar.html',
          'isp': isp,
          'preview': preview
        }
        
        self.getBase(template_values) 
      else:
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)

        template_values = {
          'content': 'commissario/ispezione.html',
          'content_left': 'commissario/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form
        }

        self.getBase(template_values)
        

class CMNonconfHandler(BasePage):
  
  def get(self): 
    if( self.request.get("cmd") == "open" ):
      nc = Nonconformita.get(self.request.get("key"))
  

      template_values = {
        'content': 'commissario/nonconf_read.html',
        'content_left': 'commissario/leftbar.html',
        'nc': nc
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      nc = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("nc"))

      user = users.get_current_user()
      commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
      
      form = NonconformitaForm(instance=nc)
      
      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
      
      form.data["commissione"] = nc.commissione

      template_values = {
        'content': 'commissario/nonconf.html',
        'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
      commissario = Commissario.all().filter("user", users.get_current_user()).filter("stato", 1).get()
  
      nc = Nonconformita(commissario = commissario) 
      form = NonconformitaForm(instance=nc)

      for field in form:
        form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'content': 'commissario/nonconf.html',
        'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  def post(self):    
   
    preview = self.request.get("preview")
   
    if( preview ):
      nc = memcache.get(preview)
      memcache.delete(preview)
      nc.put()
      memcache.delete("stats")
      memcache.delete("statsMese")
      
      self.redirect("/commissario?tab=nc")
    else:
      key = self.request.get("k")
      if( key != "" ) :
        nc = Nonconformita.get(key)
      else:
        nc = Nonconformita()
    
      form = NonconformitaForm(data=self.request.POST, instance=nc)
      #for field in form:
        #logging.info("%s, %s",field.name, field)

      user = users.get_current_user()
      commissario = Commissario.all().filter("user", user).filter("stato", 1).get()

      if form.is_valid():
        nc = form.save(commit=False)
        nc.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, nc, 3600)
  
  
        template_values = {
          'content': 'commissario/nonconf_read.html',
          'content_left': 'commissario/leftbar.html',
          'nc': nc,
          'preview': preview
        }
        
      else:
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)
  
        
        template_values = {
          'content': 'commissario/nonconf.html',
          'content_left': 'commissario/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form
        }
        
      self.getBase(template_values)
        
application = webapp.WSGIApplication([
  ('/commissario/ispezione', CMIspezioneHandler),
  ('/commissario/nonconf', CMNonconfHandler),
  ('/commissario/registrazione', CMRegistrazioneHandler),
  ('/commissario', CMCommissarioHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
