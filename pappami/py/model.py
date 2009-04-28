from datetime import date, datetime, time, timedelta

from google.appengine.ext import db

class CentroCucina(db.Model):
  nome = db.StringProperty()
  strada = db.StringProperty()
  civico = db.StringProperty()
  citta = db.StringProperty()
  cap = db.StringProperty()
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
 
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
  dataIspezione = db.DateProperty()

  aaRispettoCapitolato = db.BooleanProperty()
  aaTavoliApparecchiati = db.BooleanProperty()
  aaTermichePulite = db.BooleanProperty()
  aaScaldaVivande = db.BooleanProperty()  
  aaLavastovigliePresente = db.BooleanProperty()
  aaTabellaEsposta = db.BooleanProperty()
  
  ricicloStoviglie = db.BooleanProperty()
  ricicloPosate = db.BooleanProperty()
  ricicloBicchieri = db.BooleanProperty()

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
  primoCondito = db.StringProperty()
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
  contornoCondito = db.StringProperty()
  contornoCottura = db.IntegerProperty()
  contornoTemperatura = db.IntegerProperty()
  contornoQuantita = db.IntegerProperty()
  contornoAssaggio = db.IntegerProperty()
  contornoGradimento = db.IntegerProperty()

  paneTipo = db.StringProperty()
  paneServito = db.StringProperty()
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

  ncMenuDiverso = db.BooleanProperty()
  ncCiboAvanzato = db.BooleanProperty()
  ncQuantita = db.BooleanProperty()
  ncStoviglie = db.BooleanProperty()
  ncArredi = db.BooleanProperty()
  ncPulizia = db.BooleanProperty()
  ncRifiuti = db.BooleanProperty()
  ncDiete = db.BooleanProperty()
  ncRitardo = db.BooleanProperty()
  ncCorpiEstranei = db.BooleanProperty()
  ncRichiestaCampionatura = db.BooleanProperty()
  ncNote = db.TextProperty(default="")

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

  ncCrudoBruciato = int(0)
  ncCorpiEstranei = int(0)
  ncCattivoOdore = int(0)
  ncGustoSospetto = int(0)
  ncRichiestaCampionatura = int(0)
