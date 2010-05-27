from datetime import date, datetime, time, timedelta
import logging

from google.appengine.ext import db

class CentroCucina(db.Model):
  nome = db.StringProperty()
  codice = db.StringProperty()
  strada = db.StringProperty()
  civico = db.StringProperty()
  citta = db.StringProperty()
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

class Commissione(db.Model):
  nome = db.StringProperty(default="")
  nomeScuola = db.StringProperty(default="")
  tipoScuola = db.StringProperty(default="")
  codiceScuola = db.StringProperty(default="")
  distretto = db.StringProperty(default="")
  zona = db.StringProperty(default="")
  strada = db.StringProperty(default="")
  civico = db.StringProperty(default="")
  citta = db.StringProperty(default="")
  cap = db.StringProperty(default="")
  telefono = db.StringProperty(default="")
  fax = db.StringProperty(default="")
  email = db.EmailProperty()
  centroCucina = db.ReferenceProperty(CentroCucina)
  
  geo = db.GeoPtProperty()

  numCommissari = db.IntegerProperty(default=0)
    
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
  def commissari(self):
    commissari = []
    for cc in CommissioneCommissario.all().filter("commissione", self):
      #logging.info(cc.key().id())
      #logging.info(cc.commissario.key().id())
      commissari.append(cc.commissario)
    return commissari

class Commissario(db.Model):
  user = db.UserProperty()
  nome = db.StringProperty()
  cognome = db.StringProperty()

  ultimo_accesso_il = db.DateTimeProperty()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)

  ultimo_accesso_il = db.DateTimeProperty(auto_now=True)

  stato = db.IntegerProperty()
  
  def commissioni(self):
    commissioni = []
    for cc in CommissioneCommissario.all().filter("commissario", self):
      commissioni.append(cc.commissione)
    return commissioni
  
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
  
class Ispezione(db.Model):
      
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
 
  dataIspezione = db.DateProperty()
  turno = db.IntegerProperty()

  aaRispettoCapitolato = db.IntegerProperty()
  aaTavoliApparecchiati = db.IntegerProperty()
  aaTermichePulite = db.IntegerProperty()
  aaAcqua = db.IntegerProperty()
  aaScaldaVivande = db.IntegerProperty()  
  aaSelfService = db.IntegerProperty()
  aaTabellaEsposta = db.IntegerProperty()
  
  ricicloStoviglie = db.IntegerProperty()
  ricicloPosate = db.IntegerProperty()
  ricicloBicchieri = db.IntegerProperty()

  numeroPastiTotale = db.IntegerProperty()
  numeroPastiBambini = db.IntegerProperty()
  numeroPastiSpeciali = db.IntegerProperty()
  numeroAddetti = db.IntegerProperty()

  puliziaCentroCottura = db.IntegerProperty()
  puliziaRefettorio = db.IntegerProperty()

  arrivoDist = db.IntegerProperty()

  primoDist = db.IntegerProperty()
  primoPrevisto = db.StringProperty(default="")
  primoEffettivo = db.StringProperty(default="")
  primoCondito = db.IntegerProperty()
  primoCottura = db.IntegerProperty()
  primoTemperatura = db.IntegerProperty()
  primoQuantita = db.IntegerProperty()
  primoAssaggio = db.IntegerProperty()
  primoGradimento = db.IntegerProperty()

  secondoDist = db.IntegerProperty()
  secondoPrevisto = db.StringProperty(default="")
  secondoEffettivo = db.StringProperty(default="")
  secondoCottura = db.IntegerProperty()
  secondoTemperatura = db.IntegerProperty()
  secondoQuantita = db.IntegerProperty()
  secondoAssaggio = db.IntegerProperty()
  secondoGradimento = db.IntegerProperty()

  contornoPrevisto = db.StringProperty(default="")
  contornoEffettivo = db.StringProperty(default="")
  contornoCondito = db.IntegerProperty()
  contornoCottura = db.IntegerProperty()
  contornoTemperatura = db.IntegerProperty()
  contornoQuantita = db.IntegerProperty()
  contornoAssaggio = db.IntegerProperty()
  contornoGradimento = db.IntegerProperty()

  paneTipo = db.StringProperty()
  paneServito = db.IntegerProperty()
  paneQuantita = db.IntegerProperty()
  paneAssaggio = db.IntegerProperty()
  paneGradimento = db.IntegerProperty()

  fruttaTipo = db.StringProperty(default="")
  fruttaServita = db.StringProperty()
  fruttaQuantita = db.IntegerProperty()
  fruttaAssaggio = db.IntegerProperty()
  fruttaGradimento = db.IntegerProperty()
  fruttaMaturazione = db.IntegerProperty()

  durataPasto = db.IntegerProperty()

  lavaggioFinale = db.IntegerProperty()
  smaltimentoRifiuti = db.IntegerProperty()
  giudizioGlobale = db.IntegerProperty()
  note = db.TextProperty(default="")

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

class Nonconformita(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
 
  dataNonconf = db.DateProperty()
  turno = db.IntegerProperty()
  
  tipo = db.IntegerProperty()
  richiestaCampionatura = db.IntegerProperty()

  note = db.TextProperty(default="")

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

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
  
class Statistiche:
  numeroCommissioni = int(0)
  numeroSchede = int(0) 
  ncTotali = int(0)

class StatisticheIspezioniNew(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)
  
  dataInizio = db.DateProperty()
  datafine = db.DateProperty()

  numeroSchede = db.IntegerProperty()
  
  nomeValore = db.StringProperty()

  totaleSomma = db.IntegerProperty()
  valoreSomma1 = db.IntegerProperty()
  valoreSomma2 = db.IntegerProperty()
  valoreSomma3 = db.IntegerProperty()
  valoreSomma4 = db.IntegerProperty()
  valoreSomma5 = db.IntegerProperty()

class StatisticheIspezioni(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)

  timePeriod = db.StringProperty() # W, M, Y
  timeId = db.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = db.DateProperty()
  dataFine = db.DateProperty()
  
  numeroSchede = db.IntegerProperty(default=0)

  puliziaRefettorio = db.FloatProperty(default=0.0)
  puliziaRefettorio1 = db.IntegerProperty(default=0)
  puliziaRefettorio2 = db.IntegerProperty(default=0)
  puliziaRefettorio3 = db.IntegerProperty(default=0)
  puliziaRefettorio4 = db.IntegerProperty(default=0)

  puliziaCentroCottura = db.FloatProperty(default=0.0)
  puliziaCentroCottura1 = db.IntegerProperty(default=0)
  puliziaCentroCottura2 = db.IntegerProperty(default=0)
  puliziaCentroCottura3 = db.IntegerProperty(default=0)
  puliziaCentroCottura4 = db.IntegerProperty(default=0)

  smaltimentoRifiuti = db.FloatProperty(default=0.0)
  smaltimentoRifiuti1 = db.IntegerProperty(default=0)
  smaltimentoRifiuti2 = db.IntegerProperty(default=0)
  smaltimentoRifiuti3 = db.IntegerProperty(default=0)
  smaltimentoRifiuti4 = db.IntegerProperty(default=0)

  giudizioGlobale = db.FloatProperty(default=0.0)
  giudizioGlobale1 = db.IntegerProperty(default=0)
  giudizioGlobale2 = db.IntegerProperty(default=0)
  giudizioGlobale3 = db.IntegerProperty(default=0)
  
  primoDistribuzione1 = db.IntegerProperty(default=0)
  primoDistribuzione2 = db.IntegerProperty(default=0)
  primoDistribuzione3 = db.IntegerProperty(default=0)

  primoCottura1 = db.IntegerProperty(default=0)
  primoCottura2 = db.IntegerProperty(default=0)
  primoCottura3 = db.IntegerProperty(default=0)

  primoTemperatura1 = db.IntegerProperty(default=0)
  primoTemperatura2 = db.IntegerProperty(default=0)
  primoTemperatura3 = db.IntegerProperty(default=0)

  primoQuantita1 = db.IntegerProperty(default=0)
  primoQuantita2 = db.IntegerProperty(default=0)
  primoQuantita3 = db.IntegerProperty(default=0)

  primoAssaggio = db.FloatProperty(default=0.0)
  primoAssaggio1 = db.IntegerProperty(default=0)
  primoAssaggio2 = db.IntegerProperty(default=0)
  primoAssaggio3 = db.IntegerProperty(default=0)

  primoGradimento = db.FloatProperty(default=0.0)
  primoGradimento1 = db.IntegerProperty(default=0)
  primoGradimento2 = db.IntegerProperty(default=0)
  primoGradimento3 = db.IntegerProperty(default=0)
  primoGradimento4 = db.IntegerProperty(default=0)

  secondoCottura1 = db.IntegerProperty(default=0)
  secondoCottura2 = db.IntegerProperty(default=0)
  secondoCottura3 = db.IntegerProperty(default=0)

  secondoTemperatura1 = db.IntegerProperty(default=0)
  secondoTemperatura2 = db.IntegerProperty(default=0)
  secondoTemperatura3 = db.IntegerProperty(default=0)

  secondoQuantita1 = db.IntegerProperty(default=0)
  secondoQuantita2 = db.IntegerProperty(default=0)
  secondoQuantita3 = db.IntegerProperty(default=0)
  
  secondoAssaggio = db.FloatProperty(default=0.0)
  secondoAssaggio1 = db.IntegerProperty(default=0)
  secondoAssaggio2 = db.IntegerProperty(default=0)
  secondoAssaggio3 = db.IntegerProperty(default=0)

  secondoGradimento = db.FloatProperty(default=0.0)
  secondoGradimento1 = db.IntegerProperty(default=0)
  secondoGradimento2 = db.IntegerProperty(default=0)
  secondoGradimento3 = db.IntegerProperty(default=0)
  secondoGradimento4 = db.IntegerProperty(default=0)

  contornoCottura1 = db.IntegerProperty(default=0)
  contornoCottura2 = db.IntegerProperty(default=0)
  contornoCottura3 = db.IntegerProperty(default=0)

  contornoTemperatura1 = db.IntegerProperty(default=0)
  contornoTemperatura2 = db.IntegerProperty(default=0)
  contornoTemperatura3 = db.IntegerProperty(default=0)

  contornoQuantita1 = db.IntegerProperty(default=0)
  contornoQuantita2 = db.IntegerProperty(default=0)
  contornoQuantita3 = db.IntegerProperty(default=0)
  
  contornoAssaggio = db.FloatProperty(default=0.0)
  contornoAssaggio1 = db.IntegerProperty(default=0)
  contornoAssaggio2 = db.IntegerProperty(default=0)
  contornoAssaggio3 = db.IntegerProperty(default=0)

  contornoGradimento = db.FloatProperty(default=0.0)
  contornoGradimento1 = db.IntegerProperty(default=0)
  contornoGradimento2 = db.IntegerProperty(default=0)
  contornoGradimento3 = db.IntegerProperty(default=0)
  contornoGradimento4 = db.IntegerProperty(default=0)

  paneQuantita1 = db.IntegerProperty(default=0)
  paneQuantita2 = db.IntegerProperty(default=0)
  paneQuantita3 = db.IntegerProperty(default=0)
  
  paneAssaggio = db.FloatProperty(default=0.0)
  paneAssaggio1 = db.IntegerProperty(default=0)
  paneAssaggio2 = db.IntegerProperty(default=0)
  paneAssaggio3 = db.IntegerProperty(default=0)

  paneGradimento = db.FloatProperty(default=0.0)
  paneGradimento1 = db.IntegerProperty(default=0)
  paneGradimento2 = db.IntegerProperty(default=0)
  paneGradimento3 = db.IntegerProperty(default=0)
  paneGradimento4 = db.IntegerProperty(default=0)
  
  fruttaMaturazione1 = db.IntegerProperty(default=0)
  fruttaMaturazione2 = db.IntegerProperty(default=0)
  fruttaMaturazione3 = db.IntegerProperty(default=0)

  fruttaQuantita1 = db.IntegerProperty(default=0)
  fruttaQuantita2 = db.IntegerProperty(default=0)
  fruttaQuantita3 = db.IntegerProperty(default=0)
  
  fruttaAssaggio = db.FloatProperty(default=0.0)
  fruttaAssaggio1 = db.IntegerProperty(default=0)
  fruttaAssaggio2 = db.IntegerProperty(default=0)
  fruttaAssaggio3 = db.IntegerProperty(default=0)

  fruttaGradimento = db.FloatProperty(default=0.0)
  fruttaGradimento1 = db.IntegerProperty(default=0)
  fruttaGradimento2 = db.IntegerProperty(default=0)
  fruttaGradimento3 = db.IntegerProperty(default=0)
  fruttaGradimento4 = db.IntegerProperty(default=0)
  
  def primoDistribuzione1Norm(self):
    return int(self.primoDistribuzione1 * 100 / 1 / self.numeroSchede)
  def primoDistribuzione2Norm(self):
    return int(self.primoDistribuzione2 * 100 / 2 / self.numeroSchede)
  def primoDistribuzione3Norm(self):
    return int(self.primoDistribuzione3 * 100 / 3 / self.numeroSchede)

  def primoCottura1Norm(self):
    return int(self.primoCottura1 * 100 / 1 / self.numeroSchede)
  def primoCottura2Norm(self):
    return int(self.primoCottura2 * 100 / 2 / self.numeroSchede)
  def primoCottura3Norm(self):
    return int(self.primoCottura3 * 100 / 3 / self.numeroSchede)

  def primoTemperatura1Norm(self):
    return int(self.primoTemperatura1 * 100 / 1 / self.numeroSchede)
  def primoTemperatura2Norm(self):
    return int(self.primoTemperatura2 * 100 / 2 / self.numeroSchede)
  def primoTemperatura3Norm(self):
    return int(self.primoTemperatura3 * 100 / 3 / self.numeroSchede)

  def primoQuantita1Norm(self):
    return int(self.primoQuantita1 * 100 / 1 / self.numeroSchede)
  def primoQuantita2Norm(self):
    return int(self.primoQuantita2 * 100 / 2 / self.numeroSchede)
  def primoQuantita3Norm(self):
    return int(self.primoQuantita3 * 100 / 3 / self.numeroSchede)

  def primoAssaggioNorm(self):
    return int(self.primoAssaggio * 100 / 3)

  def primoAssaggio1Norm(self):
    return int(self.primoAssaggio1 * 100 / 1 / self.numeroSchede)
  def primoAssaggio2Norm(self):
    return int(self.primoAssaggio2 * 100 / 2 / self.numeroSchede)
  def primoAssaggio3Norm(self):
    return int(self.primoAssaggio3 * 100 / 3 / self.numeroSchede)

  def primoGradimentoNorm(self):
    return int(self.primoGradimento * 100 / 4)

  def primoGradimento1Norm(self):
    return int(self.primoGradimento1 * 100 / 1 / self.numeroSchede)
  def primoGradimento2Norm(self):
    return int(self.primoGradimento2 * 100 / 2 / self.numeroSchede)
  def primoGradimento3Norm(self):
    return int(self.primoGradimento3 * 100 / 3 / self.numeroSchede)
  def primoGradimento4Norm(self):
    return int(self.primoGradimento4 * 100 / 4 / self.numeroSchede)
  
  def secondoCottura1Norm(self):
    return int(self.secondoCottura1 * 100 / 1 / self.numeroSchede)
  def secondoCottura2Norm(self):
    return int(self.secondoCottura2 * 100 / 2 / self.numeroSchede)
  def secondoCottura3Norm(self):
    return int(self.secondoCottura3 * 100 / 3 / self.numeroSchede)

  def secondoTemperatura1Norm(self):
    return int(self.secondoTemperatura1 * 100 / 1 / self.numeroSchede)
  def secondoTemperatura2Norm(self):
    return int(self.secondoTemperatura2 * 100 / 2 / self.numeroSchede)
  def secondoTemperatura3Norm(self):
    return int(self.secondoTemperatura3 * 100 / 3 / self.numeroSchede)

  def secondoQuantita1Norm(self):
    return int(self.secondoQuantita1 * 100 / 1 / self.numeroSchede)
  def secondoQuantita2Norm(self):
    return int(self.secondoQuantita2 * 100 / 2 / self.numeroSchede)
  def secondoQuantita3Norm(self):
    return int(self.secondoQuantita3 * 100 / 3 / self.numeroSchede)

  def secondoAssaggioNorm(self):
    return int(self.secondoAssaggio * 100 / 3)

  def secondoGradimentoNorm(self):
    return int(self.secondoGradimento * 100 / 4)

  def contornoCottura1Norm(self):
    return int(self.contornoCottura1 * 100 / 1 / self.numeroSchede)
  def contornoCottura2Norm(self):
    return int(self.contornoCottura2 * 100 / 1 / self.numeroSchede)
  def contornoCottura3Norm(self):
    return int(self.contornoCottura3 * 100 / 1 / self.numeroSchede)

  def contornoTemperatura1Norm(self):
    return int(self.contornoTemperatura1 * 100 / 1 / self.numeroSchede)
  def contornoTemperatura2Norm(self):
    return int(self.contornoTemperatura2 * 100 / 2 / self.numeroSchede)
  def contornoTemperatura3Norm(self):
    return int(self.contornoTemperatura3 * 100 / 3 / self.numeroSchede)

  def contornoQuantita1Norm(self):
    return int(self.contornoQuantita1 * 100 / 1 / self.numeroSchede)
  def contornoQuantita2Norm(self):
    return int(self.contornoQuantita2 * 100 / 2 / self.numeroSchede)
  def contornoQuantita3Norm(self):
    return int(self.contornoQuantita3 * 100 / 3 / self.numeroSchede)

  def contornoAssaggioNorm(self):
    return int(self.contornoAssaggio * 100 / 3)

  def contornoGradimentoNorm(self):
    return int(self.contornoGradimento * 100 / 4)
  
  def paneQuantita1Norm(self):
    return int(self.paneQuantita1 * 100 / 1 / self.numeroSchede)
  def paneQuantita2Norm(self):
    return int(self.paneQuantita2 * 100 / 2 / self.numeroSchede)
  def paneQuantita3Norm(self):
    return int(self.paneQuantita3 * 100 / 3 / self.numeroSchede)

  def paneAssaggioNorm(self):
    return int(self.paneAssaggio * 100 / 3)

  def paneGradimentoNorm(self):
    return int(self.paneGradimento * 100 / 4)

  def fruttaMaturazione1Norm(self):
    return int(self.fruttaMaturazione1 * 100 / 1 / self.numeroSchede)
  def fruttaMaturazione2Norm(self):
    return int(self.fruttaMaturazione2 * 100 / 2 / self.numeroSchede)
  def fruttaMaturazione3Norm(self):
    return int(self.fruttaMaturazione3 * 100 / 3 / self.numeroSchede)

  def fruttaQuantita1Norm(self):
    return int(self.fruttaQuantita1 * 100 / 1 / self.numeroSchede)
  def fruttaQuantita2Norm(self):
    return int(self.fruttaQuantita2 * 100 / 2 / self.numeroSchede)
  def fruttaQuantita3Norm(self):
    return int(self.fruttaQuantita3 * 100 / 3 / self.numeroSchede)

  def fruttaAssaggioNorm(self):
    return int(self.fruttaAssaggio * 100 / 3)

  def fruttaGradimentoNorm(self):
    return int(self.fruttaGradimento * 100 / 4)

  def giudizioGlobaleNorm(self):
    return int(self.giudizioGlobale * 100 / 3)

  def puliziaRefettorioNorm(self):
    return int(self.puliziaRefettorio * 100 / 4)

  def puliziaCentroCotturaNorm(self):
    return int(self.puliziaCentroCottura * 100 / 4)

  def smaltimentoRifiutiNorm(self):
    return int(self.smaltimentoRifiuti * 100 / 4)

class StatisticheNonconf(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)

  timePeriod = db.StringProperty() # W, M, Y
  timeId = db.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = db.DateProperty()
  dataFine = db.DateProperty()
  
  numeroSchede = db.IntegerProperty(default=0)

  data = {1:db.IntegerProperty(default=0),2:db.IntegerProperty(default=0),3:db.IntegerProperty(default=0),4:db.IntegerProperty(default=0),5:db.IntegerProperty(default=0),6:db.IntegerProperty(default=0),7:db.IntegerProperty(default=0),8:db.IntegerProperty(default=0),9:db.IntegerProperty(default=0),10:db.IntegerProperty(default=0),11:db.IntegerProperty(default=0),12:db.IntegerProperty(default=0),99:db.IntegerProperty(default=0)}
  #data = db.ListProperty(int, default={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,99:0})