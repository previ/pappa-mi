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
from py.form import CommissioneForm
from py.gviz_api import *
from py.main import BasePage


TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class CMStatsHandlerOld(BasePage):
    
  def get(self):
    template_values = dict()
    template_values["content"] = "statistiche.html"
    self.getBase(template_values)

class CMStatsHandler(BasePage):
    
  def get(self):
    cm = None
    cc = None
    statCC = None
    statCM = None
    stat = StatisticheIspezioni.all().filter("commissione",None).filter("centroCucina", None).get()
    if(self.request.get("cm")):
      cm = Commissione.get(self.request.get("cm"))
      cc = cm.centroCucina
      statCC = StatisticheIspezioni.all().filter("centroCucina",cc).get()
      statCM = StatisticheIspezioni.all().filter("commissione",cm).get()

    pa_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 25%"),
               "2": ("number", "25% < 50%"),
               "3": ("number", "50% < 75%"),
               "4": ("number", ">75%")}

    pa_data = list()
    pa_data.append({"group": ("Tutte"), "1": stat.primoGradimento1Norm(), "2": stat.primoGradimento2Norm(), "3": stat.primoGradimento3Norm(), "4": stat.primoGradimento4Norm()})
    if(statCC):
      pa_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoGradimento1Norm(), "2": statCC.primoGradimento2Norm(), "3": statCC.primoGradimento3Norm(), "4": statCC.primoGradimento4Norm()})
    if(statCM):
      pa_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoGradimento1Norm(), "2": statCM.primoGradimento2Norm(), "3": statCM.primoGradimento3Norm(), "4": statCM.primoGradimento4Norm()})
    
    pa_table = DataTable(pa_desc)
    pa_table.LoadData(pa_data)

    pg_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Non Accettabile"),
               "2": ("number", "Accettabile"),
               "3": ("number", "Gradevole")}

    pg_data = list()
    pg_data.append({"group": ("Tutte"), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    if(statCC):
      pg_data.append({"group": (statCC.centroCucina.nome), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    if(statCM):
      pg_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    
    pg_table = DataTable(pg_desc)
    pg_table.LoadData(pg_data)
    
    template_values = dict()
    template_values["content"] = "stats/statindex.html"
    template_values["pa_table"] = pa_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["pg_table"] = pg_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["stat"] = stat
    template_values["statCC"] = statCC
    template_values["statCM"] = statCM
    self.getBase(template_values)

class CMStatsDataHandler(BasePage):
    
  def get(self):
    path = os.path.join(os.path.dirname(__file__), '../templates/stats/statdata.js')
    self.response.out.write(template.render(path, template_values))
    
class CMStatCalcHandler(BasePage):
  def get(self):
    stats = StatisticheIspezioni()
    statCM = StatisticheIspezioni()
    statCC = StatisticheIspezioni()
    statsCM = dict()
    statsCC = dict()

    #for c in Commissione.all() :
    #  if c.numCommissari > 0:
    #    stats.numeroCommissioni = stats.numeroCommissioni + 1

    stats.dataInizio = datetime.datetime(year=2009, month=9, day=1).date()
    stats.dataFine = datetime.datetime.now().date()
    for isp in Ispezione.all().filter("dataIspezione >", stats.dataInizio):
      if( isp.commissione.key() not in statsCM ):          
        statCM = StatisticheIspezioni()
        statCM.dataInizio = stats.dataInizio
        statCM.dataFine = stats.dataFine
        statCM.commissione = isp.commissione
        statsCM[statCM.commissione.key()] = statCM
      else:
        statCM = statsCM[isp.commissione.key()]
        
      if( isp.commissione.centroCucina.key() not in statsCC ):
        statCC = StatisticheIspezioni()
        statCC.dataInizio = stats.dataInizio
        statCC.dataFine = stats.dataFine
        statCC.centroCucina = isp.commissione.centroCucina
        statsCC[statCC.centroCucina.key()] = statCC
      else:
        statCC = statsCC[isp.commissione.centroCucina.key()]
        
      self.calc(isp,statCM)
      self.calc(isp,statCC)
      self.calc(isp,stats)
      
    if stats.numeroSchede > 0 :
      self.comp(stats)
      stats.put()
      
    for stat in statsCM.values() :
      self.comp(stat)
      stat.put()

    for stat in statsCC.values() :
      self.comp(stat)
      stat.put()
      

  def calc(self, isp, stats):
    stats.numeroSchede = stats.numeroSchede + 1;
    
    if(isp.primoAssaggio == 1):
      stats.primoAssaggio1 = stats.primoAssaggio1 + isp.primoAssaggio
    if(isp.primoAssaggio == 2):
      stats.primoAssaggio2 = stats.primoAssaggio2 + isp.primoAssaggio
    if(isp.primoAssaggio == 3):
      stats.primoAssaggio3 = stats.primoAssaggio3 + isp.primoAssaggio

    if(isp.primoGradimento == 1):
      stats.primoGradimento1 = stats.primoGradimento1 + isp.primoGradimento
    if(isp.primoGradimento == 2):
      stats.primoGradimento2 = stats.primoGradimento2 + isp.primoGradimento
    if(isp.primoGradimento == 3):
      stats.primoGradimento3 = stats.primoGradimento3 + isp.primoGradimento
    if(isp.primoGradimento == 4):
      stats.primoGradimento4 = stats.primoGradimento4 + isp.primoGradimento

    if(isp.primoCottura == 1):
      stats.primoCottura1 = stats.primoCottura1 + isp.primoCottura
    if(isp.primoCottura == 2):
      stats.primoCottura2 = stats.primoCottura2 + isp.primoCottura
    if(isp.primoCottura == 3):
      stats.primoCottura3 = stats.primoCottura3 + isp.primoCottura

    if(isp.primoTemperatura == 1):
      stats.primoTemperatura1 = stats.primoTemperatura1 + isp.primoTemperatura
    if(isp.primoTemperatura == 2):
      stats.primoTemperatura2 = stats.primoTemperatura2 + isp.primoTemperatura
    if(isp.primoTemperatura == 3):
      stats.primoTemperatura3 = stats.primoTemperatura3 + isp.primoTemperatura

    if(isp.primoQuantita == 1):
      stats.primoQuantita1 = stats.primoQuantita1 + isp.primoQuantita
    if(isp.primoQuantita == 2):
      stats.primoQuantita2 = stats.primoQuantita2 + isp.primoQuantita
    if(isp.primoQuantita == 3):
      stats.primoQuantita3 = stats.primoQuantita3 + isp.primoQuantita
      
    if(isp.secondoAssaggio == 1):
      stats.secondoAssaggio1 = stats.secondoAssaggio1 + isp.secondoAssaggio
    if(isp.secondoAssaggio == 2):
      stats.secondoAssaggio2 = stats.secondoAssaggio2 + isp.secondoAssaggio
    if(isp.secondoAssaggio == 3):
      stats.secondoAssaggio3 = stats.secondoAssaggio3 + isp.secondoAssaggio

    if(isp.secondoGradimento == 1):
      stats.secondoGradimento1 = stats.secondoGradimento1 + isp.secondoGradimento
    if(isp.secondoGradimento == 2):
      stats.secondoGradimento2 = stats.secondoGradimento2 + isp.secondoGradimento
    if(isp.secondoGradimento == 3):
      stats.secondoGradimento3 = stats.secondoGradimento3 + isp.secondoGradimento
    if(isp.secondoGradimento == 4):
      stats.secondoGradimento4 = stats.secondoGradimento4 + isp.secondoGradimento

    if(isp.secondoCottura == 1):
      stats.secondoCottura1 = stats.secondoCottura1 + isp.secondoCottura
    if(isp.secondoCottura == 2):
      stats.secondoCottura2 = stats.secondoCottura2 + isp.secondoCottura
    if(isp.secondoCottura == 3):
      stats.secondoCottura3 = stats.secondoCottura3 + isp.secondoCottura

    if(isp.secondoTemperatura == 1):
      stats.secondoTemperatura1 = stats.secondoTemperatura1 + isp.secondoTemperatura
    if(isp.secondoTemperatura == 2):
      stats.secondoTemperatura2 = stats.secondoTemperatura2 + isp.secondoTemperatura
    if(isp.secondoTemperatura == 3):
      stats.secondoTemperatura3 = stats.secondoTemperatura3 + isp.secondoTemperatura

    if(isp.secondoQuantita == 1):
      stats.secondoQuantita1 = stats.secondoQuantita1 + isp.secondoQuantita
    if(isp.secondoQuantita == 2):
      stats.secondoQuantita2 = stats.secondoQuantita2 + isp.secondoQuantita
    if(isp.secondoQuantita == 3):
      stats.secondoQuantita3 = stats.secondoQuantita3 + isp.secondoQuantita

    if(isp.contornoAssaggio == 1):
      stats.contornoAssaggio1 = stats.contornoAssaggio1 + isp.contornoAssaggio
    if(isp.contornoAssaggio == 2):
      stats.contornoAssaggio2 = stats.contornoAssaggio2 + isp.contornoAssaggio
    if(isp.contornoAssaggio == 3):
      stats.contornoAssaggio3 = stats.contornoAssaggio3 + isp.contornoAssaggio

    if(isp.contornoGradimento == 1):
      stats.contornoGradimento1 = stats.contornoGradimento1 + isp.contornoGradimento
    if(isp.contornoGradimento == 2):
      stats.contornoGradimento2 = stats.contornoGradimento2 + isp.contornoGradimento
    if(isp.contornoGradimento == 3):
      stats.contornoGradimento3 = stats.contornoGradimento3 + isp.contornoGradimento
    if(isp.contornoGradimento == 4):
      stats.contornoGradimento4 = stats.contornoGradimento4 + isp.contornoGradimento

    if(isp.contornoCottura == 1):
      stats.contornoCottura1 = stats.contornoCottura1 + isp.contornoCottura
    if(isp.contornoCottura == 2):
      stats.contornoCottura2 = stats.contornoCottura2 + isp.contornoCottura
    if(isp.contornoCottura == 3):
      stats.contornoCottura3 = stats.contornoCottura3 + isp.contornoCottura

    if(isp.contornoTemperatura == 1):
      stats.contornoTemperatura1 = stats.contornoTemperatura1 + isp.contornoTemperatura
    if(isp.contornoTemperatura == 2):
      stats.contornoTemperatura2 = stats.contornoTemperatura2 + isp.contornoTemperatura
    if(isp.contornoTemperatura == 3):
      stats.contornoTemperatura3 = stats.contornoTemperatura3 + isp.contornoTemperatura

    if(isp.contornoQuantita == 1):
      stats.contornoQuantita1 = stats.contornoQuantita1 + isp.contornoQuantita
    if(isp.contornoQuantita == 2):
      stats.contornoQuantita2 = stats.contornoQuantita2 + isp.contornoQuantita
    if(isp.contornoQuantita == 3):
      stats.contornoQuantita3 = stats.contornoQuantita3 + isp.contornoQuantita

    if(isp.paneAssaggio == 1):
      stats.paneAssaggio1 = stats.paneAssaggio1 + isp.paneAssaggio
    if(isp.paneAssaggio == 2):
      stats.paneAssaggio2 = stats.paneAssaggio2 + isp.paneAssaggio
    if(isp.paneAssaggio == 3):
      stats.paneAssaggio3 = stats.paneAssaggio3 + isp.paneAssaggio

    if(isp.paneGradimento == 1):
      stats.paneGradimento1 = stats.paneGradimento1 + isp.paneGradimento
    if(isp.paneGradimento == 2):
      stats.paneGradimento2 = stats.paneGradimento2 + isp.paneGradimento
    if(isp.paneGradimento == 3):
      stats.paneGradimento3 = stats.paneGradimento3 + isp.paneGradimento
    if(isp.paneGradimento == 4):
      stats.paneGradimento4 = stats.paneGradimento4 + isp.paneGradimento

    if(isp.paneQuantita == 1):
      stats.paneQuantita1 = stats.paneQuantita1 + isp.paneQuantita
    if(isp.paneQuantita == 2):
      stats.paneQuantita2 = stats.paneQuantita2 + isp.paneQuantita
    if(isp.paneQuantita == 3):
      stats.paneQuantita3 = stats.paneQuantita3 + isp.paneQuantita

    if(isp.fruttaAssaggio == 1):
      stats.fruttaAssaggio1 = stats.fruttaAssaggio1 + isp.fruttaAssaggio
    if(isp.fruttaAssaggio == 2):
      stats.fruttaAssaggio2 = stats.fruttaAssaggio2 + isp.fruttaAssaggio
    if(isp.fruttaAssaggio == 3):
      stats.fruttaAssaggio3 = stats.fruttaAssaggio3 + isp.fruttaAssaggio

    if(isp.fruttaGradimento == 1):
      stats.fruttaGradimento1 = stats.fruttaGradimento1 + isp.fruttaGradimento
    if(isp.fruttaGradimento == 2):
      stats.fruttaGradimento2 = stats.fruttaGradimento2 + isp.fruttaGradimento
    if(isp.fruttaGradimento == 3):
      stats.fruttaGradimento3 = stats.fruttaGradimento3 + isp.fruttaGradimento
    if(isp.fruttaGradimento == 4):
      stats.fruttaGradimento4 = stats.fruttaGradimento4 + isp.fruttaGradimento

    if(isp.fruttaMaturazione == 1):
      stats.fruttaMaturazione1 = stats.fruttaMaturazione1 + isp.fruttaMaturazione
    if(isp.fruttaMaturazione == 2):
      stats.fruttaMaturazione2 = stats.fruttaMaturazione2 + isp.fruttaMaturazione
    if(isp.fruttaMaturazione == 3):
      stats.fruttaMaturazione3 = stats.fruttaMaturazione3 + isp.fruttaMaturazione

    if(isp.fruttaQuantita == 1):
      stats.fruttaQuantita1 = stats.fruttaQuantita1 + isp.fruttaQuantita
    if(isp.fruttaQuantita == 2):
      stats.fruttaQuantita2 = stats.fruttaQuantita2 + isp.fruttaQuantita
    if(isp.fruttaQuantita == 3):
      stats.fruttaQuantita3 = stats.fruttaQuantita3 + isp.fruttaQuantita

    if(isp.puliziaCentroCottura == 1):
      stats.puliziaCentroCottura1 = stats.puliziaCentroCottura1 + isp.puliziaCentroCottura
    if(isp.puliziaCentroCottura == 2):
      stats.puliziaCentroCottura2 = stats.puliziaCentroCottura2 + isp.puliziaCentroCottura
    if(isp.puliziaCentroCottura == 3):
      stats.puliziaCentroCottura3 = stats.puliziaCentroCottura3 + isp.puliziaCentroCottura
    if(isp.puliziaCentroCottura == 4):
      stats.puliziaCentroCottura4 = stats.puliziaCentroCottura4 + isp.puliziaCentroCottura

    if(isp.puliziaRefettorio == 1):
      stats.puliziaRefettorio1 = stats.puliziaRefettorio1 + isp.puliziaRefettorio
    if(isp.puliziaRefettorio == 2):
      stats.puliziaRefettorio2 = stats.puliziaRefettorio2 + isp.puliziaRefettorio
    if(isp.puliziaRefettorio == 3):
      stats.puliziaRefettorio3 = stats.puliziaRefettorio3 + isp.puliziaRefettorio
    if(isp.puliziaRefettorio == 4):
      stats.puliziaRefettorio4 = stats.puliziaRefettorio4 + isp.puliziaRefettorio

    if(isp.smaltimentoRifiuti == 1):
      stats.smaltimentoRifiuti1 = stats.smaltimentoRifiuti1 + isp.smaltimentoRifiuti
    if(isp.smaltimentoRifiuti == 2):
      stats.smaltimentoRifiuti2 = stats.smaltimentoRifiuti2 + isp.smaltimentoRifiuti
    if(isp.smaltimentoRifiuti == 3):
      stats.smaltimentoRifiuti3 = stats.smaltimentoRifiuti3 + isp.smaltimentoRifiuti
    if(isp.smaltimentoRifiuti == 4):
      stats.smaltimentoRifiuti4 = stats.smaltimentoRifiuti4 + isp.smaltimentoRifiuti
      
    if(isp.giudizioGlobale == 1):
      stats.giudizioGlobale1 = stats.giudizioGlobale1 + isp.giudizioGlobale
    if(isp.giudizioGlobale == 2):
      stats.giudizioGlobale2 = stats.giudizioGlobale2 + isp.giudizioGlobale
    if(isp.giudizioGlobale == 3):
      stats.giudizioGlobale3 = stats.giudizioGlobale3 + isp.giudizioGlobale

  def comp(self, stats):
    stats.primoAssaggio = float(stats.primoAssaggio1 + stats.primoAssaggio2 + stats.primoAssaggio3) / stats.numeroSchede
    stats.primoGradimento = float(stats.primoGradimento1 + stats.primoGradimento2 + stats.primoGradimento3 + stats.primoGradimento4) / stats.numeroSchede
    stats.secondoAssaggio = float(stats.secondoAssaggio1 + stats.secondoAssaggio2 + stats.secondoAssaggio3) / stats.numeroSchede
    stats.secondoGradimento = float(stats.secondoGradimento1 + stats.secondoGradimento2 + stats.secondoGradimento3 + stats.secondoGradimento4) / stats.numeroSchede
    stats.contornoAssaggio = float(stats.contornoAssaggio1 + stats.contornoAssaggio2 + stats.contornoAssaggio3) / stats.numeroSchede
    stats.contornoGradimento = float(stats.contornoGradimento1 + stats.contornoGradimento2 + stats.contornoGradimento3 + stats.contornoGradimento4) / stats.numeroSchede
    stats.paneAssaggio = float(stats.paneAssaggio1 + stats.paneAssaggio2 + stats.paneAssaggio3) / stats.numeroSchede
    stats.paneGradimento = float(stats.paneGradimento1 + stats.paneGradimento2 + stats.paneGradimento3  + stats.paneGradimento4) / stats.numeroSchede
    stats.fruttaAssaggio = float(stats.fruttaAssaggio1 + stats.fruttaAssaggio2 + stats.fruttaAssaggio3) / stats.numeroSchede
    stats.fruttaGradimento = float(stats.fruttaGradimento1 + stats.fruttaGradimento2 + stats.fruttaGradimento3 + stats.fruttaGradimento4) / stats.numeroSchede

    stats.puliziaRefettorio = float(stats.puliziaRefettorio1 + stats.puliziaRefettorio2 + stats.puliziaRefettorio3 + stats.puliziaRefettorio4) / stats.numeroSchede
    stats.puliziaCentroCottura = float(stats.puliziaCentroCottura1 + stats.puliziaCentroCottura2 + stats.puliziaCentroCottura3 + stats.puliziaCentroCottura4) / stats.numeroSchede
    stats.smaltimentoRifiuti = float(stats.smaltimentoRifiuti1 + stats.smaltimentoRifiuti2 + stats.smaltimentoRifiuti3 + stats.smaltimentoRifiuti4) / stats.numeroSchede
    stats.giudizioGlobale = float(stats.giudizioGlobale1 + stats.giudizioGlobale2 + stats.giudizioGlobale3) / stats.numeroSchede
  
class CMStatCalcHandlerOld(BasePage):
  def get(self):
    logging.info("CMStatCalcHandler")
    self.calc(date(year=2009, month=1,day=1),date(year=2010, month=12,day=31) )
    self.redirect("/")
  def calc(self, inizio, fine):
    attrs = {"puliziaCentroCottura": StatisticheIspezioni(),
             "puliziaRefettorio": StatisticheIspezioni(),
             "arrivoDist": StatisticheIspezioni(),
             "primoDist": StatisticheIspezioni(),
             "primoCondito": StatisticheIspezioni(),
             "primoCottura": StatisticheIspezioni(),
             "primoTemperatura": StatisticheIspezioni(),
             "primoQuantita": StatisticheIspezioni(),
             "primoAssaggio": StatisticheIspezioni(),
             "primoGradimento": StatisticheIspezioni(),
             "secondoDist": StatisticheIspezioni(),
             "secondoCottura": StatisticheIspezioni(),
             "secondoTemperatura": StatisticheIspezioni(),
             "secondoQuantita": StatisticheIspezioni(),
             "secondoAssaggio": StatisticheIspezioni(),
             "secondoGradimento": StatisticheIspezioni(),
             "contornoCondito": StatisticheIspezioni(),
             "contornoCottura": StatisticheIspezioni(),
             "contornoTemperatura": StatisticheIspezioni(),
             "contornoQuantita": StatisticheIspezioni(),
             "contornoAssaggio": StatisticheIspezioni(),
             "contornoGradimento": StatisticheIspezioni(),
             "paneServito": StatisticheIspezioni(),
             "paneQuantita": StatisticheIspezioni(),
             "paneAssaggio": StatisticheIspezioni(),
             "paneGradimento": StatisticheIspezioni(),
             "fruttaQuantita": StatisticheIspezioni(),
             "fruttaAssaggio": StatisticheIspezioni(),
             "fruttaGradimento": StatisticheIspezioni(),
             "fruttaMaturazione": StatisticheIspezioni(),
             "durataPasto": StatisticheIspezioni(),
             "smaltimentoRifiuti": StatisticheIspezioni(),
             "giudizioGlobale": StatisticheIspezioni()}
    
    for attr, stat in attrs.iteritems():
      stat.nomeValore = attr;
      stat.dataInizio = inizio
      stat.datafine = fine
      stat.numeroSchede = long(0)
      stat.totaleSomma = long(0)
      stat.valoreSomma1 = long(0)
      stat.valoreSomma2 = long(0)
      stat.valoreSomma3 = long(0)
      stat.valoreSomma4 = long(0)
      stat.valoreSomma5 = long(0)

    for isp in Ispezione.all().filter("dataIspezione >=",inizio).filter("dataIspezione <=",fine):
      for attr, stat in attrs.iteritems():
        stat.numeroSchede = stat.numeroSchede + 1
        stat.totaleSomma = stat.totaleSomma + long(getattr(isp, attr))
        stat.valoreSomma1 = stat.valoreSomma1 + 1 if getattr(isp, attr) == 1 else 0
        stat.valoreSomma2 = stat.valoreSomma2 + 1 if getattr(isp, attr) == 2 else 0
        stat.valoreSomma3 = stat.valoreSomma3 + 1 if getattr(isp, attr) == 3 else 0
        stat.valoreSomma4 = stat.valoreSomma4 + 1 if getattr(isp, attr) == 4 else 0
        stat.valoreSomma5 = stat.valoreSomma5 + 1 if getattr(isp, attr) == 5 else 0
    for attr, stat in attrs.iteritems():
      stat.put()

class CMStatsHandlerOld(BasePage):

  def getStats(self):

    stats = memcache.get("stats")
    statsMese = memcache.get("statsMese")
    if(stats is None):
      stats = Statistiche()

      for c in Commissione.all() :
        if c.numCommissari > 0:
          stats.numeroCommissioni = stats.numeroCommissioni + 1
          
      for isp in Ispezione.all().order("-dataIspezione"):
        stats.numeroSchede = stats.numeroSchede + 1;
            
      memcache.add("stats", stats)
    
    return stats
  
  @login_required
  def get(self):
    user = users.get_current_user()
    commissario = Commissario.all().filter("user", user).filter("stato", 1).get()
    if(commissario is None):
      self.redirect("/")

    template_values = dict()
    template_values["content"] = "stats/statindex.html"
    self.getBase(template_values)
      
application = webapp.WSGIApplication([
  ('/stats', CMStatsHandler),
  ('/stats/calc', CMStatCalcHandler),
  ('/stats/getdata', CMStatsDataHandler),
], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
    