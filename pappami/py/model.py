#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from datetime import date, datetime, time, timedelta
import logging
import fpformat
import google.appengine.api.images

from google.appengine.ext import db
from google.appengine.ext import blobstore

class Citta(db.Model):
  nome = db.StringProperty()
  codice =  db.StringProperty()
  provincia = db.StringProperty()
  geo = db.GeoPtProperty()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)

  stato = db.IntegerProperty()
  
class Configurazione(db.Model):
  nome = db.StringProperty()
  valore = db.StringProperty()
  
class CentroCucina(db.Model):
  nome = db.StringProperty()
  codice = db.StringProperty()
  strada = db.StringProperty()
  civico = db.StringProperty()
  #citta = db.StringProperty()
  citta = db.ReferenceProperty(Citta)
  cap = db.StringProperty()
  nomeContatto = db.StringProperty()
  cognomeContatto = db.StringProperty()
  telefono = db.StringProperty()
  fax = db.StringProperty()
  email = db.EmailProperty()
  menuOffset = db.IntegerProperty()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

  _ce_cu_zo_cache = None
  def getZona(self, data=datetime.now().date()):
    if not(CentroCucina._ce_cu_zo_cache and CentroCucina._ce_cu_zo_cache.validitaDa <= data and CentroCucina._ce_cu_zo_cache.validitaA >= data):
      CentroCucina._ce_cu_zo_cache = CentroCucinaZona.all().filter("centroCucina",self).filter("validitaDa <=",data).order("-validitaDa").get().zona
    return CentroCucina._ce_cu_zo_cache
  
  _zo_of_cache = None
  def getMenuOffset(self, data=datetime.now().date()):
    if not(CentroCucina._zo_of_cache and CentroCucina._zo_of_cache.validitaDa <= data and CentroCucina._zo_of_cache.validitaA >= data):
      CentroCucina._zo_of_cache = ZonaOffset.all().filter("zona",self.getZona(data)).filter("validitaDa <=",data).order("-validitaDa").get()
    return CentroCucina._zo_of_cache.offset
  
class Commissione(db.Model):
  nome = db.StringProperty(default="")
  nomeScuola = db.StringProperty(default="")
  tipoScuola = db.StringProperty(default="")
  codiceScuola = db.StringProperty(default="")
  distretto = db.StringProperty(default="")
  zona = db.StringProperty(default="")
  strada = db.StringProperty(default="")
  civico = db.StringProperty(default="")
  #citta = db.StringProperty(default="")
  citta = db.ReferenceProperty(Citta)
  cap = db.StringProperty(default="")
  telefono = db.StringProperty(default="")
  fax = db.StringProperty(default="")
  email = db.EmailProperty()
  centroCucina = db.ReferenceProperty(CentroCucina)
  
  geo = db.GeoPtProperty()

  numCommissari = db.IntegerProperty(default=0)

  calendario = db.StringProperty(default="")
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
  def commissari(self):
    commissari = []
    for cc in CommissioneCommissario.all().filter("commissione", self):
      commissari.append(cc.commissario)
    return commissari

  _com_cen_cuc_last = None
  
  def getCentroCucina(self, data=datetime.now().date()):
    if not (Commissione._com_cen_cuc_last and Commissione._com_cen_cuc_last.validitaDa <= data and Commissione._com_cen_cuc_last.validitaA >= data):
      Commissione._com_cen_cuc_last = CommissioneCentroCucina.all().filter("commissione",self).filter("validitaDa <=",data).order("-validitaDa").get()
    return Commissione._com_cen_cuc_last.centroCucina

  def desc(self):
    return self.nome + " " + self.tipoScuola
  
class Commissario(db.Model):
  user = db.UserProperty()
  nome = db.StringProperty()
  cognome = db.StringProperty()
  
  avatar_url = db.StringProperty()
  avatar_data = db.BlobProperty()

  emailComunicazioni = db.StringProperty()

  user_email_lower = db.StringProperty()
  
  citta = db.ReferenceProperty(Citta)
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)

  ultimo_accesso_il = db.DateTimeProperty()

  stato = db.IntegerProperty()
  
  cmdefault = None
  
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

  _commissioni = None
  def commissioni(self):
    if self._commissioni is None:
      self._commissioni = []
      for cc in CommissioneCommissario.all().filter("commissario", self):
        self._commissioni.append(cc.commissione)      
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
  
  def nomecompleto(self):
    if self.nome or self.cognome:
      return self.nome + " " + self.cognome
    else:
      return self.user.nickname()

  def titolo(self):
    titolo = None
    if self.isCommissario():
      titolo = "Commissione Mensa - ["
    else:
      titolo = "Genitore - ["
    for c in self.commissioni():
      titolo = titolo + c.tipoScuola + " " + c.nome + "; "
    return titolo + "]"
    
  def avatar(self):
    if not self.avatar_url:
      return "/img/default_avatar.png"
    else:
      return self.avatar_url
    
  
class CommissioneCommissario(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
  
class Menu(db.Model):
  tipoScuola = db.StringProperty()
  validitaDa = db.DateProperty()
  validitaA = db.DateProperty()
  settimana = db.IntegerProperty()
  giorno = db.IntegerProperty()
  primo = db.StringProperty()
  secondo = db.StringProperty()
  contorno = db.StringProperty()
  dessert = db.StringProperty()
  data = None

  _giorni = ["Lunedi'", "Martedi'", "Mercoledi'", "Giovedi'", "Venerdi'","Sabato", "Domenica"]
  def getData(self):
    return self._giorni[self.giorno-1]
  def today(self):
    return datetime.now().date() == self.data

class MenuNew(db.Model):
  nome = db.StringProperty()
  citta = db.ReferenceProperty(Citta)

  validitaDa = db.DateProperty()
  validitaA = db.DateProperty()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  stato = db.IntegerProperty()

  _menu_cache = dict()
  
  @staticmethod
  def get_by(citta, data):
    menu = None
    if citta in MenuNew._menu_cache:
      menu = MenuNew._menu_cache[citta]
      if not(menu and menu.validitaDa <= data and menu.validitaDa >= data):
        MenuNew._menu_cache[citta] = menu
    else:
      menu = MenuNew.all().filter("citta", citta).filter("validitaDa <=", data).order("-validitaDa").get()
      MenuNew._menu_cache[citta] = menu
    return menu
  
class Piatto(db.Model):
  nome = db.StringProperty()
  calorie = db.IntegerProperty()
  proteine = db.IntegerProperty()
  grassi = db.IntegerProperty()
  carboidrati = db.IntegerProperty()
  gi = db.IntegerProperty()
  
  _pi_gi_cache = dict()
  
  @staticmethod
  def get_by(settimana):
    pi_gi = None
    if settimana not in Piatto._pi_gi_cache:
      pi_gi = dict()
      for pg in PiattoGiorno.all().filter("settimana", settimana ):
        if not pg.giorno in pi_gi:
          pi_gi[pg.giorno] = dict()
        pi_gi[pg.giorno][pg.tipo] = pg.piatto
      Piatto._pi_gi_cache[settimana] = pi_gi
    else:
      pi_gi = Piatto._pi_gi_cache[settimana]
    return pi_gi
        
  
  #creato_da = db.UserProperty(auto_current_user_add=True)
  #creato_il = db.DateTimeProperty(auto_now_add=True)
  #stato = db.IntegerProperty()
  
class Ingrediente(db.Model):
  nome = db.StringProperty()

  #creato_da = db.UserProperty(auto_current_user_add=True)
  #creato_il = db.DateTimeProperty(auto_now_add=True)
  #stato = db.IntegerProperty()

class PiattoIngrediente(db.Model):
  piatto = db.ReferenceProperty(Piatto)
  ingrediente = db.ReferenceProperty(Ingrediente)
  
class PiattoGiorno(db.Model):
  menu = db.ReferenceProperty(MenuNew)
  settimana = db.IntegerProperty()
  giorno = db.IntegerProperty()
  piatto = db.ReferenceProperty(Piatto, collection_name='piatto_giorni')
  tipo = db.StringProperty()

  #creato_da = db.UserProperty(auto_current_user_add=True)
  #creato_il = db.DateTimeProperty(auto_now_add=True)
  #stato = db.IntegerProperty()
  
class MenuHelper():
  primo = None
  secondo = None
  contorno = None
  dessert = None
  data = None
  giorno = None
  settimana = None

  _giorni = ["Lunedi'", "Martedi'", "Mercoledi'", "Giovedi'", "Venerdi'","Sabato", "Domenica"]
  def getData(self):
    return self._giorni[self.giorno-1]
  def today(self):
    return datetime.now().date() == self.data
  
  
class StatistichePiatto(db.Model):
  piatto = db.ReferenceProperty(Piatto)
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)

  timePeriod = db.StringProperty() # W, M, Y
  timeId = db.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = db.DateProperty()
  dataFine = db.DateProperty()

  dataCalcolo = db.DateTimeProperty()

  numeroSchede = db.IntegerProperty(default=0) 
  numeroSchedeSettimana = db.ListProperty(int, default=[0])

  cottura = db.ListProperty(int,default=[0,0,0], indexed=False)
  temperatura = db.ListProperty(int,default=[0,0,0], indexed=False)
  quantita = db.ListProperty(int,default=[0,0,0], indexed=False)
  assaggio = db.ListProperty(int,default=[0,0,0], indexed=False)
  gradimento = db.ListProperty(int,default=[0,0,0,0], indexed=False)

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
class CommissioneCentroCucina(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)
  validitaDa = db.DateProperty()
  validitaA = db.DateProperty()

class CentroCucinaZona(db.Model):
  centroCucina = db.ReferenceProperty(CentroCucina)
  zona = db.IntegerProperty()
  validitaDa = db.DateProperty()
  validitaA = db.DateProperty()

class ZonaOffset(db.Model):
  zona = db.IntegerProperty()
  offset = db.IntegerProperty()
  validitaDa = db.DateProperty()
  validitaA = db.DateProperty()
  
class Ispezione(db.Model):
      
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
 
  dataIspezione = db.DateProperty()
  turno = db.IntegerProperty()

  aaRispettoCapitolato = db.IntegerProperty(indexed=False)
  aaTavoliApparecchiati = db.IntegerProperty(indexed=False)
  aaTermichePulite = db.IntegerProperty(indexed=False)
  aaAcqua = db.IntegerProperty(indexed=False)
  aaScaldaVivande = db.IntegerProperty(indexed=False)  
  aaSelfService = db.IntegerProperty(indexed=False)
  aaTabellaEsposta = db.IntegerProperty(indexed=False)
  
  ricicloStoviglie = db.IntegerProperty(indexed=False)
  ricicloPosate = db.IntegerProperty(indexed=False)
  ricicloBicchieri = db.IntegerProperty(indexed=False)

  numeroPastiTotale = db.IntegerProperty(indexed=False)
  numeroPastiBambini = db.IntegerProperty(indexed=False)
  numeroPastiSpeciali = db.IntegerProperty(indexed=False)
  numeroAddetti = db.IntegerProperty(indexed=False)

  puliziaCentroCottura = db.IntegerProperty(indexed=False)
  puliziaRefettorio = db.IntegerProperty(indexed=False)

  arrivoDist = db.IntegerProperty(indexed=False)

  primoDist = db.IntegerProperty(indexed=False)
  primoPrevisto = db.StringProperty(default="",indexed=False)
  primoEffettivo = db.StringProperty(default="",indexed=False)
  primoCondito = db.IntegerProperty(indexed=False)
  primoCottura = db.IntegerProperty(indexed=False)
  primoTemperatura = db.IntegerProperty(indexed=False)
  primoQuantita = db.IntegerProperty(indexed=False)
  primoAssaggio = db.IntegerProperty(indexed=False)
  primoGradimento = db.IntegerProperty(indexed=False)

  secondoDist = db.IntegerProperty(indexed=False)
  secondoPrevisto = db.StringProperty(default="",indexed=False)
  secondoEffettivo = db.StringProperty(default="",indexed=False)
  secondoCottura = db.IntegerProperty(indexed=False)
  secondoTemperatura = db.IntegerProperty(indexed=False)
  secondoQuantita = db.IntegerProperty(indexed=False)
  secondoAssaggio = db.IntegerProperty(indexed=False)
  secondoGradimento = db.IntegerProperty(indexed=False)

  contornoPrevisto = db.StringProperty(default="",indexed=False)
  contornoEffettivo = db.StringProperty(default="",indexed=False)
  contornoCondito = db.IntegerProperty(indexed=False)
  contornoCottura = db.IntegerProperty(indexed=False)
  contornoTemperatura = db.IntegerProperty(indexed=False)
  contornoQuantita = db.IntegerProperty(indexed=False)
  contornoAssaggio = db.IntegerProperty(indexed=False)
  contornoGradimento = db.IntegerProperty(indexed=False)

  paneTipo = db.StringProperty(indexed=False)
  paneServito = db.IntegerProperty(indexed=False)
  paneQuantita = db.IntegerProperty(indexed=False)
  paneAssaggio = db.IntegerProperty(indexed=False)
  paneGradimento = db.IntegerProperty(indexed=False)

  fruttaTipo = db.StringProperty(default="",indexed=False)
  fruttaServita = db.StringProperty(indexed=False)
  fruttaQuantita = db.IntegerProperty(indexed=False)
  fruttaAssaggio = db.IntegerProperty(indexed=False)
  fruttaGradimento = db.IntegerProperty(indexed=False)
  fruttaMaturazione = db.IntegerProperty(indexed=False)

  durataPasto = db.IntegerProperty(indexed=False)

  lavaggioFinale = db.IntegerProperty(indexed=False)
  smaltimentoRifiuti = db.IntegerProperty(indexed=False)
  giudizioGlobale = db.IntegerProperty(indexed=False)
  note = db.TextProperty(default="",indexed=False)

  anno = db.IntegerProperty()
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
  def data(self): 
    return self.dataIspezione  

class Nonconformita(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
 
  dataNonconf = db.DateProperty()
  turno = db.IntegerProperty()
  
  tipo = db.IntegerProperty()
  richiestaCampionatura = db.IntegerProperty()

  note = db.TextProperty(default="")

  anno = db.IntegerProperty()
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

  def data(self): return self.dataNonconf  

  _tipi = {1:0,
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

class Dieta(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
 
  dataIspezione = db.DateProperty()
  turno = db.IntegerProperty()
  
  tipoDieta = db.IntegerProperty()
  etichettaLeggibile = db.IntegerProperty(indexed=False)
  temperaturaVaschetta = db.IntegerProperty(indexed=False)
  vicinoEducatore = db.IntegerProperty(indexed=False)
  vaschettaOriginale = db.IntegerProperty(indexed=False)
  condimentiVicini = db.IntegerProperty(indexed=False)
  primoAccettato = db.IntegerProperty(indexed=False)
  secondoAccettato = db.IntegerProperty(indexed=False)
  contornoAccettato = db.IntegerProperty(indexed=False)
  fruttaAccettata = db.IntegerProperty(indexed=False)
  gradimentoPrimo = db.IntegerProperty(indexed=False)
  gradimentoSecondo = db.IntegerProperty(indexed=False)
  gradimentoContorno = db.IntegerProperty(indexed=False)
  comunicazioneGenitori = db.IntegerProperty(indexed=False)

  note = db.TextProperty(default="")

  anno = db.IntegerProperty()
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

  def data(self): return self.dataIspezione

  _tipi = {1:0,
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
  
  def tipi(self):
    return self._tipi
  
  def tipoNome(self):
    return self._tipi[self.tipoDieta]

class Nota(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
 
  dataNota = db.DateProperty()
  titolo = db.StringProperty(default="")
  note = db.TextProperty(default="")
  anno = db.IntegerProperty()
  
  allegati = list() #helper, not stored
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  stato = db.IntegerProperty()
  
  tags = None

  def data(self): return self.dataNota  

  def allegati(self): 
    return Allegato.all().filter("obj", self)
  
class Tag(db.Model):
  obj = db.ReferenceProperty(db.Model)
  tag = db.StringProperty(default="")

class Allegato(db.Model):
  obj = db.ReferenceProperty(db.Model)
  path = db.StringProperty()
  blob_key = blobstore.BlobReferenceProperty()
  nome = db.StringProperty(default="")
  descrizione = db.StringProperty(default="",indexed=False)
  
  dati=None
  
  def isImage(self):
    return ".png" in self.nome.lower() or ".gif" in ".png" in self.nome.lower() or ".jpg" in self.nome.lower() or ".jpeg" in self.nome.lower()
  def contentType(self):
    return self._tipi[self.nome.lower()[self.nome.rfind("."):]]
  
  def imgthumb(self):
    if self.isImage():
      return google.appengine.api.images.get_serving_url(blob_key=self.blob_key,size=128)

  def path(self):
    return "/blob/get?key=" + str(self.blob_key.key())
    
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

class StatisticheIspezioni(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)

  timePeriod = db.StringProperty() # W, M, Y
  timeId = db.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = db.DateProperty()
  dataFine = db.DateProperty()

  dataCalcolo = db.DateTimeProperty()

  numeroSchede = db.IntegerProperty(default=0,indexed=False) 
  numeroSchedeSettimana = db.ListProperty(int, default=[0],indexed=False)

  ambiente_names = {"aaRispettoCapitolato":0,"aaTavoliApparecchiati":1,"aaTermichePulite":2,"aaAcqua":3, "aaScaldaVivande":4, "aaSelfService":5, "aaTabellaEsposta":6, "ricicloStoviglie":7, "ricicloPosate":8, "ricicloBicchieri":9}
  ambiente_desc = ["Rispetto Capitolato","Tavoli Apparecchiati","Termiche Pulite","Acqua da cucina", "Scalda Vivande", "Self Service", "Tabella Dietetica Esposta", "Riciclo Stoviglie", "Riciclo Posate", "Riciclo Bicchieri"]
  ambiente = db.ListProperty(int,default=[0,0,0,0,0,0,0,0,0,0],indexed=False)
  arrivoDist = db.ListProperty(int,default=[0,0,0,0],indexed=False)
  durataPasto = db.ListProperty(int,default=[0,0,0,0],indexed=False)

  numeroPastiTotale = db.IntegerProperty(indexed=False)
  numeroPastiBambini = db.IntegerProperty(indexed=False)
  numeroPastiSpeciali = db.IntegerProperty(indexed=False)
  numeroAddetti = db.IntegerProperty(indexed=False)
  
  puliziaRefettorio = db.ListProperty(int,default=[0,0,0,0],indexed=False)
  puliziaCentroCottura = db.ListProperty(int,default=[0,0,0,0],indexed=False)
  smaltimentoRifiuti = db.ListProperty(int,default=[0,0,0,0],indexed=False)

  giudizioGlobale = db.ListProperty(int,default=[0,0,0],indexed=False)
  
  primoCondito = db.ListProperty(int,default=[0,0],indexed=False)
  primoDist = db.ListProperty(int,default=[0,0,0],indexed=False)
  primoCottura = db.ListProperty(int,default=[0,0,0],indexed=False)
  primoTemperatura = db.ListProperty(int,default=[0,0,0],indexed=False)
  primoQuantita = db.ListProperty(int,default=[0,0,0],indexed=False)
  primoAssaggio = db.ListProperty(int,default=[0,0,0],indexed=False)
  primoGradimento = db.ListProperty(int,default=[0,0,0,0],indexed=False)

  secondoDist = db.ListProperty(int,default=[0,0,0],indexed=False)
  secondoCottura = db.ListProperty(int,default=[0,0,0],indexed=False)
  secondoTemperatura = db.ListProperty(int,default=[0,0,0],indexed=False)
  secondoQuantita = db.ListProperty(int,default=[0,0,0],indexed=False)
  secondoAssaggio = db.ListProperty(int,default=[0,0,0],indexed=False)
  secondoGradimento = db.ListProperty(int,default=[0,0,0,0],indexed=False)
  
  contornoCondito = db.ListProperty(int,default=[0,0],indexed=False)
  contornoCottura = db.ListProperty(int,default=[0,0,0],indexed=False)
  contornoTemperatura = db.ListProperty(int,default=[0,0,0],indexed=False)
  contornoQuantita = db.ListProperty(int,default=[0,0,0],indexed=False)
  contornoAssaggio = db.ListProperty(int,default=[0,0,0],indexed=False)
  contornoGradimento = db.ListProperty(int,default=[0,0,0,0],indexed=False)

  paneQuantita = db.ListProperty(int,default=[0,0,0],indexed=False)
  paneAssaggio = db.ListProperty(int,default=[0,0,0],indexed=False)
  paneGradimento = db.ListProperty(int,default=[0,0,0,0],indexed=False)
  paneServito = db.ListProperty(int,default=[0,0,0],indexed=False)
  
  fruttaMaturazione = db.ListProperty(int,default=[0,0,0],indexed=False)
  fruttaQuantita = db.ListProperty(int,default=[0,0,0],indexed=False)
  fruttaAssaggio = db.ListProperty(int,default=[0,0,0],indexed=False)
  fruttaGradimento = db.ListProperty(int,default=[0,0,0,0],indexed=False)

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
      return self.centroCucina.nome
    elif self.commissione:
      return self.commissione.nome
    else:
      return "Tutte"
    
  def incVal(self, attrname, isp):
    attr_stat = getattr(self,attrname)
    attr_isp = getattr(isp,attrname)
    attr_stat[attr_isp-1] += attr_isp

  def incValSub(self, attrname, subattr, isp):
    attr_stat = getattr(self,attrname)
    attr_index = getattr(self,attrname+"_names")[subattr]
    attr_isp = getattr(isp,subattr)
    attr_stat[attr_index] += attr_isp
    
  def getVals(self, attrname):
    attr = getattr(self,attrname)
    return attr

  def getVal(self, attrname, voto):
    attr = getattr(self,attrname)
    return attr[voto-1]

  def getNormVal(self, attrname, voto):
    attr = getattr(self,attrname)
    return attr[voto-1] * 100 / voto
      
  def getNormValMedia(self, attrname):
    attr = getattr(self,attrname)
    value = 0
    for v in attr:
      val += v 
    return val * 100 / len(attr)

  _attrs = ["puliziaCentroCottura",
             "puliziaRefettorio",
             "arrivoDist",
             "primoDist",
             "primoCondito",
             "primoCottura",
             "primoTemperatura",
             "primoQuantita",
             "primoAssaggio",
             "primoGradimento",
             "secondoDist",
             "secondoCottura",
             "secondoTemperatura",
             "secondoQuantita",
             "secondoAssaggio",
             "secondoGradimento",
             "contornoCondito",
             "contornoCottura",
             "contornoTemperatura",
             "contornoQuantita",
             "contornoAssaggio",
             "contornoGradimento",
             "paneServito",
             "paneQuantita",
             "paneAssaggio",
             "paneGradimento",
             "fruttaQuantita",
             "fruttaAssaggio",
             "fruttaGradimento",
             "fruttaMaturazione",
             "durataPasto",
             "smaltimentoRifiuti",
             "giudizioGlobale"]
  _attrs_sub = ["ambiente"]
  
  def calc(self, isp):  
    for attr in self._attrs:
      self.incVal(attr,isp)
    for attr in self._attrs_sub:
      for attr_sub in getattr(self,attr+"_names"):
        self.incValSub(attr, attr_sub, isp)
  

class StatisticheNonconf(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)

  timePeriod = db.StringProperty() # W, M, Y
  timeId = db.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = db.DateProperty()
  dataFine = db.DateProperty()
  dataCalcolo = db.DateTimeProperty()
  
  numeroNonconf = db.IntegerProperty(default=0,indexed=False)
  numeroNonconfSettimana = db.ListProperty(int, default=[0],indexed=False)

  data = db.ListProperty(int,default=[0,0,0,0,0,0,0,0,0,0,0,0,0])
  
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

  def getData(self, tipo):
    return self.data[self._tipiPos[tipo]]
  
  def incData(self, tipo):
    self.data[self._tipiPos[tipo]] += 1

  def getTipiPos(self):
    return self._tipiPos
  