#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from py.base import BasePage

import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext.ndb import model
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.model import *
from py.base import BasePage, handle_404, handle_500
import py.PyRSS2Gen

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMFeedIspHandler(BasePage):

  def get(self): 
    buff = memcache.get("feed_isp")
    
    if(buff is None):
      isps = Ispezione.all().order("-dataIspezione").fetch(limit=10)
      isp_items = list()

      for isp in isps:
        note = "nessuna"
        if isp.note is not None:
          note = isp.note
        isp_items.append(py.PyRSS2Gen.RSSItem(title = isp.commissione.nome + " - " + isp.commissione.tipoScuola,
                          description = "Ispezione - note:" + note,
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + "/genitore/ispezione?key="+str(isp.key())),
                          pubDate = isp.dataIspezione.strftime("%a, %d %b %Y %H:%M:%S +0100")))
      

      rss = py.PyRSS2Gen.RSS2(
        title = "Pappa-Mi - Ispezioni",
        link = "http://"+ self.getHost() + "/feed/ispezioni",
        description = "Le ultime Ispezioni inserite dalle Commissioni Mensa di Milano",
        items = isp_items)
      buff = rss.to_xml()
      memcache.add("feed_isp", buff)
        
        
    expires_date = datetime.utcnow() + timedelta(1)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)

class CMFeedIspNCHandler(BasePage):

  def get(self): 
    buff = memcache.get("feed_ispnc")
    cm = None
    if self.request.get("key"):
      cm = Commissione.get(self.request.get("key"))
    
    path = "/genitore/"
    if self.request.get('public'):
      path = "/public/"
      
    if (buff is None) or (cm is not None):
      if cm is not None:
        isps = Ispezione.all().filter("commissione", cm).order("-dataIspezione")
      else:
        isps = Ispezione.all().order("-dataIspezione").fetch(limit=5)
      items = list()

      for isp in isps:
        logging.info(isp)        
        items.append((isp.dataIspezione, isp, None, None, None))
      
      if cm:
        ncs = Nonconformita.all().filter("commissione", cm).order("-dataNonconf")
      else:
        ncs = Nonconformita.all().order("-dataNonconf").fetch(limit=5)
      
      for nc in ncs:
        items.append((nc.dataNonconf, None, nc, None, None))

      if cm:
        diete = Dieta.all().filter("commissione", cm).order("-dataIspezione")
      else:
        diete = Dieta.all().order("-dataIspezione").fetch(limit=5)

      for dieta in diete:
        items.append((dieta.dataIspezione, None, None, dieta))

      if cm:
        note = Nota.all().filter("commissione", cm).order("-dataNota")
      else:
        note = Nota.all().order("-dataNota").fetch(limit=5)
        
      for nota in note:
        items.append((nota.dataNota, None, None, None, nota))
        
      items = sorted(items, key=lambda item: item[0], reverse=True)
      feeditems = list()
      for i in items:
        if i[1] :
          isp = i[1]
          note = "nessuna"
          if isp.note is not None:
            note = isp.note
          feeditems.append(py.PyRSS2Gen.RSSItem(title = isp.commissione.nome + " - " + isp.commissione.tipoScuola,
                            description = "Ispezione - note:" + note,
                            guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + path + "ispezione?key="+str(isp.key())),
                            pubDate = isp.dataIspezione.strftime("%a, %d %b %Y %H:%M:%S +0100")))
        elif i[2]:
          nc = i[2]
          note = "nessuna"
          if nc.note is not None:
            note = nc.note
          feeditems.append(py.PyRSS2Gen.RSSItem(title = nc.commissione.nome + " - " + nc.commissione.tipoScuola,
                          description = "Non Conformita': " + nc.tipoNome() + " note:" + note,
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + path + "nonconf?key="+str(nc.key())),
                          pubDate = nc.dataNonconf.strftime("%a, %d %b %Y %H:%M:%S +0100")))

        elif i[3]:
          dieta = i[3]
          note = "nessuna"
          if dieta.note is not None:
            note = dieta.note
          feeditems.append(py.PyRSS2Gen.RSSItem(title = dieta.commissione.nome + " - " + dieta.commissione.tipoScuola,
                          description = "Ispezione Diete speciali: " + dieta.tipoNome() + " note:" + note,
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + path + "dieta?key="+str(dieta.key())),
                          pubDate = dieta.dataIspezione.strftime("%a, %d %b %Y %H:%M:%S +0100")))
          
        else:
          nota = i[4]
          note = "nessuna"
          if nota.note is not None:
            note = nota.note
          feeditems.append(py.PyRSS2Gen.RSSItem(title = nota.commissione.nome + " - " + nota.commissione.tipoScuola,
                          description = "Nota': " + nota.titolo + " note:" + note,
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + path + "nota?key="+str(nota.key())),
                          pubDate = nota.dataNota.strftime("%a, %d %b %Y %H:%M:%S +0100")))
      

      titolo = "Pappa-Mi - Ispezioni, Non conformita' e Note"
      if cm:
        titolo += " " + cm.tipoScuola + " " + cm.nome

      rss = py.PyRSS2Gen.RSS2(
        title = titolo,      
        link = "http://"+ self.getHost() + "/feed/ispnc",
        description = "Le ultime rilevazioni delle Commissioni Mensa di Milano",
        items = feeditems)
      
      buff = rss.to_xml()
      if cm is None:
        memcache.add("feed_ispnc", buff)
        
        
    expires_date = datetime.utcnow() + timedelta(1)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)
    
class CMFeedNCHandler(BasePage):
  def get(self): 
    buff = memcache.get("feed_nc")
    
    if(buff is None):
      ncs = Nonconformita.all().order("-dataNonconf").fetch(limit=10)
      nc_items = list()

      for nc in ncs:
        note = "nessuna"
        if nc.note is not None:
          note = nc.note
        nc_items.append(py.PyRSS2Gen.RSSItem(title = nc.commissione.nome + " - " + nc.commissione.tipoScuola,
                          description = "Non Conformita': " + nc.tipoNome() + " note:" + note,
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + "/genitore/nonconf?key="+str(nc.key())),
                          pubDate = nc.dataNonconf.strftime("%a, %d %b %Y %H:%M:%S +0100")))
      

      rss = py.PyRSS2Gen.RSS2(
        title = "Pappa-Mi - Non Conformita'",
        link = "http://"+ self.getHost() +"/feed/nc",
        description = "Le ultime Non Conformita' inserite dalle Commissioni Mensa di Milano",
        items = nc_items)
      buff = rss.to_xml()
      memcache.add("feed_nc", buff)
            
        
    expires_date = datetime.utcnow() + timedelta(1)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)

class CMFeedDietaHandler(BasePage):
  def get(self): 
    buff = memcache.get("feed_diete")
    
    if(buff is None):
      diete = Dieta.all().order("-dataIspezione").fetch(limit=10)
      diete_items = list()

      for dieta in diete:
        note = "nessuna"
        if dieta.note is not None:
          note = dieta.note
        diete_items.append(py.PyRSS2Gen.RSSItem(title = dieta.commissione.nome + " - " + dieta.commissione.tipoScuola,
                          description = "Ispezione Dieta: " + dieta.tipoNome() + " note:" + note,
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + "/genitore/dieta?key="+str(dieta.key())),
                          pubDate = dieta.dataIspezione.strftime("%a, %d %b %Y %H:%M:%S +0100")))
      

      rss = py.PyRSS2Gen.RSS2(
        title = "Pappa-Mi - Ispezione Diete speciali",
        link = "http://"+ self.getHost() +"/feed/dieta",
        description = "Le ultime Ispezioni Diete speciali inserite dalle Commissioni Mensa di Milano",
        items = diete_items)
      buff = rss.to_xml()
      memcache.add("feed_diete", buff)
            
        
    expires_date = datetime.utcnow() + timedelta(1)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)

class CMFeedNotaHandler(BasePage):
  def get(self): 
    buff = memcache.get("feed_note")
    
    if(buff is None):
      notes = Nota.all().order("-dataNota").fetch(limit=10)
      nota_items = list()

      for nota in notes:
        note = "nessuna"
        if nota.note is not None:
          note = nota.note
        nota_items.append(py.PyRSS2Gen.RSSItem(title = nota.commissione.nome + " - " + nota.commissione.tipoScuola,
                          description = "Nota: " + nota.titolo + " note:" + note,
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + "/genitore/nota?key="+str(nota.key())),
                          pubDate = nota.dataNota.strftime("%a, %d %b %Y %H:%M:%S +0100")))
      

      rss = py.PyRSS2Gen.RSS2(
        title = "Pappa-Mi - Note",
        link = "http://"+ self.getHost() +"/feed/nota",
        description = "Le ultime Note inserite dalle Commissioni Mensa di Milano",
        items = nota_items)
      buff = rss.to_xml()
      memcache.add("feed_note", buff)
            
        
    expires_date = datetime.utcnow() + timedelta(1)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)
    
class CMFeedHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "feed.html"
    self.getBase(template_values)
    
app = webapp.WSGIApplication([
  ('/feed/isp', CMFeedIspHandler),
  ('/feed/ispnc', CMFeedIspNCHandler),
  ('/feed/nc', CMFeedNCHandler),
  ('/feed/dieta', CMFeedDietaHandler),
  ('/feed/nota', CMFeedNotaHandler),
  ('/feed', CMFeedHandler)  
], debug=os.environ['HTTP_HOST'].startswith('localhost'))

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()