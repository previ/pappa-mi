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

from py.base import BasePage, CMMenuHandler, Const, ActivityFilter, commissario_required, user_required
import cgi, logging, os
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
from jinja2.filters import do_pprint
from google.appengine.api import memcache
from google.appengine.api import mail

import py.feedparser

from py.widget import CMMenuWidgetHandler, CMStatWidgetHandler

from py.model import *
from py.modelMsg import *
from py.comments import *

if 'lib' not in sys.path:
  sys.path[0:0] = ['lib']
    
class MainPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["host"] = self.getHost()
        
    commissario = self.getCommissario(users.get_current_user())
    if commissario and commissario.isCommissario():
      return self.getPrivate(template_values)
    if commissario and commissario.isGenitore():
      return self.getPrivate(template_values)
          
    activities = self.get_activities()
    template_values["activities"] = activities
    template_values["content"] = "public.html"
    template_values["billboard"] = "billboard.html"
    template_values["content_right"] = "rightbar.html"
    template_values["stat"] = stats = self.getStats()
    
    geo = db.GeoPt(45.463681,9.188171)
    commissario = self.getCommissario(users.get_current_user())
    
    template_values["news_pappami"] = self.getNews("news_pappami")
    template_values["news_pappami_alt"] = "http://blog.pappa-mi.it/"
    template_values["geo"] = geo
      
    self.getBase(template_values)

  def getPrivate(self, template_values):

    c = None
    geo = db.GeoPt(45.463681,9.188171)
    commissario = self.getCommissario(users.get_current_user())
    c = commissario.commissione()
    geo = commissario.citta.geo

    offset = 0
    if self.request.get("offset") != "":
      offset = int(self.request.get("offset"))

    logging.info("tag1: " + self.request.get("tag"))
    
    template_values = dict()
    template_values["bgcolor"] = "eeeeff"
    template_values["fgcolor"] = "000000"    
    activities = self.get_activities(offset)
    template_values["activities"] = activities
    template_values["act_offset"] = Const.ACTIVITY_FETCH_LIMIT
    #template_values["act_last"] = activities[0]
    template_values["geo"] = geo
    template_values["billboard"] = "navigation.html"
    template_values["content"] = "activities.html"
    template_values["host"] = self.getHost()
    template_values["commissari"] = Commissario.all().order('user')
    
    #tags = list()
    #types = list()
    #userlist = list()
    #if self.request.get("tag") != "":
      #tags.append(self.request.get("tag"))
    #if self.request.get("type") != "":
      #types.append(int(self.request.get("type")))
    #if self.request.get("user") != "":
      #userlist.append(self.request.get("user"))
    
    #act_filter = ActivityFilter(tags,types,userlist)
    #template_values["activities"] = self.get_activities_by_filter(act_filter)

    userlist = list()
    for cr in Commissario.all():
      userlist.append(cr.user)
    
    template_values["users"] = userlist

    template_values["tags"] = self.getTopTags()
   

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
        stats.numeroSchede = StatisticheIspezioni.all().filter("commissione",None).filter("centroCucina",None).filter("timeId",anno).get().numeroSchede
        stats.ncTotali = StatisticheNonconf.all().filter("commissione",None).filter("centroCucina",None).filter("timeId",anno).get().numeroNonconf
      except :
        stats.numeroSchede = 0
        stats.ncTotali = 0      
      stats.diete = Dieta.all().count()
      stats.note = Nota.all().count()
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
    template_values["main"] = "../templates/condizioni.html"
    self.getBase(template_values)    
    
class CMMenuDataHandler(CMMenuHandler):
  
  def get(self): 
    if( self.request.get("cmd") == "getbydate" ):
      menu = Menu();
      data = datetime.strptime(self.request.get("data"),Const.DATE_FORMAT).date()
      c = Commissione.get(self.request.get("commissione"))
      menu = self.getMenu(data, c)[0]
      
      self.response.out.write(menu.primo.nome)
      self.response.out.write("|")
      self.response.out.write(menu.secondo.nome)
      self.response.out.write("|")
      self.response.out.write(menu.contorno.nome)
      self.response.out.write("\n")

    else:
      template_values = dict()
      template_values['content'] = 'menu.html'      
      self.getBase(template_values)

class CMMenuSlideHandler(CMMenuHandler):
  
  def get(self): 
    template_values = dict()
    template_values['main'] = 'menu_slides.html'    
    self.getBase(template_values)
      
class CMMapDataHandler(webapp.RequestHandler):
  
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
              markers_list.append( '<marker key="' + str(c.key()) + '" nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta.nome + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" cc="' + c.getCentroCucina(datetime.now().date()).key().name() + '" />\n')
        except db.Timeout:
          logging.error("Timeout")
        if i >= limit:
          markers = "<markers cur='" + commissioni.cursor() + "'>\n"
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
              markers_list.append( '<marker key="' + str(c.key()) + '" nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta.nome + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" cc="' + c.getCentroCucina(datetime.now().date()).key().name() + '" />\n')
        except db.Timeout:
          logging.error("Timeout")
          
        logging.info(markers_list)
        if i >= limit:
          markers = "<markers cur='" + commissioni.cursor() + "'>\n"
        else:
          markers = "<markers>\n"
          
        markers = markers + "".join(markers_list) + "</markers>"
        memcache.add("markers"+str(offset), markers)
      
      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)

class CalendarioHandler(BasePage):
  @user_required
  def post(self):
    return self.get()
  @user_required
  def get(self):    
    commissario = self.getCommissario(users.get_current_user())
    if self.request.get("cmd") == "create":
      cm = Commissione.get(self.request.get("cm"))
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
        cm = Commissione.all().get()
        
    template_values = dict()
    template_values["content"] = "calendario/calendario.html"
    template_values["commissioni"] = commissario.commissioni()
    template_values["creacal"] = (cm.calendario == None or cm.calendario == "") and commissario.is_registered(cm)
    template_values["cm"] = cm
    self.getBase(template_values)
      
class TagsPage(BasePage):
  
  @user_required
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

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    },
    'webapp2_extras.auth': {
        #        'user_model': 'models.User',
        'user_attributes': ['displayName', 'email'],
        },
    'webapp2_extras.jinja2': {
        'filters': {
            'do_pprint': do_pprint,
            },
        },
    }

app = webapp.WSGIApplication([
  ('/', MainPage),
  ('/tags', TagsPage),
  ('/chi', ChiSiamoPage),
  ('/map', CMMapDataHandler),
  ('/menu', CMMenuDataHandler),
  ('/menuslide', CMMenuSlideHandler),
  ('/calendario', CalendarioHandler),
  ('/supporto', CMSupportoHandler),
  ('/condizioni', CMCondizioniHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

def main():
  app.run();

if __name__ == "__main__":
  main()
"""
def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/tags', TagsPage),
  #('/fb', FbPage),
  ('/docs', DocPage),
  #('/blog', BlogPage),
  ('/chi', ChiSiamoPage),
  ('/map', CMMapDataHandler),
  ('/menu', CMMenuDataHandler),
  ('/supporto', CMSupportoHandler),
  ('/condizioni', CMCondizioniHandler),
  ('/registrazione', CMRegistrazioneHandler),
  ('/signup', CMSignupHandler)
  ], debug=debug)
  
  wsgiref.handlers.CGIHandler().run(application)
"""
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

  