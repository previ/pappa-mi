import datetime
from google.appengine.ext import db
from py.model import *

class CommissioneLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'Commissione',
                    [('nome', str),
                     ('nomeScuola', str),
                     ('codiceScuola', str),
                     ('tipo', str),
                     ('strada', str),
                     ('civico', str),
                     ('citta', str),
                     ('cap', str),
                     ('telefono', str),
                     ('fax', str),
                     ('email', str),
                     ('zona', str),
                     ('distretto', str),
                     ('centroCucina', lambda x: db.Key.from_path('CentroCucina',x))
                     ])