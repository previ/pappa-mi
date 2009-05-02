import datetime
from google.appengine.ext import db
from google.appengine.tools.bulkloader import Loader
from py.model import *

DATE_FORMAT = "%d/%m/%Y"

class MenuLoader(Loader):
  def __init__(self):
    Loader.__init__(self, 'Menu',
                    [('centroCucina', lambda x: db.Key.from_path('CentroCucina',x)),
                     ('validitaDa', lambda x: datetime.strptime(x,DATE_FORMAT).date()),
                     ('validitaA', lambda x: datetime.strptime(x,DATE_FORMAT).date()),
                     ('settimana', int),
                     ('giorno', int),
                     ('primo', str),
                     ('secondo', str),
                     ('contorno', str)
                     ])
    self.alias_old_names()
    
loaders = [MenuLoader]
