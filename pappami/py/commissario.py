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
from py.form import IspezioneForm

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMCommissarioHandler(webapp.RequestHandler):

  def get(self): 
    user = users.get_current_user()
    commissario = db.GqlQuery("SELECT * FROM Commissario WHERE user = :1", user).get()
    if( commissario is None):
      self.redirect("/commissario/registrazione")
    else:
      # Creating the data
      description = {"commissione": ("string", "Commissione"),
                     "dataIspezione": ("date", "Data"),
                     "primo": ("string", "Primo"),
                     "secondo": ("string", "Secondo"),
                     "contorno": ("string", "Contorno"),
                     "frutta": ("string", "Frutta"),
                     "pasti": ("string", "Pasti serviti"),
                     "nc": ("string", u"Non conformita"),
                     "key": ("string", "")}
      
      data = list()
      for ispezione in Ispezione.all().filter("commissario",commissario).order("-dataIspezione"):
        data.append({"commissione": str(ispezione.commissione.nome), "dataIspezione": ispezione.dataIspezione, "primo": str(ispezione.primoAssaggio) + " " + str(ispezione.primoGradimento), "secondo": str(ispezione.secondoAssaggio) + " " + str(ispezione.secondoGradimento), "contorno":str(ispezione.contornoAssaggio) + " " + str(ispezione.contornoGradimento), "frutta":str(ispezione.fruttaAssaggio) + " " + str(ispezione.fruttaGradimento), "pasti":str(ispezione.numeroPastiTotale) + " " + str(ispezione.numeroPastiBambini), "nc":str(ispezione.ncPresenti()), "key":"<a href='/commissario/ispezione?cmd=open&key="+str(ispezione.key())+"'>Apri</a>"})

      # Loading it into gviz_api.DataTable
      data_table = DataTable(description)
      data_table.LoadData(data)

      # Creating a JSon string
      ispezioni = data_table.ToJSon(columns_order=("commissione", "dataIspezione", "primo", "secondo", "contorno", "frutta", "pasti", "nc", "key"), order_by="dataIspezione")

      url = users.create_logout_url("/")
      url_linktext = 'Logout'

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

      self.sendRegistrationRequestMail(commissario)
    
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

  def sendRegistrationRequestMail(self, commissario) :

    message = mail.EmailMessage()
    message.sender = "aiuto.pappami@gmail.com"
    message.to = "aiuto.pappami@gmail.com"
    message.subject = "Richiesta di Registrazione da " + commissario.nome + " " + commissario.cognome
    message.body = commissario.nome + " " + commissario.cognome + " " + commissario.user.email() + """ ha inviato una richiesta di registrazione come Commissario. 
    
    Per abilitarlo usare il seguente link:
    
    """ + "http://test-pappa-mi.appspot.com/admin/commissario?cmd=enable&key="+str(commissario.key())

    message.send()
      
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
      
      form.data["ncPresenti"] = str(isp.ncPresenti())
      form.data["commissione"] = isp.commissione
      logging.info(form.data["ncPresenti"])
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
      #form.data["ncPresenti"] = isp.ncPresenti()
        
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

  def post(self):    
    user = users.get_current_user()
    commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
   
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
  
        commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
        
        template_values = {
          'user': user,
          'admin': users.is_current_user_admin(),
          'commissario': commissario is not None,
          'commissioni': commissario.commissioni(),
          'url': url,
          'url_linktext': url_linktext,
          'form': form
        }
        
        path = os.path.join(os.path.dirname(__file__), '../templates/commissario/ispezione.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([
  ('/commissario/ispezione', CMIspezioneHandler),
  ('/commissario/registrazione', CMRegistrazioneHandler),
  ('/commissario', CMCommissarioHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
