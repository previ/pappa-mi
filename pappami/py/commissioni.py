#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from py.base import *

import os
import cgi
import logging
import wsgiref.handlers

from ndb import model
from google.appengine.api import users
import webapp2 as webapp
from jinja2.filters import do_pprint
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from model import *

class CommissioniHandler(BasePage):

  def get(self):
    template_values = dict()
    return self.getBase(template_values)
  def getBase(self,template_values):
    geo = model.GeoPt(45.463681,9.188171)
    commissario = self.getCommissario(users.get_current_user())
    if commissario:
      geo = commissario.citta.get().geo
    template_values["content"] = "map.html"
    template_values["limit"] = 100
    template_values["centriCucina"] = CentroCucina.get_by_citta(Citta.get_first().key)
    template_values['action'] = self.request.path
    template_values['geo'] = geo
    super(CommissioniHandler,self).getBase(template_values)

class ContattiHandler(BasePage):

  def get(self):
    template_values = dict()
    cm = None
    commissario = self.getCommissario(users.get_current_user())
    if self.request.get("cm") != "":
      cm = Commissione.get(self.request.get("cm"))
    elif commissario and commissario.commissione() :
      cm = commissario.commissione()
    else:
      cm = Commissione.get_all_cursor(None).get()

    template_values["content"] = "contatti.html"
    template_values['commissari'] = cm.commissari()
    self.getBase(template_values)

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    },
    'webapp2_extras.auth': {
        #        'user_model': 'models.User',
        'user_attributes': ['displayName', 'email'],
        },
    'webapp2_extras.jinja2': {
        'filters': {
            'do_pprint': do_pprint,
            },
        },
    }
    
app = webapp.WSGIApplication([
  ('/contatti', ContattiHandler),
  ('/commissioni', CommissioniHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

def main():
  app.run();

if __name__ == "__main__":
  main()
