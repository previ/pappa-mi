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
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.api.taskqueue import Task, Queue

from py.model import *
from py.form import CommissioneForm
from py.gviz_api import *
from py.base import BasePage, config, handle_404, handle_500

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
    sts = StatisticheIspezioni.get_cy_cc_cm_time()
    for st in sts:
      logging.info(st.timeId)
      anni.append(st.timeId)
    anni = sorted(anni)
      

    cy_key = model.Key("Citta", self.get_context().get("citta_key"))
    if self.request.get("citta"):
      cy_key = model.Key("Citta", int(self.request.get("citta")))
    
    statCY = StatisticheIspezioni.get_cy_cc_cm_time(cy=cy_key, timeId=anno).get()
      
    #if(self.request.get("cm") == "" and len(self.getCommissario(users.get_current_user()).commissioni())):
    #  cm = self.getCommissario(users.get_current_user()).commissioni()[0]
    cm_key = self.get_context().get("cm_key")
    if cm_key:
      cm = model.Key("Commissione", cm_key).get()
    if self.request.get("cm"):
      cm = model.Key("Commissione", int(self.request.get("cm"))).get()
    if cm:
      cc = cm.getCentroCucina(now)
      statCC = StatisticheIspezioni.get_cy_cc_cm_time(cc=cc.key, timeId=anno).get()
      statCM = StatisticheIspezioni.get_cy_cc_cm_time(cm=cm.key, timeId=anno).get()
    stats = [statCY,statCC,statCM]
    
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

    a_stat = statCY
    if statCC:
      a_stat = statCC
    if statCM:
      a_stat = statCM
    aa_data = list()
    if a_stat:
      for a_idx in range(0, len(a_stat.ambiente)):
        aa_data.append({"tipo": a_stat.ambiente_desc[a_idx], "count": a_stat.ambiente[a_idx]})
    aa_table = DataTable(a_desc)
    aa_table.LoadData(aa_data)    
    
    nc_desc = {"tipo": ("string", "Tipo"), 
               "count": ("number", "Occorrenze")}
    
    if cm:
      ncstat = StatisticheNonconf.get_cy_cc_cm_time(cm=cm.key, timeId=anno).get()
    else:
      ncstat = StatisticheNonconf.get_cy_cc_cm_time(cy=statCY.citta, timeId=anno).get()

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

    if a_stat:
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
    template_values["statCY"] = statCY
    template_values["statCC"] = statCC
    template_values["statCM"] = statCM
    template_values['action'] = self.request.path
    template_values["content"] = "stats/stats.html"
    template_values["cmsro"] = self.getCommissario()
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
    year = None

    limit = 50
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))
    if self.request.get("year"):
      year = int(self.request.get("year"))      
      
    logging.info("year: %d", year)
    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)

    self.putTask('/admin/stats/calcisp', year=year, limit=limit, offset=offset)
    self.putTask('/admin/stats/calcnc', year=year, limit=limit, offset=offset)
    
  def putTask(self, aurl, year, offset=0, limit=50):
    task = Task(url=aurl, params={"year": str(year), "limit": str(limit), "offset":str(offset)}, method="GET")
    queue = Queue()
    queue.add(task)
    
class CMStatNCCalcHandler(CMStatCalcHandler):
  def get(self):
    
    statAll = None
    statCM = None
    statCC = None
    statCY = None
    statsCM = dict()
    statsCC = dict()
    statsCY = dict()

    now = datetime.datetime.now().date()
    year = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1
    
    limit = 50
    #logging.info("limit: %s", limit)
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    #logging.info("offset: %s", offset)
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))
    
    if self.request.get("year"):
      year = int(self.request.get("year"))      

    logging.info("year: %d", year)
    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)
      
    dataInizio = datetime.datetime(year=year, month=9, day=1).date() + datetime.timedelta(DAYS_OF_WEEK - datetime.date(year=year, month=9, day=1).isoweekday() + 1)
    dataFine = min(datetime.datetime.now().date() + datetime.timedelta(DAYS_OF_WEEK - datetime.datetime.now().isoweekday()), dataInizio + timedelta(335))
    
    dataCalcolo = datetime.datetime.now()
    dataUltimoCalcolo = datetime.datetime(dataInizio.year, dataInizio.month, dataInizio.day) #default dataUltimoCalcolo = data inizio anno
    timeId=year
    timePeriod = "Y"
    wtot = (dataFine - dataInizio).days / 7

    #load stat for cache
    for s in StatisticheNonconf.get_from_year(year):
      if s.citta:
        statsCY[s.citta] = s
      elif s.centroCucina:
        statsCC[s.centroCucina] = s        
      elif s.commissione:
        statsCM[s.commissione] = s
      else:
        statAll = s
        if not self.request.get("year"):
          dataUltimoCalcolo = statAll.dataCalcolo
        
      s.dataFine = dataFine
      self.initWeek(s, wtot)
      
    if not statAll:
      statAll = StatisticheNonconf()
      #statAll.creato_da = self.get_current_user()
      statAll.dataInizio = dataInizio
      statAll.dataFine = dataFine
      statAll.timeId = timeId
      statAll.timePeriod = timePeriod
      self.initWeek(statAll, wtot)      
    
    count = 0 

    logging.info("dataInizio: " + str(dataInizio))    
    logging.info("dataFine: " + str(dataFine))    
    logging.info("dataUltimoCalcolo: " + str(dataUltimoCalcolo))    
    
    for nc in Nonconformita.query().filter(Nonconformita.creato_il > dataUltimoCalcolo).order(Nonconformita.creato_il).fetch(limit=limit+1, offset=offset):
      if nc.dataNonconf >= dataInizio and nc.dataNonconf < dataFine :
        if nc.commissione not in statsCM:          
          statCM = StatisticheNonconf()
          #statCM.creato_da = self.get_current_user()
          statCM.dataInizio = dataInizio
          statCM.dataFine = dataFine
          statCM.commissione = nc.commissione
          statCM.timeId = timeId
          statCM.timePeriod = timePeriod
          statsCM[statCM.commissione] = statCM
          self.initWeek(statCM, wtot)
        else:
          statCM = statsCM[nc.commissione]
          
        if nc.commissione.get().getCentroCucina(now).key not in statsCC:
          statCC = StatisticheNonconf()
          #statCC.creato_da = self.get_current_user()
          statCC.dataInizio = dataInizio
          statCC.dataFine = dataFine
          statCC.centroCucina = nc.commissione.get().getCentroCucina(now).key
          statCC.timeId = timeId
          statCC.timePeriod = timePeriod
          statsCC[statCC.centroCucina] = statCC
          self.initWeek(statCC, wtot)
        else:
          statCC = statsCC[nc.commissione.get().getCentroCucina(now).key]

        if( nc.commissione.get().citta not in statsCY ):
          statCY = StatisticheNonconf()
          #statCY.creato_da = self.get_current_user()
          statCY.citta = nc.commissione.get().citta
          statCY.dataInizio = dataInizio
          statCY.dataFine = dataFine
          statCY.timeId = timeId
          statCY.timePeriod = timePeriod
          statsCY[statCY.citta] = statCY
          self.initWeek(statCY, wtot)
        else:
          statCY = statsCY[nc.commissione.get().citta]
          
        self.calcNC(nc,statCM)
        self.calcNC(nc,statCC)
        self.calcNC(nc,statCY)
        self.calcNC(nc,statAll)
      count += 1
      if count == limit : break           
    
    for stat in statsCM.values() :
      #when no more data to process, update dataCalcolo
      if count < limit :  
        logging.info("when no more data to process, update statsCM.dataCalcolo for " + stat.commissione.get().nome)
        stat.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCC.values() :
      if count < limit :  
        logging.info("when no more data to process, update statsCC.dataCalcolo for " + stat.centroCucina.get().nome)
        stat.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCY.values() :
      if count < limit :  
        logging.info("when no more data to process, update statsCY.dataCalcolo for " + stat.citta.get().nome)
        stat.dataCalcolo = dataCalcolo
      stat.put()

    if count < limit :  
      logging.info("when no more data to process, update statAll.dataCalcolo")
      statAll.dataCalcolo = dataCalcolo
    statAll.put()
      
    finish = count < limit    
    logging.info("finish: " + str(finish))  
    if not finish:
      self.putTask("/admin/stats/calcnc", year, offset + limit)

  def initWeek(self, stat, wtot):
    for nc in range(0,len(stat._tipiPos.keys())):
      stat.data.append(0)
    for ns in range(len(stat.numeroNonconfSettimana),wtot + 1):
      stat.numeroNonconfSettimana.append(0)

  def calcNC(self, nc, stats):
    #logging.info(stats)
    stats.incData(nc.tipo)
    stats.numeroNonconf += 1
    settimana = (nc.dataNonconf - stats.dataInizio).days / 7

    #logging.info("dataInizio: " + str(stats.dataInizio))    
    #logging.info("dataNonconf: " + str(nc.dataNonconf))        
    #logging.info("stats.numeroNonconfSettimana " + str(len(stats.numeroNonconfSettimana)) + " settimana: " + str(settimana))
    
    stats.numeroNonconfSettimana[settimana] += 1
    
class CMStatIspCalcHandler(CMStatCalcHandler):
  def get(self):
    
    statAll = None
    statCM = None
    statCC = None
    statCY = None
    statsCM = dict()
    statsCC = dict()
    statsCY = dict()

    now = datetime.datetime.now().date()
    year = now.year
    if now.month < 8: #siamo in inverno -estate, data inizio = settembre anno precedente
      year = year - 1
    
    limit = 50
    #logging.info("limit: %s", limit)
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))
    #logging.info("offset: %s", offset)
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))

    if self.request.get("year"):
      year = int(self.request.get("year"))      
      
    logging.info("year: %d", year)
    logging.info("limit: %d", limit)
    logging.info("offset: %d", offset)

    
    dataInizio = datetime.datetime(year=year, month=9, day=1).date() + datetime.timedelta(DAYS_OF_WEEK - datetime.date(year=year, month=9, day=1).isoweekday() + 1)
    dataFine = min(datetime.datetime.now().date() + datetime.timedelta(DAYS_OF_WEEK - datetime.datetime.now().isoweekday()), dataInizio + timedelta(330))
    dataCalcolo = datetime.datetime.now()
    dataUltimoCalcolo = datetime.datetime(dataInizio.year, dataInizio.month, dataInizio.day) #default dataUltimoCalcolo = data inizio anno

    timeId=year
    timePeriod = "Y"
    wtot = (dataFine - dataInizio).days / 7

    #logging.info("dataInizio: " + str(dataInizio))
    #logging.info("dataFine: " + str(dataFine))
    #logging.info("wtot: " + str(wtot))
    
    # carica gli elementi creati successivamente all'ultimo calcolo
    for s in StatisticheIspezioni.get_from_year(year):
      if s.citta:
        statsCY[s.citta] = s
      elif s.centroCucina:
        statsCC[s.centroCucina] = s        
      elif s.commissione:
        statsCM[s.commissione] = s
      else:
        statAll = s
        if not self.request.get("year"):
          dataUltimoCalcolo = s.dataCalcolo
      s.dataFine = dataFine
      self.initWeek(s, wtot)

    if not statAll:
      statAll = StatisticheIspezioni()
      #statAll.creato_da = self.get_current_user()
      statAll.dataInizio = dataInizio
      statAll.dataFine = dataFine
      statAll.timeId = timeId
      statAll.timePeriod = timePeriod
      self.initWeek(statAll, wtot)      
      statAll.init()
     
    count = 0

    logging.info("dataInizio: " + str(dataInizio))    
    logging.info("dataFine: " + str(dataFine))    
    logging.info("dataUltimoCalcolo: " + str(dataUltimoCalcolo))    
      
    for isp in Ispezione.query().filter(Ispezione.creato_il > dataUltimoCalcolo).order(Ispezione.creato_il).fetch(limit=limit+1, offset=offset):
      if isp.dataIspezione >= dataInizio and isp.dataIspezione < dataFine:
        if( isp.commissione not in statsCM ):          
          statCM = StatisticheIspezioni()
          #statCM.creato_da = self.get_current_user()
          statCM.dataInizio = dataInizio
          statCM.dataFine = dataFine
          statCM.timeId = timeId
          statCM.timePeriod = timePeriod
          statCM.commissione = isp.commissione
          statsCM[statCM.commissione] = statCM
          self.initWeek(statCM, wtot)
          statCM.init()
        else:
          statCM = statsCM[isp.commissione]
  
        if( isp.commissione.get().getCentroCucina(now).key not in statsCC ):
          statCC = StatisticheIspezioni()
          #statCC.creato_da = self.get_current_user()
          statCC.dataInizio = dataInizio
          statCC.dataFine = dataFine
          statCC.timeId = timeId
          statCC.timePeriod = timePeriod
          statCC.centroCucina = isp.commissione.get().getCentroCucina(now).key
          statsCC[statCC.centroCucina] = statCC
          self.initWeek(statCC, wtot)
          statCC.init()
        else:
          statCC = statsCC[isp.commissione.get().getCentroCucina(now).key]
          
        if( isp.commissione.get().citta not in statsCY ):          
          statCY = StatisticheIspezioni()
          #statCY.creato_da = self.get_current_user()
          statCY.dataInizio = dataInizio
          statCY.dataFine = dataFine
          statCY.timeId = timeId
          statCY.timePeriod = timePeriod
          statCY.citta = isp.commissione.get().citta
          statsCY[statCY.citta] = statCY
          self.initWeek(statCY, wtot)
          statCY.init()
        else:
          statCY = statsCY[isp.commissione.get().citta]
          
        self.calcIsp(isp,statCM)
        self.calcIsp(isp,statCC)
        self.calcIsp(isp,statCY)
        self.calcIsp(isp,statAll)
      count += 1
      if count == limit : break
        
    for stat in statsCM.values() :
      if count < limit :  
        logging.info("when no more data to process, update statsCM.dataCalcolo for " + stat.commissione.get().nome)
        stat.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCC.values() :
      if count < limit :  
        logging.info("when no more data to process, update statsCM.dataCalcolo for " + stat.centroCucina.get().nome)
        stat.dataCalcolo = dataCalcolo
      stat.put()

    for stat in statsCY.values() :
      if count < limit :  
        logging.info("when no more data to process, update statsCM.dataCalcolo for " + stat.citta.get().nome)
        stat.dataCalcolo = dataCalcolo
      stat.put()

    if count < limit :  
      logging.info("when no more data to process, update statAll.dataCalcolo")
      statAll.dataCalcolo = dataCalcolo
    statAll.put()
      
    finish = count < limit    
    logging.info("finish: " + str(finish))  
    if not finish:
      self.putTask("/admin/stats/calcisp", year, offset + limit)

  def initWeek(self, stat, wtot):
    for ns in range(len(stat.numeroSchedeSettimana),wtot + 1):
      stat.numeroSchedeSettimana.append(0)

  def calcIsp(self, isp, stats):
    stats.numeroSchede += 1;
    settimana = (isp.dataIspezione - stats.dataInizio).days / 7
    
    #logging.info("dataInizio: " + str(stats.dataInizio))    
    #logging.info("dataNonconf: " + str(isp.dataIspezione))    
    #logging.info("stats.numeroSchedeSettimana " + str(len(stats.numeroSchedeSettimana)) + " settimana: " + str(settimana))
    
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
      #stat.creato_da = self.get_current_user()
      stat.put()

      
app = webapp.WSGIApplication([
  ('/stats', CMStatsHandler),
  ('/admin/stats/calc', CMStatCalcHandler),
  ('/admin/stats/calcisp', CMStatIspCalcHandler),
  ('/admin/stats/calcnc', CMStatNCCalcHandler)], config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()