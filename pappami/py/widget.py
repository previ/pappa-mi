#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from py.base import BasePage, CMCommissioniDataHandler, CMMenuHandler

import os
import cgi
import logging
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext.ndb import model
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
import py.feedparser

from py.model import *

TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class CMMenuWidgetHandler(CMMenuHandler):
  
  def get(self): 
    menu = Menu();

    bgcolor = self.request.get("bc")
    if(bgcolor is None): 
      bgcolor = "eeeeff"
    fcolor = self.request.get("fc")
    if(fcolor is None): 
      fcolor = "000000"

    template_values = dict()
    template_values["bgcolor"] = bgcolor
    template_values["fcolor"] = fcolor

    c = None
    if self.request.get("cm"):
      c = model.Key(urlsafe=self.request.get("cm")).get()
    
    self.createMenu(self.request,c,template_values)

    if self.request.get("i") == "n":
      path = os.path.join(os.path.dirname(__file__), '../templates/widget/menu.html')
    else:
      path = os.path.join(os.path.dirname(__file__), '../templates/widget/wmenu.html')
    self.response.out.write(template.render(path, template_values))

    
class CMStatWidgetHandler(webapp.RequestHandler):
  
  def get(self): 

    bgcolor = self.request.get("bc")
    if(bgcolor == ""): 
      bgcolor = "eeeeff"
    fcolor = self.request.get("fc")
    if(fcolor == ""): 
      fcolor = "000000"

    template_values = dict()
    template_values["bgcolor"] = bgcolor
    template_values["fcolor"] = fcolor

    c = None
    if self.request.get("cm"):
      c = model.Key(urlsafe=self.request.get("cm")).get()
    
    self.createStat(self.request,c,template_values)
    
    t = ""
    if self.request.get("t") == "c":
      t = "_" + self.request.get("t")

    template_values["wcontent"] = "stat" + t + ".html"
    
    if self.request.get("i") == "n":
      path = os.path.join(os.path.dirname(__file__), '../templates/widget/' + template_values["wcontent"])
    else:
      path = os.path.join(os.path.dirname(__file__), '../templates/widget/wstat.html')
    self.response.out.write(template.render(path, template_values))

  def createStat(self,request,c,template_values):

    now = datetime.now().date()
    year = now.year
    if now.month <= 9: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1

    stats = memcache.get("statAll")
    if not stats:
      logging.info("statAll miss")
      stats = StatisticheIspezioni.get_cc_cm_time(timeId=year).get()
      memcache.set("statAll", stats, 3600)

    statCC = None
    statCM = None
    if c:
      statCC = memcache.get("statCC" + str(c.centroCucina.key()))
      if not statCC:
        logging.info("statCC miss")
        statCC = StatisticheIspezioni.get_cc_cm_time(cc=c.centroCucina, timeId=year).get()
        memcache.set("statCC" + str(c.centroCucina.key()), statCC, 3600)
      statCM = memcache.get("statCM" + str(c.key()))
      if not statCM:
        logging.info("statCM miss")
        statCM = StatisticheIspezioni.StatisticheIspezioni.get_cc_cm_time(cm=c, timeId=year).get()
        memcache.set("statCM" + str(c.key()), statCM, 3600)
      
    template_values["stats"] = stats
    template_values["statCC"] = statCC
    template_values["statCM"] = statCM

class WidgetListitem:
  item = None
  date = None
  def __init__(self,item,date):
    self.item=item
    self.date=date
  def scuola(self):
    return self.item.commissione.tipoScuola + " " + self.item.commissione.nome
  def tipo(self):
    if isinstance(self.item, Ispezione):
      return "Ispezione"
    if isinstance(self.item, Nonconformita):
      return "Non Conformità"
    if isinstance(self.item, Dieta):
      return "Ispezione Diete speciali"
    if isinstance(self.item, Nota):
      return "Note"
    return ""
  def date(self):
    if isinstance(self.item, Ispezione):
      return self.item.dataIspezione
    if isinstance(self.item, Nonconformita):
      return self.item.dataNonconf
    if isinstance(self.item, Dieta):
      return self.item.dataIspezione
    if isinstance(self.item, Nota):
      return self.item.dataNota
    
  def url(self):
    u = "../public/"
    if isinstance(self.item, Ispezione):
      u += "isp?key="
    if isinstance(self.item, Nonconformita):
      u += "nc?key="
    if isinstance(self.item, Dieta):
      u += "dieta?key="
    if isinstance(self.item, Nota):
      u += "nota?key="
    u += str(self.item.key())
    return u

  
class CMListWidgetHandler(BasePage):
  
  def get(self): 
    template_values = dict()

    bgcolor = self.request.get("bc")
    if(bgcolor is None): 
      bgcolor = "eeeeff"
    fcolor = self.request.get("fc")
    if(fcolor is None): 
      fcolor = "000000"

    template_values["bgcolor"] = bgcolor
    template_values["fcolor"] = fcolor
    
    items=list()
    cm = Commissione.get(self.request.get("cm"))
    if cm:      
      cmk = model.Key(urlsafe=cm)
      isps = Ispezione.get_by_cm(cmk)
      for isp in isps:
        items.append(WidgetListitem(isp, isp.dataIspezione))
      
      ncs = Nonconformita.get_by_cm(cmk)
      for nc in ncs:
        items.append(WidgetListitem(item=nc, date=nc.dataNonconf))

      diete = Dieta.get_by_cm(cmk)
      for dieta in diete:
        items.append(WidgetListitem(item=dieta, date=dieta.dataIspezione))

      note = Nota.get_by_cm(cmk)
      for nota in note:
        items.append(WidgetListitem(item=nota, date=nota.dataNota))
        
      items = sorted(items, key=lambda item: item.date, reverse=True)
    
    template_values["host"] = self.getHost()
    template_values["items"] = items
    template_values["scuola"] = cmk.get().desc()

    path = os.path.join(os.path.dirname(__file__), '../templates/widget/list.html')
    self.response.out.write(template.render(path, template_values))

class CMGadgetHandler(BasePage):
  
  def get(self): 
    template_values = dict()
    template_values["main"] = "../templates/widget/gadget.xml"
    template_values["host"] = self.getHost()
    template_values["cms"] = Commissione.all().order("nome")
    self.getBase(template_values)
    
        
class CMWidgetHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "widget/widgetindex.html"
    template_values["host"] = self.getHost()
    self.getBase(template_values)
    
app = webapp.WSGIApplication([
  ('/widget/get', CMWidgetHandler),
  ('/widget/menu', CMMenuWidgetHandler),
  ('/widget/stat', CMStatWidgetHandler),
  ('/widget/list', CMListWidgetHandler),
  ('/widget/gadget', CMGadgetHandler),
  ('/widget/getcm', CMCommissioniDataHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'))
    
def main():
  app.run();

if __name__ == "__main__":
  main()