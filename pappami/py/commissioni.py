#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from py.base import *

import os
import cgi
import logging
import wsgiref.handlers

from google.appengine.ext.ndb import model
from google.appengine.api import users
import webapp2 as webapp
from jinja2.filters import do_pprint
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
import threading

from model import *

class CommissioniHandler(BasePage):

  def get(self):
    lat = 45.463681
    lon = 9.188171
    latlongstr = self.request.headers.get("X-AppEngine-CityLatLong")
    logging.info("latlong: " + str(latlongstr))
    if latlongstr:
      latlong = latlongstr.split(",")
      lat = float(latlong[0])
      lon = float(latlong[1])

    template_values = dict()
    geo = model.GeoPt(lat, lon)
    commissario = self.getCommissario()
    citta = None
    if self.get_context().get("citta_key"):
      citta = model.Key("Citta", self.get_context().get("citta_key")).get()
      geo = citta.geo
    
    centri_cucina= list()
    if citta:
      centri_cucina = CentroCucina.query().filter(CentroCucina.citta == citta.key).order(CentroCucina.nome)
      
    template_values["content"] = "map.html"
    template_values["limit"] = 100
    template_values["cittas"] = Citta.get_all()
    template_values["citta"] = citta
    template_values["geo"] = geo
    template_values["centriCucina"] = centri_cucina
    template_values['action'] = self.request.path
    self.getBase(template_values)


class ContattiHandler(BasePage):

  def get(self):
    template_values = dict()
    cm = None
    commissario = self.getCommissario()
    if self.request.get("cm") != "":
      cm = model.Key('Commissione', int(self.request.get("cm"))).get()
    elif commissario and commissario.commissione() :
      cm = commissario.commissione()

    if cm:
      template_values['commissari'] = cm.commissari()
      ctx = self.get_context()
      ctx["cm_key"] = cm.key.id()
      ctx["cm_name"] = cm.desc()
      self.set_context()

    template_values["citta"] = Citta.get_all()
    template_values["content"] = "contatti.html"
    self.getBase(template_values)

  _contacts_lock = threading.RLock()
  _contacts = None
  @classmethod
  def get_contacts(cls, num=12):
    if not cls._contacts:
      with cls._contacts_lock:
        cls._contacts = list()
        for c in Commissario.get_all_reverse(limit=num):
          cls._contacts.append(c)
    return cls._contacts

  def post(self):
    cm_key = self.get_context().get("cm_key")
    cm = None
    if cm_key:
      cm = model.Key("Commissione", cm_key).get()
    if self.request.get("cm"):
      logging.info(self.request.get("cm"))
      cm = model.Key("Commissione", int(self.request.get("cm"))).get()

    template_values = dict()
    template_values['content'] = 'contatti.html'
    template_values["citta"] = Citta.get_all()

    if cm:
      template_values['commissari'] = cm.commissari()
      self.get_context()["citta_key"] = cm.citta.id()
      self.get_context()["cm_key"] = cm.key.id()
      self.get_context()["cm_name"] = cm.desc()
    self.getBase(template_values)



app = webapp.WSGIApplication([
  ('/contatti', ContattiHandler),
  ('/commissioni', CommissioniHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()
