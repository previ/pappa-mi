#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from py.base import BasePage, CMCommissioniDataHandler, CMCommissioniHandler, CMMenuHandler, roleCommissario

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

from django.utils import simplejson as json

from py.gviz_api import *
from py.model import *
from py.site import *
from py.form import IspezioneForm, NonconformitaForm, DietaForm, NotaForm
from py.stats import CMStatsHandler
from py.calendar import *
from py.modelMsg import *

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

class CMCommentHandler(BasePage):
  
  def init(self, msg_rif, tipo):
    messaggio = Messaggio.all().filter("par", msg_rif).get()
    if not messaggio:  
      messaggio = Messaggio()
      messaggio.par = msg_rif
      messaggio.root = msg_rif
      messaggio.livello = 0
      messaggio.tipo = tipo
      messaggio.put()
    return messaggio

  def initActivity(self, msg_rif, tipo, last):    

    CMCommentHandler().init(msg_rif, tipo)
    
    buff = ""

    activities = list()
    for msg in Messaggio.all().filter("__key__ >", last):
      activities.append(msg)
    activities = sorted(activities, key=lambda student: student.creato_il, reverse=True)

    template_values = {
      'main': '../templates/activity.html'
    }

    path = os.path.join(os.path.dirname(__file__), template_values["main"])
    
    for activity in activities:
      template_values['activity'] = activity 
      buff += template.render(path, template_values)

    return buff

  def getRoot(self, msg_rif):
    return Messaggio.all().filter("par", msg_rif).get()
  
  
  def post(self):
    par = None
    rif = self.request.get("par")    
    if rif:
      par = db.Key(rif)

    messaggio = Messaggio()
    messaggio.par = par
    messaggio.tipo = int(self.request.get("tipo"))
    messaggio.livello = int(self.request.get("livello"))
    messaggio.titolo = self.request.get("titolo")
    messaggio.testo = self.request.get("testo")
    messaggio.put()
    
    CMTagHandler().saveTags(messaggio, self.request.get_all("tags[]"))
    
    template_values = {
      'main': '../templates/activity.html',
      'activity': messaggio
    }
    
    buff = ""
    path = os.path.join(os.path.dirname(__file__), template_values["main"])

    activities = list()
    for msg in Messaggio.all().filter("__key__ >", db.Key(self.request.get("last"))):
      activities.append(msg)
    activities = sorted(activities, key=lambda student: student.creato_il, reverse=True)

    for activity in activities:
      template_values['activity'] = activity 
      buff += template.render(path, template_values)

    self.response.out.write(buff)
    
    
  def get(self):
    root = self.request.get("par")
    commento_root = Messaggio.get(db.Key(root))
    commenti = Messaggio.all().filter("par", commento_root).order("creato_il")
    
    template_values = {
      'main': '../templates/comments/comment.html',
      'comment_root': commento_root,
      'commenti': commenti
    }
    self.getBase(template_values)
      
class CMVoteHandler(BasePage):
  def get(self):
    messaggio = Messaggio.get(self.request.get('msg'))
      
    voto = Voto()
    for p_voto in messaggio.voto_reference_set:
      if p_voto.creato_da == users.get_current_user():
        voto = p_voto
        break;
    voto.messaggio = messaggio
    voto.voto = int(self.request.get('voto'))
    if voto.voto == 0 and voto.key:
      voto.delete()
    else:
      voto.put()
    self.response.out.write(messaggio.voto_reference_set.count())

class CMVotersHandler(BasePage):
  def get(self):
    messaggio = Messaggio.get(self.request.get('msg'))
    template_values = {
      'main': '../templates/comments/voters.html',
      'voters': messaggio.voto_reference_set
    }
    self.getBase(template_values)    

class CMTagHandler(BasePage):
  def get(self):
    alltags = list()
    assignedtags = list()
    msg = None
    if self.request.get('msg'):
      msg = db.Key(self.request.get('msg'))
    tagobjs = TagObj.all().filter("obj", msg)
    for tagobj in tagobjs:
      assignedtags.append(tagobj.tag.nome)
    for tag in Tag.all():
      alltags.append(tag.nome)

    buff = json.JSONEncoder().encode({'assignedTags': assignedtags, 'availableTags':alltags})      
    self.response.out.write(buff)
    
  def post(self):
    tagnames = self.request.get_all("tags[]")
    msg = db.Key(self.request.get('msg'))
      
    self.saveTags(msg,tagnames)

    buff = json.JSONEncoder().encode({'status': 'ok'})      
    self.response.out.write(buff)
    
  def saveTags(self,obj,tagnames):
    tagobjs = TagObj.all().filter("obj", obj)
    tagold = dict()
    for tagobj in tagobjs:
      tagold[tagobj.tag.nome] = tagobj
    for tagname in tagnames:
      #logging.info("tagname: " + tagname)
      if (tagname in tagold) is False:
        #logging.info("adding: " + tagname)
        tag = Tag.all().filter("nome",tagname).get()
        if not tag:
          tag = Tag(nome=tagname, numRef=0)
          tag.put()
        tagobj = TagObj(tag=tag,obj=obj)
        tagobj.put()
        tagobj.tag.numRef += 1
        tagobj.tag.put()
    for name in tagold:
      logging.info(name)
      
      if (name in tagnames) is False:
        logging.info("removing:" + name)
        tagobj = tagold[name]
        tagobj.tag.numRef-=1
        tagobj.tag.put()
        tagobj.delete()
      
def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   
   
  application = webapp.WSGIApplication([
    ('/comments/message', CMCommentHandler),
    ('/comments/comment', CMCommentHandler),
    ('/comments/vote', CMVoteHandler),
    ('/comments/voters', CMVotersHandler),
    ('/comments/gettags', CMTagHandler), 
    ('/comments/updatetags', CMTagHandler)    
  ], debug=debug)

  wsgiref.handlers.CGIHandler().run(application)
  
if __name__ == "__main__":
  main()
