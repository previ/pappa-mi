#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from datetime import date, datetime, time, timedelta
import logging
import fpformat
from py.model import Commissario, Commissione
from common import Const

from google.appengine.api import users
from ndb import model
from google.appengine.api import memcache

class Messaggio(model.Model):
  def __init__(self, *args, **kwargs):
    self._commissario = None
    self._tags = None
    super(Messaggio, self).__init__(*args, **kwargs)  

  root = model.KeyProperty()
  par = model.KeyProperty()
  grp = model.KeyProperty()
  tipo = model.IntegerProperty()
  livello = model.IntegerProperty()
  commenti = model.IntegerProperty()
  pop = model.IntegerProperty()
  titolo = model.StringProperty(indexed=False)
  testo = model.TextProperty(indexed=False)
  
  creato_da = model.UserProperty(auto_current_user_add=True)
  creato_il = model.DateTimeProperty(auto_now_add=True)
  modificato_da = model.UserProperty(auto_current_user=True)
  modificato_il = model.DateTimeProperty(auto_now=True)

  @classmethod
  def get_by_tagname(cls, tagname, offset=0):
    #logging.info("get_activities_by_tagname")
    activities = memcache.get("msg-tag-" + tagname + "-" + str(offset))
    if activities == None:
      activities = list()
      tag = Tag.get_by_name(tagname)
      if tag:
        count = 0
        for tagobj in TagObj.get_by_tag(tag):
          count += 1
          if count > Const.ACTIVITY_FETCH_LIMIT:
            break
          activities.append(tagobj.obj)
      activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      memcache.add("msg-tag-" + tagname + "-" + str(offset/Const.ACTIVITY_FETCH_LIMIT), activities, Const.ACTIVITY_CACHE_EXP)
    return activities

  @classmethod
  def get_by_msgtype(cls, msgtype, offset=0):
    #logging.info("get_activities_by_msgtype")
    activities = memcache.get("msg-type-" + str(msgtype) + "-" + str(offset))
    if activities == None:
      activities = list()
      #logging.info("get_activities_by_msgtype: " + str(msgtype))
      for msg in Messaggio.query().filter(Messaggio.tipo == msgtype).order(-Messaggio.creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT, offset=offset*Const.ACTIVITY_FETCH_LIMIT):
        #logging.info("get_activities_by_msgtype: " + str(msg.tipo))
        activities.append(msg)
      memcache.add("msg-type-" + str(msgtype) + "-" + str(offset), activities, Const.ACTIVITY_CACHE_EXP)
    return activities

  @classmethod
  def get_by_user(cls, user_email, offset=0):
    activities = memcache.get("msg-user-" + user_email + "-" + str(offset))
    if activities == None:
      activities = list()
      for msg in Messaggio.query().filter(Messaggio.creato_da == users.User(user_email)).order(-Messaggio.creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT, offset=offset*Const.ACTIVITY_FETCH_LIMIT):
        activities.append(msg)
      memcache.add("msg-user-" + user_email + "-" + str(offset), activities, Const.ACTIVITY_CACHE_EXP)
    return activities

  @classmethod
  def get_all(cls, offset=0):
    #logging.info('get_activities_all')
    activities = memcache.get("msg-all-" + str(offset))
    if not activities:
      activities = list()
      for msg in Messaggio.query().filter(Messaggio.livello == 0).order(-Messaggio.creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT, offset=offset*Const.ACTIVITY_FETCH_LIMIT):
        activities.append(msg)
        
      activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      memcache.add("msg-all-" + str(offset), activities, Const.ACTIVITY_CACHE_EXP)
    return activities

  @classmethod
  def get_by_grp(cls, grp_key, offset=0):
    activities = memcache.get("msg-grp-" + str(grp_key) + "-" + str(offset))
    if not activities:
      activities = list()
      for msg in Messaggio.query().filter(Messaggio.grp == grp_key).order(-Messaggio.creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT, offset=offset*Const.ACTIVITY_FETCH_LIMIT):
        activities.append(msg)
        
      activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      memcache.add("msg-grp-" + str(grp_key) + "-" + str(offset), activities, Const.ACTIVITY_CACHE_EXP)
    return activities
  
  @classmethod
  def get_by_parent(cls, parent):
    activities = list()
    for a in Messaggio.query().filter(Messaggio.par == parent).order(Messaggio.creato_il):
      activities.append(a)
    return activities
  
  @classmethod
  def get_all_from_item(cls, item_key, descending = True):
    activities = list()
    for msg in Messaggio.query().filter(Messaggio.livello == 0).filter(Messaggio.creato_il > item_key.get().creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT):
      activities.append(msg)
    activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=descending)
    return activities
  
  @classmethod
  def get_all_from_item_parent(cls, item_key, activity):
    activities = list()
    msgs = Messaggio.query()
    if activity.par:
      msgs = msgs.filter(Messaggio.par == activity.par)
    
    if item_key:
      msgs = msgs.filter(Messaggio.creato_il > item_key.get().creato_il)
      
    for msg in msgs.filter(Messaggio.livello == activity.livello):
      activities.append(msg)    
      
    activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      
    return activities
      
  @classmethod
  def get_root(cls, parent):
    return cls.query().filter(Messaggio.par == parent).get()

  def invalidate_cache(self):
    for i in range(0,1000):
      if memcache.get("msg-user-"+self.creato_da.email()+"-"+str(i)) == None:
        break
      memcache.delete("msg-user-"+self.creato_da.email()+"-"+str(i))
    for i in range(0,1000):
      if memcache.get("msg-grp-"+str(self.grp)+"-"+str(i)) == None:
        break
      memcache.delete("msg-grp-"+str(self.grp)+"-"+str(i))
    for i in range(0,1000):
      if memcache.get("msg-type-"+str(self.tipo)+"-"+str(i)) == None:
        break
      memcache.delete("msg-type-"+str(self.tipo)+"-"+str(i))
    for i in range(0,1000):
      if memcache.get("msg-all-"+str(i)) == None:
        break
      memcache.delete("msg-all-"+str(i))
    
  def get_commissario(self):
    if not self._commissario:
      self._commissario = Commissario.get_by_user(self.modificato_da)
    return self._commissario
    
  def likes(self):
    return len(self.get_votes())

  def canvote(self):
    canvote = True
    for p_voto in self.get_votes():
      if p_voto.creato_da == users.get_current_user():
        canvote = False
        break;
    return canvote

  def get_votes(self):
    voti = memcache.get("msg-voti-"+str(self.key.id()))
    if voti is None:
      voti = list()
      for voto in Voto.get_by_msg(self.key):
        voti.append(voto)
      memcache.add("msg-voti-"+str(self.key.id()), voti)
    return voti
  
  def vote(self, vote, user):
    voto = Voto()
    for p_voto in self.get_votes():
      if p_voto.creato_da == user:
        voto = p_voto
        break;
    voto.messaggio = self.key
    voto.voto = vote
    if voto.voto == 0 and voto.key:
      voto.key.delete()
    else:
      voto.put()
    memcache.delete("msg-voti-"+str(self.key.id()))
  
  def data(self):
    delta = datetime.now() - self.creato_il
    if delta.days == 0 and delta.seconds < 3600:
      return str(delta.seconds / 60) + " minuti fa"
    elif delta.days == 0 and delta.seconds < 3600*24:
      return str(delta.seconds / 3600) + " ore fa"
    else:
      return "il " + datetime.strftime(self.creato_il, Const.DATE_FORMAT + " alle " + Const.ACTIVITY_TIME_FORMAT)

  def author(self):
    return self.get_commissario().nomecompleto()

  def author_title(self):
    return self.get_commissario().titolo()

  def author_avatar(self):
    return self.get_commissario().avatar()

  def tags(self):
    if not self._tags:
      self._tags = list()
      for to in TagObj.get_by_obj_key(self.key):
        self._tags.append(to.tag.get())
    return self._tags
  
  def title(self):
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      return self.root.get().commissione.get().desc() + " - " + self.tipodesc() + " del " + datetime.strftime(self.root.get().data(), Const.DATE_FORMAT)
    if self.tipo == 201:
      return self.titolo
    if self.tipo == 202:
      return ""
    return "default"

  def body(self):
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      return self.root.get()
    if self.tipo == 201 or self.tipo == 202:
      return self.testo

  def summary(self):
    if self.tipo == 101 :
      return self.root.get().note
    if self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      return ""
    if self.tipo == 201 or self.tipo == 202:
      s = ""
      if len(self.testo) > 77:
        s = "(leggi...)"
      else:
        s = self.testo
        
      return s

  def comments(self):
    if self.commenti is None:
      return 0
    else:
      return self.commenti
  
  def tipodesc(self):
    return Messaggio._tipi[int(self.tipo)]

  _tipi = {101:"Ispezione",
           102:"Non Conformita",
           103:"Ispezione Dieta",
           104:"Nota",
           201:"Messaggio",
           202:"Commento"}

  
class Tag(model.Model):
  nome = model.StringProperty()
  numRef = model.IntegerProperty()
  last = model.DateTimeProperty(auto_now_add=True)
  maxRef = int()

  creato_da = model.UserProperty(auto_current_user_add=True)
  creato_il = model.DateTimeProperty(auto_now_add=True)

  @classmethod
  def get_all(cls):
    return Tag.query().order(Tag.nome)
  
  @classmethod
  def get_top_referenced(cls, num):
    tags = memcache.get("toptags")
    if not tags:
      tags = list()
      for tag in Tag.query().order(-Tag.numRef).fetch(num):
        tags.append(tag)
      memcache.add("toptags", tags, 60)      
    return tags
  

  _tag_cache = dict()
  @classmethod
  def get_by_name(cls, name):
    tag = cls._tag_cache.get(name)
    if not tag:
      tag = Tag.query().filter(Tag.nome == name).get()
      cls._tag_cache[name] = tag
    return tag
        
  def size(self):
    return self.numRef
    

class TagObj(model.Model):
  tag = model.KeyProperty(kind=Tag)
  obj = model.KeyProperty()
  
  @classmethod
  def get_by_obj_key(cls, obj):
    return TagObj.query().filter(TagObj.obj == obj)
  
class Voto(model.Model):
  def __init__(self, *args, **kwargs):
    self._commissario = None
    super(Voto, self).__init__(*args, **kwargs)  
  
  messaggio = model.KeyProperty(kind=Messaggio)
  voto = model.IntegerProperty()
  creato_da = model.UserProperty(auto_current_user_add=True)
  creato_il = model.DateTimeProperty(auto_now_add=True)
  
  def author(self):
    if not self._commissario:
      self._commissario = Commissario.get_by_user(self.creato_da)
    return self._commissario.nomecompleto()
  def author_title(self):
    if not self._commissario:
      self._commissario = Commissario.get_by_user(self.creato_da)
    return self._commissario.titolo()
  def author_avatar(self):
    if not self._commissario:
      self._commissario = Commissario.get_by_user(self.creato_da)
    return self._commissario.avatar()
  
  @classmethod
  def get_by_msg(cls, msg):
    return Voto.query().filter(Voto.messaggio==msg)
    
  
  
class UserSubscription(model.Model):
  user = model.UserProperty(auto_current_user_add=True)
  obj = model.KeyProperty()
  tipo = model.StringProperty()

class Group(model.Model):
  nome = model.StringProperty()
  tipo = model.IntegerProperty()
  desc = model.TextProperty()
  
  stato = model.IntegerProperty()
  creato_da = model.UserProperty(auto_current_user_add=True)
  creato_il = model.DateTimeProperty(auto_now_add=True)
  
class UserGroup(model.Model):
  user = model.UserProperty(auto_current_user_add=True)
  group = model.KeyProperty(kind=Group)