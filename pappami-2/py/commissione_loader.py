import datetime
import base64
from google.appengine.ext.ndb import model
from google.appengine.tools.bulkloader import Loader, Exporter
from google.appengine.api import users
from py.model import *

DATE_FORMAT = "%d/%m/%Y"

class MenuLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'Menu',
                    [('tipoScuola', str),
                     ('validitaDa', lambda x: datetime.strptime(x,DATE_FORMAT).date()),
                     ('validitaA', lambda x: datetime.strptime(x,DATE_FORMAT).date()),
                     ('settimana', int),
                     ('giorno', int),
                     ('primo', str),
                     ('secondo', str),
                     ('contorno', str),
                     ('dessert', str)
                     ])
    self.alias_old_names()
    
class CentroCucinaZonaLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'CentroCucinaZona',
                    [('centroCucina', lambda x: db.Key.from_path('CentroCucina',x)),
                     ('zona', int),
                     ('validitaDa', lambda x: datetime.strptime(x,DATE_FORMAT).date()),
                     ('validitaA', lambda x: datetime.strptime(x,DATE_FORMAT).date())                     
                     ])
    self.alias_old_names()

class CommissioneCentroCucinaLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'CommissioneCentroCucina',
                    [('commissione', lambda x: Commissione.get(x)),
                     ('centroCucina', lambda x: db.Key.from_path('CentroCucina',x)),
                     ('validitaDa', lambda x: datetime.strptime(x,DATE_FORMAT).date()),
                     ('validitaA', lambda x: datetime.strptime(x,DATE_FORMAT).date())                     
                     ])
    self.alias_old_names()
    
class CommissioneLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'Commissione',
                    [('nome', str),
                     ('nomeScuola', str),
                     ('codiceScuola', str),
                     ('tipoScuola', str),
                     ('strada', str),
                     ('civico', str),
                     ('citta', str),
                     ('cap', str),
                     ('telefono', str),
                     ('fax', str),
                     ('zona', str),
                     ('distretto', str),
                     ('centroCucina', lambda x: db.Key.from_path('CentroCucina',x)),
                     ('geo', lambda x: db.GeoPt(float(x.split(":")[0]),float(x.split(":")[1])))
                     ])
    self.alias_old_names()

class NonconfLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'Nonconformita',
                    [('commissione', lambda x: Commissione.get_by_id(int(x))),
                     ('commissario', lambda x: Commissario.get_by_id(int(x))),
                     ('dataNonconf', lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
                     ('turno', int),
                     ('tipo', int),
                     ('richiestaCampionatura', int),
                     ('note', decode_note),
                     ('creato_da', lambda x: users.User(x)),
                     ('creato_il', lambda x: datetime.strptime(x.split('.')[0], "%Y-%m-%d %H:%M:%S")),
                     ('modificato_da', lambda x: users.User(x)),
                     ('modificato_il', lambda x: datetime.strptime(x.split('.')[0], "%Y-%m-%d %H:%M:%S")),
                     ('stato', decode_int)
                     ])
    self.alias_old_names()    

class CentroCucinaLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'CentroCucina',
                    [('key_name', str),
                     ('nome', str),
                     ('strada', str),
                     ('civico', str),
                     ('citta', lambda x: Citta.all().filter("codice",x).get()),
                     ('cap', str),
                     ('nomeContatto', str),
                     ('cognomeContatto', str),
                     ('telefono', str),
                     ('fax', str),
                     ('codice', str)
                     ])
                     
    self.alias_old_names()
    
loaders = [MenuLoader, CentroCucinaZonaLoader, CommissioneCentroCucinaLoader, CommissioneLoader, NonconfLoader, CentroCucinaLoader]

class CommissioneExporter(Exporter):
  def __init__(self):
    Exporter.__init__(self, 'Commissione',
                    [('__key__', str, None), 
                     ('nome', str, None), 
                     ('nomeScuola', str, None),
                     ('codiceScuola', str, None),
                     ('tipoScuola', str, None),
                     ('strada', str, None),
                     ('civico', str, None),
                     ('citta', str, None),
                     ('cap', str, None),
                     ('telefono', str, ""),
                     ('fax', str, ""),
                     ('zona', str, ""),
                     ('distretto', str, ""),
                     ('centroCucina', lambda x: x.name(), ""),
                     ('geo', lambda x: str(x.lat)+":"+str(x.lon), "0.0:0.0")
                     ])

class CommissioneCentroCucinaExporter(Exporter):
  def __init__(self):
    Exporter.__init__(self, 'CommissioneCentroCucina',
                    [('commissione', str, None), 
                     ('commissione', lambda x: Commissione.get(x).nome, None), 
                     ('centroCucina', lambda x: x.name(), ""),
                     ('validitaDa', lambda x: datetime.date(x).strftime(DATE_FORMAT), None),
                     ('validitaA', lambda x: datetime.date(x).strftime(DATE_FORMAT), None),
                     ])
    
class NonconfExporter(Exporter):
  def __init__(self):
    
    Exporter.__init__(self, 'Nonconformita',
                    [('commissione', lambda x: Commissione.get(x).nome, None), 
                     ('commissario', lambda x: Commissario.get(x).user.email(), None),
                     ('dataNonconf', str, None),
                     ('turno', str, None),
                     ('tipo', str, None),
                     ('richiestaCampionatura', str, None),
                     ('note', convert_note, ""),
                     ('creato_da', str, None),
                     ('creato_il', str, ""),
                     ('modificato_da', str, ""),
                     ('modificato_il', str, ""),
                     ('stato', str, "")
                     ])
class IspezioneExporter(Exporter):
  def __init__(self):
    
    Exporter.__init__(self, 'Ispezione',
                    [('commissione', str, None), 
                     ('commissione', lambda x: Commissione.get(x).nome, None), 
                     ('commissario', lambda x: Commissario.get(x).user.email(), None),
                     ('dataIspezione', str, None),
                     ('turno', str, None),                    
                     ('aaRispettoCapitolato', str, None),
                     ('aaTavoliApparecchiati', str, None),
                     ('aaTermichePulite', str, None),
                     ('aaAcqua', str, None),
                     ('aaScaldaVivande', str, None),
                     ('aaSelfService', str, None),
                     ('aaTabellaEsposta', str, None),
                     ('ricicloStoviglie', str, None),
                     ('ricicloPosate', str, None),
                     ('ricicloBicchieri', str, None),
                     ('numeroPastiTotale', str, None),
                     ('numeroPastiBambini', str, None),
                     ('numeroPastiSpeciali', str, None),
                     ('numeroAddetti', str, None),
                     ('puliziaCentroCottura', str, None),
                     ('puliziaRefettorio', str, None),
                     ('arrivoDist', str, None),
                     ('primoDist', str, None),
                     ('primoPrevisto', encode, None),
                     ('primoEffettivo', encode, None),
                     ('primoCondito', str, None),
                     ('primoCottura', str, None),
                     ('primoTemperatura', str, None),
                     ('primoQuantita', str, None),
                     ('primoAssaggio', str, None),
                     ('primoGradimento', str, None),
                     ('secondoDist', str, None),
                     ('secondoPrevisto', encode, None),
                     ('secondoEffettivo', encode, None),
                     ('secondoCottura', str, None),
                     ('secondoTemperatura', str, None),
                     ('secondoQuantita', str, None),
                     ('secondoAssaggio', str, None),
                     ('secondoGradimento', str, None),
                     ('contornoPrevisto', encode, None),
                     ('contornoEffettivo', encode, None),
                     ('contornoCondito', str, None),
                     ('contornoCottura', str, None),
                     ('contornoTemperatura', str, None),
                     ('contornoQuantita', str, None),
                     ('contornoAssaggio', str, None),
                     ('contornoGradimento', str, None),
                     ('paneTipo', encode, None),
                     ('paneServito', str, None),
                     ('paneQuantita', str, None),
                     ('paneAssaggio', str, None),
                     ('paneGradimento', str, None),
                     ('fruttaTipo', encode, None),
                     ('fruttaServita', encode, None),
                     ('fruttaQuantita', str, None),
                     ('fruttaAssaggio', str, None),
                     ('fruttaGradimento', str, None),
                     ('fruttaMaturazione', str, None),
                     ('durataPasto', str, None),
                     ('lavaggioFinale', str, None),
                     ('smaltimentoRifiuti', str, None),
                     ('giudizioGlobale', str, None),
                     ('note', convert_note, ""),
                     ('creato_da', str, None),
                     ('creato_il', str, ""),
                     ('modificato_da', str, ""),
                     ('modificato_il', str, ""),
                     ('stato', str, "")
                     ])
  
def encode(x):
  if x != None :
    return x.encode('utf-8')
  else:
    return ""
    
def convert_note(x):
  if x != None :
    return base64.b64encode(x.encode('utf-8'))
  else:
    return base64.b64encode("")

def decode_note(x):
  denote = base64.b64decode(x).decode('utf-8')
  return denote

def decode_int(x):
  if x != 'None' :
    return int(x)
  else:
    return None

class CentroCucinaZonaExporter(Exporter):
  def __init__(self):
    Exporter.__init__(self, 'CentroCucinaZona',
                    [('centroCucina', lambda x: x.name(), ""),
                     ('zona', int, None),
                     ('validitaDa', lambda x: datetime.date(x).strftime(DATE_FORMAT), None),
                     ('validitaA', lambda x: datetime.date(x).strftime(DATE_FORMAT), None),
                     ])

class MenuExporter(Exporter):
  def __init__(self):
    Exporter.__init__(self, 'Menu',
                    [('tipoScuola', str, None),
                     ('validitaDa', lambda x: datetime.date(x).strftime(DATE_FORMAT), None),
                     ('validitaA', lambda x: datetime.date(x).strftime(DATE_FORMAT), None),
                     ('settimana', int, None),
                     ('giorno', int, None),
                     ('primo', str, None),
                     ('secondo', str, None),
                     ('contorno', str, None),
                     ('dessert', str, None)
                     ])
    
  
exporters = [CommissioneExporter, CommissioneCentroCucinaExporter, NonconfExporter, IspezioneExporter, CentroCucinaZonaExporter, MenuExporter]
