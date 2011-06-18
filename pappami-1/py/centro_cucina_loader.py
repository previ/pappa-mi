import datetime
from google.appengine.ext import db
from google.appengine.tools.bulkloader import Loader
from py.model import *

class CentroCucinaLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'CentroCucina',
                    [('key_name', str),
                     ('nome', str),
                     ('strada', str),
                     ('civico', str),
                     ('citta', str),
                     ('cap', str),
                     ('nomeContatto', str),
                     ('cognomeContatto', str),
                     ('telefono', str),
                     ('fax', str),
                     ('codice', str)
                     ])
                     
    self.alias_old_names()
    
loaders = [CentroCucinaLoader]
