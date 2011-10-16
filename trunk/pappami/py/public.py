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


from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.modelMsg import *
from py.form import IspezioneForm, NonconformitaForm
from py.base import BasePage, CMCommissioniDataHandler, CMCommissioniHandler, CMMenuHandler
from py.stats import CMStatsHandler
from py.commissario import CMCommissarioDataHandler
from py.comments import CMCommentHandler

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMIspezionePublicHandler(BasePage):
  
  def get(self): 
    isp = Ispezione.get(self.request.get("key"))
    template_values = dict()
    template_values["isp"] = isp
    template_values["public_url"] = "http://" + self.getHost() + "/public/isp?key=" + str(isp.key())
    template_values["main"] = "../templates/public/main.html"
    template_values["content"] = "../public/ispezione_read.html"
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler().getRoot(isp.key())
    
    self.getBase(template_values)
 
class CMNonconfPublicHandler(BasePage):
  
  def get(self): 
    nc = Nonconformita.get(self.request.get("key"))
    template_values = dict()
    template_values["nc"] = nc
    template_values["public_url"] = "http://" + self.getHost() + "/public/nc?key=" + str(nc.key())
    template_values["main"] = "../templates/public/main.html"
    template_values["content"] = "../public/nonconf_read.html"
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler().getRoot(nc.key())
    self.getBase(template_values)

class CMDietePublicHandler(BasePage):
  
  def get(self): 
    dieta = Dieta.get(self.request.get("key"))
    template_values = dict()
    template_values["dieta"] = dieta
    template_values["public_url"] = "http://" + self.getHost() + "/public/dieta?key=" + str(dieta.key())
    template_values["main"] = "../templates/public/main.html"
    template_values["content"] = "../public/dieta_read.html"
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler().getRoot(dieta.key())
    self.getBase(template_values)

class CMNotePublicHandler(BasePage):
  
  def get(self): 
    nota = Nota.get(self.request.get("key"))
    allegati = None
    if nota.allegato_set.count():
      allegati = nota.allegato_set
    
    template_values = dict()
    template_values["nota"] = nota
    template_values["public_url"] = "http://" + self.getHost() + "/public/nota?key=" + str(nota.key())
    template_values["main"] = "../templates/public/main.html"
    template_values["content"] = "../public/nota_read.html"
    template_values["allegati"] = allegati
    template_values["comments"] = True
    template_values["comment_root"] = CMCommentHandler().getRoot(nota.key())
    
    self.getBase(template_values)

class CMAllegatoPublicHandler(BasePage):
  
  def get(self): 
    allegato = Allegato.get(self.request.get("key"))   
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
      template_values["main"] = "../templates/public/robot.html"
      self.getBase(template_values)
    else:
      self.redirect("/")

class CMDetailHandler(BasePage):
  
  def get(self): 
    logging.info("CMDetailHandler")
    msg = Messaggio.get(self.request.get("key"))
    
    temp = "../templates/public/detail_"
    tipo = int(msg.tipo)
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
    template_values["msg"] = msg
    
    comment_root = msg
    template_values["comments"] = True,
    template_values["comment_root"] = comment_root
    
    path = os.path.join(os.path.dirname(__file__), template_values["main"])
    #logging.info("CMDetailHandler: " + template.render(path, template_values))
    
    self.getBase(template_values)
      
    
app = webapp.WSGIApplication([
    ('/public/robot', CMRobotPublicHandler),
    ('/public/isp', CMIspezionePublicHandler),
    ('/public/nc', CMNonconfPublicHandler),
    ('/public/dieta', CMDietePublicHandler),
    ('/public/nota', CMNotePublicHandler),
    ('/public/allegato', CMAllegatoPublicHandler),
    ('/public/avatar', CMAvatarHandler),
    ('/public/detail', CMDetailHandler),
    ('/public/getcm', CMCommissioniDataHandler),
    ('/public/getcity', CMCittaHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'))
    
def main():
  app.run();

if __name__ == "__main__":
  main()