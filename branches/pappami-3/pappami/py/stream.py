#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from py.base import *
import os
import cgi
import logging
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
from google.appengine.ext.ndb import model
from google.appengine.api.taskqueue import Task, Queue

import webapp2 as webapp
from google.appengine.api import memcache

import time

class StreamMainHandler(BasePage):

  def get(self):
    node_list = list()
    subs = list()
    user=self.get_current_user()
    cmsro = None

    if user:
      node_list = SocialNodeSubscription.get_nodes_by_user(user)
      subs = SocialNodeSubscription.get_by_user(user)
      cmsro = self.getCommissario(user)
      if not cmsro.ultimo_accesso_notifiche:
        cmsro.ultimo_accesso_notifiche = datetime.now()
        cmsro.put()
        cmsro.set_cache()

    node_recent=[]
    for node in SocialNode.get_most_recent():
      if node not in node_list:
        node_recent.append(node)
      if len(node_recent) >= 5:
        break

    node_active=[]
    for node in SocialNode.get_most_active():
      if node not in node_list:
        node_active.append(node)
      if len(node_active) >= 5:
        break

    template_values = {
            'content': 'stream.html',
            'subs':subs,
            'node_list':node_list,
            'node_active': node_active,
            'node_recent': node_recent,
    }
    self.getBase(template_values)

  @reguser_required
  def post(self):
    return self.get()

app = webapp.WSGIApplication([
  ('/stream', StreamMainHandler),
  ],
  debug = os.environ['HTTP_HOST'].startswith('localhost'), config=config)
