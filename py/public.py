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


from py.base import *

import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import webapp2 as webapp


from google.appengine.ext.ndb import model
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.modelMsg import *

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class ActivityPublicHandler(BasePage):

  def get(self):
    message = model.Key("Messaggio", int(self.request.get("key"))).get()
    if message.par:
      post = SocialPost.get_by_resource(message.par)[0]
      if post:
        self.redirect("/post/"+post.id)

  def post(self):
    return self.get()

class CMRobotPublicHandler(BasePage):

  def get(self):
    if "Googlebot" in self.request.headers["User-Agent"]:
      template_values = dict()
      msgs = self.get_activities()
      template_values["activities"] = msgs
      template_values["public_url"] = "http://" + self.getHost() + "/public/act?key="
      template_values["main"] = "public/robot.html"
      self.getBase(template_values)
    else:
      self.redirect("/")

class CMAvatarRenderHandler(BasePage):

  def get(self):
    user_id = self.request.get("id")
    user = model.Key("User", int(user_id)).get()
    commissario = self.getCommissario(user)
    self.response.headers['Content-Type'] = "image/png"
    img = commissario.avatar_data
    if self.request.get("size") != "big":
      img = images.resize(img, 48,48)
    self.response.out.write(img)

app = webapp.WSGIApplication([
    ('/public/robot', CMRobotPublicHandler),
    ('/public/avatar', CMAvatarRenderHandler),
    ('/public/act', ActivityPublicHandler),
    ('/public/getcm', CMCommissioniDataHandler),
    ('/public/getcity', CMCittaHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()
