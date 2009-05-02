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
  #creato_da = db.UserProperty(auto_current_user_add=True)
  #creato_il = db.DateTimeProperty(auto_now_add=True)
  #modificato_da = db.UserProperty(auto_current_user=True)
  #modificato_il = db.DateTimeProperty(auto_now=True)
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
  
class Ispezione(db.Expando):
      
  commissione = db.ReferenceProperty(Commissione)
  commissario = db.ReferenceProperty(Commissario)
 
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
  dataIspezione = db.DateProperty()

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

  ncMenuDiverso = db.IntegerProperty()
  ncCiboAvanzato = db.IntegerProperty()
  ncQuantita = db.IntegerProperty()
  ncStoviglie = db.IntegerProperty()
  ncArredi = db.IntegerProperty()
  ncPulizia = db.IntegerProperty()
  ncRifiuti = db.IntegerProperty()
  ncDiete = db.IntegerProperty()
  ncRitardo = db.IntegerProperty()
  ncCorpiEstranei = db.IntegerProperty()
  ncRichiestaCampionatura = db.IntegerProperty()
  ncNote = db.TextProperty(default="")

  def ncPresenti(self):
    s = self.ncMenuDiverso + self.ncCiboAvanzato + self.ncQuantita + self.ncStoviglie + self.ncArredi + self.ncPulizia + self.ncRifiuti + self.ncDiete + self.ncRitardo + self.ncCorpiEstranei + self.ncRichiestaCampionatura
    #for n in self.properties():
      #if n.find("nc") == 0:        
        #v = self.properties()[n]
        #s = s + v
    if s > 0 :
      s = 1
    else:
      s = 0
    return s
  
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
