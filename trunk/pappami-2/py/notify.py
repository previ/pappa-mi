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
from google.appengine.api import mail
import threading

from model import *

class NotifyHandler(BasePage):

  def get(self):
    limit = 50
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))
    #logging.info("limit: %d", limit)
    #logging.info("offset: %d", offset)

    self.putTask('/admin/notify/jit',limit=limit,offset=offset)
    self.putTask('/admin/notify/daily',limit=limit,offset=offset)
    self.putTask('/admin/notify/weekly',limit=limit,offset=offset)
    self.putTask('/admin/notify/monthly',limit=limit,offset=offset)
    
  def putTask(self, aurl, msg_key, offset=0, limit=50):
    task = Task(url=aurl, params={"msg_key":str(msg_key)}, "limit": str(limit), "offset":str(offset)}, method="GET")
    queue = Queue()
    queue.add(task)
      
    
class NotifyTaskHandler(NotifyHandler):

  def get(self):
    msg_key = None
    if self.request.get("msg_key"):
      msg_key = model.Key("Messaggio", int(self.request.get("msg_key")))      
    limit = 50
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))
    #logging.info("limit: %d", limit)
    #logging.info("offset: %d", offset)

    now = datetime.datetime.now().date()
    since = now - datetime.timedelta(1)
          

class NotifyEventTaskHandler(NotifyHandler):

  def get(self):
    msg_key = None
    if self.request.get("msg_key"):
      msg_key = model.Key("Messaggio", int(self.request.get("msg_key")))      
   
    for msg in Messaggio.query().filter(Messaggio.par):
      pass
      #if msg.grp in 
      
