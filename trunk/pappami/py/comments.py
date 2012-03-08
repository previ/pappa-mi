#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from py.base import Const, BasePage, commissario_required, reguser_required

import os, cgi, logging, urllib, json
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext.ndb import model
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
from py.gcalendar import *
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
  @classmethod
  def init(cls, msg_rif, msg_grp, tipo, tags, user):
    messaggio = Messaggio.get_by_parent(msg_rif)
    if not messaggio:  
      messaggio = Messaggio()
      messaggio.par = msg_rif
      messaggio.root = msg_rif
      messaggio.grp = msg_grp
      messaggio.livello = 0
      messaggio.tipo = tipo
      messaggio.commenti = 0
      messaggio.c_ua = user.key
      messaggio.put()
      if tags:
        CMTagHandler.saveTags(messaggio, tags)
        
      messaggio.invalidate_cache();
    return messaggio

  """
  init a comment structure, attaching a root message to an existing object
  and return the delta activity stream html
  """
  @classmethod
  def initActivity(self, msg_rif, msg_grp, tipo, last, tags, user):

    CMCommentHandler.init(msg_rif, msg_grp, tipo, tags, user)
    
    buff = ""

    activities = Messaggio.get_all_from_item(last)

    template_values = {
      'main': 'activity.html',
      'ease': True
    }
    template_values['activities'] = activities       

    return template_values

  """
  return the root object of a given message (comment)
  """
  @classmethod
  def getRoot(cls, msg_rif):
    return Message.get_parent(msg_rif)
  
  """
  http post handler
  handle both new message and new comment (livello is the discriminant)
  return the delta activity stream in html
  """
  @reguser_required
  def post(self):
    par_key = None
    rif = self.request.get("par")
    if rif:
      par_key = model.Key("Messaggio", int(rif))

    messaggio = Messaggio()
    messaggio.par = par_key
    messaggio.tipo = int(self.request.get("tipo"))
    messaggio.livello = int(self.request.get("livello"))
    messaggio.titolo = self.request.get("titolo")
    messaggio.testo = self.request.get("testo")
    messaggio.commenti = 0
    messaggio.c_ua = self.request.user.key    
    messaggio.put()

    logging.info("testo: " + self.request.get("testo"))
    logging.info("last: " + self.request.get("last"))
    
    if messaggio.livello > 0 and par_key:
      par = par_key.get()
      commenti = par.commenti
      if commenti is None:
        commenti = 0
      par.commenti = commenti + 1
      par.put()
   
    CMTagHandler.saveTags(messaggio, self.request.get_all("tags"))
  
    template_values = {
      'activity': messaggio,
      'ease': True
    }
    messaggio.invalidate_cache();
    last_key = None
    if self.request.get("last") != "":
      last_key = model.Key("Messaggio", int(self.request.get("last")))
    activities = Messaggio.get_all_from_item_parent(last_key, messaggio)

    template_values['main'] = 'comments/comment.html'
          
    if messaggio.livello == 0: #posting root message      
      template_values['main'] = 'activity.html'
      comment_root = messaggio
    else:
      comment_root = model.Key("Messaggio",int(self.request.get("root"))).get()
  
    template_values['activities'] = activities
    template_values['comments'] = activities
    template_values['comment_root'] = comment_root

    return self.getBase(template_values)
    
  """
  load comments html put under a message
  """
  def get(self):
    root = self.request.get("par")
    commento_root = model.Key("Messaggio", int(root)).get()
    commenti = Messaggio.get_by_parent(commento_root.key)

    comments = list()
    for msg in commenti:
      comments.append(msg)
      
    comment_last = None
    if len(comments):
      comment_last = comments[len(comments)-1]
      
    logging.info("comment_last: " + str(comment_last))
    template_values = {
      'main': 'comments/comment.html',
      'comment_root': commento_root,
      'comments': comments,
      'comment_last': comment_last,
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

    limit = None
    if self.request.get("limit") != "":     
      template_values['limit'] = int(self.request.get("limit"))
    template_values['activities'] = self.get_activities(offset)

    self.getBase(template_values)
    
  
class CMVoteHandler(BasePage):
  @reguser_required
  def get(self):
    messaggio = model.Key("Messaggio", int(self.request.get('msg'))).get()

    messaggio.vote(int(self.request.get('voto')), self.request.user)
    self.response.out.write(len(messaggio.get_votes()))

class CMVotersHandler(BasePage):  
  def get(self):
    messaggio = model.Key("Messaggio", int(self.request.get('msg'))).get()    
    template_values = {
      'main': 'comments/voters.html',
      'votes': messaggio.get_votes()
    }
    self.getBase(template_values)    

class CMTagHandler(BasePage):
  def get(self):
    alltags = list()
    assignedtags = list()
    msg = None
    if self.request.get('msg'):
      msg = model.Key("Messaggio", int(self.request.get('msg')))
    tagobjs = TagObj.get_by_obj_key(msg)
    for tagobj in tagobjs:
      assignedtags.append(tagobj.tag.get().nome)
    for tag in Tag.get_all():
      alltags.append(tag.nome)

    buff = json.JSONEncoder().encode({'assignedTags': assignedtags, 'availableTags':alltags})      
    self.response.out.write(buff)
    
  @reguser_required
  def post(self):
    tagnames = self.request.get_all("tags")
      
    CMTagHandler.saveTags(messaggio.Key("Messaggio", int(self.request.get('msg'))),tagnames)

    buff = json.JSONEncoder().encode({'status': 'ok'})      
    self.response.out.write(buff)
    
  @classmethod
  def saveTags(cls,obj,tagnames):
    logging.info("tags")
    tagobjs = TagObj.get_by_obj_key(obj.key)
    tagold = dict()
    for tagobj in tagobjs:
      tagold[tagobj.tag.nome] = tagobj
    for tagname in tagnames:
      logging.info("tagname: " + tagname)
      if (tagname in tagold) is False:
        logging.info("adding: " + tagname)
        tag = Tag.get_by_name(tagname)
        if not tag:
          tag = Tag(nome=tagname, numRef=0)
          tag.c_ua = obj.c_ua
          tag.put()
        tagobj = TagObj(tag=tag.key,obj=obj.key)
        tagobj.put()
        tag = tagobj.tag.get()
        tag.numRef += 1
        tag.put()
    for name in tagold:
      logging.info(name)
      
      if (name in tagnames) is False:
        logging.info("removing:" + name)
        tagobj = tagold[name]
        tag = tagobj.tag.get()
        tag.numRef -= 1
        tag.put()
        tagobj.key.delete()
        
  def getTags(self):
    tags = Tag.get_all()
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