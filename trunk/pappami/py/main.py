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

from py.base import BasePage, CMMenuHandler, Const, ActivityFilter
import cgi, logging, os
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
from jinja2 import Template
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

import py.feedparser

from py.widget import CMMenuWidgetHandler, CMStatWidgetHandler

from py.model import *
from py.modelMsg import *
from py.comments import *

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
      stats.numeroCommissioni = Commissione.all().filter("numCommissari >",0).count()
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

class CMRegistrazioneHandler(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "registrazione.html"
    self.getBase(template_values)

class CMSignupHandler(BasePage):
  
  def get(self):
    user = users.get_current_user()
    commissario = self.getCommissario(users.get_current_user())
    if(commissario == None):
      stato = 11
      if self.request.get("iscm") == "S":
        stato = 0
      
      commissario = Commissario(nome = self.request.get("nome"), cognome = self.request.get("cognome"), user = user, stato = stato)
      if self.request.get("citta"):
        commissario.citta = db.Key(self.request.get("citta"))
      commissario.emailComunicazioni = "S"
      commissario.put()
          
      for c_key in self.request.get_all("commissione"):
        commissioneCommissario = CommissioneCommissario(commissione = Commissione.get(db.Key(c_key)), commissario = commissario)
        commissioneCommissario.put()

      commissario.setCMDefault()
      memcache.set("commissario" + str(user.user_id()), commissario, 600)
        
      self.sendRegistrationRequestMail(commissario)
    template_values = dict()
    template_values['cmsro'] = commissario
    if commissario.isRegCommissario():
      template_values['content'] = 'commissario/registrazione_ok.html'
      self.getBase(template_values)
    else:
      self.redirect("/genitore")

  def sendRegistrationRequestMail(self, commissario):
    if commissario.isGenitore():
      self.sendRegistrationGenitoreRequestMail(commissario)
    else:
      self.sendRegistrationCommissarioRequestMail(commissario)      

  def sendRegistrationGenitoreRequestMail(self, commissario) :

    host = self.getHost()

    sender = "Pappa-Mi <aiuto@pappa-mi.it>"
    
    message = mail.EmailMessage()
    message.sender = sender
    message.to = commissario.user.email()
    message.bcc = sender
    message.subject = "Benvenuto in Pappa-Mi"
    message.body = """ La tua richiesta di registrazione come Genitore e' stata confermata.
    
    Ora puoi accedere all'area a te riservata:
    http://"""  + host + """/genitore

    PappaPedia (documenti):
    http://pappapedia.pappa-mi.it
    
    Ciao !
    Pappa-Mi staff
    
    """
      
    message.send()

  def sendRegistrationCommissarioRequestMail(self, commissario) :

    host = self.getHost()
    
    sender = "Pappa-Mi <aiuto@pappa-mi.it>"
    
    message = mail.EmailMessage()
    message.sender = sender
    message.to = sender
    message.subject = "Richiesta di Registrazione da " + commissario.nome + " " + commissario.cognome
    message.body = commissario.nome + " " + commissario.cognome + " " + commissario.user.email() + """ ha inviato una richiesta di registrazione come Commissario. 
    
    Per abilitarlo usare il seguente link:
    
    """ + "http://" + host + "/admin/commissario?cmd=enable&key="+str(commissario.key())

    message.send()
    
    
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
    limit = 100
    if self.request.get("limit"):
      limit = int(self.request.get("limit"))    
    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))    

    if self.request.get("cmd") == "all":
      markers = memcache.get("markers_all"+str(offset))
      if(markers == None):
          
        commissioni = Commissione.all().order("nome").fetch(limit, offset);
          
        markers = "<markers>\n"
        try:
          for c in commissioni :
            if c.geo:
              markers = markers + '<marker key="' + str(c.key()) + '" nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta.nome + '"'
              markers = markers + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" cc="' + c.getCentroCucina(datetime.now().date()).key().name() + '" />\n'
        except db.Timeout:
          logging.error("Timeout")
          
        markers = markers + "</markers>"    
        memcache.add("markers_all"+str(offset), markers)
      
      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)      
    else:
      markers = memcache.get("markers")
      if(markers == None):
          
        commissioni = Commissione.all().filter("numCommissari >", 0)
          
        markers = "<markers>\n"
        try:
          for c in commissioni :
            if c.geo :
              markers = markers + '<marker key="' + str(c.key()) + '" nome="' + c.nome + '" indirizzo="' + c.strada + ', ' + c.civico + ', ' + c.cap + " " + c.citta.nome + '"'
              markers = markers + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon) + '" tipo="' + c.tipoScuola + '" numcm="' + str(c.numCommissari) + '" cc="' + c.getCentroCucina(datetime.now().date()).key().name() + '" />\n'
        except db.Timeout:
          logging.error("Timeout")
          
        markers = markers + "</markers>"    
        memcache.add("markers", markers)
      
      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)

class CalendarioHandler(BasePage):
  def post(self):
    return self.get()
  def get(self):    
    commissario = self.getCommissario(users.get_current_user())
    if self.request.get("cmd") == "create":
      cm = Commissione.get(self.request.get("cm"))
      if((cm.calendario == None or cm.calendario == "") and CommissioneCommissario.all().filter("commissario",commissario).filter("commissione", cm).get() is not None):
        calendario = Calendario()
        calendario.logon(user=Configurazione.all().filter("nome","calendar_user").get().valore, password=Configurazione.all().filter("nome", "calendar_password").get().valore)
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
    template_values["creacal"] = (cm.calendario == None or cm.calendario == "") and CommissioneCommissario.all().filter("commissario",commissario).filter("commissione", cm).get() is not None
    template_values["cm"] = cm
    self.getBase(template_values)
      
class TagsPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "tags.html"
    template_values["tags"] = CMTagHandler().getTags()
    
    self.getBase(template_values)
      
class DocPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "docs.html"
    template_values["iframesrc"] = "http://docs.pappa-mi.it/allegati"
    self.getBase(template_values)

class BlogPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "docs.html"
    template_values["iframesrc"] = "http://blog.pappa-mi.it/"
    self.getBase(template_values)

class FbPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "fb.html"
    self.getBase(template_values)

class ChiSiamoPage(BasePage):
  
  def get(self):
    template_values = dict()
    template_values["content"] = "chi.html"
    self.getBase(template_values)

app = webapp.WSGIApplication([
  ('/', MainPage),
  ('/tags', TagsPage),
  #('/fb', FbPage),
  ('/docs', DocPage),
  #('/blog', BlogPage),
  ('/chi', ChiSiamoPage),
  ('/map', CMMapDataHandler),
  ('/menu', CMMenuDataHandler),
  ('/menuslide', CMMenuSlideHandler),
  ('/calendario', CalendarioHandler),
  ('/supporto', CMSupportoHandler),
  ('/condizioni', CMCondizioniHandler),
  ('/registrazione', CMRegistrazioneHandler),
  ('/signup', CMSignupHandler)
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'))

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

  