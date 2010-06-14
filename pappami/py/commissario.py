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

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
    
class CMCommissarioHandler(BasePage):
  def getMenu(self, data, cm): 
    menu = list();

    #logging.info("data: %s", data)

    cc = cm.centroCucina
    offset = cc.menuOffset
    if offset == None:
      offset = 0
      
    # settimana corrente
    menus = Menu.all().filter("validitaDa <=", data).filter("tipoScuola", cm.tipoScuola).order("-validitaDa")
    logging.info("len %d" , menus.count())

    count = 0
    for m in menus:
      if((((((data-m.validitaDa).days) / 7)+offset)%4 + 1) == m.settimana):
        menu.append(m)
        logging.info("m" + m.primo)
        count += 1
        if count >=5 :
          break

    return sorted(menu, key=lambda menu: menu.giorno)

  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      self.redirect("/commissario/registrazione")
    else:
      tab=self.request.get("tab")
      template_values = {
        'content_left': 'commissario/leftbar.html',
        'tab': tab
        }
      if tab == "nc" :
        template_values['content'] = 'commissario/nonconfs.html'
      elif tab == "ud" :
        template_values['content'] = 'commissario/profilo.html'
        template_values['cmsro'] = commissario
      elif tab == "mn" :
        cm = self.request.get("cm")
        if(cm):
          cm = Commissione.get(cm)
        else:
          cm = commissario.commissioni()[0]
        date = self.request.get("data")
        if date:
          date = datetime.strptime(date,DATE_FORMAT).date()
        else:
          date = datetime.now().date()
        
        date1 = date - timedelta(datetime.now().isoweekday() - 1)
        date2 = date1 + timedelta(7)
        template_values['content'] = 'menu.html'
        template_values['menu1'] = self.getMenu(date1, cm )
        template_values['menu2'] = self.getMenu(date2, cm )
        template_values['data'] = date
        template_values['data1'] = date1
        template_values['data2'] = date2
        template_values['cm'] = cm
        template_values['action'] = self.request.path
      else:
        template_values['content'] = 'commissario/ispezioni.html'
      
      #logging.info("OK")
      self.getBase(template_values)

class CMCommissioniDataHandler(BasePage):

  def get(self): 
    user = users.get_current_user()
    buff = memcache.get("cmall")
    if(buff is None):
  
      description = {"nome": ("string", "Nome"), 
                     "key": ("string", "Key")}
      data_table = DataTable(description)
      
      cms = Commissione.all().order("nome")
      buff = ""
      buff = '{"label": "nome", "identifier": "key", "items": ['
      buff = buff + '{ "nome": "", "key": ""},'
  
      
      notfirst = False
      for cm in cms.order("nome"):
        if(notfirst) :
          buff = buff + ','
        notfirst = True
        buff = buff + '{ "nome": "' + cm.nome + ' - ' + cm.tipoScuola + '", "key": "' + str(cm.key()) + '"}'
        
      buff = buff + ']}'
      memcache.add("cmall", buff)
        
    expires_date = datetime.utcnow() + timedelta(20)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)
      
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
          dataInizio = date(year=int(anno), month=9, day=1)
          dataFine = date(year=int(anno)+1, month=9, day=1)
          ncs = ncs.filter("dataNonconf >=",dataInizio)      
          ncs = ncs.filter("dataNonconf <",dataFine)      
          ncs.order("dataNonconf")
        
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

      else:

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
          dataInizio = date(year=int(anno), month=9, day=1)
          dataFine = date(year=int(anno)+1, month=9, day=1)
          isps = isps.filter("dataIspezione >=",dataInizio)      
          isps = isps.filter("dataIspezione <",dataFine)      
          isps.order("dataIspezione")
        
        if cm != "":
          isps = isps.filter("commissione",Commissione.get(cm))

        url_path = "commissario"
        if commissario.isGenitore():
          url_path = "genitore"
          
        if(orderby.find("data") != -1):
          orderby = orderby + "Ispezione"
        for ispezione in isps.order(orderby).fetch(limit, offset):
          data.append({"commissione": (ispezione.commissione.nome + " - " + ispezione.commissione.tipoScuola), "data": ispezione.dataIspezione, "turno": ispezione.turno, 
                       #"complessivo": "<img src='img/icon" + str(ispezione.giudizioGlobale) + ".png'/>", 
                       "primo": "<img src='img/icoasg" + str(ispezione.primoAssaggio) + ".png' title='Assaggio'/>" + "<img src='img/icogra" + str(ispezione.primoGradimento) + ".png' title='Gradimento'/>" + "<img src='img/icocot" + str(ispezione.primoCottura) + ".png' title='Cottura'/>"+ "<img src='img/icotmp" + str(ispezione.primoTemperatura) + ".png' title='Temperatura'/>" + "<img src='img/icoqta" + str(ispezione.primoQuantita) + ".png' title='Quantit&agrave;'/>",
                       "secondo": "<img src='img/icoasg" + str(ispezione.secondoAssaggio) + ".png' title='Assaggio'/>" + "<img src='img/icogra" + str(ispezione.secondoGradimento) + ".png' title='Gradimento'/>" + "<img src='img/icocot" +str(ispezione.secondoCottura) + ".png' title='Cottura'/>"+ "<img src='img/icotmp" + str(ispezione.secondoTemperatura) + ".png' title='Temperatura'/>" + "<img src='img/icoqta" + str(ispezione.secondoQuantita) + ".png' title='Quantit&agrave;'/>",
                       "contorno": "<img src='img/icoasg" + str(ispezione.contornoAssaggio) + ".png' title='Assaggio'/>" + "<img src='img/icogra" + str(ispezione.contornoGradimento) + ".png' title='Gradimento'/>" + "<img src='img/icocot" + str(ispezione.contornoCottura) + ".png' title='Cottura'/>"+ "<img src='img/icotmp" + str(ispezione.contornoTemperatura) + ".png' title='Temperatura'/>" + "<img src='img/icoqta" + str(ispezione.contornoQuantita) + ".png' title='Quantit&agrave;'/>",
                       "frutta": "<img src='img/icoasg" + str(ispezione.fruttaAssaggio) + ".png' title='Assaggio'/>" + "<img src='img/icogra" + str(ispezione.fruttaGradimento) + ".png' title='Gradimento'/>" + "<img src='img/icomat" + str(ispezione.fruttaMaturazione) + ".png' title='Maturazione'/>" + "<img src='img/icoqta" + str(ispezione.fruttaQuantita) + ".png' title='Quantit&agrave;'/>", 
                       "pasti":str(ispezione.numeroPastiTotale) + " " + str(ispezione.numeroPastiBambini), "key":"<a class='btn' href='/" + url_path + "/ispezione?cmd=open&key="+str(ispezione.key())+"'>Apri</a>"})
  
        # Loading it into gviz_api.DataTable
        data_table = DataTable(description)
        data_table.LoadData(data)
  
        # Creating a JSon string
        self.response.out.write(data_table.ToJSonResponse(columns_order=("commissione", "data", "turno", "primo", "secondo", "contorno", "frutta", "pasti", "key")))
      
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

    host = self.getHost()
    
    #if self.request.url.find("test") != -1:
      #url = "test-pappa-mi.appspot.com"
    #else if self.request.url.find("test") != -1:
      #url = "pappa-mi.appspot.com"
    #else:
      #url = "pappa-mi.appspot.com"
    
    message = mail.EmailMessage()
    message.sender = "aiuto@pappa-mi.it"
    message.to = "aiuto@pappa-mi.it"
    message.subject = "Richiesta di Registrazione da " + commissario.nome + " " + commissario.cognome
    message.body = commissario.nome + " " + commissario.cognome + " " + commissario.user.email() + """ ha inviato una richiesta di registrazione come Commissario. 
    
    Per abilitarlo usare il seguente link:
    
    """ + "http://" + host + "/admin/commissario?cmd=enable&key="+str(commissario.key())

    message.send()

class CMProfiloCommissarioHandler(BasePage):
  
  def post(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario):
      commissario.nome = self.request.get("nome")
      commissario.cognome = self.request.get("cognome")
      commissario.put()
      for cc in CommissioneCommissario.all().filter("commissario",commissario):
        cc.delete()
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()
   
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
      
      template_values = {
        'content': 'commissario/ispezione_read.html',
        'content_left': 'commissario/leftbar.html',
        'isp': isp,
        'cancopy': cancopy
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
        'content': 'commissario/ispezione.html',
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
        

class CMNonconfHandler(BasePage):
  
  def get(self): 
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if commissario is None or not commissario.isCommissario() :
      return

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
        'content': 'commissario/nonconf.html',
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

def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   
   
  application = webapp.WSGIApplication([
    ('/commissario/ispezione', CMIspezioneHandler),
    ('/commissario/nonconf', CMNonconfHandler),
    ('/commissario/registrazione', CMRegistrazioneHandler),
    ('/commissario/profilo', CMProfiloCommissarioHandler),
    ('/commissario', CMCommissarioHandler),
    ('/commissario/getcm', CMCommissioniDataHandler),
    ('/commissario/getdata', CMCommissarioDataHandler)
  ], debug=debug)

  wsgiref.handlers.CGIHandler().run(application)
  
if __name__ == "__main__":
  main()
