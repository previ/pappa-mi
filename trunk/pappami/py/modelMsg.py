#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from datetime import date, datetime, time, timedelta
import logging
import fpformat
from py.model import Commissario
from common import Const

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache

class Messaggio(db.Model):
  root = db.ReferenceProperty(db.Model, collection_name="children_all_set")
  par = db.ReferenceProperty(db.Model, collection_name="children_set")
  tipo = db.IntegerProperty()
  livello = db.IntegerProperty()
  commenti = db.IntegerProperty()
  pop = db.IntegerProperty()
  titolo = db.StringProperty(indexed=False)
  testo = db.TextProperty(indexed=False)
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)

  @classmethod
  def get_by_tagname(cls, tagname, offset=0):
    #logging.info("get_activities_by_tagname")
    activities = memcache.get("activities_tag_" + tagname + "_" + str(offset))
    if activities == None:
      activities = list()
      tag = Tag.get_by_name(tagname)
      if tag:
        count = 0
        for tagobj in tag.tagobj_reference_set[offset*Const.ACTIVITY_FETCH_LIMIT:(offset+1)*Const.ACTIVITY_FETCH_LIMIT]:
          count += 1
          if count > Const.ACTIVITY_FETCH_LIMIT:
            break
          activities.append(tagobj.obj)
      activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      memcache.add("activities_tag_" + tagname + "_" + str(offset/Const.ACTIVITY_FETCH_LIMIT), activities, 60)
    return activities

  @classmethod
  def get_by_msgtype(cls, msgtype, offset=0):
    #logging.info("get_activities_by_msgtype")
    activities = memcache.get("activities_type_" + str(msgtype) + "_" + str(offset))
    if activities == None:
      activities = list()
      #logging.info("get_activities_by_msgtype: " + str(msgtype))
      for msg in cls.all().filter("tipo", msgtype).order("-creato_il").fetch(Const.ACTIVITY_FETCH_LIMIT, offset*Const.ACTIVITY_FETCH_LIMIT):
        #logging.info("get_activities_by_msgtype: " + str(msg.tipo))
        activities.append(msg)
      memcache.add("activities_type_" + str(msgtype) + "_" + str(offset), activities, 60)
    return activities

  @classmethod
  def get_by_user(cls, user_email, offset=0):
    activities = memcache.get("activities_user_" + user_email + "_" + str(offset))
    if activities == None:
      activities = list()
      for msg in cls.all().filter("creato_da", users.User(user_email)).order("-creato_il").fetch(Const.ACTIVITY_FETCH_LIMIT, offset*Const.ACTIVITY_FETCH_LIMIT):
        activities.append(msg)
      memcache.add("activities_user_" + user_email + "_" + str(offset), activities, 60)
    return activities

  @classmethod
  def get_all(cls, offset=0):
    #logging.info('get_activities_all')
    activities = memcache.get("activities_all_" + str(offset))
    if not activities:
      activities = list()
      for msg in cls.all().filter("livello", 0).order("-creato_il").fetch(Const.ACTIVITY_FETCH_LIMIT, offset*Const.ACTIVITY_FETCH_LIMIT):
        activities.append(msg)
        
      activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      memcache.add("activities_all_" + str(offset), activities, 60)
    return activities

  @classmethod
  def get_by_parent(cls, parent):
    activities = list()
    for a in cls.all().filter("par", parent).order("creato_il"):
      activities.append(a)
    return activities
  
  @classmethod
  def get_all_from_item(cls, item_key, descending = True):
    activities = list()
    for msg in cls.all().filter("livello", 0).filter("creato_il >", Messaggio.get(item_key).creato_il).fetch(Const.ACTIVITY_FETCH_LIMIT):
      activities.append(msg)
    activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=descending)
    return activities
  
  @classmethod
  def get_all_from_item_parent(cls, item_key, activity):
    activities = list()
    msgs = Messaggio.all()
    if activity.par:
      msgs = msgs.filter("par", activity.par)
    
    if item_key:
      msgs = msgs.filter("creato_il >", Messaggio.get(item_key).creato_il)
      
    for msg in msgs.filter("livello", activity.livello):
      activities.append(msg)    
      
    activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
      
    return activities
      
  @classmethod
  def get_root(cls, parent):
    return cls.all().filter("par", parent).get()
  
  _cache = dict()
  commissario = None
  def get_commissario(self):
    if not self.commissario:
      self.commissario = Messaggio._cache.get(self.modificato_da)
      if self.commissario is None:
        self.commissario = Commissario.get_by_user(self.modificato_da)
        Messaggio._cache[self.modificato_da] = self.commissario
    return self.commissario
    
  __tags__ = None

  _likes = None
  def likes(self):
    if self._likes == None:
      self._likes = self.voto_reference_set.count()
    return self._likes

  _canvote = None
  def canvote(self):
    if self._canvote is None:
      canvote = True
      for p_voto in self.voto_reference_set:
        if p_voto.creato_da == users.get_current_user():
          canvote = False
          break;
      self._canvote = canvote
      
    return self._canvote
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
    if not self.__tags__:
      self.__tags__ = list()
      for to in self.tagobj_reference_set:
        self.__tags__.append(to.tag)
    return self.__tags__
  
  def title(self):
    #logging.info("tipo: " +self.tipodesc() )
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      #logging.info("tipo: " +self.tipodesc() + " " + self.root.commissione.nome)
      #logging.info(self.root.commissione.desc() + " - " + self.tipodesc() + " del " + datetime.strftime(self.root.creato_il, DATE_FORMAT))
      return self.root.commissione.desc() + " - " + self.tipodesc() + " del " + datetime.strftime(self.root.data(), Const.DATE_FORMAT)
    if self.tipo == 201:
      return self.titolo
    if self.tipo == 202:
      return ""
    return "default"

  def body(self):
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      return self.root
    if self.tipo == 201 or self.tipo == 202:
      return self.testo

  def summary(self):
    if self.tipo == 101 :
      return self.root.note
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
    return self._tipi[int(self.tipo)]

  _tipi = {101:"Ispezione",
           102:"Non Conformita",
           103:"Ispezione Dieta",
           104:"Nota",
           201:"Messaggio",
           202:"Commento"}

  
class Tag(db.Model):
  nome = db.StringProperty()
  numRef = db.IntegerProperty()
  last = db.DateTimeProperty(auto_now_add=True)
  maxRef = int()

  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)

  @classmethod
  def get_all(cls, num):
    return Tag.all().order("nome")
  
  @classmethod
  def get_top_referenced(cls, num):
    tags = memcache.get("toptags")
    if not tags:
      tags = list()
      for tag in cls.all().order("-numRef").fetch(num):
        tags.append(tag)
      memcache.add("toptags", tags, 60)      
    return tags
  

  _tag_cache = dict()
  @classmethod
  def get_by_name(cls, name):
    tag = cls._tag_cache.get(name)
    if not tag:
      tag = cls.all().filter("nome", name).get()
      cls._tag_cache[name] = tag
    return tag
        
  def size(self):
    return self.numRef
    

class TagObj(db.Model):
  tag = db.ReferenceProperty(Tag,collection_name="tagobj_reference_set")
  obj = db.ReferenceProperty(db.Model,collection_name="tagobj_reference_set" )
  
  @classmethod
  def get_by_obj(cls, obj):
    return TagObj.all().filter("obj", obj)
  
class Voto(db.Model):
  messaggio = db.ReferenceProperty(Messaggio,collection_name="voto_reference_set")
  voto = db.IntegerProperty()
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)

  commissario = None
  
  def author(self):
    if not self.commissario:
      self.commissario = Commissario.all().filter("user", self.creato_da).get()
    return self.commissario.nomecompleto()
  def author_title(self):
    if not self.commissario:
      self.commissario = Commissario.all().filter("user", self.creato_da).get()
    return self.commissario.titolo()
  def author_avatar(self):
    if not self.commissario:
      self.commissario = Commissario.all().filter("user", self.creato_da).get()
    return self.commissario.avatar()
  
  
class UserSubscription(db.Model):
  user = db.UserProperty(auto_current_user_add=True)
  obj = db.ReferenceProperty(db.Model)
  tipo = db.StringProperty()

class Group(db.Model):
  nome = db.StringProperty()
  tipo = db.IntegerProperty()
  desc = db.TextProperty()
  
  stato = db.IntegerProperty()
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  
class UserGroup(db.Model):
  user = db.UserProperty(auto_current_user_add=True)
  group = db.ReferenceProperty(Group)
