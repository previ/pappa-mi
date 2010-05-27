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
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.model import *
from py.main import BasePage
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
                          guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + "/commissario/ispezione?cmd=open&key="+str(isp.key())),
                          pubDate = isp.dataIspezione.strftime("%a, %d %b %Y %H:%M:%S +0000")))
      

      rss = py.PyRSS2Gen.RSS2(
        title = "Pappa-Mi - Ispezioni",
        link = "http://www.pappa-mi.it/rss/ispezioni",
        description = "Le ultime Ispezioni inserite dalle Commissioni Mensa di Milano",
        items = isp_items)

      memcache.add("feed_isp", rss.to_xml())     
        
        
    expires_date = datetime.utcnow() + timedelta(1)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(buff)


application = webapp.WSGIApplication([
  ('/feed/ispezione', CMFeedIspHandler)
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
