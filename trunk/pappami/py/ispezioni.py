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

from google.appengine.ext.ndb import model
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
from py.base import BasePage, CMCommissioniDataHandler, CMMenuHandler, commissario_required, reguser_required, Const
from py.modelMsg import *
from py.comments import CMCommentHandler
         
class CMGetIspDataHandler(BasePage):

  @commissario_required
  def get(self): 
    commissario = self.getCommissario()
    logging.info("isp1")
    if( commissario is not None):    
      cm_id = self.request.get("cm")
      isp = Ispezione.get_last_by_cm(model.Key("Commissione", int(cm_id)))
      logging.info("isp: " + str(isp))
        
      buff = ""
      if( isp ):
        buff = str(isp.aaRispettoCapitolato)+"|"+str(isp.aaTavoliApparecchiati)+"|"+str(isp.aaTermichePulite)+"|"+str(isp.aaAcqua)+"|"+str(isp.aaScaldaVivande)+"|"+str(isp.aaSelfService)+"|"+str(isp.aaTabellaEsposta)+"|"+str(isp.ricicloStoviglie)+"|"+str(isp.ricicloPosate)+"|"+str(isp.ricicloBicchieri)
      
    self.response.out.write(buff) 


class IspezioneValidationHandler(BasePage):
  def post(self):
    turno = int(self.request.get("turno"))
    cm_id = self.request.get("commissione")
    dataIspezione = datetime.strptime(self.request.get("dataIspezione"),Const.DATE_FORMAT).date()

    
    message = "Ok"
    if Ispezione.get_by_cm_data_turno(model.Key("Commissione", int(cm_id)), dataIspezione, turno).get() :
      message = "<ul><li>Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.</li></ul>"

    self.response.out.write(message)
    
class DietaValidationHandler(BasePage):    
  def post(self):
    turno = int(self.request.get("turno"))
    cm_id = self.request.get("commissione")
    dataIspezione = datetime.strptime(self.request.get("dataIspezione"),Const.DATE_FORMAT).date()
    tipo = int(self.request.get("tipoDieta"))

    logging.info(dataIspezione);
    
    message = "Ok"
    if Dieta.get_by_cm_data_turno(model.Key("Commissione", int(cm_id)), dataIspezione, turno).get() :
      message = "<ul><li>Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.</li></ul>"

    logging.info(message);
    self.response.out.write(message)
    
  
def populate_tags_attach(request, obj):
  obj.tags = list()
  for tag in request.get_all("tags"):
    logging.info(tag)
    obj.tags.append(tag)
  
  obj.allegati = list()
  for i in range(1,10):
    if request.get('allegato_file_' + str(i)):
      if len(request.get('allegato_file' + str(i))) < 10000000 :
        allegato = Allegato()
        allegato.descrizione = request.get('allegato_desc_' + str(i))
        allegato.nome = request.POST['allegato_file_' + str(i)].filename
        blob = Blob()
        blob.create(allegato.nome)
        allegato.blob_key = blob.write(request.get('allegato_file_' + str(i)))
        obj.allegati.append(allegato)
      else:
        logging.info("attachment is too big.")

class IspezioneHandler(BasePage):

  @commissario_required
  def get(self): 
    commissario = self.getCommissario()

    if( self.request.get("cmd") == "open" ):
      isp = Ispezione.get(self.request.get("key"))
  
      cancopy = None;
      if( isp.commissario.key == commissario.key):
        cancopy = True
      
      comment_root = CMCommentHandler.getRoot(isp.key)
        
      template_values = {
        'content': 'commissario/ispezione_read.html',
        'content_left': 'commissario/leftbar.html',
        'isp': isp,
        'cancopy': cancopy,
        "public_url": "http://" + self.getHost() + "/public/isp?key=" + str(isp.key.id()),
        "comments": True,
        "comment_root": comment_root
        }
                
    else:       
      isp = Ispezione(commissario = commissario.key) 
      form = IspezioneForm(self.request.POST,isp)

      template_values = {
        'main': 'ispezioni/ispezione_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }


    self.getBase(template_values)

  @commissario_required
  def post(self):    
   
    commissario = self.getCommissario()

    preview = self.request.get("preview")

    if( self.request.get("cmd") == "copy" ):
   
      key = self.request.get("key")
      isp = Ispezione.get(key)

      form = IspezioneForm(self.request.POST,isp)            
      form.commissione = isp.commissione
  
      template_values = {
        'main': 'ispezioni/ispezione_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }
        
      self.getBase(template_values) 

    elif( preview ):
      isp = self.session.get("pw_obj")
      isp.allegati = self.session.get("pw_att")
      isp.tags = self.session.get("pw_tags")

      if isp.dataIspezione.month >= 9:
        isp.anno = isp.dataIspezione.year
      else:
        isp.anno = isp.dataIspezione.year - 1
        
      isp.put()

      for allegato in isp.allegati:
        allegato.obj = isp
        allegato.put()
      
      memcache.delete("stats")
      memcache.delete("statsMese")
      
      template_values = CMCommentHandler.initActivity(isp.key, isp.commissione, 101, model.Key("Messaggio",int(self.request.get("last"))), tags=isp.tags, user=self.request.user)

      self.getBase(template_values) 
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        isp = Ispezione.get(key)
      else:
        isp = Ispezione()
    
      form = IspezioneForm(self.request.POST, isp)
      form.commissione = model.Key("Commissione", int(self.request.get("commissione")))
            
      if form.primoEffettivo.data == form.secondoEffettivo.data:
        form.secondoQuantita.data = form.primoQuantita.data
        form.secondoDist.data = form.primoDist.data
        form.secondoTemperatura.data = form.primoTemperatura.data
        form.secondoAssaggio.data = form.primoAssaggio.data
        form.secondoCottura.data = form.primoCottura.data
        form.secondoGradimento.data = form.primoGradimento.data
        
      if form.validate():
        form.populate_obj(isp)        
        isp.commissario = commissario.key
        isp.commissione = form.commissione
   
        self.session["pw_obj"] = isp
        self.session["pw_att"] = isp.allegati
        self.session["pw_tags"] = isp.tags
    
        template_values = {
          'main': 'ispezioni/ispezione_read_div.html',
          'isp': isp,
          'preview': True
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
    commissario = self.getCommissario()

    if( self.request.get("cmd") == "open" ):
      nc = Nonconformita.get(self.request.get("key"))

      comment_root = CMCommentHandler.getRoot(nc.key)
      
      template_values = {
        'main': 'ispezioni/nonconf_read.html',
        'nc': nc,
        "public_url": "http://" + self.getHost() + "/public/nc?key=" + str(nc.key.id()),
        "comments": True,
        "comment_root": comment_root
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      nc = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("preview"))
     
      form = NonconformitaForm(self.request.POST,nc)      
      form.commissione = nc.commissione

      template_values = {
        'content': 'commissario/nonconf_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      nc = Nonconformita(commissario = commissario.key) 
      form = NonconformitaForm(self.request.POST,nc)
      form.commissione = nc.commissione

        
      template_values = {
        'main': 'ispezioni/nonconf_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  @commissario_required
  def post(self):    
   
    commissario = self.getCommissario()

    preview = self.request.get("preview")
   
    if( preview ):
      nc = self.session.get("pw_obj")
      nc.allegati = self.session.get("pw_att")
      nc.tags = self.session.get("pw_tags")
      
      if nc.dataNonconf.month >= 9:
        nc.anno = nc.dataNonconf.year
      else:
        nc.anno = nc.dataNonconf.year - 1

      nc.put()

      for allegato in nc.allegati:
        allegato.obj = nc
        allegato.put()

      memcache.delete("stats")
      memcache.delete("statsMese")

      template_values = CMCommentHandler.initActivity(nc.key, nc.commissione, 102, model.Key("Messaggio",int(self.request.get("last"))), nc.tags, user=self.request.user)

      self.getBase(template_values) 
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        nc = Nonconformita.get(key)
      else:
        nc = Nonconformita()
    
      form = NonconformitaForm(self.request.POST,nc)
      form.commissione = model.Key("Commissione", int(self.request.get("commissione")))
      
      if form.validate():
        form.populate_obj(nc)
        nc.commissario = commissario.key
        nc.commissione = form.commissione
        
        populate_tags_attach(self.request, nc)
        logging.info(nc.allegati)
        
        self.session["pw_obj"] = nc
        self.session["pw_att"] = nc.allegati
        self.session["pw_tags"] = nc.tags
   
        template_values = {
          'main': 'ispezioni/nonconf_read_div.html',
          'nc': nc,
          'preview': True
        }
        
      else:
        logging.info("data: %s", form.data)
        for f in form.errors :
          for e in form[f].errors:
            logging.info("errors: %s %s", f, e)

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
    commissario = self.getCommissario()
    if commissario is None or not commissario.isCommissario() :
      return

    if( self.request.get("cmd") == "open" ):
      dieta = Dieta.get(self.request.get("key"))
  
      comment_root = CMCommentHandler.getRoot(dieta.key)

      template_values = {
        'content': 'commissario/dieta_read.html',
        'content_left': 'commissario/leftbar.html',
        'dieta': dieta,
        "public_url": "http://" + self.getHost() + "/public/dieta?key=" + str(dieta.key.id()),
        "comments": True,
        "comment_root": comment_root
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      dieta = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("dieta"))
    
      form = DietaForm(self.request.POST,dieta)
      
      form.commissione = dieta.commissione

      template_values = {
        'content': 'commissario/dieta.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      dieta = Dieta(commissario = commissario.key) 
      form = NonconformitaForm(self.request.POST,dieta)
      form.commissione = dieta.commissione

        
      template_values = {
        'main': 'ispezioni/dieta_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  @commissario_required
  def post(self):    
   
    commissario = self.getCommissario()

    preview = self.request.get("preview")
   
    if( preview ):
      dieta = self.session.get("pw_obj")
      dieta.allegati = self.session.get("pw_att")
      dieta.tags = self.session.get("pw_tags")

      if dieta.dataIspezione.month >= 9:
        dieta.anno = dieta.dataIspezione.year
      else:
        dieta.anno = dieta.dataIspezione.year - 1

      dieta.put()

      for allegato in dieta.allegati:
        allegato.obj = dieta
        allegato.put()
      
      memcache.delete("stats")
      memcache.delete("statsMese")

      template_values = CMCommentHandler.initActivity(dieta.key, dieta.commissione, 103, model.Key("Messaggio", int(self.request.get("last"))), tags=dieta.tags, user=self.request.user)

      self.getBase(template_values) 
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        dieta = Dieta.get(key)
      else:
        dieta = Dieta()
    
      form = DietaForm(self.request.POST,dieta)
      form.commissione = model.Key("Commissione", int(self.request.get("commissione")))

      if form.validate():
        form.populate_obj(dieta)
        dieta.commissario = commissario.key
        dieta.commissione = form.commissione

        populate_tags_attach(self.request, dieta)
        
        self.session["pw_obj"] = dieta
        self.session["pw_att"] = dieta.allegati
        self.session["pw_tags"] = dieta.tags
    
        template_values = {
          'main': 'ispezioni/dieta_read_div.html',
          'dieta': dieta,
          'preview': True
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
  
  @reguser_required
  def get(self): 
    commissario = self.getCommissario()
    if commissario is None or not commissario.isCommissario() :
      return

    if( self.request.get("cmd") == "open" ):
      nota = Nota.get(self.request.get("key"))
      allegati = None
      if nota.allegato_set.count():
        allegati = nota.allegato_set
  
      comment_root = CMCommentHandler.getRoot(nota.key)
      
      template_values = {
        'content': 'commissario/nota_read.html',
        'content_left': 'commissario/leftbar.html',
        'nota': nota,
        "public_url": "http://" + self.getHost() + "/public/nota?key=" + str(nota.key.id()),
        "comments": True,
        "comment_root": comment_root
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      nota = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("nota"))

      form = NotaForm(self.request.POST,nota)
      
      form.commissione = nota.commissione

      template_values = {
        'content': 'commissario/nota.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      nota = Nota() 
      form = NotaForm(obj=nota)
      form.commissione = nota.commissione
       
      template_values = {
        'main': 'ispezioni/nota_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

  @reguser_required
  def post(self):    
   
    commissario = self.getCommissario()

    preview = self.request.get("preview")
   
    if( preview ):
      nota = self.session.get("pw_obj")
      nota.allegati = self.session.get("pw_att")
      nota.tags = self.session.get("pw_tags")

      if nota.dataNota.month >= 9:
        nota.anno = nota.dataNota.year
      else:
        nota.anno = nota.dataNota.year - 1
     
      nota.put()
      
      logging.info(nota.allegati)
            
      for allegato in nota.allegati:
        allegato.obj = nota.key
        allegato.put()

      memcache.delete("stats")
      memcache.delete("statsMese")

      template_values = CMCommentHandler.initActivity(nota.key, nota.commissione, 104, model.Key("Messaggio",int(self.request.get("last"))), nota.tags, user=self.request.user)
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        nota = Nota.get(key)
      else:
        nota = Nota()
    
      form = NotaForm(self.request.POST,nota)
      form.commissione = model.Key("Commissione", int(self.request.get("commissione")))
      
      if form.validate():
        form.populate_obj(nota)
        nota.commissario = commissario.key
        nota.commissione = form.commissione

        populate_tags_attach(self.request, nota)
            
        self.session["pw_obj"] = nota
        self.session["pw_att"] = nota.allegati
        self.session["pw_tags"] = nota.tags

        logging.info(nota.allegati)
        
        template_values = {
          'main': 'ispezioni/nota_read_div.html',
          'nota': nota,
          'preview': True
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