#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from py.base import Const, BasePage, CMCommissioniDataHandler, CMCommissioniHandler, CMMenuHandler, roleCommissario

import os, cgi, logging, urllib, json
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from py.gviz_api import *
from py.model import *
from py.site import *
from py.form import IspezioneForm, NonconformitaForm, DietaForm, NotaForm
from py.stats import CMStatsHandler
from py.calendar import *
from py.modelMsg import *

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"

"""
comment handler
handle both messages (comments not attached to other objects) and comments (comments attached to a "root" message object
"""
class CMCommentHandler(BasePage):

  """ 
  init a comment structure, attaching an empty root message to an existing object
  """
  def init(self, msg_rif, tipo, tags):
    messaggio = Messaggio.all().filter("par", msg_rif).get()
    if not messaggio:  
      messaggio = Messaggio()
      messaggio.par = msg_rif
      messaggio.root = msg_rif
      messaggio.livello = 0
      messaggio.tipo = tipo
      messaggio.put()
      if tags:
        CMTagHandler().saveTags(messaggio, tags)
    return messaggio

  """
  init a comment structure, attaching a root message to an existing object
  and return the delta activity stream html
  """
  def initActivity(self, msg_rif, tipo, last, tags=None):    

    CMCommentHandler().init(msg_rif, tipo, tags)
    
    buff = ""

    activities = list()
    for msg in Messaggio.all().filter("livello", 0).filter("creato_il >", last.creato_il).fetch(Const.ACTIVITY_FETCH_LIMIT):
      activities.append(msg)
    activities = sorted(activities, key=lambda student: student.creato_il, reverse=True)

    template_values = {
      'main': 'activity.html',
      'ease': True
    }
    template_values['activities'] = activities       

    return self.gateBase(template_values)

  """
  return the root object of a given message (comment)
  """
  def getRoot(self, msg_rif):
    return Messaggio.all().filter("par", msg_rif).get()
  
  """
  http post handler
  handle both new message and new comment (livello is the discriminant)
  return the delta activity stream in html
  """
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
   
    CMTagHandler().saveTags(messaggio, self.request.get_all("tags"))
  
    template_values = {
      'activity': messaggio,
      'ease': True
    }
    
    activities = list()
    msgs = Messaggio.all()
    if self.request.get("par"):
      msgs = msgs.filter("par", db.Key(self.request.get("par")))

    if self.request.get("last"):
      logging.info("last: " + self.request.get("last"))
      msgs = msgs.filter("creato_il >", Messaggio.get(db.Key(self.request.get("last"))).creato_il)
      
    for msg in msgs.filter("livello", messaggio.livello):
      #logging.info("msg: " + msg.testo)
      activities.append(msg)    

    template_values['main'] = 'comments/comment.html'
      
    if messaggio.livello == 0: #posting root message      
      activities = sorted(activities, key=lambda student: student.creato_il, reverse=True)
      template_values['main'] = 'activity.html'
  
    template_values['activities'] = activities
    template_values['comments'] = activities

    return self.getBase(template_values)
    
  """
  load comments html put under a message
  """
  def get(self):
    root = self.request.get("par")
    commento_root = Messaggio.get(db.Key(root))
    commenti = Messaggio.all().filter("par", commento_root).order("creato_il")

    comments = list()
    for msg in commenti:
      comments.append(msg)
      
    comment_last = None
    if len(comments):
      comment_last = comments[len(comments)-1].key()
      
    logging.info("comment_last: " + str(comment_last))
    template_values = {
      'main': 'comments/comment.html',
      'comment_root': commento_root,
      'comments': comments,
      'comment_last': str(comment_last),
      'last': comment_last,
      'ease': False
    }
    self.getBase(template_values)

class ActivityLoadHandler(BasePage):
  def get(self):

    template_values = {
      'main': 'activity.html',
      'ease': self.request.get("ease")
    }

    buff = ""
    
    
    offset = 0
    if self.request.get("offset") != "":
      offset = int(self.request.get("offset"))
    
    template_values['activities'] = self.get_activities(offset)       

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
      'main': 'comments/voters.html',
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
    tagnames = self.request.get_all("tags")
    msg = db.Key(self.request.get('msg'))
      
    self.saveTags(msg,tagnames)

    buff = json.JSONEncoder().encode({'status': 'ok'})      
    self.response.out.write(buff)
    
  def saveTags(self,obj,tagnames):
    logging.info("tags")
    tagobjs = TagObj.all().filter("obj", obj)
    tagold = dict()
    for tagobj in tagobjs:
      tagold[tagobj.tag.nome] = tagobj
    for tagname in tagnames:
      logging.info("tagname: " + tagname)
      if (tagname in tagold) is False:
        logging.info("adding: " + tagname)
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
        
  def getTags(self):
    tags = Tag.all().order("nome")
    return tags
    
    
app = webapp.WSGIApplication([
    ('/comments/load', ActivityLoadHandler),
    ('/comments/message', CMCommentHandler),
    ('/comments/comment', CMCommentHandler),
    ('/comments/vote', CMVoteHandler),
    ('/comments/voters', CMVotersHandler),
    ('/comments/gettags', CMTagHandler), 
    ('/comments/updatetags', CMTagHandler)    
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'))

def main():
  app.run();

if __name__ == "__main__":
  main()