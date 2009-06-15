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
                     ('geo', lambda x: db.Geo(float(split(x,":")[0]),float(split(x,":")[1])))
                     ])
    self.alias_old_names()
    
loaders = [CommissioneLoader]

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

exporters = [CommissioneExporter]
