from datetime import date, datetime, time, timedelta

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
  geo = db.GeoPtProperty()
  
  centroCucina = db.ReferenceProperty(CentroCucina)
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

class Commissario(db.Model):
  user = db.UserProperty()
  nome = db.StringProperty()
  cognome = db.StringProperty()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
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
  centroCucina = db.ReferenceProperty(CentroCucina)
  validitaDa = db.DateProperty()
  validitaA = db.DateProperty()
  settimana = db.IntegerProperty()
  giorno = db.IntegerProperty()
  primo = db.StringProperty()
  secondo = db.StringProperty()
  contorno = db.StringProperty()
  
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
  aaLavastovigliePresente = db.IntegerProperty()
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

  arrivoTermiche = db.TimeProperty()
  aperturaTermiche = db.TimeProperty()

  primoInizioDist = db.TimeProperty()
  primoFineDist = db.TimeProperty()
  primoPrevisto = db.StringProperty(default="")
  primoEffettivo = db.StringProperty(default="")
  primoCondito = db.IntegerProperty()
  primoCottura = db.IntegerProperty()
  primoTemperatura = db.IntegerProperty()
  primoQuantita = db.IntegerProperty()
  primoAssaggio = db.IntegerProperty()
  primoGradimento = db.IntegerProperty()

  secondoInizioDist = db.TimeProperty()
  secondoFineDist = db.TimeProperty()
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

  finePasto = db.TimeProperty()

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
           4:"Stoviglie in numero insufficiente",
           5:"Arredi e attrezzature inadeguate della sala di rigoverno",
           6:"Inadeguata pulizia dei locali",
           7:"Mancata consegna diete speciali",
           8:"Ritardo o anticipo nella consegna delle termiche",
           9:"Corpo estraneo",
           10:"Temperatura non conforme alla legge",
           99:"Altro"}
  def tipi(self):
    return self._tipi
  
  def tipoNome(self):
    return self._tipi[self.tipo]
  
class Statistiche:
  numeroSchede = int(0)
  
  primoAssaggio = float(0)
  primoGradimento = float(0)
  secondoAssaggio = float(0)
  secondoGradimento = float(0)
  contornoAssaggio = float(0)
  contornoGradimento = float(0)

  puliziaRefettorio = float(0)
  lavaggioFinale = float(0)
  smaltimentoRifiuti = float(0)
  giudizioGlobale = float(0)

  ncTotali = int(0)
  ncRichiestaCampionatura = int(0)
