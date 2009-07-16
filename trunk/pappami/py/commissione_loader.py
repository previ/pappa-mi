import datetime
from google.appengine.ext import db
from google.appengine.tools.bulkloader import Loader, Exporter
from py.model import *

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
                    [('commissione', lambda x: db.Key.from_path('Commissione',x)),
                     ('commissario', lambda x: db.Key.from_path('Commissario',x)),
                     ('dataNonconf', str),
                     ('turno', str),
                     ('tipo', str),
                     ('richiestaCampionatura', str),
                     ('note', str),
                     ('creato_da', str),
                     ('creato_il', str),
                     ('modificato_da', str),
                     ('modificato_il', str),
                     ('stato', str)
                     ])
    self.alias_old_names()    

loaders = [CommissioneLoader, NonconfLoader]

class CommissioneExporter(Exporter):
  def __init__(self):
    Exporter.__init__(self, 'Commissione',
                    [('nome', str, None), 
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
                     ('centroCucina', lambda x: x.key().name(), ""),
                     ('geo', lambda x: str(x.lat)+":"+str(x.lon), "0.0:0.0")
                     ])

class NonconfExporter(Exporter):
  def __init__(self):
    Exporter.__init__(self, 'Nonconformita',
                    [('commissione', str, None), 
                     ('commissario', str, None),
                     ('dataNonconf', str, None),
                     ('turno', str, None),
                     ('tipo', str, None),
                     ('richiestaCampionatura', str, None),
                     ('note', convert_note, None),
                     ('creato_da', str, None),
                     ('creato_il', str, ""),
                     ('modificato_da', str, ""),
                     ('modificato_il', str, ""),
                     ('stato', str, "")
                     ])
def convert_note(val): 
  if val != None:
    return unicode(val, 'utf-8')
  else:
    return unicode("", 'utf-8')

exporters = [CommissioneExporter, NonconfExporter]
