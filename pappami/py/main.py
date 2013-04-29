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

from base import BasePage, CMMenuHandler, Const, commissario_required, user_required, reguser_required, config, handle_404, handle_500
from commissioni import ContattiHandler
import cgi, logging, os
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import fixpath
import jinja2

from google.appengine.ext.ndb import model
from google.appengine.api import users
import webapp2 as webapp
from jinja2.filters import do_pprint
from google.appengine.api import memcache
from google.appengine.api import mail

from py.widget import CMMenuWidgetHandler, CMStatWidgetHandler

from py.model import *

class MainPage(BasePage):

  def get(self):
    template_values = dict()
    template_values["host"] = self.getHost()

    commissario = self.getCommissario(self.get_current_user())
    if commissario and commissario.is_active():
      self.redirect("/stream")
      return
    if commissario and commissario.is_deactivated():
      self.redirect("/signup")
      return
      #return self.getPrivate(template_values)

    template_values["main"] = "public.html"
    template_values["contacts"] = ContattiHandler.get_contacts()

    geo = model.GeoPt(41.754922,12.502441)

    template_values["news_pappami_alt"] = "http://blog.pappa-mi.it/"
    template_values["geo"] = geo

    self.getBase(template_values)

  def post(self):
    return self.get()

  def getPrivate(self, template_values):

    c = None
    geo = model.GeoPt(45.463681,9.188171)
    commissario = self.getCommissario(self.get_current_user())
    c = commissario.commissione()
    geo = commissario.citta.get().geo

    offset = 0
    if self.request.get("offset") != "":
      offset = int(self.request.get("offset"))

    template_values = dict()
    template_values["bgcolor"] = "eeeeff"
    template_values["fgcolor"] = "000000"
    template_values["geo"] = geo
    template_values["billboard"] = "navigation.html"
    template_values["host"] = self.getHost()

    self.getBase(template_values)

  def getStats(self):
    stats = memcache.get("stats")
    if(stats is None):
      now = datetime.now().date()
      anno = now.year
      if now.month <= 9: #siamo in inverno -estate, data inizio = settembre anno precedente
        anno = anno - 1

      stats = Statistiche()
      stats.numeroCommissioni = Commissione.get_active()
      try:
        stats.numeroSchede = StatisticheIspezioni.get_cc_cm_time(timeId=anno).get().numeroSchede
        stats.ncTotali = StatisticheNonconf.get_cc_cm_time(timeId=anno).get().numeroNonconf
      except :
        stats.numeroSchede = 0
        stats.ncTotali = 0
      stats.diete = Dieta.query().count()
      stats.note = Nota.query().count()
      stats.anno1 = anno
      stats.anno2 = anno + 1
      memcache.add("stats", stats)

    return stats

class CMSupportoHandler(BasePage):

  def get(self):
    template_values = dict()
    template_values["content"] = "supporto.html"
    self.getBase(template_values)

class CMCondizioniHandler(BasePage):

  def get(self):
    template_values = dict()
    template_values["content"] = "condizioni.html"
    self.getBase(template_values)

class MapDataHandler(webapp.RequestHandler):

  def get(self):
    cursor = self.request.get("cur")

    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))

    if self.request.get("cmd") == "all":
      markers = memcache.get("markers_all"+str(offset))
      if(markers == None):

        commissioni = Commissione.get_all_cursor(cursor)

        limit = Const.ENTITY_FETCH_LIMIT
        i = 0
        markers_list = list()
        try:
          for c in commissioni :
            i += 1
            if i >= limit:
              break
            if c.geo:
              mark = '<marker key="' + str(c.key.id()) + '" nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta.get().nome + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" citta="' + str(c.citta.id()) + '" cc="'
              if c.getCentroCucina(datetime.now().date()):
                mark += str(c.getCentroCucina(datetime.now().date()).key.id()) + '" />\n'
              else:
                mark += '" />\n'
              markers_list.append(mark)
        except:
          logging.error("Timeout")
        if i >= limit:
          markers = "<markers cur='" + commissioni.cursor_after().to_websafe_string() + "'>\n"
        else:
          markers = "<markers>\n"

        markers = markers + "".join(markers_list) + "</markers>"

        memcache.add("markers_all"+str(offset), markers)

      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)
    else:
      markers = memcache.get("markers"+str(offset))
      if(markers == None):

        commissioni = Commissione.get_active_cursor(cursor)

        limit = Const.ENTITY_FETCH_LIMIT
        i = 0
        markers_list = list()
        try:
          for c in commissioni :
            i += 1
            if i >= limit:
              break
            if c.geo :
              mark = '<marker key="' + str(c.key.id()) + '" nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta.get().nome + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" citta="' + str(c.citta.id()) + '" cc="'
              if c.getCentroCucina(datetime.now().date()):
                mark += str(c.getCentroCucina(datetime.now().date()).key.id()) + '" />\n'
              else:
                mark += '" />\n'
              markers_list.append(mark)
        except:
          raise
          logging.error("Timeout")

        #logging.info(markers_list)
        if i >= limit:
          markers = "<markers cur='" + commissioni.cursor_after().to_websafe_string() + "'>\n"
        else:
          markers = "<markers>\n"

        markers = markers + "".join(markers_list) + "</markers>"
        memcache.add("markers"+str(offset), markers)

      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)

class CalendarioHandler(BasePage):
  @reguser_required
  def post(self):
    return self.get()
  @reguser_required
  def get(self):
    commissario = self.getCommissario(self.get_current_user())
    if self.request.get("cmd") == "create":
      cm = Commissione.get(model.Key(Commissione,self.request.get("cm")))
      if((cm.calendario == None or cm.calendario == "") and commissario.is_registered(cm)):
        calendario = Calendario()
        calendario.logon(user=Configurazione.get_value_by_name("calendar_user"), password=Configurazione.get_value_by_name("calendar_password"))
        calendario.create(cm.nome + " - " + cm.tipoScuola)
        for c in cm.commissari():
          if c.isCommissario() :
            calendario.share(c.user.email())
        cm.calendario = str(calendario.GetId())
        cm.put()

    else:
      cm = None
      if self.request.get("cm") != "":
        cm = Commissione.get(self.request.get("cm"))
      elif commissario and commissario.commissione() :
        cm = commissario.commissione()
      else:
        cm = Commissione.query().get()

    template_values = dict()
    template_values["content"] = "calendario/calendario.html"
    template_values["commissioni"] = commissario.commissioni()
    template_values["creacal"] = (cm.calendario == None or cm.calendario == "") and commissario.is_registered(cm)
    template_values["cm"] = cm
    self.getBase(template_values)

class TagsPage(BasePage):

  @reguser_required
  def get(self):
    template_values = dict()
    template_values["content"] = "tags.html"
    template_values["tags"] = CMTagHandler().getTags()

    self.getBase(template_values)

class ChiSiamoPage(BasePage):

  def get(self):
    template_values = dict()
    template_values["content"] = "chi.html"
    self.getBase(template_values)

class AddCityHandler(BasePage):

  def get(self):
    self.redirect("https://docs.google.com/a/pappa-mi.it/spreadsheet/viewform?formkey=dGpyOHNISHBjQnZqWjUwSzdJU3hPMnc6MQ")

class ContactusHandler(BasePage):

  def get(self):
    self.redirect("https://docs.google.com/spreadsheet/viewform?formkey=dE82eHdyRVJ0VVpNUVBCLXIwNDMwN1E6MQ#gid=0")

app = webapp.WSGIApplication([
  ('/', MainPage),
  ('/chi', ChiSiamoPage),
  ('/map', MapDataHandler),
  ('/calendario', CalendarioHandler),
  ('/supporto', CMSupportoHandler),
  ('/condizioni', CMCondizioniHandler),
  ('/citta', AddCityHandler),
  ('/contattaci', ContactusHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

#def profile_main():
    ## This is the main function for profiling
    ## We've renamed our original main() above to real_main()
    #import cProfile, pstats
    #prof = cProfile.Profile()
    #prof = prof.runctx("real_main()", globals(), locals())
    #print "<pre>"
    #stats = pstats.Stats(prof)
    #stats.sort_stats("time")  # Or cumulative
    #stats.print_stats(100)  # 80 = how many to print
    ## The rest is optional.
    ##stats.print_callees()
    ##stats.print_callers()
    #print "</pre>"

#import py.dblog
#py.dblog.patch_appengine()


