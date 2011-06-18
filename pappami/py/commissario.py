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
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.site import *
from py.form import IspezioneForm, NonconformitaForm, DietaForm, NotaForm
from py.base import BasePage, CMCommissioniDataHandler, CMCommissioniHandler, CMMenuHandler, roleCommissario
from py.stats import CMStatsHandler
from py.calendar import *
from py.modelMsg import *
from py.comments import CMCommentHandler

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
    
class CMCommissarioHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      self.redirect("/commissario/registrazione")
    else:
  
      c = None
      geo = db.GeoPt(45.463681,9.188171)
      commissario = self.getCommissario(users.get_current_user())
      c = commissario.commissione()
      geo = commissario.citta.geo
      
      template_values = dict()
      template_values["bgcolor"] = "eeeeff"
      template_values["fgcolor"] = "000000"    
      template_values["activities"] = self.getActivities()
      template_values["activity_last"] = self.getActivities()[0]
      template_values["geo"] = geo
      template_values["billboard"] = "navigation.html"
      template_values["content"] = "activities.html"
      template_values["host"] = self.getHost()  

      self.getBase(template_values)

class CMDatiHandler(BasePage):
  
  @roleCommissario
  def get(self): 
    template_values = dict()
    template_values["billboard"] = "navigation.html"
    template_values['content'] = 'commissario/ispezioni.html'
    self.getBase(template_values)
      
class CMIspezioniCommissarioHandler(BasePage):
  @roleCommissario
  def get(self):
    template_values = dict()
    template_values["content_left"] = "commissario/leftbar.html"
    template_values['content'] = 'commissario/ispezioni.html'
    self.getBase(template_values)

class CMNonconfsCommissarioHandler(BasePage):
  @roleCommissario
  def get(self):
    template_values = dict()
    template_values["content_left"] = "commissario/leftbar.html"
    template_values['content'] = 'commissario/nonconfs.html'
    self.getBase(template_values)

class CMDieteCommissarioHandler(BasePage):
  @roleCommissario
  def get(self):
    template_values = dict()
    template_values["content_left"] = "commissario/leftbar.html"
    template_values['content'] = 'commissario/diete.html'
    self.getBase(template_values)

class CMNoteCommissarioHandler(BasePage):
  @roleCommissario
  def get(self):
    template_values = dict()
    template_values["content_left"] = "commissario/leftbar.html"
    template_values['content'] = 'commissario/note.html'
    self.getBase(template_values)
        
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
      
      
class CMRegistrazioneHandler(BasePage):
  
  def get(self): 
    template_values = dict()
      
    commissario = self.getCommissario(users.get_current_user())
    if commissario is not None and not commissario.isRegCommissario:
      self.redirect("/")
    if commissario is not None and commissario.isRegCommissario:
      template_values["content"] = "commissario/registrazione_ok.html"
      template_values["cmsro"] = commissario
    else:
      template_values["content"] = "commissario/registrazione.html"
      
    self.getBase(template_values)
  
  def post(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario == None):
      commissario = Commissario(nome = self.request.get("nome"), cognome = self.request.get("cognome"), user = user, stato = 0)
      commissario.emailComunicazioni = self.request.get("emailalert")
      commissario.put()
          
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()

      commissario.setCMDefault()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
        
      self.sendRegistrationRequestMail(commissario)
    
    template_values = {
      'content': 'commissario/registrazione_ok.html',
      'cmsro': commissario
    }
    self.getBase(template_values)

  def sendRegistrationRequestMail(self, commissario) :

    host = self.getHost()
    
    sender = "Pappa-Mi <aiuto@pappa-mi.it>"
    
    message = mail.EmailMessage()
    message.sender = sender
    message.to = sender
    message.subject = "Richiesta di Registrazione da " + commissario.nome + " " + commissario.cognome
    message.body = commissario.nome + " " + commissario.cognome + " " + commissario.user.email() + """ ha inviato una richiesta di registrazione come Commissario. 
    
    Per abilitarlo usare il seguente link:
    
    """ + "http://" + host + "/admin/commissario?cmd=enable&key="+str(commissario.key())

    message.send()

class CMProfiloCommissarioHandler(BasePage):
  
  def get(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    template_values = {
      'content_left': 'commissario/leftbar.html',
      'content': 'commissario/profilo.html',
      'cmsro': commissario
    }
    self.getBase(template_values)
    
  def post(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario):
      commissario.nome = self.request.get("nome")
      commissario.cognome = self.request.get("cognome")
      commissario.citta = db.Key(self.request.get("citta"))
      commissario.emailComunicazioni = self.request.get("emailalert")
      commissario.put()

      old = list()
      for cc in CommissioneCommissario.all().filter("commissario",commissario):
        old.append(str(cc.commissione.key()))
        #logging.info("old " + cc.commissione.nome)
      old = set(old)

      new = list()
      for c_key in self.request.get_all("commissione"):
        new.append(c_key)
        #logging.info("new " + Commissione.get(db.Key(c_key)).nome)
      new = set(new)

      todel = old - new
      toadd = new - old

      for cm in todel:
        cmd = Commissione.get(db.Key(cm))
        logging.info("delete " + cmd.nome)
        
        cc = CommissioneCommissario.all().filter("commissario",commissario).filter("commissione",cmd).get()
        if cc.commissione.calendario :
          calendario = Calendario();        
          calendario.logon(user=Configurazione.all().filter("nome","calendar_user").get().valore, password=Configurazione.all().filter("nome", "calendar_password").get().valore)
          calendario.load(cc.commissione.calendario)
          calendario.unShare(commissario.user.email())
        cc.delete()
        cmd.numCommissari -= 1
        cmd.put()
        
        
        
      for cm in toadd:
        cma = Commissione.get(db.Key(cm))
        logging.info("add " + cma.nome)

        cc = CommissioneCommissario(commissione = cma, commissario = commissario)
        cc.put()
        cma.numCommissari += 1
        cma.put()
        if cc.commissione.calendario :
          calendario = Calendario();        
          calendario.logon(user=Configurazione.all().filter("nome","calendar_user").get().valore, password=Configurazione.all().filter("nome", "calendar_password").get().valore)
          calendario.load(cc.commissione.calendario)
          calendario.share(commissario.user.email())

      commissario.setCMDefault()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
        
    template_values = {
      'content_left': 'commissario/leftbar.html',
      'content': 'commissario/profilo.html',
      'saved': True,
      'cmsro': commissario
    }
    self.getBase(template_values)
      

    
class CMIspezioneHandler(BasePage):
  
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
     
      form = IspezioneForm(instance=isp)
      
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
      isp = Ispezione(commissario = commissario) 
      form = IspezioneForm(instance=isp)

      for field in form:
        #logging.info(field.name)
        form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'content': '../templates/commissario/ispezione.html',
        'content_left': 'commissario/leftbar.html',
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
      form = IspezioneForm(instance=isp)
      
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
        
      self.getBase(template_values) 
    elif( preview ):
      isp = memcache.get(preview)
      memcache.delete(preview)
      if isp.dataIspezione.month >= 9:
        isp.anno = isp.dataIspezione.year
      else:
        isp.anno = isp.dataIspezione.year - 1
        
      isp.put()

      comment_root = CMCommentHandler().init(isp.key())

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
        #logging.info(preview)
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
     
      form = IspezioneForm(instance=isp)
      
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
      isp = Ispezione(commissario = commissario) 
      form = IspezioneForm(instance=isp)

      for field in form:
        #logging.info(field.name)
        form.data[field.name] = str(form.initial[field.name])
        
      template_values = {
        'main': '../templates/commissario/ispezione_div.html',
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
      form = IspezioneForm(instance=isp)
      
      for field in form:
        #logging.info(field.name)
        form.data[field.name] = unicode(form.initial[field.name])
      
      form.data["commissione"] = isp.commissione
  
      template_values = {
        'main': '../templates/commissario/ispezione_div.html',
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
      
      self.response.out.write(CMCommentHandler().initActivity(isp.key(), 101, db.Key(self.request.get("last"))))
      
    else:
      key = self.request.get("key")
      if( key != "" ) :
        isp = Ispezione.get(key)
      else:
        isp = Ispezione()
    
      form = IspezioneForm(data=self.request.POST, instance=isp)
      
      logging.info(preview)
      
      if form.is_valid():
        logging.info("valid")

        isp = form.save(commit=False)
        
        isp.commissario = commissario
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        logging.info(preview)
        memcache.add(preview, isp, 3600)
    
        template_values = {
          'main': '../templates/commissario/ispezione_read_div.html',
          'isp': isp,
          'preview': preview
        }
        
        self.getBase(template_values) 
      else:
        logging.info("data: %s", form.data)
        for e in form.errors["__all__"] :
          logging.info("errors: %s", e)

        template_values = {
          'main': '../templates/commissario/ispezione_div.html',
          'commissioni': commissario.commissioni(),
          'form': form
        }

        self.getBase(template_values)
        
        
class CMNonconfHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      return

    if( self.request.get("cmd") == "open" ):
      nc = Nonconformita.get(self.request.get("key"))

      comment_root = CMCommentHandler().getRoot(nc.key())
      
      template_values = {
        'content': 'commissario/nonconf_read.html',
        'content_left': 'commissario/leftbar.html',
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
      
      form.data["commissione"] = nc.commissione

      template_values = {
        'content': 'commissario/nonconf.html',
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
        'content': '../templates/commissario/nonconf.html',
        'content_left': 'commissario/leftbar.html',
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
      comment_root = CMCommentHandler().init(nc.key())

      memcache.delete("stats")
      memcache.delete("statsMese")
      
      self.redirect("/commissario/nc")
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
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, nc, 3600)
   
        template_values = {
          'content': 'commissario/nonconf_read.html',
          'content_left': 'commissario/leftbar.html',
          'nc': nc,
          'preview': preview
        }
        
      else:
       
        template_values = {
          'content': 'commissario/nonconf.html',
          'content_left': 'commissario/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form
        }
      logging.info(template_values)
        
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
        'main': '../templates/commissario/nonconf_read.html',
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
      
      form.data["commissione"] = nc.commissione

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
        'main': '../templates/commissario/nonconf_div.html',
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

      self.response.out.write(CMCommentHandler().initActivity(nc.key(), 102, db.Key(self.request.get("last"))))     
      
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
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, nc, 3600)
   
        template_values = {
          'main': '../templates/commissario/nonconf_read_div.html',
          #'content_left': 'commissario/leftbar.html',
          'nc': nc,
          'preview': preview
        }
        
      else:
        for error in form.errors["__all__"]:
          logging.info(error)
        template_values = {
          'main': '../templates/commissario/nonconf_read_div.html',
          #'content_left': 'commissario/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form,
          'form_errors': form.errors["__all__"]
        }
        
      self.getBase(template_values)
      
class CMDietaHandler(BasePage):
  
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
        'content': 'commissario/dieta.html',
        'content_left': 'commissario/leftbar.html',
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
      key = self.request.get("k")
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
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, dieta, 3600)
    
        template_values = {
          'content': 'commissario/dieta_read.html',
          'content_left': 'commissario/leftbar.html',
          'dieta': dieta,
          'preview': preview
        }
        
      else:
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)
  
        
        template_values = {
          'content': 'commissario/dieta.html',
          'content_left': 'commissario/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form
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
        'main': '../templates/commissario/dieta_div.html',
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

      self.response.out.write(CMCommentHandler().initActivity(nc.key(), 103, db.Key(self.request.get("last"))))
      
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
   
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, dieta, 3600)
    
        template_values = {
          'main': '../templates/commissario/dieta_read_div.html',
          'dieta': dieta,
          'preview': preview
        }
        
      else:
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)
          
        template_values = {
          'main': '../templates/commissario/dieta_read.html',
          'commissioni': commissario.commissioni(),
          'form': form
        }
        
      self.getBase(template_values)
      
class CMNotaHandler(BasePage):
  
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
        'content': 'commissario/nota.html',
        'content_left': 'commissario/leftbar.html',
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

      comment_root = CMCommentHandler().init(nota.key())

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
      
      self.redirect("/commissario/note")
    else:
      key = self.request.get("k")
      if( key != "" ) :
        nota = Nota.get(key)
      else:
        nota = Nota()
    
      form = NotaForm(data=self.request.POST, instance=nota)
      #for field in form:
        #logging.info("%s, %s",field.name, field)

      if form.is_valid():
        nota = form.save(commit=False)
        nota.commissario = commissario
        
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
            
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, nota, 3600)
    
        template_values = {
          'content': 'commissario/nota_read.html',
          'content_left': 'commissario/leftbar.html',
          'nota': nota,
          'allegati': nota.allegati,
          'preview': preview
        }
        
      else:
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)
  
        
        template_values = {
          'content': 'commissario/nota.html',
          'content_left': 'commissario/leftbar.html',
          'commissioni': commissario.commissioni(),
          'form': form
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
        'main': '../templates/commissario/nota_div.html',
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
      
      self.response.out.write(CMCommentHandler().initActivity(nc.key(), 102, db.Key(self.request.get("last"))))
    else:
      key = self.request.get("key")
      if( key != "" ) :
        nota = Nota.get(key)
      else:
        nota = Nota()
    
      form = NotaForm(data=self.request.POST, instance=nota)
      #for field in form:
        #logging.info("%s, %s",field.name, field)

      if form.is_valid():
        nota = form.save(commit=False)
        nota.commissario = commissario
        
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
            
        preview = user.email() + datetime.strftime(datetime.now(), TIME_FORMAT)
        memcache.add(preview, nota, 3600)
    
        template_values = {
          'main': '../templates/commissario/nota_read_div.html',
          'nota': nota,
          'allegati': nota.allegati,
          'preview': preview
        }
        
      else:
        #logging.info("data: %s", form.data)
        #for e in form.errors["__all__"] :
          #logging.info("errors: %s", e)
  
        
        template_values = {
          'main': '../templates/commissario/nota_div.html',
          'commissioni': commissario.commissioni(),
          'form': form
        }
        
      self.getBase(template_values)
      
class CMCommissarioCommissioniHandler(CMCommissioniHandler):
  def get(self):
    #logging.info("CMCommissioniHandler.get")
    template_values = dict()
    template_values["path"] = "/commissario/commissioni"
    #template_values["content_left"] = "commissario/leftbar.html"
    template_values["billboard"] = "navigation.html"    
    self.getBase(template_values)
    
      
class CMCommissarioStatsHandler(CMStatsHandler):
  def post(self):
    return self.get()

  def get(self):
    #logging.info("CMCommissarioStatsHandler.get")
    template_values = dict()
    #template_values["content_left"] = "commissario/leftbar.html"
    template_values["billboard"] = "navigation.html"    
    self.getBase(template_values)

class CMCommissarioMenuHandler(CMMenuHandler):
  def post(self):
    return self.get()

  def get(self):
    template_values = dict()
    #template_values["content_left"] = "commissario/leftbar.html"
    template_values["billboard"] = "navigation.html"    
    self.getBase(template_values)

class CMCommissarioCalendarioHandler(BasePage):
  def post(self):
    return self.get()
  def get(self):    
    commissario = self.getCommissario(users.get_current_user())
    if self.request.get("cmd") == "create":
      cm = Commissione.get(self.request.get("cm"))
      if((cm.calendario == None or cm.calendario == "") and CommissioneCommissario.all().filter("commissario",commissario).filter("commissione", cm).get() is not None):
        calendario = Calendario()
        calendario.logon(user=Configurazione.all().filter("nome","calendar_user").get().valore, password=Configurazione.all().filter("nome", "calendar_password").get().valore)
        calendario.create(cm.nome + " - " + cm.tipoScuola)
        for c in cm.commissari():
          if c.isCommissario() :
            calendario.share(c.user.email())
        cm.calendario = str(calendario.GetId())
        cm.put()
      
    else:
      cm = None
      if self.request.get("cm") != "":
        cm = Commissione.get(self.request.get("cm"))
      elif commissario and commissario.commissione() :
        cm = commissario.commissione()
      else:
        cm = Commissione.all().get()
        
    template_values = dict()
    template_values["content"] = "commissario/calendario.html"
    template_values["content_left"] = "commissario/leftbar.html"
    template_values["commissioni"] = commissario.commissioni()
    template_values["creacal"] = (cm.calendario == None or cm.calendario == "") and CommissioneCommissario.all().filter("commissario",commissario).filter("commissione", cm).get() is not None
    template_values["cm"] = cm
    self.getBase(template_values)

    
def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   
   
  application = webapp.WSGIApplication([
    ('/commissario', CMCommissarioHandler),
    ('/commissario/dati', CMDatiHandler),
    ('/commissario/isp', CMIspezioniCommissarioHandler),
    ('/commissario/nc', CMNonconfsCommissarioHandler),
    ('/commissario/diete', CMDieteCommissarioHandler),
    ('/commissario/note', CMNoteCommissarioHandler),
    ('/commissario/ispezione', CMIspezioneHandler),
    ('/commissario/ispezione_div', IspezioneHandler),
    ('/commissario/nonconf', CMNonconfHandler),
    ('/commissario/nonconf_div', NonconfHandler),
    ('/commissario/dieta', CMDietaHandler),
    ('/commissario/dieta_div', DietaHandler),
    ('/commissario/nota', CMNotaHandler),
    ('/commissario/nota_div', NotaHandler),
    ('/commissario/registrazione', CMRegistrazioneHandler),
    ('/commissario/profilo', CMProfiloCommissarioHandler),
    ('/commissario/avatar', CMAvatarHandler),
    ('/commissario/stats', CMCommissarioStatsHandler),
    ('/commissario/commissioni', CMCommissarioCommissioniHandler),
    ('/commissario/menu', CMCommissarioMenuHandler),
    ('/commissario/calendario', CMCommissarioCalendarioHandler),
    ('/commissario/getcm', CMCommissioniDataHandler),
    ('/commissario/getdata', CMCommissarioDataHandler),
    ('/commissario/getispdata', CMGetIspDataHandler),
    ('/commissario/getcity', CMCittaHandler)])

  wsgiref.handlers.CGIHandler().run(application)
  
if __name__ == "__main__":
  main()
