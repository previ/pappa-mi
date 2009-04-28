import datetime
from google.appengine.ext import db
from pappami.model import *

class CentroCucinaLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'CentroCucina',
                    [('key_name', str),
                     ('nome', str),
                     ('strada', str),
                     ('civico', str),
                     ('citta', str),
                     ('cap', str),
                     ('telefono', str),
                     ('fax', str),
                     ('email', str)
                     ])
                     
