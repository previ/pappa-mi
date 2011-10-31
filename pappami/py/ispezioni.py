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
from py.form import IspezioneForm, NonconformitaForm, DietaForm, NotaForm
from py.base import BasePage, CMCommissioniDataHandler, CMCommissioniHandler, CMMenuHandler, roleCommissario, Const
from py.modelMsg import *
from py.comments import CMCommentHandler

         
class CMCommissarioDataHandler(BasePage):
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if( commissario is not None):    
      tq = urllib.unquote(self.request.get("tq"))
      #logging.info(tq)
      query = tq[:tq.find("limit")]
      #logging.info(query)
      
      orderby = "-data"
      if(query.find("by") > 0):
        orderby = query[query.find("`"):query.rfind("`")].strip("` ")
      if(query.find("desc") > 0):
        orderby = "-" + orderby

      frm = ""
      if(query.find("from") >= 0):
        frm = query[(query.find("from ") + len("from ")):]
        frm = frm[:frm.find(" ")]

      cm = ""
      if(query.find("commissione") >= 0):
        cm = query[(query.find("commissione ") + len("commissione ")):]
        cm = cm[:cm.find(" ")]

      me = "on"
      if(query.find("me") >= 0):
        me = query[(query.find("me ") + len("me ")):]
        me = me[:me.find(" ")]

      anno = ""
      if(query.find("anno") >= 0):
        anno = query[(query.find("anno ") + len("anno ")):]
        anno = anno[:anno.find(" ")]
        
      #logging.info(orderby)
      
      params = tq[tq.find("limit"):].split()
      #logging.info(params)
      limit = int(params[1])
      offset = int(params[3])
      
      if params[3] >= 0:
        offset = int(params[3])
      else:
        offset = 0
        
      if offset > 0:
        prev = offset - 10
      else:
        prev = None
      next = offset + 10

      if frm == "nc":
        
        # Creating the data
        description_nc = {"commissione": ("string", "Commissione"), 
                       "data": ("date", "Data"),
                       "turno": ("string", "Turno"),
                       "tipo": ("string", "Tipo"),
                       "key": ("string", "")}
        
        data_nc = list()

        ncs = Nonconformita.all()

        if me == "on":
          ncs = ncs.filter("commissario",commissario)

        if anno != "":
          ncs = ncs.filter("anno",int(anno))      
        
        if cm != "":
          ncs = ncs.filter("commissione",Commissione.get(cm))
        
        url_path = "commissario"
        if commissario.isGenitore():
          url_path = "genitore"
          
        if(orderby.find("data") != -1):
          orderby = orderby + "Nonconf"
        for nc in ncs.order(orderby).fetch(limit, offset):
          data_nc.append({"commissione": (nc.commissione.nome + " - " + nc.commissione.tipoScuola), "data": nc.dataNonconf, "turno": str(nc.turno), "tipo": nc.tipoNome(), 
                       "key":"<a class='btn' href='/" + url_path + "/nonconf?cmd=open&key="+str(nc.key())+"'>Apri</a>"})
  
        # Loading it into gviz_api.DataTable
        data_table_nc = DataTable(description_nc)
        data_table_nc.LoadData(data_nc)
        
        # Creating a JSon string
        self.response.out.write(data_table_nc.ToJSonResponse(columns_order=("commissione", "data", "turno", "tipo", "key")))

      elif frm == "isp":

        # Creating the data
        description = {"commissione": ("string", "Commissione"),
                       "data": ("date", "Data"),
                       "turno": ("string", "Turno"),
                       #"complessivo": ("string", "Glob"),
                       "primo": ("string", "Primo"),
                       "secondo": ("string", "Secondo"),
                       "contorno": ("string", "Contorno"),
                       "frutta": ("string", "Frutta"),
                       "pasti": ("string", "Pasti serviti"),
                       "key": ("string", "")}
        
        data = list()
        isps = Ispezione.all()
        
        if me == "on":
          isps = isps.filter("commissario",commissario)
          me = "on"

        if anno != "":
          isps = isps.filter("anno",long(anno))
        
        if cm != "":
          isps = isps.filter("commissione",Commissione.get(cm))

        url_path = "commissario"
        if commissario.isGenitore():
          url_path = "genitore"
          
        if(orderby.find("data") != -1):
          orderby = orderby + "Ispezione"
        for ispezione in isps.order(orderby).fetch(limit, offset):
          data.append({"commissione": (ispezione.commissione.nome + " - " + ispezione.commissione.tipoScuola), "data": ispezione.dataIspezione, "turno": ispezione.turno, 
                       #"complessivo": "<img src='/img/icon" + str(ispezione.giudizioGlobale) + ".png'/>", 
                       "primo": "<img src='/img/icoasg" + str(ispezione.primoAssaggio) + ".png' title='Assaggio'/>" + "<img src='/img/icogra" + str(ispezione.primoGradimento) + ".png' title='Gradimento'/>" + "<img src='/img/icocot" + str(ispezione.primoCottura) + ".png' title='Cottura'/>"+ "<img src='/img/icotmp" + str(ispezione.primoTemperatura) + ".png' title='Temperatura'/>" + "<img src='/img/icoqta" + str(ispezione.primoQuantita) + ".png' title='Quantit&agrave;'/>",
                       "secondo": "<img src='/img/icoasg" + str(ispezione.secondoAssaggio) + ".png' title='Assaggio'/>" + "<img src='/img/icogra" + str(ispezione.secondoGradimento) + ".png' title='Gradimento'/>" + "<img src='/img/icocot" +str(ispezione.secondoCottura) + ".png' title='Cottura'/>"+ "<img src='/img/icotmp" + str(ispezione.secondoTemperatura) + ".png' title='Temperatura'/>" + "<img src='/img/icoqta" + str(ispezione.secondoQuantita) + ".png' title='Quantit&agrave;'/>",
                       "contorno": "<img src='/img/icoasg" + str(ispezione.contornoAssaggio) + ".png' title='Assaggio'/>" + "<img src='/img/icogra" + str(ispezione.contornoGradimento) + ".png' title='Gradimento'/>" + "<img src='/img/icocot" + str(ispezione.contornoCottura) + ".png' title='Cottura'/>"+ "<img src='/img/icotmp" + str(ispezione.contornoTemperatura) + ".png' title='Temperatura'/>" + "<img src='/img/icoqta" + str(ispezione.contornoQuantita) + ".png' title='Quantit&agrave;'/>",
                       "frutta": "<img src='/img/icoasg" + str(ispezione.fruttaAssaggio) + ".png' title='Assaggio'/>" + "<img src='/img/icogra" + str(ispezione.fruttaGradimento) + ".png' title='Gradimento'/>" + "<img src='/img/icomat" + str(ispezione.fruttaMaturazione) + ".png' title='Maturazione'/>" + "<img src='/img/icoqta" + str(ispezione.fruttaQuantita) + ".png' title='Quantit&agrave;'/>", 
                       "pasti":str(ispezione.numeroPastiTotale) + " " + str(ispezione.numeroPastiBambini), "key":"<a class='btn' href='/" + url_path + "/ispezione?cmd=open&key="+str(ispezione.key())+"'>Apri</a>"})
  
        # Loading it into gviz_api.DataTable
        data_table = DataTable(description)
        data_table.LoadData(data)
  
        # Creating a JSon string
        self.response.out.write(data_table.ToJSonResponse(columns_order=("commissione", "data", "turno", "primo", "secondo", "contorno", "frutta", "pasti", "key")))

      elif frm == 'dieta':
        # Creating the data
        description_dieta = {"commissione": ("string", "Commissione"), 
                       "data": ("date", "Data"),
                       "turno": ("string", "Turno"),
                       "tipoDieta": ("string", "Tipo"),
                       "key": ("string", "")}
        
        data_dieta = list()

        diete = Dieta.all()

        if me == "on":
          diete= diete.filter("commissario",commissario)

        if anno != "":
          diete = diete.filter("anno",int(anno))      
        
        if cm != "":
          diete = diete.filter("commissione",Commissione.get(cm))
        
        url_path = "commissario"
        if commissario.isGenitore():
          url_path = "genitore"
          
        if(orderby.find("data") != -1):
          orderby = orderby + "Ispezione"
        for dieta in diete.order(orderby).fetch(limit, offset):
          data_dieta.append({"commissione": (dieta.commissione.nome + " - " + dieta.commissione.tipoScuola), "data": dieta.dataIspezione, "turno": str(dieta.turno), "tipoDieta": dieta.tipoNome(), 
                       "key":"<a class='btn' href='/" + url_path + "/dieta?cmd=open&key="+str(dieta.key())+"'>Apri</a>"})
  
        # Loading it into gviz_api.DataTable
        data_table_dieta = DataTable(description_dieta)
        data_table_dieta.LoadData(data_dieta)
        
        # Creating a JSon string
        self.response.out.write(data_table_dieta.ToJSonResponse(columns_order=("commissione", "data", "turno", "tipoDieta", "key")))

      elif frm == "note":

        # Creating the data
        description = {"commissione": ("string", "Commissione"),
                       "data": ("date", "Data"),
                       "titolo": ("string", "Titolo"),
                       "testo": ("string", "Testo"),
                       "key": ("string", "")}
        
        data = list()
        note = Nota.all()
        
        if me == "on":
          note = note.filter("commissario",commissario)
          me = "on"

        if anno != "":
          note = note.filter("anno",long(anno))
        
        if cm != "":
          note = note.filter("commissione",Commissione.get(cm))

        url_path = "commissario"
        if commissario.isGenitore():
          url_path = "genitore"
          
        if(orderby.find("data") != -1):
          orderby = orderby + "Nota"
        for nota in note.order(orderby).fetch(limit, offset):
          titolo = nota.titolo
          if len(titolo) > 30: titolo = titolo[0:30] + "..."
          testo = nota.note
          if len(testo) > 50: testo = testo[0:50] + "..."
            
          data.append({"commissione": (nota.commissione.nome + " - " + nota.commissione.tipoScuola), "data": nota.dataNota,
                       "titolo": titolo, "testo": testo, "key":"<a class='btn' href='/" + url_path + "/nota?cmd=open&key="+str(nota.key())+"'>Apri</a>"})
  
        # Loading it into gviz_api.DataTable
        data_table = DataTable(description)
        data_table.LoadData(data)
  
        # Creating a JSon string
        self.response.out.write(data_table.ToJSonResponse(columns_order=("commissione", "data", "titolo", "testo", "key")))


class CMGetIspDataHandler(BasePage):
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if( commissario is not None):    
      cm = self.request.get("cm")
      isp = Ispezione.all().filter("commissione",Commissione.get(cm)).order("-dataIspezione").get()
        
      buff = ""
      if( isp ):
        buff = str(isp.aaRispettoCapitolato)+"|"+str(isp.aaTavoliApparecchiati)+"|"+str(isp.aaTermichePulite)+"|"+str(isp.aaAcqua)+"|"+str(isp.aaScaldaVivande)+"|"+str(isp.aaSelfService)+"|"+str(isp.aaTabellaEsposta)+"|"+str(isp.ricicloStoviglie)+"|"+str(isp.ricicloPosate)+"|"+str(isp.ricicloBicchieri)
      
    self.response.out.write(buff) 


class IspezioneValidationHandler(BasePage):    
  def post(self):
    #logging.info(self.request.get("commissione"));
    #logging.info(self.request.get("dataIspezione"));
    #logging.info(self.request.get("turno"));
    turno = int(self.request.get("turno"))
    commissione = self.request.get("commissione")
    dataIspezione = datetime.strptime(self.request.get("dataIspezione"),Const.DATE_FORMAT).date()

    logging.info(dataIspezione);
    
    message = "Ok"
    if Ispezione.all().filter("dataIspezione",dataIspezione).filter("commissione",db.Key(commissione)).filter("turno",turno).count() > 0 :
      message = "<ul><li>Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.</li></ul>"

    logging.info(message);
    self.response.out.write(message)
    
class DietaValidationHandler(BasePage):    
  def post(self):
    turno = int(self.request.get("turno"))
    commissione = self.request.get("commissione")
    dataIspezione = datetime.strptime(self.request.get("dataIspezione"),Const.DATE_FORMAT).date()
    tipo = int(self.request.get("tipoDieta"))

    logging.info(dataIspezione);
    
    message = "Ok"
    if Dieta.all().filter("dataIspezione",dataIspezione).filter("commissione",db.Key(commissione)).filter("turno",turno).filter("tipoDieta",tipo).count() > 0 :
      message = "<ul><li>Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.</li></ul>"

    logging.info(message);
    self.response.out.write(message)
    
  
class IspezioneHandler(BasePage):
  
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
      
      #for field in form:
        #logging.info(field.name)
        #form.data[field.name] = unicode(form.initial[field.name])
      
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
        #'content_left': 'commissario/leftbar.html',
        'nc': nc,
        "public_url": "http://" + self.getHost() + "/public/nc?key=" + str(nc.key()),
        "comments": True,
        "comment_root": comment_root
        }

      self.getBase(template_values)

    elif( self.request.get("cmd") == "edit" ):
   
      nc = memcache.get(self.request.get("preview"))
      memcache.delete(self.request.get("nc"))
    
      form = NonconformitaForm(instance=nc)
      
      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
      
      form.commissione.data = isp.commissione

      template_values = {
        'content': 'commissario/nonconf_div.html',
        'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      nc = Nonconformita(commissario = commissario) 
      form = NonconformitaForm(instance=nc)

      for field in form:
        form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'main': 'ispezioni/nonconf_div.html',
        #'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

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

      self.response.out.write(CMCommentHandler().initActivity(nc.key(), 102, db.Key(self.request.get("last")), nc.tags))     
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        nc = Nonconformita.get(key)
      else:
        nc = Nonconformita()
    
      form = NonconformitaForm(data=self.request.POST, instance=nc)

      #logging.info(nc)
      
      if form.is_valid():
        nc = form.save(commit=False)
        nc.commissario = commissario
   
        nc.tags = list()
        for tag in self.request.get_all("tags"):
          logging.info(tag)
          nc.tags.append(tag)
        
        preview = user.email() + datetime.strftime(datetime.now(), Const.TIME_FORMAT)
        memcache.add(preview, nc, 3600)
   
        template_values = {
          'main': 'ispezioni/nonconf_read_div.html',
          #'content_left': 'commissario/leftbar.html',
          'nc': nc,
          'preview': preview
        }
        
      else:
        for error in form.errors["__all__"]:
          logging.info(error)
        template_values = {
          'main': 'ispezioni/nonconf_read_div.html',
          #'content_left': 'commissario/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form,
          'form_errors': form.errors["__all__"]
        }
        
      self.getBase(template_values)
      

class DietaHandler(BasePage):
  
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
    
      form = DietaForm(instance=dieta)
      
      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
      
      form.data["commissione"] = dieta.commissione

      template_values = {
        'content': 'commissario/dieta.html',
        'content_left': 'commissario/leftbar.html',
        'form': form,
        'commissioni': commissario.commissioni()
      }

      self.getBase(template_values)
          
    else:     
  
      dieta = Dieta(commissario = commissario) 
      form = DietaForm(instance=dieta)

      for field in form:
        form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'main': 'ispezioni/dieta_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

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

      self.response.out.write(CMCommentHandler().initActivity(dieta.key(), 103, db.Key(self.request.get("last"))))
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        dieta = Dieta.get(key)
      else:
        dieta = Dieta()
    
      form = DietaForm(data=self.request.POST, instance=dieta)
      #for field in form:
        #logging.info("%s, %s",field.name, field)

      if form.is_valid():
        dieta = form.save(commit=False)
        dieta.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), Const.TIME_FORMAT)
        memcache.add(preview, dieta, 3600)
    
        template_values = {
          'main': 'ispezioni/dieta_read_div.html',
          'dieta': dieta,
          'preview': preview
        }
        
      else:
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)
          
        template_values = {
          'main': 'ispezioni/err_div.html',
          'commissioni': commissario.commissioni(),
          'form': form,
          'form_errors': form.errors["__all__"]
        }
        
      self.getBase(template_values)
      
class NotaHandler(BasePage):
  
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
    
      form = NotaForm(instance=nota)
      
      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
      
      form.data["commissione"] = nota.commissione

      template_values = {
        'content': 'commissario/nota.html',
        'content_left': 'commissario/leftbar.html',
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
        'main': 'ispezioni/nota_div.html',
        'form': form,
        'commissioni': commissario.commissioni()
        }

      self.getBase(template_values)

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
      
      saveTags
      username = Configurazione.all().filter("nome", "attach_user").get().valore
      password = Configurazione.all().filter("nome", "attach_password").get().valore
      site = Configurazione.all().filter("nome", "attach_site").get().valore
      path = Configurazione.all().filter("nome", "attach_path").get().valore
      site = Site(username, password, site)

      for allegato in nota.allegati:
        allegato.obj = nota
        allegato.path = site.uploadDoc(allegato.dati, str(nota.key().id()) + "_" + allegato.nome, allegato.contentType(), path)
        allegato.put()

      memcache.delete("stats")
      memcache.delete("statsMese")
      
      self.response.out.write(CMCommentHandler().initActivity(nota.key(), 104, db.Key(self.request.get("last")), nota.tags))
    else:
      key = self.request.get("key")
      if( key != "" ) :
        nota = Nota.get(key)
      else:
        nota = Nota()
    
      form = NotaForm(data=self.request.POST, instance=nota)
      #for field in form:
        #logging.info("%s, %s",field.name, field)
      
      if form.validate():
        nota = form.save(commit=False)
        nota.commissario = commissario

        nota.tags = list()
        for tag in self.request.get_all("tags"):
          logging.info(tag)
          nota.tags.append(tag)
        
        if self.request.get("allegato_file"):
          nota.allegati = list()
          allegato = Allegato()
          allegato.descrizione = self.request.get('allegato_desc')
          allegato.nome = self.request.POST['allegato_file'].filename
          allegato.dati = self.request.get("allegato_file")
          if len(allegato.dati) < 1000000 :         
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
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)
  
        
        template_values = {
          'main': 'ispezioni/nota_div.html',
          'commissioni': commissario.commissioni(),
          'form': form
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