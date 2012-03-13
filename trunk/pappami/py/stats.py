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
import fixpath

from google.appengine.ext.ndb import model
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.api.taskqueue import Task, Queue

from py.model import *
from py.form import CommissioneForm
from py.gviz_api import *
from py.base import BasePage, config

TIME_FORMAT = "T%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
DAYS_OF_WEEK = 7

class CMStatsHandler(BasePage):

  def getTable(self, stats, attr, desc):
    data = list()
    for stat in stats:
      if stat:
        sr = 0.0
        sublist = {"group": stat.getNome()}
        for d in range(0,len(stat.getVals(attr))):
          sublist[str(d+1)] = round(float(stat.getVal(attr,d+1))/(d+1)*100/stat.numeroSchede,2)
          sr += round(float(stat.getVal(attr,d+1))/(d+1)*100/stat.numeroSchede,2)
        dt = sr - 100.0
        for d in range(0,len(stat.getVals(attr))):
          if sublist[str(d+1)] >= dt:
            sublist[str(d+1)] -= dt
            break
        data.append(sublist)

    table = DataTable(desc)
    table.LoadData(data)
    return table
    
  def post(self):
    return self.get()

  def get(self):
    template_values = dict()
    self.getBase(template_values)
  
  def getBase(self,template_values):
    cm = None
    cc = None
    statCC = None
    statCM = None

    #logging.info("anno: " + self.request.get("anno"))
    now = datetime.datetime.now().date()

    anno = int(self.get_context().get("anno"))

    if self.request.get("anno"):
      anno = int(self.request.get("anno"))

    if not anno:
      anno = now.year
      if now.month <= 9: #siamo in inverno -estate, data inizio = settembre anno precedente
        anno = anno - 1

    anni = list()
    sts = StatisticheIspezioni.get_cc_cm_time()
    for st in sts:
      anni.append(st.timeId)
      

    stat = StatisticheIspezioni.get_cc_cm_time(timeId=anno).get()
      
    #if(self.request.get("cm") == "" and len(self.getCommissario(users.get_current_user()).commissioni())):
    #  cm = self.getCommissario(users.get_current_user()).commissioni()[0]
    cm_key = self.get_context().get("cm_key")
    if cm_key:
      cm = model.Key("Commissione", cm_key).get()
    if self.request.get("cm"):
      cm = model.Key("Commissione", int(self.request.get("cm"))).get()
    if cm:
      cc = cm.getCentroCucina(now)
      statCC = StatisticheIspezioni.get_cc_cm_time(cc=cc.key, timeId=anno).get()
      statCM = StatisticheIspezioni.get_cc_cm_time(cm=cm.key, timeId=anno).get()
    stats = [stat,statCC,statCM]
    
    z_desc = {"group": ("string", "Gruppo"), 
               "1": ("number", "Scarso"),
               "2": ("number", "Sufficiente"),
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
    
    gg_table = self.getTable(stats,"giudizioGlobale",a_desc)
    zr_table = self.getTable(stats,"puliziaRefettorio",z_desc)
    zc_table = self.getTable(stats,"puliziaCentroCottura",z_desc)
    sr_table = self.getTable(stats,"smaltimentoRifiuti",z_desc)
    dp_table = self.getTable(stats,"durataPasto",d_desc)

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

    a_stat = stat
    if statCC:
      a_stat = statCC
    if statCM:
      a_stat = statCM
    aa_data = list()
    for a_idx in range(0, len(a_stat.ambiente)):
      aa_data.append({"tipo": a_stat.ambiente_desc[a_idx], "count": a_stat.ambiente[a_idx]})
    aa_table = DataTable(a_desc)
    aa_table.LoadData(aa_data)    
    
    nc_desc = {"tipo": ("string", "Tipo"), 
               "count": ("number", "Occorrenze")}
    
    if cm:
      ncstat = StatisticheNonconf.get_cc_cm_time(cm=cm.key, timeId=anno).get()
    else:
      ncstat = StatisticheNonconf.get_cc_cm_time(timeId=anno).get()

    nc_table = DataTable(nc_desc)
    if ncstat is not None:      
      nc_data = list()
      nci = Nonconformita();
      for nd in ncstat.getTipiPos():
        nc_data.append({"tipo": nci.tipi()[nd], "count": ncstat.getData(nd)})
      nc_table.LoadData(nc_data)
    
    di_desc = {"time": ("string", "Settimane"), 
               "schede": ("number", "Schede"),
               "nonconf": ("number", "Non Conformita")}
    di_data = list()

    for w in range(len(a_stat.numeroSchedeSettimana)):
      if ncstat is not None:
        di_data.append({"time": w, "schede": a_stat.numeroSchedeSettimana[w], "nonconf": ncstat.numeroNonconfSettimana[w]})
      else:
        di_data.append({"time": w, "schede": a_stat.numeroSchedeSettimana[w], "nonconf": 0})
    di_table = DataTable(di_desc)
    di_table.LoadData(di_data)

    cm_desc = {"tipo": ("string", "Tipo Scuola"), 
               "iscritte": ("number", "Iscritte"),
               "totali": ("number", "Totali")}
    cm_data = list()
    for cm_t in ["Materna", "Primaria", "Secondaria"]:
      cm_data.append({"tipo": cm_t, "iscritte": Commissione.query().filter(Commissione.numCommissari > 0).filter(Commissione.tipoScuola == cm_t).count(), 
                                    "totali": Commissione.query().filter(Commissione.tipoScuola == cm_t).count()})
    cm_table = DataTable(cm_desc)
    cm_table.LoadData(cm_data)
    
    template_values["anni"] = anni
    template_values["aa_table"] = aa_table.ToJSon(columns_order=("tipo", "count"))
    template_values["cm_data"] = cm_table.ToJSon(columns_order=("tipo", "iscritte", "totali"))
    template_values["di_table"] = di_table.ToJSon(columns_order=("time", "schede", "nonconf"))
    template_values["nc_table"] = nc_table.ToJSon(columns_order=("tipo", "count"))
    template_values["zr_table"] = zr_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["zc_table"] = zc_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["sr_table"] = sr_table.ToJSon(columns_order=("group", "1", "2", "3", "4"))
    template_values["dp_table"] = dp_table.ToJSon(columns_order=("group", "1", "2", "3"))
    template_values["gg_table"] = gg_table.ToJSon(columns_order=("group", "1", "2", "3"))
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
    template_values['action'] = self.request.path
    template_values["content"] = "stats/stats.html"
    template_values["cmsro"] = self.getCommissario(users.get_current_user())
    template_values["citta"] = Citta.get_all()
    template_values["anno"] = anno
    self.get_context()["anno"] = anno    
    
    if cm:
      self.get_context()["citta_key"] = cm.citta.id()
      self.get_context()["cm_key"] = cm.key.id()
      self.get_context()["cm_name"] = cm.desc()    

    super(CMStatsHandler, self).getBase(template_values)

    
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
    #logging.info("limit: %d", limit)
    #logging.info("offset: %d", offset)

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
    #logging.info("limit: %d", limit)
    #logging.info("offset: %d", offset)
    
    now = datetime.datetime.now().date()
    year = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1
    dataInizio = datetime.datetime(year=year, month=9, day=1).date() + datetime.timedelta(DAYS_OF_WEEK - datetime.date(year=year, month=9, day=1).isoweekday() + 1)
    dataFine = datetime.datetime.now().date() + datetime.timedelta(DAYS_OF_WEEK - datetime.datetime.now().isoweekday())
    dataCalcolo = datetime.datetime.now()

    timeId=year
    timePeriod = "Y"
    wtot = (dataFine - dataInizio).days / 7

    for s in StatisticheNonconf.get_from_date(dataInizio):
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
      stats.dataCalcolo = datetime.datetime(stats.dataInizio.year, stats.dataInizio.month, stats.dataInizio.day)
      
    count = 0
   
      
    for nc in Nonconformita.all().filter("creato_il >", stats.dataCalcolo).order("creato_il").fetch(limit+1, offset):
      if nc.dataNonconf >= dataInizio and nc.dataNonconf < dataFine :
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
          
        if( nc.commissione.getCentroCucina(now).key() not in statsCC ):
          statCC = StatisticheNonconf()
          statCC.dataInizio = stats.dataInizio
          statCC.dataFine = stats.dataFine
          statCC.centroCucina = nc.commissione.getCentroCucina(now)
          statCC.timeId=timeId
          statCC.timePeriod = statCM.timePeriod
          statsCC[statCC.centroCucina.key()] = statCC
          self.initWeek(statCC, wtot)
        else:
          statCC = statsCC[nc.commissione.getCentroCucina(now).key()]
  
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

    #logging.info("limit: %d", limit)
    #logging.info("offset: %d", offset)

    now = datetime.datetime.now().date()
    year = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1
    
    dataInizio = datetime.datetime(year=year, month=9, day=1).date() + datetime.timedelta(DAYS_OF_WEEK - datetime.date(year=year, month=9, day=1).isoweekday() + 1)
    dataFine = datetime.datetime.now().date() + datetime.timedelta(DAYS_OF_WEEK - datetime.datetime.now().isoweekday())
    dataCalcolo = datetime.datetime.now()

    timeId=year
    timePeriod = "Y"
    wtot = (dataFine - dataInizio).days / 7

    #logging.info("dataInizio: " + str(dataInizio))
    #logging.info("dataFine: " + str(dataFine))
    #logging.info("wtot: " + str(wtot))
    
    # carica gli elementi creati successivamente all'ultimo calcolo
    for s in StatisticheIspezioni.get_from_date(dataInizio):
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
      stats.dataCalcolo = datetime.datetime(stats.dataInizio.year, stats.dataInizio.month, stats.dataInizio.day)

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
  
        if( isp.commissione.getCentroCucina(now).key() not in statsCC ):
          statCC = StatisticheIspezioni()
          statCC.dataInizio = stats.dataInizio
          statCC.dataFine = stats.dataFine
          statCC.timeId=timeId
          statCC.timePeriod = statCM.timePeriod
          statCC.centroCucina = isp.commissione.getCentroCucina(now)
          statsCC[statCC.centroCucina.key()] = statCC
          self.initWeek(statCC, wtot)
        else:
          statCC = statsCC[isp.commissione.getCentroCucina(now).key()]
          
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

      
app = webapp.WSGIApplication([
  ('/stats', CMStatsHandler),
  ('/admin/stats/calc', CMStatCalcHandler),
  ('/admin/stats/calcisp', CMStatIspCalcHandler),
  ('/admin/stats/calcnc', CMStatNCCalcHandler)], config=config)

def main():
  app.run();

if __name__ == "__main__":
  main()