import datetime
from google.appengine.ext import db
from py.model import *

class MenuLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'Menu',
                    [('centroCucina', lambda x: db.Key.from_path('CentroCucina',x)),
                     ('validitaDa', str),
                     ('validitaA', str),
                     ('settimana', str),
                     ('giorno', str),
                     ('primo', str),
                     ('secondo', str),
                     ('contorno', str)
                     ])