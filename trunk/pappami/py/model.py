from datetime import date, datetime, time, timedelta
import logging
import fpformat

from google.appengine.ext import db

class Citta(db.Model):
  nome = db.StringProperty()
  provincia = db.StringProperty()
  codice =  db.StringProperty()
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

  def getZona(self, data=datetime.now().date()):
    return CentroCucinaZona.all().filter("centroCucina",self).filter("validitaDa <=",data).order("-validitaDa").get().zona

  def getMenuOffset(self, data=datetime.now().date()):
    return ZonaOffset.all().filter("zona",self.getZona(data)).filter("validitaDa <=",data).order("-validitaDa").get().offset
  
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

  def getCentroCucina(self, data=datetime.now().date()):
    return CommissioneCentroCucina.all().filter("commissione",self).filter("validitaDa <=",data).order("-validitaDa").get().centroCucina
      
  
class Commissario(db.Model):
  user = db.UserProperty()
  nome = db.StringProperty()
  cognome = db.StringProperty()

  emailComunicazioni = db.StringProperty()
  
  ultimo_accesso_il = db.DateTimeProperty()

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
    return self.stato == 11 or self.stato == 0
  def isRegCommissario(self):
    return self.stato == 0
  def isRegGenitore(self):
    return self.stato == 10
  
  def commissioni(self):
    commissioni = []
    for cc in CommissioneCommissario.all().filter("commissario", self):
      commissioni.append(cc.commissione)
    return commissioni

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
    logging.info(self.data)
    logging.info(datetime.now().date())
    return datetime.now().date() == self.data

class MenuNew(db.Model):
  nome = db.StringProperty()
  validitaDa = db.DateProperty()
  validitaA = db.DateProperty()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

class Piatto(db.Model):
  nome = db.StringProperty()
  calorie = db.IntegerProperty()
  proteine = db.IntegerProperty()
  grassi = db.IntegerProperty()
  carboidrati = db.IntegerProperty()
  gi = db.IntegerProperty()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
class MenuGiorno(db.Model):
  menu = db.ReferenceProperty(MenuNew)
  settimana = db.IntegerProperty()
  giorno = db.IntegerProperty()
  piatti = db.ReferenceProperty(Piatto, collection_name='menuprimi')
  secondo = db.ReferenceProperty(Piatto, collection_name='menusecondi')
  contorno = db.ReferenceProperty(Piatto, collection_name='menucontorni')
  dessert = db.ReferenceProperty(Piatto, collection_name='menudesserts')

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()
  
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

  cottura = db.ListProperty(int,default=[0,0,0])
  temperatura = db.ListProperty(int,default=[0,0,0])
  quantita = db.ListProperty(int,default=[0,0,0])
  assaggio = db.ListProperty(int,default=[0,0,0])
  gradimento = db.ListProperty(int,default=[0,0,0,0])

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

  anno = db.IntegerProperty()
  
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

  anno = db.IntegerProperty()
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

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
  etichettaLeggibile = db.IntegerProperty()
  temperaturaVaschetta = db.IntegerProperty()
  vicinoEducatore = db.IntegerProperty()
  vaschettaOriginale = db.IntegerProperty()
  condimentiVicini = db.IntegerProperty()
  primoAccettato = db.IntegerProperty()
  secondoAccettato = db.IntegerProperty()
  contornoAccettato = db.IntegerProperty()
  fruttaAccettata = db.IntegerProperty()
  gradimentoPrimo = db.IntegerProperty()
  gradimentoSecondo = db.IntegerProperty()
  gradimentoContorno = db.IntegerProperty()
  comunicazioneGenitori = db.IntegerProperty()

  note = db.TextProperty(default="")

  anno = db.IntegerProperty()
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  stato = db.IntegerProperty()

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
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  stato = db.IntegerProperty()

class Tag(db.Model):
  obj = db.ReferenceProperty(db.Model)
  tag = db.StringProperty(default="")

class Allegato(db.Model):
  obj = db.ReferenceProperty(db.Model)
  dati = db.BlobProperty()
  titolo = db.StringProperty(default="")
  def isImage(self):
    return ".png" in self.titolo.lower() or ".gif" in ".png" in self.titolo.lower() or ".jpg" in self.titolo.lower() or ".jpeg" in self.titolo.lower()
  
class Statistiche:
  numeroCommissioni = int(0)
  numeroSchede = int(0) 
  ncTotali = int(0)
  diete = int(0)  

class StatisticheIspezioni(db.Model):
  commissione = db.ReferenceProperty(Commissione)
  centroCucina = db.ReferenceProperty(CentroCucina)

  timePeriod = db.StringProperty() # W, M, Y
  timeId = db.IntegerProperty()    # 1, 2, 3 - 2009, 2010
  
  dataInizio = db.DateProperty()
  dataFine = db.DateProperty()

  dataCalcolo = db.DateTimeProperty()

  numeroSchede = db.IntegerProperty(default=0) 
  numeroSchedeSettimana = db.ListProperty(int, default=[0])

  ambiente_names = {"aaRispettoCapitolato":0,"aaTavoliApparecchiati":1,"aaTermichePulite":2,"aaAcqua":3, "aaScaldaVivande":4, "aaSelfService":5, "aaTabellaEsposta":6, "ricicloStoviglie":7, "ricicloPosate":8, "ricicloBicchieri":9}
  ambiente_desc = ["Rispetto Capitolato","Tavoli Apparecchiati","Termiche Pulite","Acqua da cucina", "Scalda Vivande", "Self Service", "Tabella Dietetica Esposta", "Riciclo Stoviglie", "Riciclo Posate", "Riciclo Bicchieri"]
  ambiente = db.ListProperty(int,default=[0,0,0,0,0,0,0,0,0,0])
  arrivoDist = db.ListProperty(int,default=[0,0,0,0])
  durataPasto = db.ListProperty(int,default=[0,0,0,0])

  numeroPastiTotale = db.IntegerProperty()
  numeroPastiBambini = db.IntegerProperty()
  numeroPastiSpeciali = db.IntegerProperty()
  numeroAddetti = db.IntegerProperty()
  
  puliziaRefettorio = db.ListProperty(int,default=[0,0,0,0])
  puliziaCentroCottura = db.ListProperty(int,default=[0,0,0,0])
  smaltimentoRifiuti = db.ListProperty(int,default=[0,0,0,0])

  giudizioGlobale = db.ListProperty(int,default=[0,0,0])
  
  primoCondito = db.ListProperty(int,default=[0,0])
  primoDist = db.ListProperty(int,default=[0,0,0])
  primoCottura = db.ListProperty(int,default=[0,0,0])
  primoTemperatura = db.ListProperty(int,default=[0,0,0])
  primoQuantita = db.ListProperty(int,default=[0,0,0])
  primoAssaggio = db.ListProperty(int,default=[0,0,0])
  primoGradimento = db.ListProperty(int,default=[0,0,0,0])

  secondoDist = db.ListProperty(int,default=[0,0,0])
  secondoCottura = db.ListProperty(int,default=[0,0,0])
  secondoTemperatura = db.ListProperty(int,default=[0,0,0])
  secondoQuantita = db.ListProperty(int,default=[0,0,0])
  secondoAssaggio = db.ListProperty(int,default=[0,0,0])
  secondoGradimento = db.ListProperty(int,default=[0,0,0,0])
  
  contornoCondito = db.ListProperty(int,default=[0,0])
  contornoCottura = db.ListProperty(int,default=[0,0,0])
  contornoTemperatura = db.ListProperty(int,default=[0,0,0])
  contornoQuantita = db.ListProperty(int,default=[0,0,0])
  contornoAssaggio = db.ListProperty(int,default=[0,0,0])
  contornoGradimento = db.ListProperty(int,default=[0,0,0,0])

  paneQuantita = db.ListProperty(int,default=[0,0,0])
  paneAssaggio = db.ListProperty(int,default=[0,0,0])
  paneGradimento = db.ListProperty(int,default=[0,0,0,0])
  paneServito = db.ListProperty(int,default=[0,0,0])
  
  fruttaMaturazione = db.ListProperty(int,default=[0,0,0])
  fruttaQuantita = db.ListProperty(int,default=[0,0,0])
  fruttaAssaggio = db.ListProperty(int,default=[0,0,0])
  fruttaGradimento = db.ListProperty(int,default=[0,0,0,0])

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
  
  numeroNonconf = db.IntegerProperty(default=0)
  numeroNonconfSettimana = db.ListProperty(int, default=[0])

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
  