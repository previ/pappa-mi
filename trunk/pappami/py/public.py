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
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.modelMsg import *
from py.form import IspezioneForm, NonconformitaForm
from py.base import BasePage, CMCommissioniDataHandler, config, handle_404, handle_500
from py.stats import CMStatsHandler
from py.comments import CMCommentHandler

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMIspezionePublicHandler(BasePage):
  
  def get(self): 
    isp = model.Key("Ispezione", int(self.request.get("key"))).get()
    template_values = dict()
    template_values["isp"] = isp
    template_values["public_url"] = "http://" + self.getHost() + "/public/isp?key=" + str(isp.key.id())
    template_values["main"] = "public/main.html"
    template_values["content"] = "../public/ispezione_read.html"
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler.getRoot(isp.key.id())
    
    self.getBase(template_values)
 
class CMNonconfPublicHandler(BasePage):
  
  def get(self): 
    nc = model.Key("Nonconformita", int(self.request.get("key"))).get()
    template_values = dict()
    template_values["nc"] = nc
    template_values["public_url"] = "http://" + self.getHost() + "/public/nc?key=" + str(nc.key.id())
    template_values["main"] = "public/main.html"
    template_values["content"] = "../public/nonconf_read.html"
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler.getRoot(nc.key.id())
    self.getBase(template_values)

class CMDietePublicHandler(BasePage):
  
  def get(self): 
    dieta = model.Key("Dieta", int(self.request.get("key"))).get()
    template_values = dict()
    template_values["dieta"] = dieta
    template_values["public_url"] = "http://" + self.getHost() + "/public/dieta?key=" + str(dieta.key.id())
    template_values["main"] = "public/main.html"
    template_values["content"] = "../public/dieta_read.html"
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler.getRoot(dieta.key.id())
    self.getBase(template_values)

class CMNotePublicHandler(BasePage):
  
  def get(self): 
    nota = model.Key("Nota", int(self.request.get("key"))).get()
    allegati = None
    if nota.allegati().count() > 0:
      allegati = nota.allegati()
    
    template_values = dict()
    template_values["nota"] = nota
    template_values["public_url"] = "http://" + self.getHost() + "/public/nota?key=" + str(nota.key.id())
    template_values["main"] = "public/main.html"
    template_values["content"] = "../public/nota_read.html"
    template_values["allegati"] = allegati
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler.getRoot(nota.key.id())
    
    self.getBase(template_values)

class ActivityPublicHandler(BasePage):
  
  def get(self): 
    message = model.Key("Messaggio", int(self.request.get("key"))).get()

    template_values = dict()
    template_values["activity"] = message
    if message.root is None:
      template_values["msg"] = message
      template_values["detail"] = "public/detail_msg.html"      
    elif message.tipo == 101:
      template_values["isp"] = message.root.get()
      template_values["detail"] = "ispezioni/ispezione_read_div.html"      
    elif message.tipo == 102:
      template_values["nc"] = message.root.get()
      template_values["detail"] = "ispezioni/nonconf_read_div.html"
    elif message.tipo == 103:
      template_values["dieta"] = message.root.get()
      template_values["detail"] = "ispezioni/dieta_read_div.html"
    elif message.tipo == 104:
      template_values["nota"] = message.root.get()
      template_values["detail"] = "ispezioni/nota_read_div.html"
    
    template_values["content"] = "public/activity.html"
    template_values["activities"] = [message]
    
    self.getBase(template_values)
    
class CMAllegatoPublicHandler(BasePage):
  
  def get(self): 
    allegato = model.Key("Allegato", int(self.request.get("key"))).get()
    if allegato.isImage():
      self.response.headers['Content-Type'] = "image/png"
    else:
      self.response.headers['Content-Type'] = "application/pdf"
    self.response.out.write(allegato.dati)    

class CMRobotPublicHandler(BasePage):
  
  def get(self): 
    if "Googlebot" in self.request.headers["User-Agent"]:
      template_values = dict()
      isps = Ispezione.all()
      template_values["isps"] = isps
      template_values["public_url"] = "http://" + self.getHost() + "/public/isp?key="
      template_values["main"] = "public/robot.html"
      self.getBase(template_values)
    else:
      self.redirect("/")

class CMDetailHandler(BasePage):
  
  def get(self): 
    logging.info("CMDetailHandler")
    message = model.Key("Messaggio", int(self.request.get("key"))).get()
    
    temp = "public/detail_"
    tipo = int(message.tipo)
    if tipo == 101:
      temp += "isp"
    if tipo == 102:
      temp += "nc"
    if tipo == 103:
      temp += "dieta"
    if tipo == 104:
      temp += "nota"
    if tipo == 201:
      temp += "msg"
      
    template_values = dict()
    template_values["main"] = temp + ".html"
    template_values["msg"] = message
    
    comment_root = message
    template_values["comments"] = True,
    template_values["comment_root"] = comment_root
       
    self.getBase(template_values)
      
class CMAvatarRenderHandler(BasePage):
  
  def get(self):
    user_id = self.request.get("id")
    user = model.Key("User", int(user_id)).get()
    commissario = self.getCommissario(user)
    self.response.headers['Content-Type'] = "image/png"
    img = commissario.avatar_data
    #logging.info("len: " + str(len(img)))
    #logging.info("size: " + self.request.get("size"))
    if self.request.get("size") != "big":
      img = images.resize(img, 48,48)
    self.response.out.write(img)
    
app = webapp.WSGIApplication([
    ('/public/robot', CMRobotPublicHandler),
    ('/public/isp', CMIspezionePublicHandler),
    ('/public/nc', CMNonconfPublicHandler),
    ('/public/dieta', CMDietePublicHandler),
    ('/public/nota', CMNotePublicHandler),
    ('/public/allegato', CMAllegatoPublicHandler),
    ('/public/avatar', CMAvatarRenderHandler),
    ('/public/detail', CMDetailHandler),
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