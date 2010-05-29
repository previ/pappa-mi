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
from google.appengine.api.labs.taskqueue import Task, Queue

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

    pg_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 25%"),
               "2": ("number", "25% < 50%"),
               "3": ("number", "50% < 75%"),
               "4": ("number", ">75%")}

    pg_data = list()
    pg_data.append({"group": ("Tutte"), "1": stat.primoGradimento1Norm(), "2": stat.primoGradimento2Norm(), "3": stat.primoGradimento3Norm(), "4": stat.primoGradimento4Norm()})
    if(statCC):
      pg_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoGradimento1Norm(), "2": statCC.primoGradimento2Norm(), "3": statCC.primoGradimento3Norm(), "4": statCC.primoGradimento4Norm()})
    if(statCM):
      pg_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoGradimento1Norm(), "2": statCM.primoGradimento2Norm(), "3": statCM.primoGradimento3Norm(), "4": statCM.primoGradimento4Norm()})
    
    pg_table = DataTable(pg_desc)
    pg_table.LoadData(pg_data)

    pa_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Non Accettabile"),
               "2": ("number", "Accettabile"),
               "3": ("number", "Gradevole")}

    pa_data = list()
    pa_data.append({"group": ("Tutte"), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    if(statCC):
      pa_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoAssaggio1Norm(), "2": statCC.primoAssaggio2Norm(), "3": statCC.primoAssaggio3Norm()})
    if(statCM):
      pa_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoAssaggio1Norm(), "2": statCM.primoAssaggio2Norm(), "3": statCM.primoAssaggio3Norm()})
    
    pa_table = DataTable(pa_desc)
    pa_table.LoadData(pa_data)

    pc_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarsa"),
               "2": ("number", "Corretta"),
               "3": ("number", "Eccessiva")}

    pc_data = list()
    pc_data.append({"group": ("Tutte"), "1": stat.primoCottura1Norm(), "2": stat.primoCottura2Norm(), "3": stat.primoCottura3Norm()})
    if(statCC):
      pc_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoCottura1Norm(), "2": statCC.primoCottura2Norm(), "3": statCC.primoCottura3Norm()})
    if(statCM):
      pc_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoCottura1Norm(), "2": statCM.primoCottura2Norm(), "3": statCM.primoCottura3Norm()})
    
    pc_table = DataTable(pc_desc)
    pc_table.LoadData(pc_data)

    pt_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Freddo"),
               "2": ("number", "Corretta"),
               "3": ("number", "Caldo")}

    pt_data = list()
    pt_data.append({"group": ("Tutte"), "1": stat.primoTemperatura1Norm(), "2": stat.primoTemperatura2Norm(), "3": stat.primoTemperatura3Norm()})
    if(statCC):
      pt_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoTemperatura1Norm(), "2": statCC.primoTemperatura2Norm(), "3": statCC.primoTemperatura3Norm()})
    if(statCM):
      pt_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoTemperatura1Norm(), "2": statCM.primoTemperatura2Norm(), "3": statCM.primoTemperatura3Norm()})
    
    pt_table = DataTable(pt_desc)
    pt_table.LoadData(pt_data)
    
    pq_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Giusta"),
               "3": ("number", "Abbondante")}

    pq_data = list()
    pq_data.append({"group": ("Tutte"), "1": stat.primoQuantita1Norm(), "2": stat.primoQuantita2Norm(), "3": stat.primoQuantita3Norm()})
    if(statCC):
      pq_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoQuantita1Norm(), "2": statCC.primoQuantita2Norm(), "3": statCC.primoQuantita3Norm()})
    if(statCM):
      pq_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoQuantita1Norm(), "2": statCM.primoQuantita2Norm(), "3": statCM.primoQuantita3Norm()})
    
    pq_table = DataTable(pq_desc)
    pq_table.LoadData(pq_data)

    pd_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 10min"),
               "2": ("number", "10min - 20min"),
               "3": ("number", "> 20min")}

    pd_data = list()
    pd_data.append({"group": ("Tutte"), "1": stat.primoDistribuzione1Norm(), "2": stat.primoDistribuzione2Norm(), "3": stat.primoDistribuzione3Norm()})
    if(statCC):
      pd_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoDistribuzione1Norm(), "2": statCC.primoDistribuzione2Norm(), "3": statCC.primoDistribuzione3Norm()})
    if(statCM):
      pd_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoDistribuzione1Norm(), "2": statCM.primoDistribuzione2Norm(), "3": statCM.primoDistribuzione3Norm()})
    
    pd_table = DataTable(pd_desc)
    pd_table.LoadData(pd_data)

    sg_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 25%"),
               "2": ("number", "25% < 50%"),
               "3": ("number", "50% < 75%"),
               "4": ("number", ">75%")}

    sg_data = list()
    sg_data.append({"group": ("Tutte"), "1": stat.primoGradimento1Norm(), "2": stat.primoGradimento2Norm(), "3": stat.primoGradimento3Norm(), "4": stat.primoGradimento4Norm()})
    if(statCC):
      sg_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoGradimento1Norm(), "2": statCC.primoGradimento2Norm(), "3": statCC.primoGradimento3Norm(), "4": statCC.primoGradimento4Norm()})
    if(statCM):
      sg_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoGradimento1Norm(), "2": statCM.primoGradimento2Norm(), "3": statCM.primoGradimento3Norm(), "4": statCM.primoGradimento4Norm()})
    
    sg_table = DataTable(sg_desc)
    sg_table.LoadData(sg_data)

    sa_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Non Accettabile"),
               "2": ("number", "Accettabile"),
               "3": ("number", "Gradevole")}

    sa_data = list()
    sa_data.append({"group": ("Tutte"), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    if(statCC):
      sa_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoAssaggio1Norm(), "2": statCC.primoAssaggio2Norm(), "3": statCC.primoAssaggio3Norm()})
    if(statCM):
      sa_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoAssaggio1Norm(), "2": statCM.primoAssaggio2Norm(), "3": statCM.primoAssaggio3Norm()})
    
    sa_table = DataTable(sa_desc)
    sa_table.LoadData(sa_data)

    sc_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarsa"),
               "2": ("number", "Corretta"),
               "3": ("number", "Eccessiva")}

    sc_data = list()
    sc_data.append({"group": ("Tutte"), "1": stat.primoCottura1Norm(), "2": stat.primoCottura2Norm(), "3": stat.primoCottura3Norm()})
    if(statCC):
      sc_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoCottura1Norm(), "2": statCC.primoCottura2Norm(), "3": statCC.primoCottura3Norm()})
    if(statCM):
      sc_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoCottura1Norm(), "2": statCM.primoCottura2Norm(), "3": statCM.primoCottura3Norm()})
    
    sc_table = DataTable(sc_desc)
    sc_table.LoadData(sc_data)

    st_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Freddo"),
               "2": ("number", "Corretta"),
               "3": ("number", "Caldo")}

    st_data = list()
    st_data.append({"group": ("Tutte"), "1": stat.primoTemperatura1Norm(), "2": stat.primoTemperatura2Norm(), "3": stat.primoTemperatura3Norm()})
    if(statCC):
      st_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoTemperatura1Norm(), "2": statCC.primoTemperatura2Norm(), "3": statCC.primoTemperatura3Norm()})
    if(statCM):
      st_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoTemperatura1Norm(), "2": statCM.primoTemperatura2Norm(), "3": statCM.primoTemperatura3Norm()})
    
    st_table = DataTable(st_desc)
    st_table.LoadData(st_data)
    
    sq_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Giusta"),
               "3": ("number", "Abbondante")}

    sq_data = list()
    sq_data.append({"group": ("Tutte"), "1": stat.primoQuantita1Norm(), "2": stat.primoQuantita2Norm(), "3": stat.primoQuantita3Norm()})
    if(statCC):
      sq_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoQuantita1Norm(), "2": statCC.primoQuantita2Norm(), "3": statCC.primoQuantita3Norm()})
    if(statCM):
      sq_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoQuantita1Norm(), "2": statCM.primoQuantita2Norm(), "3": statCM.primoQuantita3Norm()})
    
    sq_table = DataTable(sq_desc)
    sq_table.LoadData(sq_data)

    sd_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 10min"),
               "2": ("number", "10min - 20min"),
               "3": ("number", "> 20min")}

    sd_data = list()
    sd_data.append({"group": ("Tutte"), "1": stat.primoDistribuzione1Norm(), "2": stat.primoDistribuzione2Norm(), "3": stat.primoDistribuzione3Norm()})
    if(statCC):
      sd_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoDistribuzione1Norm(), "2": statCC.primoDistribuzione2Norm(), "3": statCC.primoDistribuzione3Norm()})
    if(statCM):
      sd_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoDistribuzione1Norm(), "2": statCM.primoDistribuzione2Norm(), "3": statCM.primoDistribuzione3Norm()})
    
    sd_table = DataTable(sd_desc)
    sd_table.LoadData(sd_data)

    cg_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 25%"),
               "2": ("number", "25% < 50%"),
               "3": ("number", "50% < 75%"),
               "4": ("number", ">75%")}

    cg_data = list()
    cg_data.append({"group": ("Tutte"), "1": stat.primoGradimento1Norm(), "2": stat.primoGradimento2Norm(), "3": stat.primoGradimento3Norm(), "4": stat.primoGradimento4Norm()})
    if(statCC):
      cg_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoGradimento1Norm(), "2": statCC.primoGradimento2Norm(), "3": statCC.primoGradimento3Norm(), "4": statCC.primoGradimento4Norm()})
    if(statCM):
      cg_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoGradimento1Norm(), "2": statCM.primoGradimento2Norm(), "3": statCM.primoGradimento3Norm(), "4": statCM.primoGradimento4Norm()})
    
    cg_table = DataTable(cg_desc)
    cg_table.LoadData(cg_data)

    ca_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Non Accettabile"),
               "2": ("number", "Accettabile"),
               "3": ("number", "Gradevole")}

    ca_data = list()
    ca_data.append({"group": ("Tutte"), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    if(statCC):
      ca_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoAssaggio1Norm(), "2": statCC.primoAssaggio2Norm(), "3": statCC.primoAssaggio3Norm()})
    if(statCM):
      ca_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoAssaggio1Norm(), "2": statCM.primoAssaggio2Norm(), "3": statCM.primoAssaggio3Norm()})
    
    ca_table = DataTable(ca_desc)
    ca_table.LoadData(ca_data)

    cc_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarsa"),
               "2": ("number", "Corretta"),
               "3": ("number", "Eccessiva")}

    cc_data = list()
    cc_data.append({"group": ("Tutte"), "1": stat.primoCottura1Norm(), "2": stat.primoCottura2Norm(), "3": stat.primoCottura3Norm()})
    if(statCC):
      cc_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoCottura1Norm(), "2": statCC.primoCottura2Norm(), "3": statCC.primoCottura3Norm()})
    if(statCM):
      cc_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoCottura1Norm(), "2": statCM.primoCottura2Norm(), "3": statCM.primoCottura3Norm()})
    
    cc_table = DataTable(cc_desc)
    cc_table.LoadData(cc_data)

    ct_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Freddo"),
               "2": ("number", "Corretta"),
               "3": ("number", "Caldo")}

    ct_data = list()
    ct_data.append({"group": ("Tutte"), "1": stat.primoTemperatura1Norm(), "2": stat.primoTemperatura2Norm(), "3": stat.primoTemperatura3Norm()})
    if(statCC):
      ct_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoTemperatura1Norm(), "2": statCC.primoTemperatura2Norm(), "3": statCC.primoTemperatura3Norm()})
    if(statCM):
      ct_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoTemperatura1Norm(), "2": statCM.primoTemperatura2Norm(), "3": statCM.primoTemperatura3Norm()})
    
    ct_table = DataTable(ct_desc)
    ct_table.LoadData(ct_data)
    
    cq_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Giusta"),
               "3": ("number", "Abbondante")}

    cq_data = list()
    cq_data.append({"group": ("Tutte"), "1": stat.primoQuantita1Norm(), "2": stat.primoQuantita2Norm(), "3": stat.primoQuantita3Norm()})
    if(statCC):
      cq_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoQuantita1Norm(), "2": statCC.primoQuantita2Norm(), "3": statCC.primoQuantita3Norm()})
    if(statCM):
      cq_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoQuantita1Norm(), "2": statCM.primoQuantita2Norm(), "3": statCM.primoQuantita3Norm()})
    
    cq_table = DataTable(cq_desc)
    cq_table.LoadData(cq_data)
    
    bg_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 25%"),
               "2": ("number", "25% < 50%"),
               "3": ("number", "50% < 75%"),
               "4": ("number", ">75%")}

    bg_data = list()
    bg_data.append({"group": ("Tutte"), "1": stat.primoGradimento1Norm(), "2": stat.primoGradimento2Norm(), "3": stat.primoGradimento3Norm(), "4": stat.primoGradimento4Norm()})
    if(statCC):
      bg_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoGradimento1Norm(), "2": statCC.primoGradimento2Norm(), "3": statCC.primoGradimento3Norm(), "4": statCC.primoGradimento4Norm()})
    if(statCM):
      bg_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoGradimento1Norm(), "2": statCM.primoGradimento2Norm(), "3": statCM.primoGradimento3Norm(), "4": statCM.primoGradimento4Norm()})
    
    bg_table = DataTable(bg_desc)
    bg_table.LoadData(bg_data)

    ba_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Non Accettabile"),
               "2": ("number", "Accettabile"),
               "3": ("number", "Gradevole")}

    ba_data = list()
    ba_data.append({"group": ("Tutte"), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    if(statCC):
      ba_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoAssaggio1Norm(), "2": statCC.primoAssaggio2Norm(), "3": statCC.primoAssaggio3Norm()})
    if(statCM):
      ba_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoAssaggio1Norm(), "2": statCM.primoAssaggio2Norm(), "3": statCM.primoAssaggio3Norm()})
    
    ba_table = DataTable(ba_desc)
    ba_table.LoadData(ba_data)
    
    bq_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Giusta"),
               "3": ("number", "Abbondante")}

    bq_data = list()
    bq_data.append({"group": ("Tutte"), "1": stat.primoQuantita1Norm(), "2": stat.primoQuantita2Norm(), "3": stat.primoQuantita3Norm()})
    if(statCC):
      bq_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoQuantita1Norm(), "2": statCC.primoQuantita2Norm(), "3": statCC.primoQuantita3Norm()})
    if(statCM):
      bq_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoQuantita1Norm(), "2": statCM.primoQuantita2Norm(), "3": statCM.primoQuantita3Norm()})
    
    bq_table = DataTable(bq_desc)
    bq_table.LoadData(bq_data)

    fg_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 25%"),
               "2": ("number", "25% < 50%"),
               "3": ("number", "50% < 75%"),
               "4": ("number", ">75%")}

    fg_data = list()
    fg_data.append({"group": ("Tutte"), "1": stat.primoGradimento1Norm(), "2": stat.primoGradimento2Norm(), "3": stat.primoGradimento3Norm(), "4": stat.primoGradimento4Norm()})
    if(statCC):
      fg_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoGradimento1Norm(), "2": statCC.primoGradimento2Norm(), "3": statCC.primoGradimento3Norm(), "4": statCC.primoGradimento4Norm()})
    if(statCM):
      fg_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoGradimento1Norm(), "2": statCM.primoGradimento2Norm(), "3": statCM.primoGradimento3Norm(), "4": statCM.primoGradimento4Norm()})
    
    fg_table = DataTable(fg_desc)
    fg_table.LoadData(fg_data)

    fa_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Non Accettabile"),
               "2": ("number", "Accettabile"),
               "3": ("number", "Gradevole")}

    fa_data = list()
    fa_data.append({"group": ("Tutte"), "1": stat.primoAssaggio1Norm(), "2": stat.primoAssaggio2Norm(), "3": stat.primoAssaggio3Norm()})
    if(statCC):
      fa_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoAssaggio1Norm(), "2": statCC.primoAssaggio2Norm(), "3": statCC.primoAssaggio3Norm()})
    if(statCM):
      fa_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoAssaggio1Norm(), "2": statCM.primoAssaggio2Norm(), "3": statCM.primoAssaggio3Norm()})
    
    fa_table = DataTable(fa_desc)
    fa_table.LoadData(fa_data)

    fm_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Freddo"),
               "2": ("number", "Corretta"),
               "3": ("number", "Caldo")}

    fm_data = list()
    fm_data.append({"group": ("Tutte"), "1": stat.primoTemperatura1Norm(), "2": stat.primoTemperatura2Norm(), "3": stat.primoTemperatura3Norm()})
    if(statCC):
      fm_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoTemperatura1Norm(), "2": statCC.primoTemperatura2Norm(), "3": statCC.primoTemperatura3Norm()})
    if(statCM):
      fm_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoTemperatura1Norm(), "2": statCM.primoTemperatura2Norm(), "3": statCM.primoTemperatura3Norm()})
    
    fm_table = DataTable(fm_desc)
    fm_table.LoadData(fm_data)
    
    fq_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Giusta"),
               "3": ("number", "Abbondante")}

    fq_data = list()
    fq_data.append({"group": ("Tutte"), "1": stat.primoQuantita1Norm(), "2": stat.primoQuantita2Norm(), "3": stat.primoQuantita3Norm()})
    if(statCC):
      fq_data.append({"group": (statCC.centroCucina.nome), "1": statCC.primoQuantita1Norm(), "2": statCC.primoQuantita2Norm(), "3": statCC.primoQuantita3Norm()})
    if(statCM):
      fq_data.append({"group": (statCM.commissione.nome + " " + statCM.commissione.tipoScuola), "1": statCM.primoQuantita1Norm(), "2": statCM.primoQuantita2Norm(), "3": statCM.primoQuantita3Norm()})
    
    fq_table = DataTable(fq_desc)
    fq_table.LoadData(fq_data)

    nc_desc = {"tipo": ("string", "Tipo"), 
               "count": ("number", "Occorrenze")}
    
    ncstat = StatisticheNonconf.all().filter("commissione", None).filter("centroCucina",None).order("-dataInizio").get()
    nc_data = list()
    nci = Nonconformita();
    for nd in ncstat.getTipiPos():
      nc_data.append({"tipo": nci.tipi()[nd], "count": ncstat.getData(nd)})
    nc_table = DataTable(nc_desc)
    nc_table.LoadData(nc_data)
    
    di_desc = {"time": ("string", "Settimane"), 
               "schede": ("number", "Schede"),
               "nonconf": ("number", "Non Conformita")}
    di_data = list()
    for w in range(len(ncstat.numeroNonconfSettimana)):
      di_data.append({"time": w, "schede": stat.numeroSchedeSettimana[w], "nonconf": ncstat.numeroNonconfSettimana[w]})
    di_table = DataTable(di_desc)
    di_table.LoadData(di_data)
    
    template_values = dict()
    template_values["di_table"] = di_table.ToJSon(columns_order=("time", "schede", "nonconf"))
    template_values["nc_table"] = nc_table.ToJSon(columns_order=("tipo", "count"))
    template_values["content"] = "stats/statindex.html"
    template_values["pg_table"] = pg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["pa_table"] = pa_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["pc_table"] = pc_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["pt_table"] = pt_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["pq_table"] = pq_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["pd_table"] = pd_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["sg_table"] = sg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["sa_table"] = sa_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["sc_table"] = sc_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["st_table"] = st_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["sq_table"] = sq_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["sd_table"] = sd_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["cg_table"] = cg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["ca_table"] = ca_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["cc_table"] = cc_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["ct_table"] = ct_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["cq_table"] = cq_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["bg_table"] = bg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["ba_table"] = ba_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["bq_table"] = bq_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["fg_table"] = fg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["fa_table"] = fa_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["fm_table"] = fm_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["fq_table"] = fq_table.ToJSon(columns_order=("group", "1", "2", "3"))
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
    self.putTask('/admin/stats/calcisp',limit=self.request.get("limit"),offset=self.request.get("offset"))
    self.putTask('/admin/stats/calcnc',limit=self.request.get("limit"),offset=self.request.get("offset"))
    
  def putTask(self, aurl, offset=0, limit=50):
    task = Task(url=aurl, params={"limit": str(limit), "offset":str(offset)}, method="GET")
    queue = Queue()
    queue.add(task)
    
class CMStatNCCalcHandler(CMStatCalcHandler):
  def get(self):
    
    stats = StatisticheNonconf()
    statCM = StatisticheNonconf()
    statCC = StatisticheNonconf()
    statsCM = dict()
    statsCC = dict()

    limit = int(self.request.get("limit"))
    logging.info("limit: %s", limit)
    if limit is None:
      limit = 0
    offset = int(self.request.get("offset"))
    logging.info("offset: %s", offset)
    if offset is None:
      offset = 0
    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)
    
    dataInizio = datetime.datetime(year=2009, month=9, day=1).date()    
    dataFine = datetime.datetime.now().date() - datetime.timedelta(7 - datetime.datetime.now().isoweekday())
    dataCalcolo = datetime.datetime.now().date()
    wtot = (dataFine - dataInizio).days / 7

    logging.info("dataInizio: " + str(dataInizio))
    logging.info("dataFine: " + str(dataFine))
    logging.info("wtot: " + str(wtot))
    
    for s in StatisticheNonconf.all().filter("dataInizio >=", dataInizio):
      if s.commissione is None and s.centroCucina is None:
        stats = s
      elif s.commissione is None and s.centroCucina is not None:
        statsCC[s.centroCucina.key()]=s        
      else:
        statsCM[s.commissione.key()]=s
      self.initWeek(s, wtot)
    
    stats.dataInizio = datetime.datetime(year=2009, month=9, day=1).date()
    stats.dataFine = datetime.datetime.now().date()
    self.initWeek(stats, wtot)

    count = 0
    for nc in Nonconformita.all().filter("creato_il >", stats.dataCalcolo).order("creato_il").fetch(limit+1, offset):
      if nc.dataNonconf >= dataInizio :
        if( nc.commissione.key() not in statsCM ):          
          statCM = StatisticheNonconf()
          statCM.dataInizio = stats.dataInizio
          statCM.dataFine = stats.dataFine
          statCM.commissione = nc.commissione
          statsCM[statCM.commissione.key()] = statCM
          self.initWeek(statCM, wtot)
        else:
          statCM = statsCM[nc.commissione.key()]
          
        if( nc.commissione.centroCucina.key() not in statsCC ):
          statCC = StatisticheNonconf()
          statCC.dataInizio = stats.dataInizio
          statCC.dataFine = stats.dataFine
          statCC.centroCucina = nc.commissione.centroCucina
          statsCC[statCC.centroCucina.key()] = statCC
          self.initWeek(statCC, wtot)
        else:
          statCC = statsCC[nc.commissione.centroCucina.key()]
  
        self.calcNC(nc,statCM)
        self.calcNC(nc,statCC)
        self.calcNC(nc,stats)
        count += 1
        if count == limit : break
      
    if stats.numeroNonconf > 0 :
      if count < limit :  
        stats.dataCalcolo = dataCalcolo
      stats.put()
      
    for stat in statsCM.values() :
      if count < limit :  
        stats.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCC.values() :
      if count < limit :  
        stats.dataCalcolo = dataCalcolo
      stat.put()
    
    finish = count < limit    
    logging.info("finish: " + str(finish))  
    if not finish:
      self.putTask("/admin/stats/calcnc", offset + limit)

  def initWeek(self, stat, wtot):
    for ns in range(len(stat.numeroNonconfSettimana),wtot + 1):
      stat.numeroNonconfSettimana.append(0)

  def calcNC(self, nc, stats):
    stats.incData(nc.tipo)
    stats.numeroNonconf += 1
    settimana = (nc.dataNonconf - stats.dataInizio).days / 7
    stats.numeroNonconfSettimana[settimana] += 1
    
class CMStatIspCalcHandler(CMStatCalcHandler):
  def get(self):
    
    stats = StatisticheIspezioni()
    statCM = StatisticheIspezioni()
    statCC = StatisticheIspezioni()
    statsCM = dict()
    statsCC = dict()

    limit = int(self.request.get("limit"))
    logging.info("limit: %s", limit)
    if limit is None:
      limit = 0
    offset = int(self.request.get("offset"))
    logging.info("offset: %s", offset)
    if offset is None:
      offset = 0
    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)
    dataInizio = datetime.datetime(year=2009, month=9, day=1).date()    
    dataFine = datetime.datetime.now().date() - datetime.timedelta(7 - datetime.datetime.now().isoweekday())
    dataCalcolo = datetime.datetime.now().date()
    wtot = (dataFine - dataInizio).days / 7

    logging.info("dataInizio: " + str(dataInizio))
    logging.info("dataFine: " + str(dataFine))
    logging.info("wtot: " + str(wtot))
    
    for s in StatisticheIspezioni.all().filter("dataInizio >=", dataInizio):
      if s.commissione is None and s.centroCucina is None:
        stats = s
      elif s.commissione is None and s.centroCucina is not None:
        statsCC[s.centroCucina.key()]=s        
      else:
        statsCM[s.commissione.key()]=s
      self.initWeek(s, wtot)
    
    stats.dataInizio = datetime.datetime(year=2009, month=9, day=1).date()
    stats.dataFine = datetime.datetime.now().date()
    self.initWeek(stats, wtot)

    count = 0
    for isp in Ispezione.all().filter("creato_il >", stats.dataCalcolo).order("creato_il").fetch(limit+1, offset):
      if isp.dataIspezione >= dataInizio :
        if( isp.commissione.key() not in statsCM ):          
          statCM = StatisticheIspezioni()
          statCM.dataInizio = stats.dataInizio
          statCM.dataFine = stats.dataFine
          statCM.commissione = isp.commissione
          statsCM[statCM.commissione.key()] = statCM
          self.initWeek(statCM, wtot)
        else:
          statCM = statsCM[isp.commissione.key()]
  
        if( isp.commissione.centroCucina.key() not in statsCC ):
          statCC = StatisticheIspezioni()
          statCC.dataInizio = stats.dataInizio
          statCC.dataFine = stats.dataFine
          statCC.centroCucina = isp.commissione.centroCucina
          statsCC[statCC.centroCucina.key()] = statCC
          self.initWeek(statCC, wtot)
        else:
          statCC = statsCC[isp.commissione.centroCucina.key()]
          
        self.calcIsp(isp,statCM)
        self.calcIsp(isp,statCC)
        self.calcIsp(isp,stats)
        count += 1
        if count == limit : break
    
    if stats.numeroSchede > 0 :
      self.comp(stats)
      if count < limit :  
        stats.dataCalcolo = dataCalcolo
      stats.put()
      
    for stat in statsCM.values() :
      self.comp(stat)
      if count < limit :  
        stats.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCC.values() :
      self.comp(stat)
      if count < limit :  
        stats.dataCalcolo = dataCalcolo
      stat.put()
    
    finish = count < limit    
    logging.info("finish: " + str(finish))  
    if not finish:
      self.putTask("/admin/stats/calcisp", offset + limit)

  def initWeek(self, stat, wtot):
    for ns in range(len(stat.numeroSchedeSettimana),wtot + 1):
      stat.numeroSchedeSettimana.append(0)

  def calcIsp(self, isp, stats):
    stats.numeroSchede += 1;
    settimana = (isp.dataIspezione - stats.dataInizio).days / 7
    stats.numeroSchedeSettimana[settimana] += 1
    
    if(isp.primoDist == 1):
      stats.primoDistribuzione1 = stats.primoDistribuzione1 + isp.primoDist
    if(isp.primoDist == 2):
      stats.primoDistribuzione2 = stats.primoDistribuzione2 + isp.primoDist
    if(isp.primoDist == 3):
      stats.primoDistribuzione3 = stats.primoDistribuzione3 + isp.primoDist

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
      
    if(isp.secondoDist == 1):
      stats.secondoDistribuzione1 = stats.secondoDistribuzione1 + isp.secondoDist
    if(isp.secondoDist == 2):
      stats.secondoDistribuzione2 = stats.secondoDistribuzione2 + isp.secondoDist
    if(isp.secondoDist == 3):
      stats.secondoDistribuzione3 = stats.secondoDistribuzione3 + isp.secondoDist

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
    stats.primoDist = float(stats.primoDistribuzione1 + stats.primoDistribuzione2 + stats.primoDistribuzione3) / stats.numeroSchede
    stats.primoAssaggio = float(stats.primoAssaggio1 + stats.primoAssaggio2 + stats.primoAssaggio3) / stats.numeroSchede
    stats.primoGradimento = float(stats.primoGradimento1 + stats.primoGradimento2 + stats.primoGradimento3 + stats.primoGradimento4) / stats.numeroSchede
    stats.secondoDist = float(stats.secondoDistribuzione1 + stats.secondoDistribuzione2 + stats.secondoDistribuzione3) / stats.numeroSchede
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
  ('/admin/stats/calc', CMStatCalcHandler),
  ('/admin/stats/calcisp', CMStatIspCalcHandler),
  ('/admin/stats/calcnc', CMStatNCCalcHandler),
  ('/stats/getdata', CMStatsDataHandler)], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()  