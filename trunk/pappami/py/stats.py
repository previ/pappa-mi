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

  def getTable(self, stats, attr, desc):
    data = list()
    for stat in stats:
      if stat:
        sublist = {"group": stat.getNome()}
        for d in range(0,len(stat.getVals(attr))):
          sublist[str(d+1)] = float(stat.getVal(attr,d+1))/(d+1)*100/stat.numeroSchede
        data.append(sublist)

    table = DataTable(desc)
    table.LoadData(data)
    return table
    
  def post(self):
    return self.get()
  
  def get(self):
    cm = None
    cc = None
    statCC = None
    statCM = None

    logging.info("anno: " + self.request.get("anno"))
    
    now = datetime.datetime.now().date()
    anno = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      anno = anno - 1
    if self.request.get("anno"):
      anno = int(self.request.get("anno"))

    anni = list()
    sts = StatisticheIspezioni.all().filter("commissione",None).filter("centroCucina", None)
    for st in sts:
      anni.append(st.timeId)
      

    stat = StatisticheIspezioni.all().filter("timeId", anno).filter("commissione",None).filter("centroCucina", None).get()
      
    if(self.request.get("cm")):
      cm = Commissione.get(self.request.get("cm"))
      cc = cm.centroCucina
      statCC = StatisticheIspezioni.all().filter("timeId", anno).filter("centroCucina",cc).get()
      statCM = StatisticheIspezioni.all().filter("timeId", anno).filter("commissione",cm).get()
    stats = [stat,statCC,statCM]
    
    z_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Sifficiente"),
               "3": ("number", "Discreto"),
               "4": ("number", "Buono")}

    g_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 25%"),
               "2": ("number", "25% < 50%"),
               "3": ("number", "50% < 75%"),
               "4": ("number", ">75%")}

    a_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Non Accettabile"),
               "2": ("number", "Accettabile"),
               "3": ("number", "Gradevole")}

    c_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarsa"),
               "2": ("number", "Corretta"),
               "3": ("number", "Eccessiva")}

    t_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Freddo"),
               "2": ("number", "Corretta"),
               "3": ("number", "Caldo")}

    q_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Giusta"),
               "3": ("number", "Abbondante")}

    d_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "< 10min"),
               "2": ("number", "10min - 20min"),
               "3": ("number", "> 20min")}

    m_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Acerba"),
               "2": ("number", "Corretta"),
               "3": ("number", "Matura")}
    
    gg_table = self.getTable(stats,"giudizioGlobale",g_desc)
    zr_table = self.getTable(stats,"puliziaRefettorio",z_desc)
    zc_table = self.getTable(stats,"puliziaCentroCottura",z_desc)
    sr_table = self.getTable(stats,"smaltimentoRifiuti",z_desc)
    dp_table = self.getTable(stats,"durataPasto",z_desc)

    pg_table = self.getTable(stats,"primoGradimento",g_desc)
    pa_table = self.getTable(stats,"primoAssaggio",a_desc)
    pc_table = self.getTable(stats,"primoCottura",c_desc)
    pt_table = self.getTable(stats,"primoTemperatura",t_desc)
    pq_table = self.getTable(stats,"primoQuantita",q_desc)
    pd_table = self.getTable(stats,"primoDist",d_desc)

    sg_table = self.getTable(stats,"secondoGradimento",g_desc)
    sa_table = self.getTable(stats,"secondoAssaggio",a_desc)
    sc_table = self.getTable(stats,"secondoCottura",c_desc)
    st_table = self.getTable(stats,"secondoTemperatura",t_desc)
    sq_table = self.getTable(stats,"secondoQuantita",q_desc)
    sd_table = self.getTable(stats,"secondoDist",d_desc)

    cg_table = self.getTable(stats,"contornoGradimento",g_desc)
    ca_table = self.getTable(stats,"contornoAssaggio",a_desc)
    cc_table = self.getTable(stats,"contornoCottura",c_desc)
    ct_table = self.getTable(stats,"contornoTemperatura",t_desc)
    cq_table = self.getTable(stats,"contornoQuantita",q_desc)

    bg_table = self.getTable(stats,"paneGradimento",g_desc)
    ba_table = self.getTable(stats,"paneAssaggio",a_desc)
    bq_table = self.getTable(stats,"paneQuantita",q_desc)

    fg_table = self.getTable(stats,"fruttaGradimento",g_desc)
    fa_table = self.getTable(stats,"fruttaAssaggio",a_desc)
    fm_table = self.getTable(stats,"fruttaMaturazione",m_desc)
    fq_table = self.getTable(stats,"fruttaQuantita",q_desc)

    a_desc = {"tipo": ("string", "Descrizione"), 
               "count": ("number", "Numero")}

    aa_data = list()
    for a_idx in range(0, len(stat.ambiente)):
      aa_data.append({"tipo": stat.ambiente_desc[a_idx], "count": stat.ambiente[a_idx]})
    aa_table = DataTable(a_desc)
    aa_table.LoadData(aa_data)    
    
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

    cm_desc = {"tipo": ("string", "Tipo Scuola"), 
               "attive": ("number", "Attive"),
               "iscritte": ("number", "Iscritte"),
               "totali": ("number", "Totali")}
    cm_data = list()
    for cm_t in ["Materna", "Primaria", "Secondaria"]:
      cm_data.append({"tipo": cm_t, "attive": Commissione.all().filter("numCommissari >", 0).filter("tipoScuola", cm_t).count(), 
                                    "iscritte": Commissione.all().filter("numCommissari >", 0).filter("tipoScuola", cm_t).count(), 
                                    "totali": Commissione.all().filter("tipoScuola", cm_t).count()})
    cm_table = DataTable(cm_desc)
    cm_table.LoadData(cm_data)
    
    template_values = dict()
    template_values["anni"] = anni
    template_values["aa_table"] = aa_table.ToJSon(columns_order=("tipo", "count"))
    template_values["cm_data"] = cm_table.ToJSon(columns_order=("tipo", "attive", "iscritte", "totali"))
    template_values["di_table"] = di_table.ToJSon(columns_order=("time", "schede", "nonconf"))
    template_values["nc_table"] = nc_table.ToJSon(columns_order=("tipo", "count"))
    template_values["zr_table"] = pg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["zc_table"] = pg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["sr_table"] = pg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["dp_table"] = pg_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["gg_table"] = pg_table.ToJSon(columns_order=("group", "1", "2", "3"))
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
    template_values["content"] = "stats/statindex.html"
    self.getBase(template_values)

    
class CMStatsDataHandler(BasePage):
    
  def get(self):
    path = os.path.join(os.path.dirname(__file__), '../templates/stats/statdata.js')
    self.response.out.write(template.render(path, template_values))

class CMStatCalcHandler(BasePage):
  def get(self):
    limit = 50
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))
    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)

    self.putTask('/admin/stats/calcisp',limit=limit,offset=offset)
    self.putTask('/admin/stats/calcnc',limit=limit,offset=offset)
    
  def putTask(self, aurl, offset=0, limit=50):
    task = Task(url=aurl, params={"limit": str(limit), "offset":str(offset)}, method="GET")
    queue = Queue()
    queue.add(task)
    
class CMStatNCCalcHandler(CMStatCalcHandler):
  def get(self):
    
    stats = None
    statCM = None
    statCC = None
    statsCM = dict()
    statsCC = dict()

    limit = 50
    #logging.info("limit: %s", limit)
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    #logging.info("offset: %s", offset)
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))
    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)
    
    now = datetime.datetime.now().date()
    year = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1
    dataInizio = datetime.datetime(year=year, month=9, day=1).date()    
    dataFine = datetime.datetime.now().date() - datetime.timedelta(7 - datetime.datetime.now().isoweekday())
    dataCalcolo = datetime.datetime.now()
    timeId=year
    timePeriod = "Y"
    wtot = (dataFine - dataInizio).days / 7

    #logging.info("dataInizio: " + str(dataInizio))
    #logging.info("dataFine: " + str(dataFine))
    #logging.info("wtot: " + str(wtot))
    
    for s in StatisticheNonconf.all().filter("dataInizio >=", dataInizio):
      if s.commissione is None and s.centroCucina is None:
        stats = s
      elif s.commissione is None and s.centroCucina is not None:
        statsCC[s.centroCucina.key()]=s        
      else:
        statsCM[s.commissione.key()]=s
      s.dataFine = dataFine
      self.initWeek(s, wtot)
    
    if stats is None:
      stats = StatisticheNonconf()
      stats.dataInizio = dataInizio
      stats.dataFine = dataFine
      stats.timeId=timeId
      stats.timePeriod = timePeriod
      self.initWeek(stats, wtot)

    if stats.dataCalcolo is None:
      stats.dataCalcolo = datetime.datetime(year=year, month=9, day=1)
      
    count = 0
    # carica gli elementi creati successivamente all'ultimo calcolo
    for nc in Nonconformita.all().filter("creato_il >", stats.dataCalcolo).order("creato_il").fetch(limit+1, offset): 
      if nc.dataNonconf >= dataInizio and nc.dataNonconf < dataFine:
        if( nc.commissione.key() not in statsCM ):          
          statCM = StatisticheNonconf()
          statCM.dataInizio = stats.dataInizio
          statCM.dataFine = stats.dataFine
          statCM.commissione = nc.commissione
          statCM.timeId=timeId
          statCM.timePeriod = statCM.timePeriod
          statsCM[statCM.commissione.key()] = statCM
          self.initWeek(statCM, wtot)
        else:
          statCM = statsCM[nc.commissione.key()]
          
        if( nc.commissione.centroCucina.key() not in statsCC ):
          statCC = StatisticheNonconf()
          statCC.dataInizio = stats.dataInizio
          statCC.dataFine = stats.dataFine
          statCC.centroCucina = nc.commissione.centroCucina
          statCC.timeId=timeId
          statCC.timePeriod = statCM.timePeriod
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
        stat.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCC.values() :
      if count < limit :  
        stat.dataCalcolo = dataCalcolo
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
    
    stats = None
    statCM = None
    statCC = None
    statsCM = dict()
    statsCC = dict()

    limit = 50
    #logging.info("limit: %s", limit)
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    #logging.info("offset: %s", offset)
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))

    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)

    now = datetime.datetime.now().date()
    year = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1
    dataInizio = datetime.datetime(year=year, month=9, day=1).date()    
    dataFine = datetime.datetime.now().date() - datetime.timedelta(7 - datetime.datetime.now().isoweekday())
    dataCalcolo = datetime.datetime.now()
    timeId=year
    timePeriod = "Y"
    wtot = (dataFine - dataInizio).days / 7

    #logging.info("dataInizio: " + str(dataInizio))
    #logging.info("dataFine: " + str(dataFine))
    #logging.info("wtot: " + str(wtot))
    
    # carica gli elementi creati successivamente all'ultimo calcolo
    for s in StatisticheIspezioni.all().filter("dataInizio >=", dataInizio):
      if s.commissione is None and s.centroCucina is None:
        stats = s
      elif s.commissione is None and s.centroCucina is not None:
        statsCC[s.centroCucina.key()]=s        
      else:
        statsCM[s.commissione.key()]=s
      s.dataFine = dataFine
      self.initWeek(s, wtot)

    
    if stats is None:
      stats = StatisticheIspezioni()
      stats.dataInizio = dataInizio
      stats.dataFine = dataFine
      stats.timeId=timeId
      stats.timePeriod = timePeriod
      self.initWeek(stats, wtot)

    if stats.dataCalcolo is None:
      stats.dataCalcolo = datetime.datetime(year=year, month=9, day=1)

    count = 0
    for isp in Ispezione.all().filter("creato_il >", stats.dataCalcolo).order("creato_il").fetch(limit+1, offset):
      if isp.dataIspezione >= dataInizio and isp.dataIspezione < dataFine:
        if( isp.commissione.key() not in statsCM ):          
          statCM = StatisticheIspezioni()
          statCM.dataInizio = stats.dataInizio
          statCM.dataFine = stats.dataFine
          statCM.timeId=timeId
          statCM.timePeriod = statCM.timePeriod
          statCM.commissione = isp.commissione
          statsCM[statCM.commissione.key()] = statCM
          self.initWeek(statCM, wtot)
        else:
          statCM = statsCM[isp.commissione.key()]
  
        if( isp.commissione.centroCucina.key() not in statsCC ):
          statCC = StatisticheIspezioni()
          statCC.dataInizio = stats.dataInizio
          statCC.dataFine = stats.dataFine
          statCC.timeId=timeId
          statCC.timePeriod = statCM.timePeriod
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
      if count < limit :  
        stats.dataCalcolo = dataCalcolo
      stats.put()
      
    for stat in statsCM.values() :
      if count < limit :  
        stat.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCC.values() :
      if count < limit :  
        stat.dataCalcolo = dataCalcolo
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
    stats.calc(isp)
      
class CMStatCalcHandlerOld(BasePage):
  def get(self):
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

      
application = webapp.WSGIApplication([
  ('/stats', CMStatsHandler),
  ('/admin/stats/calc', CMStatCalcHandler),
  ('/admin/stats/calcisp', CMStatIspCalcHandler),
  ('/admin/stats/calcnc', CMStatNCCalcHandler)], debug=True)

def main():
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()  