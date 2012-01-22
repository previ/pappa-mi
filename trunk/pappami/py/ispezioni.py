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

from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.site import *
from py.blob import *
from py.form import IspezioneForm, NonconformitaForm, DietaForm, NotaForm
from py.base import BasePage, CMCommissioniDataHandler, CMMenuHandler, commissario_required, user_required, Const
from py.modelMsg import *
from py.comments import CMCommentHandler
         
class CMGetIspDataHandler(BasePage):

  @commissario_required
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    logging.info("isp1")
    if( commissario is not None):    
      cm = self.request.get("cm")
      isp = Ispezione.get_last_from_cm(cm)
      logging.info("isp: " + str(isp))
        
      buff = ""
      if( isp ):
        buff = str(isp.aaRispettoCapitolato)+"|"+str(isp.aaTavoliApparecchiati)+"|"+str(isp.aaTermichePulite)+"|"+str(isp.aaAcqua)+"|"+str(isp.aaScaldaVivande)+"|"+str(isp.aaSelfService)+"|"+str(isp.aaTabellaEsposta)+"|"+str(isp.ricicloStoviglie)+"|"+str(isp.ricicloPosate)+"|"+str(isp.ricicloBicchieri)
      
    self.response.out.write(buff) 


class IspezioneValidationHandler(BasePage):    
  def post(self):
    turno = int(self.request.get("turno"))
    commissione = self.request.get("commissione")
    dataIspezione = datetime.strptime(self.request.get("dataIspezione"),Const.DATE_FORMAT).date()

    
    message = "Ok"
    if Ispezione.get_by_cm_data_turno(commissione, dataIspezione, turno) :
      message = "<ul><li>Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.</li></ul>"

    self.response.out.write(message)
    
class DietaValidationHandler(BasePage):    
  def post(self):
    turno = int(self.request.get("turno"))
    commissione = self.request.get("commissione")
    dataIspezione = datetime.strptime(self.request.get("dataIspezione"),Const.DATE_FORMAT).date()
    tipo = int(self.request.get("tipoDieta"))

    logging.info(dataIspezione);
    
    message = "Ok"
    if Dieta.get_by_cm_data_turno(commissione, dataIspezione, turno) :
      message = "<ul><li>Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.</li></ul>"

    logging.info(message);
    self.response.out.write(message)
    
  
class IspezioneHandler(BasePage):

  @commissario_required
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      return

    if( self.request.get("cmd") == "open" ):
      isp = Ispezione.get(self.request.get("key"))
  
      cancopy = None;
      if( isp.commissario.key() == commissario.key()):
        cancopy = True
      
      comment_root = CMCommentHandler().getRoot(isp.key())
        
      template_values = {
        'content': 'commissario/ispezione_read.html',
        'content_left': 'commissario/leftbar.html',
        'isp': isp,
        'cancopy': cancopy,
        "public_url": "http://" + self.getHost() + "/public/isp?key=" + str(isp.key()),
        "comments": True,
        "comment_root": comment_root
        }
      
    elif( self.request.get("cmd") == "edit" ):
   
      isp = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("preview"))
     
      form = IspezioneForm(self.request.POST,obj=isp)
            
      form.commissione.data = isp.commissione

      template_values = {
        'content': 'commissario/ispezione.html',
        'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }
          
    else:       
      isp = Ispezione(commissario = commissario) 
      form = IspezioneForm(self.request.POST,isp)

      #for field in form:
        #logging.info(field.name)
        #form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'main': 'ispezioni/ispezione_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }


    self.getBase(template_values)

  @commissario_required
  def post(self):    
   
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      return

    preview = self.request.get("preview")
   
    if( self.request.get("cmd") == "copy" ):
   
      key = self.request.get("key")
      isp = Ispezione.get(key)
      form = IspezioneForm(self.request.POST,isp)
      
      #for field in form:
        #logging.info(field.name)
        #form.data[field.name] = unicode(form.initial[field.name])
      
      form.commissione.data = isp.commissione
  
      template_values = {
        'main': 'ispezioni/ispezione_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }
        
      self.getBase(template_values) 
    elif( preview ):
      isp = memcache.get(preview)
      memcache.delete(preview)
      if isp.dataIspezione.month >= 9:
        isp.anno = isp.dataIspezione.year
      else:
        isp.anno = isp.dataIspezione.year - 1
        
      isp.put()

      memcache.delete("stats")
      memcache.delete("statsMese")
      
      template_values = CMCommentHandler().initActivity(isp.key(), 101, db.Key(self.request.get("last")))

      self.getBase(template_values) 
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        isp = Ispezione.get(key)
      else:
        isp = Ispezione()
    
      form = IspezioneForm(self.request.POST, isp)
      
      logging.info(preview)
      
      if form.validate():
        logging.info("valid")

        form.populate_obj(isp)
        
        isp.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), Const.TIME_FORMAT)
        logging.info(preview)
        memcache.add(preview, isp, 3600)
    
        template_values = {
          'main': 'ispezioni/ispezione_read_div.html',
          'isp': isp,
          'preview': preview
        }
        
        self.getBase(template_values) 
      else:
        logging.info("data: %s", form.data)
        for e in form.errors :
          logging.info("errors: %s", e)

        template_values = {
          'main': 'ispezioni/err_div.html',
          'commissioni': commissario.commissioni(),
          'form': form,
          'form_errors': form.errors
        }

        self.getBase(template_values)
        

class NonconfHandler(BasePage):
  
  @commissario_required
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      return

    if( self.request.get("cmd") == "open" ):
      nc = Nonconformita.get(self.request.get("key"))

      comment_root = CMCommentHandler().getRoot(nc.key())
      
      template_values = {
        'main': 'ispezioni/nonconf_read.html',
        'nc': nc,
        "public_url": "http://" + self.getHost() + "/public/nc?key=" + str(nc.key()),
        "comments": True,
        "comment_root": comment_root
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      nc = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("preview"))
     
      form = NonconformitaForm(self.request.POST,nc)
      
      form.commissione.data = isp.commissione

      template_values = {
        'content': 'commissario/nonconf_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      nc = Nonconformita(commissario = commissario) 
      form = NonconformitaForm(self.request.POST,nc)

        
      template_values = {
        'main': 'ispezioni/nonconf_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  @commissario_required
  def post(self):    
   
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())

    if commissario is None or not commissario.isCommissario() :
      return
    preview = self.request.get("preview")
   
    if( preview ):
      nc = memcache.get(preview)
      memcache.delete(preview)
      
      if nc.dataNonconf.month >= 9:
        nc.anno = nc.dataNonconf.year
      else:
        nc.anno = nc.dataNonconf.year - 1

      nc.put()

      memcache.delete("stats")
      memcache.delete("statsMese")

      template_values = CMCommentHandler().initActivity(nc.key(), 102, db.Key(self.request.get("last")), nc.tags)

      self.getBase(template_values) 
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        nc = Nonconformita.get(key)
      else:
        nc = Nonconformita()
    
      form = NonconformitaForm(self.request.POST,nc)

      #logging.info(nc)
      
      if form.validate():
        form.populate_obj(nc)
        nc.commissario = commissario
   
        nc.tags = list()
        for tag in self.request.get_all("tags"):
          logging.info(tag)
          nc.tags.append(tag)
        
        preview = user.email() + datetime.strftime(datetime.now(), Const.TIME_FORMAT)
        memcache.add(preview, nc, 3600)
   
        template_values = {
          'main': 'ispezioni/nonconf_read_div.html',
          'nc': nc,
          'preview': preview
        }
        
      else:
        logging.info("data: %s", form.data)
        for e in form.errors :
          logging.info("errors: %s", e)

        template_values = {
          'main': 'ispezioni/err_div.html',
          'commissioni': commissario.commissioni(),
          'form': form,
          'form_errors': form.errors
        }

      self.getBase(template_values)
      

class DietaHandler(BasePage):
  
  @commissario_required
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      return

    if( self.request.get("cmd") == "open" ):
      dieta = Dieta.get(self.request.get("key"))
  
      comment_root = CMCommentHandler().getRoot(dieta.key())

      template_values = {
        'content': 'commissario/dieta_read.html',
        'content_left': 'commissario/leftbar.html',
        'dieta': dieta,
        "public_url": "http://" + self.getHost() + "/public/dieta?key=" + str(dieta.key()),
        "comments": True,
        "comment_root": comment_root
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      dieta = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("dieta"))
    
      form = DietaForm(self.request.POST,dieta)
      
      form.commissione.data = dieta.commissione

      template_values = {
        'content': 'commissario/dieta.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      dieta = Dieta(commissario = commissario) 
      form = NonconformitaForm(self.request.POST,dieta)

        
      template_values = {
        'main': 'ispezioni/dieta_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  @commissario_required
  def post(self):    
   
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())

    if commissario is None or not commissario.isCommissario() :
      return
    preview = self.request.get("preview")
   
    if( preview ):
      dieta = memcache.get(preview)
      memcache.delete(preview)

      if dieta.dataIspezione.month >= 9:
        dieta.anno = dieta.dataIspezione.year
      else:
        dieta.anno = dieta.dataIspezione.year - 1

      dieta.put()
    
      memcache.delete("stats")
      memcache.delete("statsMese")

      template_values = CMCommentHandler().initActivity(dieta.key(), 103, db.Key(self.request.get("last")))

      self.getBase(template_values) 
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        dieta = Dieta.get(key)
      else:
        dieta = Dieta()
    
      form = DietaForm(self.request.POST,dieta)

      if form.validate():
        form.populate_obj(dieta)
        dieta.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), Const.TIME_FORMAT)
        memcache.add(preview, dieta, 3600)
    
        template_values = {
          'main': 'ispezioni/dieta_read_div.html',
          'dieta': dieta,
          'preview': preview
        }
        
      else:
        logging.info("data: %s", form.data)
        for e in form.errors :
          logging.info("errors: %s", e)

        template_values = {
          'main': 'ispezioni/err_div.html',
          'commissioni': commissario.commissioni(),
          'form': form,
          'form_errors': form.errors
        }
        
      self.getBase(template_values)
      
class NotaHandler(BasePage):
  
  @commissario_required
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      return

    if( self.request.get("cmd") == "open" ):
      nota = Nota.get(self.request.get("key"))
      allegati = None
      if nota.allegato_set.count():
        allegati = nota.allegato_set
  
      comment_root = CMCommentHandler().getRoot(nota.key())
      
      template_values = {
        'content': 'commissario/nota_read.html',
        'content_left': 'commissario/leftbar.html',
        'nota': nota,
        "public_url": "http://" + self.getHost() + "/public/nota?key=" + str(nota.key()),
        "allegati": allegati,
        "comments": True,
        "comment_root": comment_root
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      nota = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("nota"))

      form = NotaForm(self.request.POST,nota)
      
      form.commissione.data = nota.commissione

      template_values = {
        'content': 'commissario/nota.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      nota = Nota(commissario = commissario) 
      form = NotaForm(obj=nota)
       
      template_values = {
        'main': 'ispezioni/nota_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  @commissario_required
  def post(self):    
   
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())

    if commissario is None or not commissario.isCommissario() :
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
            
      #username = Configurazione.all().filter("nome", "attach_user").get().valore
      #password = Configurazione.all().filter("nome", "attach_password").get().valore
      #site = Configurazione.all().filter("nome", "attach_site").get().valore
      #path = Configurazione.all().filter("nome", "attach_path").get().valore
      #site = Site(username, password, site)

      for allegato in nota.allegati:
        allegato.obj = nota
        #allegato.path = site.uploadDoc(allegato.dati, str(nota.key().id()) + "_" + allegato.nome, allegato.contentType(), path)
        allegato.put()

      memcache.delete("stats")
      memcache.delete("statsMese")

      template_values = CMCommentHandler().initActivity(nota.key(), 104, db.Key(self.request.get("last")), nota.tags)
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        nota = Nota.get(key)
      else:
        nota = Nota()
    
      form = NotaForm(self.request.POST,nota)
      #for field in form:
        #logging.info("%s, %s",field.name, field)
      
      if form.validate():
        form.populate_obj(nota)
        nota.commissario = commissario

        nota.tags = list()
        for tag in self.request.get_all("tags"):
          logging.info(tag)
          nota.tags.append(tag)
        
        nota.allegati = list()
        for i in range(1,10):
          if self.request.get('allegato_file_' + str(i)):
            if len(self.request.get('allegato_file' + str(i))) < 10000000 :
              allegato = Allegato()
              allegato.descrizione = self.request.get('allegato_desc_' + str(i))
              allegato.nome = self.request.POST['allegato_file_' + str(i)].filename
              blob = Blob()
              blob.create(allegato.nome)
              allegato.blob_key = blob.write(self.request.get('allegato_file_' + str(i)))
              allegato.put()
              nota.allegati.append(allegato)
            else:
              logging.info("attachment is too big.")
            
        preview = user.email() + datetime.strftime(datetime.now(), Const.TIME_FORMAT)
        memcache.add(preview, nota, 3600)
    
        template_values = {
          'main': 'ispezioni/nota_read_div.html',
          'nota': nota,
          'allegati': nota.allegati,
          'preview': preview
        }
        
      else:
        logging.info("data: %s", form.data)
        for e in form.errors :
          logging.info("errors: %s", e)

        template_values = {
          'main': 'ispezioni/err_div.html',
          'commissioni': commissario.commissioni(),
          'form': form,
          'form_errors': form.errors
        }
      
    self.getBase(template_values) 
    
app = webapp.WSGIApplication([
    ('/isp/isp', IspezioneHandler),
    ('/isp/ispval', IspezioneValidationHandler),
    ('/isp/dietaval', DietaValidationHandler),
    ('/isp/nc', NonconfHandler),
    ('/isp/dieta', DietaHandler),
    ('/isp/nota', NotaHandler),
    ('/isp/getispdata', CMGetIspDataHandler)], debug=os.environ['HTTP_HOST'].startswith('localhost'))
 
def main():
  app.run();

if __name__ == "__main__":
  main()