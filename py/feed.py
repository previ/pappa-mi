#!/usr/bin/env python
#
# Copyright 2010 Pappa-Mi org
# Authors: R.Previtera
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
from py.modelMsg import *
from py.base import BasePage, handle_404, handle_500
import py.PyRSS2Gen

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMFeedIspNCHandler(BasePage):

  def get(self):
    cm = None
    if self.request.get("key"):
      cm = model.Key(urlsafe=self.request.get("key"))
      node = SocialNode.get_by_resource(cm)
      if node:
        self.redirect("/node/" + str(node.key.id()) + "/rss", permanent=True)

class CMFeedHandler(BasePage):

  def get(self):
    template_values = dict()
    template_values["content"] = "feed.html"
    self.getBase(template_values)

app = webapp.WSGIApplication([
  ('/feed/ispnc', CMFeedIspNCHandler),
  ('/feed', CMFeedHandler)
], debug=os.environ['HTTP_HOST'].startswith('localhost'))

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
