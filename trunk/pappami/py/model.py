#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from google.appengine.api import search
from datetime import date, datetime, time, timedelta
import logging
import fpformat
import google.appengine.api.images
import threading
import math
from google.appengine.ext.ndb import model, Cursor
from google.appengine.ext import blobstore
from google.appengine.api import memcache
from google.appengine.api import users
import base
from common import cached_property, Const, Cache
from engineauth import models
import jinja2
import os
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)[0:len(os.path.dirname(__file__))-3]+"/templates"))

class Citta(model.Model):
  nome = model.StringProperty()
  codice =  model.StringProperty()
  provincia = model.StringProperty()
  geo = model.GeoPtProperty()

  creato_il = model.DateTimeProperty(auto_now_add=True)
  modificato_il = model.DateTimeProperty(auto_now=True)

  stato = model.IntegerProperty()
  
  @classmethod
  def get_all(cls):
    return cls.query().order(Citta.nome)

  @classmethod
  def get_first(cls):
    return cls.query().get()
  
  def create_resource(self):
      
      resource=self.get_resource()
      if not resource:
        resource=SocialResource(parent=self.key,
                                        name=self.nome,
                                        type="city",
                                        geo=self.geo,
                                        )
        resource.put()
      return resource
  
  def get_resource(self):
      resource=SocialResource.query(ancestor=self.key).get()
      if resource:
          assert resource.type=="city"
      return resource
  
class Configurazione(model.Model):
  nome = model.StringProperty()
  valore = model.StringProperty()
  
  @classmethod
  def get_value_by_name(cls, name):
    return Configurazione.query(Configurazione.nome == name).get().valore
  
  
      
  
      
class CentroCucina(model.Model):  
  def __init__(self, *args, **kwargs):
    self._ce_cu_zo_cache = None
    self._zo_of_cache = None
    super(CentroCucina, self).__init__(*args, **kwargs)  

  nome = model.StringProperty()
  codice = model.StringProperty()
  strada = model.StringProperty()
  civico = model.StringProperty()
  #citta = model.StringProperty()  # PRE_MIGRATION
  citta = model.KeyProperty(kind=Citta)
  cap = model.StringProperty()
  nomeContatto = model.StringProperty()
  cognomeContatto = model.StringProperty()
  telefono = model.StringProperty()
  fax = model.StringProperty()
  email = model.StringProperty()
  menuOffset = model.IntegerProperty()

  creato_il = model.DateTimeProperty(auto_now_add=True)
  modificato_il = model.DateTimeProperty(auto_now=True)
  stato = model.IntegerProperty()
  
  @classmethod
  def get_by_citta(cls, citta_key):
    CentroCucina.query().filter(CentroCucina.citta == citta_key).order(CentroCucina.nome)

  def getZona(self, data=datetime.now().date()):
    if not(self._ce_cu_zo_cache and self._ce_cu_zo_cache.validitaDa <= data and self._ce_cu_zo_cache.validitaA >= data):
      self._ce_cu_zo_cache = CentroCucinaZona.query().filter(CentroCucinaZona.centroCucina == self.key).filter(CentroCucinaZona.validitaDa <= data).order(-CentroCucinaZona.validitaDa).get()
    return self._ce_cu_zo_cache.zona
  
  def getMenuOffset(self, data=datetime.now().date()):
    if not(self._zo_of_cache and self._zo_of_cache.validitaDa <= data and self._zo_of_cache.validitaA >= data):
      self._zo_of_cache = ZonaOffset.query().filter(ZonaOffset.zona == self.getZona(data)).filter(ZonaOffset.validitaDa <=data).order(-ZonaOffset.validitaDa).get()
    return self._zo_of_cache.offset
  
class Commissione(model.Model):
  def __init__(self, *args, **kwargs):
    self._com_cen_cuc_last = None
    self._cc_last = None
    self._commissari = None
    super(Commissione, self).__init__(*args, **kwargs)  

  nome = model.StringProperty(default="")
  nomeScuola = model.StringProperty(default="")
  tipoScuola = model.StringProperty(default="")
  codiceScuola = model.StringProperty(default="")
  distretto = model.StringProperty(default="")
  zona = model.StringProperty(default="")
  strada = model.StringProperty(default="")
  civico = model.StringProperty(default="")
  #citta = model.StringProperty(default="") # PRE_MIGRATION
  citta = model.KeyProperty(kind=Citta) 
  cap = model.StringProperty(default="")
  telefono = model.StringProperty(default="")
  fax = model.StringProperty(default="")
  email = model.StringProperty()
  centroCucina = model.KeyProperty(kind=CentroCucina)
  
  geo = model.GeoPtProperty()

  numCommissari = model.IntegerProperty(default=0)

  calendario = model.StringProperty(default="")
  
  creato_il = model.DateTimeProperty(auto_now_add=True)
  creato_da = model.KeyProperty(kind=models.User)
  modificato_il = model.DateTimeProperty(auto_now=True)
  modificato_da = model.KeyProperty(kind=models.User)
  stato = model.IntegerProperty()

  @classmethod
  def get_by_citta(cls, citta_key):
    commissioni = memcache.get("cm-citta-"+str(citta_key.id()))
    if commissioni == None:
      commissioni = list()
      for cm in Commissione.query().filter(Commissione.citta == citta_key).order(Commissione.nome):
        commissioni.append(cm)
      memcache.add("cm-citta-"+str(citta_key.id()), commissioni)
    return commissioni

  @classmethod
  def get_active(cls):
    return Commissione.query().filter(Commissione.numCommissari > 0).count()
  
  @classmethod
  def get_all_cursor(cls, cursor):
    if cursor and cursor != "":
      return Commissione.query().order(Commissione.nome).iter(start_cursor=Cursor.from_websafe_string(cursor), produce_cursors=True);
    else:
      return Commissione.query().order(Commissione.nome).iter(produce_cursors=True)

  @classmethod
  def get_active_cursor(cls, cursor):
    if cursor and cursor != "":
      return Commissione.query().filter(Commissione.numCommissari > 0).iter(start_cursor=Cursor.from_websafe_string(cursor), produce_cursors=True)
    else:
      return Commissione.query().filter(Commissione.numCommissari > 0).iter(produce_cursors=True)
  
  def create_resource(self):
      
      resource=self.get_resource()
      if not resource:
        resource=SocialResource(parent=self.key,
                                        name=self.nome,                                        
                                        type="cm",
                                        geo=self.geo,
                                        )
        resource.put()
      return resource
        
        
  def get_resource(self):
      resource=SocialResource.query(ancestor=self.key).get()
      if resource:
          assert resource.type=="commission"
      return resource
  
  
  def commissari(self):
    if not self._commissari:
      self._commissari = list()
      for cc in CommissioneCommissario.query().filter(CommissioneCommissario.commissione == self.key):
        self._commissari.append(cc.commissario)
    return self._commissari
  
  def getCentroCucina(self, data=datetime.now().date()):
    if not (self._com_cen_cuc_last and self._com_cen_cuc_last.validitaDa <= data and self._com_cen_cuc_last.validitaA >= data):
      self._com_cen_cuc_last = CommissioneCentroCucina.query().filter(CommissioneCentroCucina.commissione == self.key).filter(CommissioneCentroCucina.validitaDa <= data).order(-CommissioneCentroCucina.validitaDa).get()
      if self._com_cen_cuc_last:
        self._cc_last = self._com_cen_cuc_last.centroCucina.get()
    return self._cc_last

  def desc(self):
    return self.nome + " " + self.tipoScuola
  
class Commissario(model.Model):
  def __init__(self, *args, **kwargs):
    self._commissioni = list()
    self._privacy = None
    self._notify = None
    super(Commissario, self).__init__(*args, **kwargs)  

  user = model.UserProperty()
  usera = model.KeyProperty()
  nome = model.StringProperty()
  cognome = model.StringProperty()
  
  avatar_url = model.StringProperty(indexed=False)
  avatar_data = model.BlobProperty()

  emailComunicazioni = model.StringProperty()
  newsletter=model.BooleanProperty(default=True)
  privacy = model.PickleProperty()
  notify = model.PickleProperty()

  user_email_lower = model.StringProperty()
  
  citta = model.KeyProperty(kind=Citta)
  
  creato_il = model.DateTimeProperty(auto_now_add=True)
  creato_da = model.KeyProperty(kind=models.User)
  modificato_il = model.DateTimeProperty(auto_now=True)
  modificato_da = model.KeyProperty(kind=models.User)
  
  ultimo_accesso_il = model.DateTimeProperty()
  ultimo_accesso_notifiche= model.DateTimeProperty()
  
  stato = model.IntegerProperty()
  
  cmdefault = None  

  @classmethod
  def get_by_user(cls, user):
    commissario = memcache.get("commissario-"+str(user.key.id()))
    if not commissario:
      commissario = cls.query().filter(Commissario.usera == user.key).get()
      #if not commissario and user.email:
        #commissario = cls.query().filter(Commissario.user == users.User(user.email)).get()
        #if commissario:
          #commissario.usera = user.key
          #commissario.put()
      memcache.add("commissario-"+str(user.key.id()), commissario)
    return commissario
  
  def set_cache(self):
    memcache.delete("commissario-"+str(self.usera.id()))

  @classmethod
  def get_all(cls):
    return Commissario.query()
  
  @classmethod
  def get_for_newsletter(cls):
    return Commissario.query().filter(Commissario.newsletter==True)

  @classmethod
  def get_by_email_lower(cls, email):
    return Commissario.query().filter(Commissario.user_email_lower == email).get()
      
  def is_registered(self, cm):
    return CommissioneCommissario.query().filter(CommissioneCommissario.commissario == self.key).filter(CommissioneCommissario.commissione == cm).get() is not None

  def register(self, cm):
    cc = CommissioneCommissario(commissione = cm.key, commissario = self.key)
    cc.put()
    cm.numCommissari += 1
    cm.put()
    self._commissioni = list()
  
  def unregister(self, cm):
    CommissioneCommissario.query().filter(CommissioneCommissario.commissario == self.key).filter(CommissioneCommissario.commissione == cm.key).get().key.delete()
    cm.numCommissari -= 1
    cm.put()
    self._commissioni = list()
    
  def isCommissario(self):
    return self.stato == 1
  def isGenitore(self):
    return self.stato == 11
  def isRegistering(self):
    return self.stato == 10 or self.stato == 0
  def isRegistered(self):
    return self.stato == 11 or self.stato == 1
  def isRegCommissario(self):
    return self.stato == 0
  def isRegGenitore(self):
    return self.stato == 10
  
  def commissioni(self):
    if len(self._commissioni) == 0:
      for cc in CommissioneCommissario.query().filter(CommissioneCommissario.commissario == self.key):
        self._commissioni.append(cc.commissione.get())      
    return self._commissioni

  def setCMDefault(self):
    if len(self.commissioni()) > 0:
      self.cmdefault = self.commissioni()[0]
  
  def commissione(self):
    #if not self.cmdefault and len(self.commissioni()) > 0:
      #self.cmdefault = self.commissioni()[0]
    #return self.cmdefault
    cms = self.commissioni()
    if len(cms) > 0:
      return cms[0]
  
  def nomecompleto(self, cmsro, myself=False):
    nome = ""
    if myself or self.can_show(1,self.get_user_type(cmsro)):
      nome = nome + self.nome
    if myself or self.can_show(2,self.get_user_type(cmsro)):
      if nome != "":
        nome = nome + " "
      nome = nome + self.cognome
    if nome == "":
      nome = "Anonimo"
    return nome

  def titolo(self, cmsro, myself=False):
    titolo = ""
    if self.isCommissario():
      titolo = "Commissione Mensa "
    else:
      titolo = "Genitore "
    if myself or self.can_show(3,self.get_user_type(cmsro)):
      for c in self.commissioni():
        titolo = titolo + c.tipoScuola + " " + c.nome + "; "
    return titolo
    
  def avatar(self, cmsro, size = None, myself=False):
    if self.avatar_url and ( myself or self.can_show(4,self.get_user_type(cmsro))):    
      if "?id=" in self.avatar_url and size:
        return self.avatar_url + "&size="+size
      else:
        return self.avatar_url
    else:
      return "/img/default_avatar.png"

  def email(self, cmsro, myself=False):
    email = ""
    if myself or self.can_show(0,self.get_user_type(cmsro)):
      email = self.usera.get().email
    return email

  def get_user_type(self, cmsro):
    if cmsro == None:
      return 0
    if cmsro.isGenitore():
      return 1
    if cmsro.isCommissario():
      return 2
    return 0
    
  def can_show(self, what, whom):
    if self._privacy == None:
      if self.privacy == None or len(self.privacy) < 5:
        self.privacy = [[0,1,1],[1,1,1],[0,1,1],[1,1,1],[0,1,1]]
      self._privacy = self.privacy
    return self._privacy[what][whom]

  def get_notify(self, what):
    if self._notify == None:
      if self.notify == None or len(self.notify) < 3:
        self.notify = [1,2,0]
      self._notify = self.notify
    return self._notify[what]
  
  privacy_objects = {0: "email",
                     1: "name",
                     2: "surname",
                     3: "cm",
                     4: "avatar"}
  privacy_subjects = {0: "anyone",
                      1: "registered",
                      2: "cm"}

  
class CommissioneCommissario(model.Model):
  commissione = model.KeyProperty(kind=Commissione)
  commissario = model.KeyProperty(kind=Commissario)
  
class Menu(model.Model):
  tipoScuola = model.StringProperty()
  validitaDa = model.DateProperty()
  validitaA = model.DateProperty()
  settimana = model.IntegerProperty()
  giorno = model.IntegerProperty()
  primo = model.StringProperty()
  secondo = model.StringProperty()
  contorno = model.StringProperty()
  dessert = model.StringProperty()
  data = None

  _giorni = ["Lunedi'", "Martedi'", "Mercoledi'", "Giovedi'", "Venerdi'","Sabato", "Domenica"]
  def getData(self):
    return Menu._giorni[self.giorno-1]
  def today(self):
    return datetime.now().date() == self.data

class MenuNew(model.Model):
  nome = model.StringProperty()
  citta = model.KeyProperty(kind=Citta)

  validitaDa = model.DateProperty()
  validitaA = model.DateProperty()

  creato_da = model.KeyProperty(kind=models.User)
  creato_il = model.DateTimeProperty(auto_now_add=True)
  stato = model.IntegerProperty()

  _lock = threading.RLock()
  _menu_cache = dict()
  
  @classmethod
  def get_by(cls, citta_key, data):
    menu = None
    with MenuNew._lock:
      if citta_key in MenuNew._menu_cache:
        menu = MenuNew._menu_cache[citta_key]
        if not(menu.validitaDa <= data and menu.validitaDa >= data):
          menu = MenuNew.query().filter(MenuNew.citta == citta_key).filter(MenuNew.validitaDa <= data).order(-MenuNew.validitaDa).get()
          MenuNew._menu_cache[citta_key] = menu
      else:
        menu = MenuNew.query().filter(MenuNew.citta == citta_key).filter(MenuNew.validitaDa <= data).order(-MenuNew.validitaDa).get()
        MenuNew._menu_cache[citta_key] = menu
    return menu

class Piatto(model.Model):
  nome = model.StringProperty()
  calorie = model.IntegerProperty()
  proteine = model.IntegerProperty()
  grassi = model.IntegerProperty()
  carboidrati = model.IntegerProperty()
  gi = model.IntegerProperty()
    
  _pi_gi_cache = dict()
  @classmethod
  def get_by_menu_settimana(cls, menu, settimana):
    pi_gi = None
    if str(menu.key.id) + "-" + str(settimana) not in cls._pi_gi_cache:
      pi_gi = dict()
      for pg in PiattoGiorno.query().filter(PiattoGiorno.menu == menu.key).filter(PiattoGiorno.settimana == settimana ):
        if not pg.giorno in pi_gi:
          pi_gi[pg.giorno] = dict()
        pi_gi[pg.giorno][pg.tipo] = pg.piatto.get()
      cls._pi_gi_cache[str(menu.key.id) + "-" + str(settimana)] = pi_gi
    else:
      pi_gi = cls._pi_gi_cache[str(menu.key.id) + "-" + str(settimana)]
    return pi_gi
        
  @classmethod
  def get_by_menu_date_offset(cls, menu, date, offset):
    piatti = dict()
    for pg in PiattoGiorno.query().filter(PiattoGiorno.menu == menu.key).filter(PiattoGiorno.giorno == date.isoweekday()).filter(PiattoGiorno.settimana == (((((date-menu.validitaDa).days) / 7)+offset)%4 + 1) ):
      piatti[pg.tipo] = pg.piatto.get()
    return piatti

  @classmethod
  def get_by_date(cls, data):
    settimane = dict()  
    for pg in PiattoGiorno.query().filter(PiattoGiorno.giorno == data.isoweekday()):
      if not pg.settimana in settimane:
        settimane[pg.settimana] = dict()
      settimane[pg.settimana][pg.tipo] = pg.piatto.get()
    return settimane
  
  
  #creato_da = model.UserProperty(auto_current_user_add=True)
  #creato_il = model.DateTimeProperty(auto_now_add=True)
  #stato = model.IntegerProperty()
  
class Ingrediente(model.Model):
  nome = model.StringProperty()

  #creato_da = model.UserProperty(auto_current_user_add=True)
  #creato_il = model.DateTimeProperty(auto_now_add=True)
  #stato = model.IntegerProperty()

class PiattoIngrediente(model.Model):
  piatto = model.KeyProperty(kind=Piatto)
  ingrediente = model.KeyProperty(kind=Ingrediente)
  quantita = model.FloatProperty()
  
class PiattoGiorno(model.Model):
  menu = model.KeyProperty(kind=MenuNew)
  settimana = model.IntegerProperty()
  giorno = model.IntegerProperty()
  piatto = model.KeyProperty(kind=Piatto)
  tipo = model.StringProperty()

  #creato_da = model.UserProperty(auto_current_user_add=True)
  #creato_il = model.DateTimeProperty(auto_now_add=True)
  #stato = model.IntegerProperty()
  
class MenuHelper():
  primo = None
  secondo = None
  contorno = None
  dessert = None
  data = None
  giorno = None
  settimana = None

  #_giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì","Sabato", "Domenica"]
  _giorni = ["Lunedi'", "Martedi'", "Mercoledi'", "Giovedi'", "Venerdi'","Sabato", "Domenica"]
  def getData(self):
    return self._giorni[self.giorno-1]
  def today(self):
    return datetime.now().date() == self.data
  
  def to_dict(self):
    return {"data":str(self.data), "giorno": str(self.giorno), "settimana":self.getData(),
            "primo": self.primo.nome, "primo_key": str(self.primo.key),
            "secondo": self.secondo.nome, "secondo_key": str(self.secondo.key),
            "contorno": self.contorno.nome, "contorno_key": str(self.contorno.key),
            "dessert": self.dessert.nome, "dessert_key": str(self.dessert.key)}
  
  
class StatistichePiatto(model.Model):
  piatto = model.KeyProperty(kind=Piatto)
  citta = model.KeyProperty(kind=Citta)
  commissione = model.KeyProperty(kind=Commissione)
  centroCucina = model.KeyProperty(kind=CentroCucina)

  timePeriod = model.StringProperty() # W, M, Y
  timeId = model.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = model.DateProperty()
  dataFine = model.DateProperty()

  dataCalcolo = model.DateTimeProperty()

  numeroSchede = model.IntegerProperty(default=0) 
  numeroSchedeSettimana = model.IntegerProperty(repeated=True)

  cottura = model.IntegerProperty(repeated=True, indexed=False)
  temperatura = model.IntegerProperty(repeated=True, indexed=False)
  quantita = model.IntegerProperty(repeated=True, indexed=False)
  assaggio = model.IntegerProperty(repeated=True, indexed=False)
  gradimento = model.IntegerProperty(repeated=True, indexed=False)

  creato_il = model.DateTimeProperty(auto_now_add=True)
  modificato_il = model.DateTimeProperty(auto_now=True)
  stato = model.IntegerProperty()
  
class CommissioneCentroCucina(model.Model):
  commissione = model.KeyProperty(kind=Commissione)
  centroCucina = model.KeyProperty(kind=CentroCucina)
  validitaDa = model.DateProperty()
  validitaA = model.DateProperty()

class CentroCucinaZona(model.Model):
  centroCucina = model.KeyProperty(kind=CentroCucina)
  zona = model.IntegerProperty()
  validitaDa = model.DateProperty()
  validitaA = model.DateProperty()

class ZonaOffset(model.Model):
  zona = model.IntegerProperty()
  offset = model.IntegerProperty()
  validitaDa = model.DateProperty()
  validitaA = model.DateProperty()
  
class Ispezione(model.Model):
  def __init__(self, language='en', *args, **kwargs):
    self.allegati = None
    self.tags = list()
    super(Ispezione, self).__init__(*args, **kwargs)  
      
  commissione = model.KeyProperty(kind=Commissione)
  commissario = model.KeyProperty(kind=Commissario)
 
  dataIspezione = model.DateProperty()
  turno = model.IntegerProperty()

  aaRispettoCapitolato = model.IntegerProperty(indexed=False)
  aaTavoliApparecchiati = model.IntegerProperty(indexed=False)
  aaTermichePulite = model.IntegerProperty(indexed=False)
  aaAcqua = model.IntegerProperty(indexed=False)
  aaScaldaVivande = model.IntegerProperty(indexed=False)  
  aaSelfService = model.IntegerProperty(indexed=False)
  aaTabellaEsposta = model.IntegerProperty(indexed=False)
  
  ricicloStoviglie = model.IntegerProperty(indexed=False)
  ricicloPosate = model.IntegerProperty(indexed=False)
  ricicloBicchieri = model.IntegerProperty(indexed=False)

  numeroPastiTotale = model.IntegerProperty(indexed=False)
  numeroPastiBambini = model.IntegerProperty(indexed=False)
  numeroPastiSpeciali = model.IntegerProperty(indexed=False)
  numeroAddetti = model.IntegerProperty(indexed=False)

  puliziaCentroCottura = model.IntegerProperty(indexed=False)
  puliziaRefettorio = model.IntegerProperty(indexed=False)

  arrivoDist = model.IntegerProperty(indexed=False)

  primoDist = model.IntegerProperty(indexed=False)
  primoPrevisto = model.StringProperty(default="",indexed=False)
  primoEffettivo = model.StringProperty(default="",indexed=False)
  primoPiatto = model.KeyProperty(kind=Piatto,indexed=False)
  primoCondito = model.IntegerProperty(indexed=False)
  primoCottura = model.IntegerProperty(indexed=False)
  primoTemperatura = model.IntegerProperty(indexed=False)
  primoQuantita = model.IntegerProperty(indexed=False)
  primoAssaggio = model.IntegerProperty(indexed=False)
  primoGradimento = model.IntegerProperty(indexed=False)

  secondoDist = model.IntegerProperty(indexed=False)
  secondoPrevisto = model.StringProperty(default="",indexed=False)
  secondoEffettivo = model.StringProperty(default="",indexed=False)
  secondoPiatto = model.KeyProperty(kind=Piatto,indexed=False)
  secondoCottura = model.IntegerProperty(indexed=False)
  secondoTemperatura = model.IntegerProperty(indexed=False)
  secondoQuantita = model.IntegerProperty(indexed=False)
  secondoAssaggio = model.IntegerProperty(indexed=False)
  secondoGradimento = model.IntegerProperty(indexed=False)

  contornoPrevisto = model.StringProperty(default="",indexed=False)
  contornoEffettivo = model.StringProperty(default="",indexed=False)
  contornoPiatto = model.KeyProperty(kind=Piatto,indexed=False)
  contornoCondito = model.IntegerProperty(indexed=False)
  contornoCottura = model.IntegerProperty(indexed=False)
  contornoTemperatura = model.IntegerProperty(indexed=False)
  contornoQuantita = model.IntegerProperty(indexed=False)
  contornoAssaggio = model.IntegerProperty(indexed=False)
  contornoGradimento = model.IntegerProperty(indexed=False)

  paneTipo = model.StringProperty(indexed=False)
  paneServito = model.IntegerProperty(indexed=False)
  paneQuantita = model.IntegerProperty(indexed=False)
  paneAssaggio = model.IntegerProperty(indexed=False)
  paneGradimento = model.IntegerProperty(indexed=False)

  fruttaTipo = model.StringProperty(default="",indexed=False)
  fruttaServita = model.StringProperty(indexed=False)
  fruttaQuantita = model.IntegerProperty(indexed=False)
  fruttaAssaggio = model.IntegerProperty(indexed=False)
  fruttaGradimento = model.IntegerProperty(indexed=False)
  fruttaMaturazione = model.IntegerProperty(indexed=False)

  durataPasto = model.IntegerProperty(indexed=False)

  lavaggioFinale = model.IntegerProperty(indexed=False)
  smaltimentoRifiuti = model.IntegerProperty(indexed=False)
  giudizioGlobale = model.IntegerProperty(indexed=False)
  note = model.TextProperty(default="",indexed=False)

  anno = model.IntegerProperty()
  
  creato_il = model.DateTimeProperty(auto_now_add=True)
  creato_da = model.KeyProperty(kind=models.User)
  modificato_il = model.DateTimeProperty(auto_now=True)
  modificato_da = model.KeyProperty(kind=models.User)

  stato = model.IntegerProperty()
  
  def data(self): 
    return datetime.strftime(self.dataIspezione, Const.ACTIVITY_DATE_FORMAT)  

  @property
  def restype(self):
    return "isp"
  
  testi = { "assaggio": ["", "Non accettabile", "Accettabile", "Gradevole"], 
            "gradimento": ["", "Rifiutato", "Parz. rifiutato", "Parz. accettato", "Accettato"],
            "cottura": ["", "Scarsa", "Giusta", "Eccessiva"], 
            "temperatura": ["","Freddo", "Giusta", "Caldo"], 
            "maturazione": ["","Acerba", "Giusta", "Matura"], 
            "quantita": ["","Scarsa", "Sufficiente", "Abbondante"],
            "condito": ["","No", "Si"],
            "pulizia": ["","Scarso", "Mediocre", "Sufficiente", "Ottimo"],
            "distribuzione": ["","< 30 min.", "30 < 60 min.", "> 60 min."],
            "giudizio": ["","Insufficiente", "Sufficiente", "Buono"]
           }  
  cls = {   "assaggio": ["","label131", "label132", "label133"], 
            "gradimento": ["","label41", "label42", "label43", "label44"],
            "cottura": ["","label231", "label232", "label233"], 
            "temperatura": ["","label231", "label232", "label233"], 
            "maturazione": ["","label231", "label232", "label233"], 
            "quantita": ["","label131", "label132", "label133"],
            "condito": ["label232", ""],
            "pulizia": ["","label41", "label42", "label43", "label44"],
            "distribuzione": ["","label131", "label132", "label133"], 
            "giudizio": ["","label131", "label132", "label133"] 
        }  
  
  def sommario(self):
    sommario = ""
    sommario += '<i class="primo" title="Primo piatto"></i>' + '<span class="label labelbox ' + self.cls['assaggio'][self.primoAssaggio] + '" title="' + self.testi['assaggio'][self.primoAssaggio] + '">&nbsp;&nbsp;&nbsp;</span>' + '&nbsp;<span class="label labelbox ' + self.cls['gradimento'][self.primoGradimento] + '" title="' + self.testi['gradimento'][self.primoGradimento] + '">&nbsp;&nbsp;&nbsp;</span>'
    sommario += '<i class="secondo" title="Secondo piatto"></i>' + '<span class="label labelbox ' + self.cls['assaggio'][self.secondoAssaggio] + '" title="' + self.testi['assaggio'][self.secondoAssaggio] + '">&nbsp;&nbsp;&nbsp;</span>' + '&nbsp;<span class="label labelbox ' + self.cls['gradimento'][self.secondoGradimento] + '" title="' + self.testi['gradimento'][self.secondoGradimento] + '">&nbsp;&nbsp;&nbsp;</span>'
    sommario += '<i class="contorno" title="Contorno piatto"></i>' + '<span class="label labelbox ' + self.cls['assaggio'][self.contornoAssaggio] + '" title="' + self.testi['assaggio'][self.contornoAssaggio] + '">&nbsp;&nbsp;&nbsp;</span>' + '&nbsp;<span class="label labelbox ' + self.cls['gradimento'][self.contornoGradimento] + '" title="' + self.testi['gradimento'][self.contornoGradimento] + '">&nbsp;&nbsp;&nbsp;</span>'
    sommario += '<i class="pane" title="Pane piatto"></i>' + '<span class="label labelbox ' + self.cls['assaggio'][self.paneAssaggio] + '" title="' + self.testi['assaggio'][self.paneAssaggio] + '">&nbsp;&nbsp;&nbsp;</span>' + '&nbsp;<span class="label labelbox ' + self.cls['gradimento'][self.paneGradimento] + '" title="' + self.testi['gradimento'][self.paneGradimento] + '">&nbsp;&nbsp;&nbsp;</span>'
    sommario += '<i class="dessert" title="Dessert piatto"></i>' + '<span class="label labelbox ' + self.cls['assaggio'][self.paneAssaggio] + '" title="' + self.testi['assaggio'][self.fruttaAssaggio] + '">&nbsp;&nbsp;&nbsp;</span>' + '&nbsp;<span class="label labelbox ' + self.cls['gradimento'][self.fruttaGradimento] + '" title="' + self.testi['gradimento'][self.fruttaGradimento] + '">&nbsp;&nbsp;&nbsp;</span>'
      
    return sommario  
    
  @classmethod
  def get_last_by_cm(cls, cm_key):
    return Ispezione.query().filter(Ispezione.commissione == cm_key).order(-Ispezione.dataIspezione).get()
  
  @classmethod
  def get_by_cm_data_turno(cls, cm, data, turno):
    return Ispezione.query().filter(Ispezione.dataIspezione == data).filter(Ispezione.commissione == cm).filter(Ispezione.turno == turno)

  @classmethod
  def get_by_cm(cls, cm):
    return Ispezione.query().filter(Ispezione.commissione == cm).order(-Ispezione.dataIspezione)

  @cached_property
  def get_allegati(self): 
    if not self.allegati:
      self.allegati = list()
      if self.key:
        for allegato in Allegato.query().filter(Allegato.obj == self.key):
          self.allegati.append(allegato)
    return self.allegati

  @cached_property
  def has_allegati(self):
    return len(self.get_allegati) > 0
  
class Nonconformita(model.Model):
  def __init__(self, language='en', *args, **kwargs):
    self.allegati = None
    self.tags = list()
    super(Nonconformita, self).__init__(*args, **kwargs)  
  
  commissione = model.KeyProperty(kind=Commissione)
  commissario = model.KeyProperty(kind=Commissario)
 
  dataNonconf = model.DateProperty()
  turno = model.IntegerProperty()
  
  tipo = model.IntegerProperty()
  richiestaCampionatura = model.IntegerProperty()

  note = model.TextProperty(default="")

  anno = model.IntegerProperty()
  
  creato_il = model.DateTimeProperty(auto_now_add=True)
  creato_da = model.KeyProperty(kind=models.User)
  modificato_il = model.DateTimeProperty(auto_now=True)
  modificato_da = model.KeyProperty(kind=models.User)
  stato = model.IntegerProperty()
    
  @classmethod
  def get_by_cm(cls, cm):
    return Nonconformita.query().filter(Nonconformita.commissione == cm).order(-Nonconformita.dataNonconf)

  @classmethod
  def get_by_cm_data_turno(cls, cm, data, turno):
    return Nonconformita.query().filter(Nonconformita.dataNonconf == data).filter(Nonconformita.commissione == cm).filter(Nonconformita.turno == turno)
  
  def data(self): 
    return datetime.strftime(self.dataNonconf, Const.ACTIVITY_DATE_FORMAT)  

  def sommario(self):
    return self.tipoNome()

  @property
  def restype(self):
    return "nc"

  @cached_property
  def get_allegati(self): 
    if not self.allegati:
      self.allegati = list()
      if self.key:
        for allegato in Allegato.query().filter(Allegato.obj == self.key):
          self.allegati.append(allegato)
    return self.allegati

  @cached_property
  def has_allegati(self):
    return len(self.get_allegati) > 0
  
  _tipi_n = {1:0,
           2:1,
           3:2,
           4:3,
           5:4,
           6:5,
           7:6,
           8:7,
           9:8,
           10:9,
           11:10,
           12:11,
           99:12}

  _tipi = {1:"Cambiamenti di menu",
           2:"Cibo avanzato oltre 30%",
           3:"Quantita insufficiente di una vivanda",
           4:"Tavoli o apparecchiatura tavoli non adeguata",
           5:"Arredi e attrezzature inadeguate della sala di rigoverno",
           6:"Inadeguata pulizia dei locali",
           7:"Errata / mancata consegna o distribuzione delle diete speciali",
           8:"Ritardo o anticipo nella consegna delle termiche",
           9:"Corpo estraneo",
           10:"Temperatura non conforme alla legge",
           11:"Temperatura della dieta sanitaria giudicata inadeguata",
           12:"Inadeguato smaltimento della spazzatura",
           99:"Altro"}
  def tipi(self):
    return self._tipi
  
  def tipoNome(self):
    return self._tipi[self.tipo]

class Dieta(model.Model):
  def __init__(self, language='en', *args, **kwargs):
    self.allegati = None
    self.tags = list()
    super(Dieta, self).__init__(*args, **kwargs)  

  commissione = model.KeyProperty(kind=Commissione)
  commissario = model.KeyProperty(kind=Commissario)
 
  dataIspezione = model.DateProperty()
  turno = model.IntegerProperty()
  
  tipoDieta = model.IntegerProperty()
  etichettaLeggibile = model.IntegerProperty(indexed=False)
  temperaturaVaschetta = model.IntegerProperty(indexed=False)
  vicinoEducatore = model.IntegerProperty(indexed=False)
  vaschettaOriginale = model.IntegerProperty(indexed=False)
  condimentiVicini = model.IntegerProperty(indexed=False)
  primoAccettato = model.IntegerProperty(indexed=False)
  secondoAccettato = model.IntegerProperty(indexed=False)
  contornoAccettato = model.IntegerProperty(indexed=False)
  fruttaAccettata = model.IntegerProperty(indexed=False)
  gradimentoPrimo = model.IntegerProperty(indexed=False)
  gradimentoSecondo = model.IntegerProperty(indexed=False)
  gradimentoContorno = model.IntegerProperty(indexed=False)
  comunicazioneGenitori = model.IntegerProperty(indexed=False)

  note = model.TextProperty(default="")

  anno = model.IntegerProperty()
  
  creato_il = model.DateTimeProperty(auto_now_add=True)
  creato_da = model.KeyProperty(kind=models.User)
  modificato_il = model.DateTimeProperty(auto_now=True)
  modificato_da = model.KeyProperty(kind=models.User)
  stato = model.IntegerProperty()

  def data(self): 
    return datetime.strftime(self.dataIspezione, Const.ACTIVITY_DATE_FORMAT)  

  def sommario(self):
    return self.tipoNome()
  
  @property
  def restype(self):
    return "dieta"
  
  @classmethod
  def get_by_cm_data_turno_tipo(cls, cm, data, turno, tipo):
    return Dieta.query().filter(Dieta.dataIspezione==data).filter(Dieta.commissione==cm).filter(Dieta.turno==turno).filter(Dieta.tipoDieta==tipo)

  @classmethod
  def get_by_cm(cls, cm):
    return Dieta.query().filter(Dieta.commissione == cm).order(-Dieta.dataIspezione)

  @cached_property
  def get_allegati(self): 
    if not self.allegati:
      self.allegati = list()
      if self.key:
        for allegato in Allegato.query().filter(Allegato.obj == self.key):
          self.allegati.append(allegato)
    return self.allegati

  @cached_property
  def has_allegati(self):
    return len(self.get_allegati) > 0
  
  _tipi_n = {1:0,
           2:1,
           3:2,
           4:3,
           5:4,
           6:5,
           7:6,
           8:7,
           9:8,
           10:9,
           11:10,
           12:11,
           13:12,
           14:13,
           15:14,
           16:15,
           17:16,
           18:17,
           19:18,
           20:19,
           21:20,
           22:21,
           23:22,
           24:23}

  _tipi = {1:"menu privo di fave e piselli",
           2:"menu privo di cereali contenenti glutine",
           3:"menu privo di proteine del latte",
           4:"menu privo di uovo",
           5:"menu privo di pesce, molluschi e crostacei",
           6:"menu privo di proteine del latte, e uova",
           7:"menu privo di solanacee",
           8:"menu privo di frutta a guscio, pinoli, lupini, semi di sesamo",
           9:"menu privo di legumi, soia,arachidi",
           10:"menu a ridotto apporto di sostanze istamino-liberatrici",
           11:"menu ridotto in nichel",
           12:"menu privo di tutti gli allergeni (D.L.vo n.114/ 06)",
           13:"esclusione di sola frutta",
           14:"menu diabete e/o ipocalorico",
           15:"menu ipolipidico",
           16:"menu iposodico",
           17:"menu tritato / frullato",
           18:"menu per stipsi (nido)",
           19:"menu privo di carni bianche",
           20:"menu privo di carne suina",
           21:"menu privo di tutte le carni",
           22:"menu privo di carni bovine e suine",
           23:"menu privo di carni di origine animale",
           24:"menu privo di carne e pesce"}
  
  @classmethod
  def tipi(cls):
    return cls._tipi
  
  def tipoNome(self):
    return self._tipi[self.tipoDieta]

class Nota(model.Model):
  def __init__(self, *args, **kwargs):
    #logging.info("__init__")
    self.allegati = None
    self.tags = list()
    super(Nota, self).__init__(*args, **kwargs)  
      
  commissione = model.KeyProperty(kind=Commissione)
  commissario = model.KeyProperty(kind=Commissario)
 
  dataNota = model.DateProperty()
  titolo = model.StringProperty(default="")
  note = model.TextProperty(default="")
  anno = model.IntegerProperty()
    
  creato_il = model.DateTimeProperty(auto_now=True)
  creato_da = model.KeyProperty(kind=models.User)
  modificato_il = model.DateTimeProperty(auto_now=True)
  modificato_da = model.KeyProperty(kind=models.User)
  stato = model.IntegerProperty()
  
  def data(self): 
    return datetime.strftime(self.dataNota, Const.ACTIVITY_DATE_FORMAT)  

  def sommario(self):
    return self.titolo

  @property
  def restype(self):
    return "nota"
  
  @cached_property
  def notefmt(self):
    if "<p>" in self.note:
      return self.note
    else:
      return self.note.replace("\n","<br/>")
  
  @cached_property
  def get_allegati(self): 
    if not self.allegati:
      self.allegati = list()
      if self.key:
        for allegato in Allegato.query().filter(Allegato.obj == self.key):
          self.allegati.append(allegato)
    return self.allegati

  @cached_property
  def has_allegati(self):
    return len(self.get_allegati) > 0

  @classmethod
  def get_by_cm(cls, cm):
    return Nota.query().filter(Nota.commissione == cm).order(-Nota.dataNota)
  
class Allegato(model.Model):
  obj = model.KeyProperty()
  path = model.StringProperty()
  blob_key = model.BlobKeyProperty()
  nome = model.StringProperty(default="")
  descrizione = model.StringProperty(default="",indexed=False)
  
  dati=None

  @classmethod
  def _pre_delete_hook_1(cls, key):
    blobstore.delete(key.get().blob_key)

  @classmethod
  def get_by_obj(cls, obj):
    return cls.query().filter(Allegato.obj==obj)
  
  def isImage(self):
    return ".png" in self.nome.lower() or ".gif" in ".png" in self.nome.lower() or ".jpg" in self.nome.lower() or ".jpeg" in self.nome.lower()

  def contentType(self):
    return self._tipi[self.nome.lower()[self.nome.rfind("."):]]
  
  def imgthumb(self):
    if self.isImage():
      return google.appengine.api.images.get_serving_url(blob_key=self.blob_key,size=128)

  def path(self):
    return "/blob/get?key=" + str(self.blob_key)
    
  _tipi = {".png":"image/png",
           ".jpg":"image/jpeg",
           ".jpeg":"image/jpeg",
           ".gif":"image/gif",
           ".tif":"image/tiff",
           ".tiff":"image/tiff",           
           ".pdf":"application/pdf",
           ".doc":"application/msword",
           ".pdf":"application/msword"}
  
class Statistiche:
  anno1 = int(0)
  anno2 = int(0)
  numeroCommissioni = int(0)
  numeroSchede = int(0) 
  ncTotali = int(0)
  diete = int(0)  
  note = int(0)  

class StatisticheIspezioni(model.Model):
  citta = model.KeyProperty(kind=Citta)
  commissione = model.KeyProperty(kind=Commissione)
  centroCucina = model.KeyProperty(kind=CentroCucina)

  timePeriod = model.StringProperty() # W, M, Y
  timeId = model.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = model.DateProperty()
  dataFine = model.DateProperty()

  dataCalcolo = model.DateTimeProperty()

  numeroSchede = model.IntegerProperty(default=0,indexed=False) 
  numeroSchedeSettimana = model.IntegerProperty(repeated=True,indexed=False)

  ambiente_names = {"aaRispettoCapitolato":0,"aaTavoliApparecchiati":1,"aaTermichePulite":2,"aaAcqua":3, "aaScaldaVivande":4, "aaSelfService":5, "aaTabellaEsposta":6, "ricicloStoviglie":7, "ricicloPosate":8, "ricicloBicchieri":9}
  ambiente_desc = ["Rispetto Capitolato","Tavoli Apparecchiati","Termiche Pulite","Acqua da cucina", "Scalda Vivande", "Self Service", "Tabella Dietetica Esposta", "Riciclo Stoviglie", "Riciclo Posate", "Riciclo Bicchieri"]
  ambiente = model.IntegerProperty(repeated=True,indexed=False)
  arrivoDist = model.IntegerProperty(repeated=True,indexed=False)
  durataPasto = model.IntegerProperty(repeated=True,indexed=False)

  numeroPastiTotale = model.IntegerProperty(indexed=False)
  numeroPastiBambini = model.IntegerProperty(indexed=False)
  numeroPastiSpeciali = model.IntegerProperty(indexed=False)
  numeroAddetti = model.IntegerProperty(indexed=False)
  
  puliziaRefettorio = model.IntegerProperty(repeated=True,indexed=False)
  puliziaCentroCottura = model.IntegerProperty(repeated=True,indexed=False)
  smaltimentoRifiuti = model.IntegerProperty(repeated=True,indexed=False)

  giudizioGlobale = model.IntegerProperty(repeated=True,indexed=False)
  
  primoCondito = model.IntegerProperty(repeated=True,indexed=False)
  primoDist = model.IntegerProperty(repeated=True,indexed=False)
  primoCottura = model.IntegerProperty(repeated=True,indexed=False)
  primoTemperatura = model.IntegerProperty(repeated=True,indexed=False)
  primoQuantita = model.IntegerProperty(repeated=True,indexed=False)
  primoAssaggio = model.IntegerProperty(repeated=True,indexed=False)
  primoGradimento = model.IntegerProperty(repeated=True,indexed=False)

  secondoDist = model.IntegerProperty(repeated=True,indexed=False)
  secondoCottura = model.IntegerProperty(repeated=True,indexed=False)
  secondoTemperatura = model.IntegerProperty(repeated=True,indexed=False)
  secondoQuantita = model.IntegerProperty(repeated=True,indexed=False)
  secondoAssaggio = model.IntegerProperty(repeated=True,indexed=False)
  secondoGradimento = model.IntegerProperty(repeated=True,indexed=False)
  
  contornoCondito = model.IntegerProperty(repeated=True,indexed=False)
  contornoCottura = model.IntegerProperty(repeated=True,indexed=False)
  contornoTemperatura = model.IntegerProperty(repeated=True,indexed=False)
  contornoQuantita = model.IntegerProperty(repeated=True,indexed=False)
  contornoAssaggio = model.IntegerProperty(repeated=True,indexed=False)
  contornoGradimento = model.IntegerProperty(repeated=True,indexed=False)

  paneQuantita = model.IntegerProperty(repeated=True,indexed=False)
  paneAssaggio = model.IntegerProperty(repeated=True,indexed=False)
  paneGradimento = model.IntegerProperty(repeated=True,indexed=False)
  paneServito = model.IntegerProperty(repeated=True,indexed=False)
  
  fruttaMaturazione = model.IntegerProperty(repeated=True,indexed=False)
  fruttaQuantita = model.IntegerProperty(repeated=True,indexed=False)
  fruttaAssaggio = model.IntegerProperty(repeated=True,indexed=False)
  fruttaGradimento = model.IntegerProperty(repeated=True,indexed=False)

  @classmethod
  def get_cy_cc_cm_time(cls, cy = None, cc = None, cm = None, timeId=None):
    q = StatisticheIspezioni.query().filter(StatisticheIspezioni.citta==cy).filter(StatisticheIspezioni.commissione==cm).filter(StatisticheIspezioni.centroCucina==cc)
    if timeId:
      q = q.filter(StatisticheIspezioni.timeId == timeId)
    return q
  
  @classmethod
  def get_from_date(cls, data):
    return StatisticheIspezioni.query().filter(StatisticheIspezioni.dataInizio >= data)

  @classmethod
  def get_from_year(cls, year):
    return StatisticheIspezioni.query().filter(StatisticheIspezioni.timeId == year)
  
  def primoAssaggioNorm(self):
    return fpformat.fix(float(self.primoAssaggio[0]+self.primoAssaggio[1]+self.primoAssaggio[2]-self.numeroSchede)/2*100/self.numeroSchede,2)
  def primoGradimentoNorm(self):
    return float(self.primoGradimento[0]+self.primoGradimento[1]+self.primoGradimento[2]+self.primoGradimento[3]-self.numeroSchede)/3*100/self.numeroSchede
  def secondoAssaggioNorm(self):
    return float(self.secondoAssaggio[0]+self.secondoAssaggio[1]+self.secondoAssaggio[2]-self.numeroSchede)/2*100/self.numeroSchede
  def secondoGradimentoNorm(self):
    return float(self.secondoGradimento[0]+self.secondoGradimento[1]+self.secondoGradimento[2]+self.secondoGradimento[3]-self.numeroSchede)/3*100/self.numeroSchede
  def contornoAssaggioNorm(self):
    return float(self.contornoAssaggio[0]+self.contornoAssaggio[1]+self.contornoAssaggio[2]-self.numeroSchede)/2*100/self.numeroSchede
  def contornoGradimentoNorm(self):
    return float(self.contornoGradimento[0]+self.contornoGradimento[1]+self.contornoGradimento[2]+self.contornoGradimento[3]-self.numeroSchede)/3*100/self.numeroSchede
  def paneAssaggioNorm(self):
    return float(self.paneAssaggio[0]+self.paneAssaggio[1]+self.paneAssaggio[2]-self.numeroSchede)/2*100/self.numeroSchede
  def paneGradimentoNorm(self):
    return float(self.paneGradimento[0]+self.paneGradimento[1]+self.paneGradimento[2]+self.paneGradimento[3]-self.numeroSchede)/3*100/self.numeroSchede
  def fruttaAssaggioNorm(self):
    return float(self.fruttaAssaggio[0]+self.fruttaAssaggio[1]+self.fruttaAssaggio[2]-self.numeroSchede)/2*100/self.numeroSchede
  def fruttaGradimentoNorm(self):
    return float(self.fruttaGradimento[0]+self.fruttaGradimento[1]+self.fruttaGradimento[2]+self.fruttaGradimento[3]-self.numeroSchede)/3*100/self.numeroSchede
  def giudizioGlobaleNorm(self):
    return float(self.giudizioGlobale[0]+self.giudizioGlobale[1]+self.giudizioGlobale[2]-self.numeroSchede)/2*100/self.numeroSchede
  def puliziaRefettorioNorm(self):
    return float(self.puliziaRefettorio[0]+self.puliziaRefettorio[1]+self.puliziaRefettorio[2]+self.puliziaRefettorio[3]-self.numeroSchede)/3*100/self.numeroSchede
  def smaltimentoRifiutiNorm(self):
    return float(self.smaltimentoRifiuti[0]+self.puliziaRefettorio[1]+self.puliziaRefettorio[2]+self.puliziaRefettorio[3]-self.numeroSchede)/3*100/self.numeroSchede

  def primoQuantita1Norm(self):
    return float(self.primoQuantita[0])*100/self.numeroSchede
  def primoQuantita2Norm(self):
    return float(self.primoQuantita[1])*100/self.numeroSchede/2
  def primoQuantita3Norm(self):
    return float(self.primoQuantita[2])*100/self.numeroSchede/3
  def primoCottura1Norm(self):
    return float(self.primoCottura[0])*100/self.numeroSchede
  def primoCottura2Norm(self):
    return float(self.primoCottura[1])*100/self.numeroSchede/2
  def primoCottura3Norm(self):
    return float(self.primoCottura[2])*100/self.numeroSchede/3
  def primoTemperatura1Norm(self):
    return float(self.primoTemperatura[0])*100/self.numeroSchede
  def primoTemperatura2Norm(self):
    return float(self.primoTemperatura[1])*100/self.numeroSchede/2
  def primoTemperatura3Norm(self):
    return float(self.primoTemperatura[2])*100/self.numeroSchede/3

  def secondoQuantita1Norm(self):
    return float(self.secondoQuantita[0])*100/self.numeroSchede
  def secondoQuantita2Norm(self):
    return float(self.secondoQuantita[1])*100/self.numeroSchede/2
  def secondoQuantita3Norm(self):
    return float(self.secondoQuantita[2])*100/self.numeroSchede/3
  def secondoCottura1Norm(self):
    return float(self.secondoCottura[0])*100/self.numeroSchede
  def secondoCottura2Norm(self):
    return float(self.secondoCottura[1])*100/self.numeroSchede/2
  def secondoCottura3Norm(self):
    return float(self.secondoCottura[2])*100/self.numeroSchede/3
  def secondoTemperatura1Norm(self):
    return float(self.secondoTemperatura[0])*100/self.numeroSchede
  def secondoTemperatura2Norm(self):
    return float(self.secondoTemperatura[1])*100/self.numeroSchede/2
  def secondoTemperatura3Norm(self):
    return float(self.secondoTemperatura[2])*100/self.numeroSchede/3

  def contornoQuantita1Norm(self):
    return float(self.contornoQuantita[0])*100/self.numeroSchede
  def contornoQuantita2Norm(self):
    return float(self.contornoQuantita[1])*100/self.numeroSchede/2
  def contornoQuantita3Norm(self):
    return float(self.contornoQuantita[2])*100/self.numeroSchede/3
  def contornoCottura1Norm(self):
    return float(self.contornoCottura[0])*100/self.numeroSchede
  def contornoCottura2Norm(self):
    return float(self.contornoCottura[1])*100/self.numeroSchede/2
  def contornoCottura3Norm(self):
    return float(self.contornoCottura[2])*100/self.numeroSchede/3
  def contornoTemperatura1Norm(self):
    return float(self.contornoTemperatura[0])*100/self.numeroSchede
  def contornoTemperatura2Norm(self):
    return float(self.contornoTemperatura[1])*100/self.numeroSchede/2
  def contornoTemperatura3Norm(self):
    return float(self.contornoTemperatura[2])*100/self.numeroSchede/3

  def paneQuantita1Norm(self):
    return float(self.paneQuantita[0])*100/self.numeroSchede
  def paneQuantita2Norm(self):
    return float(self.paneQuantita[1])*100/self.numeroSchede/2
  def paneQuantita3Norm(self):
    return float(self.paneQuantita[2])*100/self.numeroSchede/3
  
  def fruttaQuantita1Norm(self):
    return float(self.fruttaQuantita[0])*100/self.numeroSchede
  def fruttaQuantita2Norm(self):
    return float(self.fruttaQuantita[1])*100/self.numeroSchede/2
  def fruttaQuantita3Norm(self):
    return float(self.fruttaQuantita[2])*100/self.numeroSchede/3
  def fruttaMaturazione1Norm(self):
    return float(self.fruttaMaturazione[0])*100/self.numeroSchede
  def fruttaMaturazione2Norm(self):
    return float(self.fruttaMaturazione[1])*100/self.numeroSchede/2
  def fruttaMaturazione3Norm(self):
    return float(self.fruttaMaturazione[2])*100/self.numeroSchede/3
  
  def getNome(self):
    if self.centroCucina:
      return self.centroCucina.get().nome
    elif self.commissione:
      return self.commissione.get().nome
    else:
      return "Tutte"
    
  def incVal(self, attrname, attrbase, isp):
    attr_stat = getattr(self,attrname)
    attr_isp = getattr(isp,attrname)
    #logging.info("attr_name: " + attrname + " attr_isp: " + str(attr_isp))
    if attr_isp:
      attr_stat[attr_isp-attrbase] += attr_isp

  def incValSub(self, attrname, subattr, isp):
    attr_stat = getattr(self,attrname)
    attr_index = getattr(self,attrname+"_names")[subattr]
    attr_isp = getattr(isp,subattr)

    while len(attr_stat) <= (attr_index):
      attr_stat.append(0)

    attr_stat[attr_index] += attr_isp
    
  def getVals(self, attrname):
    attr = getattr(self,attrname)
    return attr

  def getVal(self, attrname, voto):
    attr = getattr(self,attrname)
    base = self._attrs[attrname][0]
    if len(attr) <= voto-base:
      return 0
    else:
      return attr[voto-base]

  def getNormVal(self, attrname, voto):
    attr = getattr(self,attrname)
    return attr[voto-1] * 100 / voto
      
  def getNormValMedia(self, attrname):
    attr = getattr(self,attrname)
    value = 0
    for v in attr:
      val += v 
    return val * 100 / len(attr)

  _attrs = {"puliziaCentroCottura": [1,4],
             "puliziaRefettorio": [1,4],
             "arrivoDist": [1,3],
             "primoDist": [1,3],
             "primoCondito": [0,2],
             "primoCottura": [1,3],
             "primoTemperatura": [1,3],
             "primoQuantita": [1,3],
             "primoAssaggio": [1,3],
             "primoGradimento": [1,4],
             "secondoDist": [1,3],
             "secondoCottura": [1,3],
             "secondoTemperatura": [1,3],
             "secondoQuantita": [1,3],
             "secondoAssaggio": [1,3],
             "secondoGradimento": [1,4],
             "contornoCondito": [0,2],
             "contornoCottura": [1,3],
             "contornoTemperatura": [1,3],
             "contornoQuantita": [1,3],
             "contornoAssaggio": [1,3],
             "contornoGradimento": [1,4],
             "paneServito": [0,2],
             "paneQuantita": [1,3],
             "paneAssaggio": [1,3],
             "paneGradimento": [1,4],
             "fruttaQuantita": [1,3],
             "fruttaAssaggio": [1,3],
             "fruttaGradimento": [1,4],
             "fruttaMaturazione": [1,3],
             "durataPasto": [1,3],
             "smaltimentoRifiuti": [1,4],
             "giudizioGlobale": [1,3]}
  _attrs_sub = ["ambiente"]
  
  def init(self):
    for attr, base_size in self._attrs.iteritems():
      attr_stat = getattr(self,attr)
      while len(attr_stat) < base_size[1]:
        attr_stat.append(0)              
    
  def calc(self, isp):  
    for attr, base_size in self._attrs.iteritems():
      self.incVal(attr, base_size[0], isp)
    for attr in self._attrs_sub:
      for attr_sub in getattr(self, attr+"_names"):
        self.incValSub(attr, attr_sub, isp)
        
class SocialNode(model.Model):
    name = model.StringProperty(default="")
    description = model.TextProperty(default="",indexed=False)
    active = model.BooleanProperty(default=True)
    founder = model.KeyProperty(default=None)

    default_post = model.BooleanProperty(default=True,indexed=False)
    default_comment = model.BooleanProperty(default=True,indexed=False)
    default_admin = model.BooleanProperty(default=False,indexed=False)

    last_act = model.DateTimeProperty(auto_now=True)

    #latest_activity = model.DateTimeProperty(auto_now="")
    #latest_post = model.KeyProperty(kind="SocialPost")

    resource = model.KeyProperty(repeated=True)
    res_type = model.StringProperty(repeated=True)
    
    created = model.DateTimeProperty(auto_now=True)
    rank = model.IntegerProperty()
    
    @classmethod
    def get_nodes_by_resource(cls,res_key):
      nodes=SocialNode.query().filter(SocialNode.resource==res_key).fetch()
      return nodes

    @classmethod
    def get_most_recent(cls):
      cache = Cache.get_cache("SocialNode")
      nodes = cache.get('most-recent')
      if not nodes:
        nodes = list()
        for n in SocialNode.query().order(-SocialNode.created).fetch():
            nodes.append(n)
            if len(nodes) >= 50:
                break
        cache.put('most-recent', nodes)
      return nodes

    @classmethod
    def get_most_active(cls):
      cache = Cache.get_cache("SocialNode")
      nodes = cache.get('most-actives')
      if not nodes:
        nodes = list()
        for n in SocialNode.query().order(-SocialNode.rank).fetch():
            nodes.append(n)
            if len(nodes) >= 50:
                break
        cache.put('most-actives', nodes)
      
      return nodes

    @cached_property
    def subscriptions(self):
      subs = dict()
      for s in SocialNodeSubscription.query(ancestor=self.key).fetch():
        subs[s.user] = s
      return subs

    def init_rank(self):
      init_rank = datetime.now() - Const.BASE_RANK
      self.rank = init_rank.seconds + (init_rank.days*Const.DAY_SECONDS)
      
    def calc_rank(self, activity):
      values = {SocialPost: 10,
                SocialComment: 7,
                Vote: 3 }
      now = datetime.now()
      if self.last_act is None:
        self.last_act = now
      delta = now - self.last_act
      delta_rank = delta.seconds + (delta.days*Const.DAY_SECONDS)
      self.rank += ((delta_rank * values[activity]) / 10)
        
    def _post_put_hook(self, future):
      Cache.get_cache("SocialPost").clear_all()
      Cache.get_cache("UserStream").clear_all()
      
      node=future.get_result().get()
      doc=search.Document(
                      doc_id='node-'+node.key.urlsafe(),
                      fields=[search.TextField(name='name', value=node.name),
                              search.HtmlField(name='description', value=node.description)],
                      language='it')
      
     
      index = search.Index(name='index-nodes',
                   consistency=search.Index.PER_DOCUMENT_CONSISTENT)
      try:
          index.put(doc)
      
      except search.Error, e:
          pass

    def _pre_delete_hook_1(cls, key):
        
        index = search.Index(name='index-nodes',
                     consistency=search.Index.PER_DOCUMENT_CONSISTENT)
        try:
            index.delete('node-'+key.urlsafe())
        
        except search.Error, e:
            pass

    @classmethod
    def active_nodes(cls):
           return cls.query().filter(cls.active==True)
        
              
    def __init__(self, *args, **kwargs):
        super(SocialNode, self).__init__(*args, **kwargs) 
        
    def create_open_post(self, author, title, content, resources=[], res_types=[]):
        floodControl=memcache.get("FloodControl-"+str(author.key))
        if floodControl:
          raise base.FloodControlException
        
        new_post= SocialPost(parent=self.key)
        new_post.author=author.key
        new_post.content=content
        new_post.title=title
        new_post.resource=resources
        new_post.res_type=res_types
        new_post.init_rank()
        new_post.put()
        self.last_act=new_post.created
        self.calc_rank(SocialPost)
        self.put()
        comm=Commissario.get_by_user(author)
        new_post.subscribe_user(author)
        
        #SocialNotification.create(source_key=self.key,author_key=author.key,type="new_post",target_key=new_post.key,author=comm.nome+" "+comm.cognome)
        
        SocialEvent.create(type="post", target_key=self.key, source_key=new_post.key, user_key=author.key)
        
        if Const.FLOOD_SYSTEM_ACTIVATED:       
          memcache.add("FloodControl-"+str(author.key), datetime.now(),time=Const.SOCIAL_FLOOD_TIME)
        return new_post.key
        
        
    def delete_post(self,post):
        sub=SocialPostSubscription.query(ancestor=post.key).get()
        if sub:
            sub.key.delete()
        #delete comment notifications
        model.delete_multi(model.put_multi(SocialNotification.query(ancestor=post.key)))
        #delete post notifications
        model.delete_multi(model.put_multi(SocialNotification.query(ancestor=post.key.parent()).filter(SocialNotification.source_key==post.key)))
        #delete comments
        model.delete_multi(model.put_multi(SocialComment.query(ancestor=post.key)))
        post.key.delete()
           
        
    def set_position(self,lat,lon):
        self.geo=model.GeoPt(lat,lon)
        self.put()
    
    def get_latest_posts(self,amount):
        
        posts= SocialPost.query(ancestor=self.key).order(-SocialPost.created).fetch(amount)
        return posts    
        
    def subscribe_user(self,current_user):
        #user has already subscribed to this node
        if SocialNodeSubscription.query( SocialNodeSubscription.user==current_user.key,ancestor=self.key).count()>0:
            return
        
        user1 = SocialNodeSubscription(parent=self.key)
        if current_user:
            user1.user=current_user.key
        else:
            raise users.UserNotFoundError
        
        #user1.put()
               
        user1.init_perm()
    
        Cache.get_cache("SocialNodeSubscription").clear("UserNodeSubscription-" + str(current_user.key.id))
        return user1
    
    def unsubscribe_user(self, current_user):
         subscription=SocialNodeSubscription.query( SocialNodeSubscription.user==current_user.key,ancestor=self.key).get()
         if subscription is not None:
            subscription.key.delete()
            Cache.get_cache("SocialNodeSubscription").clear("UserNodeSubscription-" + str(current_user.key.id))
                    
         else:
             raise users.UserNotFoundError
            
    def is_user_subscribed(self,user_t):
        if SocialNodeSubscription.query(ancestor=self.key).filter(SocialNodeSubscription.user==user_t.key).count()>0:
            return True
        else:
            return False
          
    def get_subscription(self,user_t):
        return SocialNodeSubscription.query(ancestor=self.key).filter(SocialNodeSubscription.user==user_t.key).get()
        
        
    def subscription_list(self,amount):
       q=SocialNodeSubscription.query(ancestor=self.key).order(-SocialNodeSubscription.starting_date).fetch(amount)
       q=[i.user.get() for i in q if (i.user is not None)]
       return q
    
    def delete_subscription(self,user_t):
        SocialNodeSubscription.query(SocialNodeSubscription.user==user_t,ancestor=self.key).get().key.delete()
        

    def permission_for_edit(self, permission):
        perm=getattr(self,"default_"+permission)
        if perm is True: 
            return "<option selected value='True'>S&igrave;</option>\n<option value='False'>No</option>"
        
        else:
            return "<option selected value='True'>S&igrave;</option>\n<option selected value='False'>No</option>"
    
    def get_latest_post(self):
        last_post=memcache.get("last_post_"+str(self.key.id()))
        if not last_post:
            last_post=SocialPost.query(ancestor=self.key).order(-SocialPost.created).fetch(1)
            memcache.add("last_post_"+str(self.key.id()),last_post)
        return last_post
    
    @classmethod    
    def get_all_cursor(cls, cursor):
        if cursor and cursor != "":
          return SocialNode.active_nodes().order(SocialNode.name).iter(start_cursor=Cursor.from_websafe_string(cursor), produce_cursors=True);
        else:
          return SocialNode.active_nodes().order(SocialNode.name).iter(produce_cursors=True)

    @classmethod    
    def get_active_cursor(cls, cursor):
        if cursor and cursor != "":
          return SocialNode.active_nodes().filter().iter(start_cursor=Cursor.from_websafe_string(cursor), produce_cursors=True)
        else:
          return SocialNode.active_nodes().filter().iter(produce_cursors=True)
    
   
   
class SocialPost(model.Model):
    def __init__(self, *args, **kwargs):
      self._comments = None
      super(SocialPost, self).__init__(*args, **kwargs)  
  
    author = model.KeyProperty(kind=models.User)
    title = model.StringProperty(default="")
    content = model.TextProperty(default="")
    #public_reference=model.StringProperty(default="")
    resource=model.KeyProperty(repeated=True)
    res_type=model.StringProperty(repeated=True)
    
    created = model.DateTimeProperty(auto_now=True)
    modified = model.DateTimeProperty(auto_now=True)
    
    comments = model.IntegerProperty(default=0)
    last_act = model.DateTimeProperty(auto_now=True)
    
    rank = model.IntegerProperty(default=0)
    
    def extended_date(self):
      delta = datetime.now() - self.created
      if delta.days == 0 and delta.seconds < 3600:
        return str(delta.seconds / 60) + " minuti fa"
      elif delta.days == 0 and delta.seconds < 3600*24:
        return str(delta.seconds / 3600) + " ore fa"
      else:
        return "il " + datetime.strftime(self.created, Const.ACTIVITY_DATE_FORMAT + " alle " + Const.ACTIVITY_TIME_FORMAT)
      
    @cached_property
    def comment_list(self):
      comment_list = list()
      for comment in SocialComment.query(ancestor=self.key).order(SocialComment.created).fetch():
        comment_list.append(comment)          
      return comment_list
    
    def reset_comment_list(self):
      self.comment_list = None
    
    def get_comments_text(self):
      text = ""
      for c in self.comment_list:
        text += c.content + " "
      return text
    
    def get_by_resource(self, res):
      return SocialPost.query().filter(SocialPost.resource==res).fetch()
          
    @cached_property
    def commissario(self):
      return Commissario.get_by_user(self.author.get())

    @cached_property
    def votes(self):
      votes = list()
      for v in Vote.get_by_ref(self.key):
        votes.append(v)
      return votes

    @cached_property
    def reshares(self):
      reshares = list()
      for p in self.get_by_resource(self.key):
        reshares.append(p)
      return reshares

    @cached_property
    def attachments(self):
      attachments = list()
      for attach in Allegato.query().filter(Allegato.obj == self.key):
        attachments.append(attach)
      return attachments
    
    def can_admin(self, user):
      sub_cache = Cache.get_cache('SocialNodeSubscription')
      cache_key = str(self.key.parent().id) + "-" + str(user.key.id)
      sub = sub_cache.get(cache_key)
      if not sub:
        sub = SocialNodeSubscription.query(ancestor=self.key.parent()).filter(SocialNodeSubscription.user==user.key).get()
        sub_cache.put(cache_key, sub)
      return sub and (sub.can_admin or self.author == user.key)

    def can_comment(self, user):
      sub_cache = Cache.get_cache('SocialNodeSubscription')
      cache_key = str(self.key.parent().id) + "-" + str(user.key.id)
      sub = sub_cache.get(cache_key)
      if not sub:
        sub = SocialNodeSubscription.query(ancestor=self.key.parent()).filter(SocialNodeSubscription.user==user.key).get()
        sub_cache.put(cache_key, sub)
      return sub.can_comment or self.author == user.key

    @cached_property
    def subscriptions(self):
      subs = dict()
      for s in SocialPostSubscription.query(ancestor=self.key).fetch():
        subs[s.user] = s
      return subs
      
    def can_sub(self, user):
      return (self.subscriptions.get(user.key) is None)
          
    def remove_attachment(self, attach_key):
      attach_key.delete()
      self.clear_attachments()

    def clear_attachments(self):
      self.attachments = None

    @classmethod
    def get_by_node_rank(cls, node, page, start_cursor=None):
      cache = Cache.get_cache("SocialPost")
      cache_key = "SocialPost-" + str(node.id) + "-" + str(start_cursor)
      postlist = cache.get(cache_key)
      next_cursor = cache.get(cache_key + "-next_cursor")
      more = cache.get(cache_key + "-more")
      if not postlist:
        postlist = list()
        posts, next_cursor, more = SocialPost.query(ancestor=node).order(-SocialPost.rank).fetch_page(page, start_cursor=start_cursor)
        postlist = [p for p in posts]
        cache.put(cache_key, postlist)
        cache.put(cache_key + "-next_cursor", next_cursor)
        cache.put(cache_key + "-more", more)
      return postlist, next_cursor, more
    
    @classmethod
    def get_user_stream(cls, user, page, start_cursor=None):
      cache =  Cache.get_cache("UserStream")
      cache_key = "UserStream-" + str(user.key.id) + "-" + str(start_cursor)
      stream = cache.get(cache_key)
      next_cursor = cache.get(cache_key + "-next_cursor")
      if not stream:
        stream = list()        
        next_cursor = int(start_cursor if start_cursor else 0) + 1
        #logging.info("next_cursor:" + str(next_cursor))
        for node in SocialNodeSubscription.get_nodes_keys_by_user(user):
          next_cursor_rank = None
          for x in range(0, next_cursor):
            postlist, next_cursor_rank, more = SocialPost.get_by_node_rank(node, page=page, start_cursor=next_cursor_rank)
            #logging.info("node: " + node.get().name + " offset: " + str(x) + " postlist: " + str(len(postlist)) + " more: " + str(more))       
            stream.extend(postlist)
            if not more:
              break
        
        stream = sorted(stream, key=lambda post: post.rank, reverse=True)
        offset = int(start_cursor if start_cursor else 0)
        #logging.info("offset: " + str(offset))
        stream = stream[offset*Const.ACTIVITY_FETCH_LIMIT : (offset+1)*Const.ACTIVITY_FETCH_LIMIT]
        cache.put(cache_key, stream)
        cache.put(cache_key + "-next_cursor", next_cursor)
      return stream, next_cursor, True

    def reshare(self,target_node,new_author,new_content, new_title):
      new_post = None
      if len(self.res_type) > 0 and self.res_type[0] == "post":
        #reshare of a reshare
        new_post = target_node.get().create_open_post(new_author, new_title, new_content, resources=[self.resource[0]], res_types=[self.res_type[0]])
      else:
        new_post = target_node.get().create_open_post(new_author, new_title, new_content, resources=[self.key], res_types=["post"])
      return new_post
      
    def reshare_old(self,target_node,new_author,new_content, new_title):
      resource=None
  
      #reshare of a reshare
      if self.resource is not None:
          resource_key=self.resource
          resource=resource_key.get()
      #reshare of a post
      else:
          #reshare of an already reshared post
          resource=SocialResource.query(ancestor=self.key).get()
          #reshare of a never reshared post
          if resource is None:
              resource=SocialResource(parent=self.key,
                                      title=self.title,
                                      type="post",
                                      author=self.author,
                                      content=self.content,
                                      created=self.created
                                      
                                      )
              resource.put()
              resource_key=resource.key
          else:
              resource_key=resource.key
              
      new_post=resource.publish(target_node,new_content,new_title,new_author)
      if new_post:
                    
          return new_post
    
    def subscribe_user(self, user):
      #user has already subscribed to this post
      if self.subscriptions.get(user.key):
        #logging.info("user already subscribed")
        return

      #logging.info("user not yet subscribed")
        
      sub = SocialPostSubscription(parent=self.key)
      
      if user:
          sub.user=user.key
      else:
          raise users.UserNotFoundError
      
      sub.put()    
      self.subscriptions = None
              
    def unsubscribe_user(self, user):
      subscription=self.subscriptions.get(user.key)
      if subscription is not None:
         subscription.key.delete()
         self.subscriptions = None
    
      else:
          raise users.UserNotFoundError
    
    def create_comment(self,content,author):
      floodControl=memcache.get("FloodControl-"+str(author.key))
      if floodControl:
        raise base.FloodControlException
      
      new_comment= SocialComment(parent=self.key)
      new_comment.author=author.key
      new_comment.content=content
      new_comment.put()
      
      self.comments=self.comments + 1
      self.calc_rank(SocialComment)
      self.put()
      self.key.parent().get().calc_rank(SocialComment)
      self.key.parent().get().put()
      
      self.subscribe_user(author)
      
      #SocialNotification.create(source_key=self.key,author_key=author.key,type="new_comment",target_key=new_comment.key,author=comm.nome+" "+comm.cognome)
      SocialEvent.create(type="comment", target_key=self.key, source_key=new_comment.key, user_key=author.key)
      
      if Const.FLOOD_SYSTEM_ACTIVATED:
        memcache.add("FloodControl-"+str(author.key), datetime.now(),time=Const.SOCIAL_FLOOD_TIME)
      
      return new_comment

    def delete_comment(self, comment_key):
      comment_key.delete()
      self.comments=self.comments-1
      self.put()

    def vote(self, vote, user):
      if vote == 0:
        for p_vote in self.votes:
          if p_vote.c_u == user.key:
            if p_vote.vote == 1:
              p_vote.key.delete()
            break;
      else :
        vote = Vote(ref = self.key, vote = vote, c_u = user.key)
        vote.put()
  
      self.votes = None
      
      self.calc_rank(Vote)
      self.key.parent().get().calc_rank(Vote)
      self.key.parent().get().put()
      
      Cache.get_cache("SocialPost").clear_all()
      Cache.get_cache("UserStream").clear_all()

    def can_vote(self, user):
      if not user:
        return False
      canvote = True
      for p_vote in self.votes:
        if p_vote.c_u == user.key:
          canvote = False
          break;
      return canvote

    def init_rank(self):
      init_rank = datetime.now() - Const.BASE_RANK
      self.rank = init_rank.seconds + (init_rank.days*Const.DAY_SECONDS)

    def calc_rank(self, activity):
      values = {SocialComment: 7,
                Vote: 3 }
      now = datetime.now()
      if self.last_act is None:
        self.last_act = now
      delta = now - self.last_act
      delta_rank = delta.seconds + (delta.days*Const.DAY_SECONDS)
      self.rank += ((delta_rank * values[activity]) / 10)

    def _post_put_hook(cls, future):
      Cache.get_cache("SocialPost").clear_all()
      Cache.get_cache("UserStream").clear_all()
      
      post=future.get_result().get()
      doc=search.Document(
                      doc_id='post-'+post.key.urlsafe(),
                      fields=[search.TextField(name='title', value=post.title),
                              search.HtmlField(name='content', value=post.content),
                              search.HtmlField(name='comments', value=post.get_comments_text())],
                      language='it')
      
     
      index = search.Index(name='index-posts',
                   consistency=search.Index.PER_DOCUMENT_CONSISTENT)
      try:
          index.put(doc)
      
      except search.Error, e:
          pass

    def _pre_delete_hook(cls, key):
        index = search.Index(name='index-posts',
                     consistency=search.Index.PER_DOCUMENT_CONSISTENT)
        try:
            index.delete('post-'+key.urlsafe())
        
        except search.Error, e:
            pass

class SocialPostSubscription(model.Model):
    user = model.KeyProperty(kind=models.User)
    has_ntfy = model.BooleanProperty(default=False)
    
    @classmethod
    def get_posts_keys_by_user(cls,user):
      sub_list=SocialPostSubscription.query().filter(SocialPostSubscription.user==user.key).fetch(keys_only=True)
      return [i.parent() for i in sub_list]  

    @classmethod
    def get_by_post(cls,post_key):
      return SocialPostSubscription.query(ancestor=post_key).fetch()
    
    @classmethod
    def get_by_ntfy(cls):
      return SocialPostSubscription.query().filter(SocialPostSubscription.has_ntfy==True).fetch()    
        
class SocialNodeSubscription(model.Model):
    starting_date=model.DateProperty(auto_now=True)
    user = model.KeyProperty(kind=models.User)

    can_comment = model.BooleanProperty(default=False)
    can_post = model.BooleanProperty(default=False)
    can_admin = model.BooleanProperty(default=False)

    ntfy_period = model.IntegerProperty(default=0)
    has_ntfy = model.BooleanProperty(default=False)
    last_ntfy_sent = model.DateTimeProperty(default=None)
    ntfy = model.IntegerProperty(default=0)
    #last_ntfy_access = model.DateTimeProperty(default=None)

    def init_perm(self):
        parent=self.key.parent().get()
        self.can_comment=parent.default_comment
        self.can_post=parent.default_post
        self.can_admin=parent.default_admin
        self.put()
        
    def reset_ntfy(self):
      self.ntfy = 0
      self.put()
      
    @classmethod
    def get_by_user(self, user_t, order_method=None):
        
        if not order_method:
            order_method=SocialNodeSubscription.starting_date
        
        subs = SocialNodeSubscription.query(SocialNodeSubscription.user==user_t.key).order(order_method).fetch()
          
        #node_list=[i.key.parent().get() for i in subscriptions_list]
        return subs
    
    @classmethod
    def get_nodes_keys_by_user(cls,user):
      cache = Cache.get_cache("UserNodeSubscription")
      cache_key = "UserNodeSubscription-" + str(user.key.id)
      nodes = cache.get(cache_key)
      if not nodes:        
        sub_list=SocialNodeSubscription.query().filter(SocialNodeSubscription.user==user.key).order(SocialNodeSubscription.starting_date).fetch(keys_only=True)
        nodes = [i.parent() for i in sub_list]
        cache.put(cache_key, nodes)
      return nodes

    @classmethod
    def get_by_node(cls, node_key, cursor):
      if cursor:
        return SocialNodeSubscription.query(ancestor=node_key).fetch_page(page_size=20, start_cursor=cursor)
      else:
        return SocialNodeSubscription.query(ancestor=node_key).fetch_page(page_size=20)
    
    @classmethod
    def get_by_ntfy(cls):
      subs = list()
      for sub in SocialNodeSubscription.query().filter(SocialNodeSubscription.has_ntfy==True).fetch():
        #logging.info(sub.last_ntfy_sent + timedelta(sub.ntfy_period) < datetime.now())
        if sub.last_ntfy_sent is None or sub.last_ntfy_sent + timedelta(days=sub.ntfy_period) < datetime.now():
          subs.append(sub)
      return subs

class SocialResource(model.Expando):
    url=model.StringProperty()
    type=model.StringProperty()
    
#    def _post_put_hook(self,future):
#        assert self.key.parent()
#        count=SocialResource.query(ancestor=self.key.parent()).count()
#        logging.info(self.key.parent().get())
#        assert count==1
#        assert False
#        logging.info("aaaaaaaaaaaaaaaaaaaaaaaaa")
#           
    @staticmethod
    def get_resource(key):
        return SocialResource.query(ancestor=key).get()
    #rompo l'MVC, possano gli Dei antichi e nuovi perdonare il mio sacrilegio    
    #deprecated
    #def render(self):
        #render_method = getattr(self,'render_'+self.type)
        #return render_method()
    
    
    #def render_post(self):
        #template_values = {
                 #"resource":self
        #}
        #template = jinja_environment.get_template("social/resources/post.html")
       
        #return template.render(template_values)  
    
    #def render_ispezione(self):
        #template_values = {
                 #"resource":self
        #}
        #template = jinja_environment.get_template("social/resources/ispezione.html")
        #return template.render(template_values)  

    #def render_nonconf(self):
        #template_values = {
                 #"resource":self
        #}
        #template = jinja_environment.get_template("social/resources/nonconf.html")
        #return template.render(template_values)  
    #def render_dieta(self):
        #template_values = {
                 #"resource":self
        #}
        #template = jinja_environment.get_template("social/resources/dieta.html")
        #return template.render(template_values)  
    #def render_nota(self):
        #template_values = {
                 #"resource":self
        #}
        #template = jinja_environment.get_template("social/resources/nota.html")
        #return template.render(template_values)  
    
    #def render_city(self):
        #template_values = {
                 #"resource":self
        #}
        #template = jinja_environment.get_template("social/resources/city.html")
        #return template.render(template_values)  
    #def render_commission(self):
        #template_values = {
                 #"resource":self
        #}
        #template = jinja_environment.get_template("social/resources/commission.html")
                
        #return template.render(template_values)  
    
    
    def publish(self,target_node,new_content, new_title,new_author):
        new_post=target_node.get().create_open_post(content=new_content,title=new_title,author=new_author,resources=[self.key], res_types=["generic"])
        return new_post
    
class SocialComment(model.Model):
    author=model.KeyProperty(kind=models.User)
    content=model.TextProperty(default="")
    #public_reference=model.StringProperty(default="")
    created=model.DateTimeProperty(auto_now_add=True)

    def _post_put_hook(self, future):
      Cache.get_cache("SocialPost").clear_all()
      Cache.get_cache("UserStream").clear_all()
      future.get_result().get().key.parent().get().reset_comment_list()
              
    def extended_date(self):
      delta = datetime.now() - self.created
      if delta.days == 0 and delta.seconds < 3600:
        return str(delta.seconds / 60) + " minuti fa"
      elif delta.days == 0 and delta.seconds < 3600*24:
        return str(delta.seconds / 3600) + " ore fa"
      else:
        return "il " + datetime.strftime(self.created, Const.ACTIVITY_DATE_FORMAT + " alle " + Const.ACTIVITY_TIME_FORMAT)
    
    @cached_property
    def commissario(self):
      return Commissario.get_by_user(self.author.get())

    def can_admin(self, user):
      sub_cache = Cache.get_cache('SocialNodeSubscription')
      cache_key = str(self.key.parent().parent().id) + "-" + str(user.key.id)
      sub = sub_cache.get(cache_key)
      if not sub:
        sub = SocialNodeSubscription.query(ancestor=self.key.parent().parent()).filter(SocialNodeSubscription.user==user.key).get()
        sub_cache.put(cache_key, sub)
      return sub and (sub.can_admin or self.author == user.key)


class Vote(model.Model):
  def __init__(self, *args, **kwargs):
    self._commissario = None
    super(Vote, self).__init__(*args, **kwargs)  
  
  ref = model.KeyProperty()
  vote = model.IntegerProperty()

  c_u = model.KeyProperty(kind=models.User)
  c_d = model.DateTimeProperty(auto_now_add=True)
  
  @cached_property
  def author(self):
    return Commissario.get_by_user(self.c_u.get())

  @classmethod
  def get_by_ref(cls, ref):
    return Vote.query().filter(Vote.ref==ref)

class SocialProfile(model.Model):
      ultimo_accesso_notifiche= model.DateTimeProperty(auto_now=True)
      
      @classmethod
      def create(cls,user):
          if cls.query(ancestor=user).get():
              return
          else:
             SocialProfile(parent=user).put()
      
      #@classmethod
      #def retrieve_notifications(self,user_t,cursor):
        #nodes_list=SocialNodeSubscription.get_nodes_keys_by_user(user_t)
        #posts_list=SocialPostSubscription.get_posts_keys_by_user(user_t)
        
        
        #sources_list=nodes_list+posts_list
        #logging.info(sources_list)
        #if not cursor or cursor == "undefined":
               #return SocialNotification.query().order(SocialNotification.author_key).filter(SocialNotification.author_key!=user_t.key,SocialNotification.source_key.IN(sources_list)).order(-SocialNotification.date).order(SocialNotification._key).fetch_page(10) 
        #else:
               #return SocialNotification.query().order(SocialNotification.author_key).filter(SocialNotification.author_key!=user_t.key,SocialNotification.source_key.IN(sources_list)).order(-SocialNotification.date).order(SocialNotification._key).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))
                    

class SocialEvent(model.Model):
  type = model.StringProperty()
  target = model.KeyProperty()
  source = model.KeyProperty()
  user = model.KeyProperty()
  date = model.DateTimeProperty(auto_now_add=True)
  status = model.IntegerProperty()

  @classmethod
  def create(cls, type, target_key, source_key, user_key):
    event=cls(type=type, target=target_key, source=source_key, user=user_key, status=cls.status_created)
    event.put()

  @classmethod
  def get_by_status(cls, status, cursor):
    return SocialEvent.query().filter(SocialEvent.status==status).order(SocialEvent.date).fetch_page(20, start_cursor=cursor)
          
  status_created = 0
  status_processed = 1
  new_post = "post"
  new_comment = "comment"
  
class SocialNotification(model.Model):
  event = model.KeyProperty()
  user = model.KeyProperty()
  date = model.DateTimeProperty(auto_now_add=True)
  
  status = model.IntegerProperty()

  def set_read(self):
    self.status=self.status_read
    self.put()
    
  @classmethod
  def create(cls, event_key, user_key):
    notification = SocialNotification(event=event_key, user=user_key, date=datetime.now(), status=cls.status_created)
    notification.put()
  
  @classmethod
  def get_by_user(cls, user, cursor=None):
    cache = Cache.get_cache('SocialNotification')
    cache_key = "SocialNotification-" + str(user.id) + "-" + str(cursor)
    ntfs = cache.get(cache_key)
    next_cursor = cache.get(cache_key + "-next-cursor")
    more = cache.get(cache_key + "-more")
    if not ntfs:
      ntfs = list()
      results, next_cursor, more = SocialNotification.query().filter(SocialNotification.user==user).order(-SocialNotification.date).fetch_page(20, start_cursor=cursor)
      for n in results:
        ntfs.append(n)
      cache.put(cache_key, ntfs)
      cache.put(cache_key + "-next-cursor", next_cursor)
      cache.put(cache_key + "-more", more)

    return ntfs, next_cursor, more

  @classmethod
  def get_by_user_date(cls, user, date):
    cursor = None
    more = True
    nns = list()
    while more:
      ns, cursor, more = cls.get_by_user(user, cursor)
      for n in ns:
        if n.date > date:
          nns.append(n)
        else:
          more = False
    return nns
  
  @classmethod
  def get_by_date(cls, date, cursor=None):
    return SocialNotification.query().order(-SocialNotification.date)
    
  @classmethod
  def get_by_user_status(cls, user, status):
    return SocialNotification.query().filter(SocialNotification.user==user).filter(SocialNotification.status==status)
  
  status_created = 0
  status_notified = 1
  status_read = 2
      
      
          
class StatisticheNonconf(model.Model):
  citta = model.KeyProperty(kind=Citta)
  commissione = model.KeyProperty(kind=Commissione)
  centroCucina = model.KeyProperty(kind=CentroCucina)

  timePeriod = model.StringProperty() # W, M, Y
  timeId = model.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = model.DateProperty()
  dataFine = model.DateProperty()
  dataCalcolo = model.DateTimeProperty()
  
  numeroNonconf = model.IntegerProperty(default=0,indexed=False)
  numeroNonconfSettimana = model.IntegerProperty(repeated=True,indexed=False)

  data = model.IntegerProperty(repeated=True)
    
  _tipiPos = {1:0,
           2:1,
           3:2,
           4:3,
           5:4,
           6:5,
           7:6,
           8:7,
           9:8,
           10:9,
           11:10,
           12:11,
           99:12}  

  @classmethod
  def get_cy_cc_cm_time(cls, cy = None, cc = None, cm = None, timeId=None):
    q = StatisticheNonconf.query().filter(StatisticheNonconf.citta==cy).filter(StatisticheNonconf.commissione==cm).filter(StatisticheNonconf.centroCucina==cc)
    if timeId:
      q = q.filter(StatisticheNonconf.timeId == timeId)
    return q

  @classmethod
  def get_from_date(cls, data):
    return StatisticheNonconf.query().filter(StatisticheNonconf.dataInizio >= data)

  @classmethod
  def get_from_year(cls, year):
    return StatisticheNonconf.query().filter(StatisticheNonconf.timeId == year)
  
  def getData(self, tipo):
    return self.data[self._tipiPos[tipo]]
  
  def incData(self, tipo):
    self.data[self._tipiPos[tipo]] += 1

  def getTipiPos(self):
    return self._tipiPos
  