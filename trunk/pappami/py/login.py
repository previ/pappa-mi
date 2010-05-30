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

import os
import cgi
import logging
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class LoginPage(webapp.RequestHandler):
  
  def get(self):
    self.redirect("/")

class LoginReqPage(webapp.RequestHandler):
  
  def get(self):
    logging.info("called")
    template_values = dict()
    template_values["continue"] = self.request.get("continue")

    path = os.path.join(os.path.dirname(__file__), '../templates/login_required.html')
    self.response.out.write(template.render(path, template_values))

class DoLoginPage(webapp.RequestHandler):
  
  def post(self):
    self.redirect("/_ah/login_redir?claimid=" + self.request.get("federated_identity") + "&" + "continue=" + self.request.get("continue"))

  def get(self):
    self.redirect("/_ah/login_redir?claimid=" + self.request.get("federated_identity") + "&" + "continue=" + self.request.get("continue"))

def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
  ('/login', LoginPage),
  ('/_ah/login_required', LoginReqPage),
  ('/_ah/do_login', DoLoginPage)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
