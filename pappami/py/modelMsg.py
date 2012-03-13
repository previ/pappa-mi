#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys
from datetime import date, datetime, time, timedelta
import logging
import threading
import fpformat
from common import cached_property
from py.model import Commissario, Commissione
from common import Const, Parser

from google.appengine.api import users
from google.appengine.ext.ndb import model
from google.appengine.api import memcache

class Messaggio(model.Model):
  def __init__(self, *args, **kwargs):
    #self._commissario = None
    #self._tags = None
    #self._votes = None
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
  
  creato_da = model.UserProperty()
  c_ua = model.KeyProperty()
  creato_il = model.DateTimeProperty(auto_now_add=True)
  modificato_da = model.UserProperty()
  modificato_il = model.DateTimeProperty(auto_now=True)

  @classmethod
  def get_by_tagname(cls, tagname, offset=0):
    #activities = memcache.get("msg-tag-" + tagname + "-" + str(offset))
    with cls._activities_lock:
      cls.check_cache()
      activities = cls._activities.get("msg-tag-" + tagname + "-" + str(offset))
      if activities == None:
        activities = list()
        tag = Tag.get_by_name(tagname)
        if tag:
          count = 0
          for tagobj in TagObj.get_by_tag(tag):
            count += 1
            if count > Const.ACTIVITY_FETCH_LIMIT:
              break
            activities.append(tagobj.obj.get())
        activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
        #memcache.add("msg-tag-" + tagname + "-" + str(offset/Const.ACTIVITY_FETCH_LIMIT), activities, Const.ACTIVITY_CACHE_EXP)
        cls._activities["msg-tag-" + tagname + "-" + str(offset)] = activities
    return activities

  @classmethod
  def get_by_msgtype(cls, msgtype, offset=0):
    #activities = memcache.get("msg-type-" + str(msgtype) + "-" + str(offset))
    with cls._activities_lock:
      cls.check_cache()
      activities = cls._activities.get("msg-type-"  + str(msgtype) + "-" + str(offset))
      if activities == None:
        activities = list()
        for msg in Messaggio.query().filter(Messaggio.tipo == msgtype).order(-Messaggio.creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT, offset=offset*Const.ACTIVITY_FETCH_LIMIT):
          activities.append(msg)
        #memcache.add("msg-type-" + str(msgtype) + "-" + str(offset), activities, Const.ACTIVITY_CACHE_EXP)
        cls._activities["msg-type-"  + str(msgtype) + "-" + str(offset)] = activities
      return activities

  @classmethod
  def get_by_user(cls, user_id, offset=0):
    #activities = memcache.get("msg-user-" + str(user_id) + "-" + str(offset))
    with cls._activities_lock:
      cls.check_cache()
      activities = cls._activities.get("msg-user-" + str(user_id) + "-" + str(offset))    
      if activities == None:
        activities = list()
        for msg in Messaggio.query().filter(Messaggio.c_ua == model.Key("User", user_id)).order(-Messaggio.creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT, offset=offset*Const.ACTIVITY_FETCH_LIMIT):
          activities.append(msg)
        #memcache.add("msg-user-" + str(user_id) + "-" + str(offset), activities, Const.ACTIVITY_CACHE_EXP)
        cls._activities["msg-user-" + str(user_id) + "-" + str(offset)] = activities
      return activities

  _activities = dict()
  _activities_cache_ver = 1
  _activities_lock = threading.RLock()
  @classmethod  
  def get_all(cls, offset=0):
    #activities = memcache.get("msg-all-" + str(offset))
    with cls._activities_lock:
      cls.check_cache()
      activities = cls._activities.get("msg-all-" + str(offset))
      if not activities:      
        activities = list()
        for msg in Messaggio.query().filter(Messaggio.livello == 0).order(-Messaggio.creato_il).fetch(limit=Const.ACTIVITY_FETCH_LIMIT, offset=offset*Const.ACTIVITY_FETCH_LIMIT):
          activities.append(msg)
          
        activities = sorted(activities, key=lambda activity: activity.creato_il, reverse=True)
        #memcache.add("msg-all-" + str(offset), activities, Const.ACTIVITY_CACHE_EXP)
        cls._activities["msg-all-" + str(offset)] = activities
      return activities

  @classmethod
  def get_by_grp(cls, grp_key, offset=0):
    #activities = memcache.get("msg-grp-" + str(grp_key) + "-" + str(offset))
    with cls._activities_lock:
      cls.check_cache()
      activities = cls._activities.get("msg-grp-" + str(grp_key) + "-" + str(offset))
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

  @classmethod
  def check_cache(cls):    
    with cls._activities_lock:
      cache_ver = memcache.get("act-cache-ver")
      if cache_ver is None:
        cache_ver = 1
        memcache.add("act-cache-ver", cache_ver)
      if cache_ver > cls._activities_cache_ver:
        logging.info("cache not valid")
        cls._activities = dict()
        cls._activities_cache_ver = cache_ver
        
        
  
  @classmethod
  def invalidate_cache(cls):
    with cls._activities_lock:      
      logging.info("invalidate_cache")
      #cls._activities_cache_ver += 1
      memcache.incr("act-cache-ver")
      
    #for i in range(0,1000):
      #if memcache.get("msg-user-"+str(self.c_ua.id())+"-"+str(i)) == None:
        #break
      #memcache.delete("msg-user-"+str(self.c_ua.id())+"-"+str(i))
    #if self.grp:
      #for i in range(0,1000):
        #if memcache.get("msg-grp-"+str(self.grp.id())+"-"+str(i)) == None:
          #break
        #memcache.delete("msg-grp-"+str(self.grp.id())+"-"+str(i))
    #for i in range(0,1000):
      #if memcache.get("msg-type-"+str(self.tipo)+"-"+str(i)) == None:
        #break
      #memcache.delete("msg-type-"+str(self.tipo)+"-"+str(i))
    #for i in range(0,1000):
      #if memcache.get("msg-all-"+str(i)) == None:
        #break
      #memcache.delete("msg-all-"+str(i))
    
  @cached_property
  def commissario(self):    
    return Commissario.get_by_user(self.c_ua.get())
  
  def likes(self):
    return len(self.votes)

  def canvote(self, user):
    if not user:
      return False
    canvote = True
    for p_voto in self.votes:
      if p_voto.c_ua == user.key:
        canvote = False
        break;
    return canvote
  
  @cached_property
  def votes(self):
    voti = list()
    for voto in Voto.get_by_msg(self.key):
      voti.append(voto)
    return voti
  
  #def get_votes(self):
    #voti = self._votes
    #if voti is None:
      #voti = list()
      #for voto in Voto.get_by_msg(self.key):
        #voti.append(voto)
      #self._votes = voti
    #return voti
  
  def vote(self, vote, user):
    if vote == 0:
      for p_voto in self.votes:
        if p_voto.c_ua == user.key:
          if p_voto.voto == 1:
            p_voto.key.delete()
          break;
    else :
      voto = Voto(messaggio = self.key, voto = vote, c_ua = user.key)
      voto.put()

    try:
      del self.cache["votes"]
    except AttributeError:
      pass
    Messaggio.invalidate_cache()
  
  def data(self):
    delta = datetime.now() - self.creato_il
    if delta.days == 0 and delta.seconds < 3600:
      return str(delta.seconds / 60) + " minuti fa"
    elif delta.days == 0 and delta.seconds < 3600*24:
      return str(delta.seconds / 3600) + " ore fa"
    else:
      return "il " + datetime.strftime(self.creato_il, Const.ACTIVITY_DATE_FORMAT + " alle " + Const.ACTIVITY_TIME_FORMAT)

  def author(self, cmsro, myself=False):
    return self.commissario.nomecompleto(cmsro, myself)

  def author_title(self, cmsro, myself=False):
    return self.commissario.titolo(cmsro, myself)

  def author_avatar(self, cmsro, myself=False):
    return self.commissario.avatar(cmsro, myself)

  @cached_property
  def tags(self):
    tags = list()
    for to in TagObj.get_by_obj_key(self.key):
      tags.append(to.tag.get())
    return tags

  @cached_property
  def title(self):
    title = ""
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      title = self.root.get().commissione.get().desc() + " - " + self.tipodesc() + " del " + self.root.get().data()
    elif self.tipo == 201:
      title = self.titolo
    elif self.tipo == 202:
      pass
    else:
      pass
    return title

  def body(self):
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      return self.root.get()
    if self.tipo == 201 or self.tipo == 202:
      return self.testo

  @cached_property
  def summary(self):
    summary = ""
    if self.tipo == 101 :
      summary = self.root.get().note
    if self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      pass
    if self.tipo == 201 or self.tipo == 202:
      if len(self.testo) > 80:        
        p = Parser()
        p.text = ""
        p.feed(self.testo)
        summary = p.text[0:80] + " (continua...)"
      else:
        summary = self.testo
    return summary

  @cached_property
  def hasdetail(self):
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      return True
    elif self.tipo == 201 or self.tipo == 202:
      return len(self.testo) > 80
        
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
  c_ua = model.KeyProperty()
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
  
  @classmethod
  def get_by_tag(cls, tag):
    return TagObj.query().filter(TagObj.tag == tag.key)
  
class Voto(model.Model):
  def __init__(self, *args, **kwargs):
    self._commissario = None
    super(Voto, self).__init__(*args, **kwargs)  
  
  messaggio = model.KeyProperty(kind=Messaggio)
  voto = model.IntegerProperty()
  creato_da = model.UserProperty(auto_current_user_add=True)  
  c_ua = model.KeyProperty()
  creato_il = model.DateTimeProperty(auto_now_add=True)
  
  def author(self, cmsro, myself=False):
    if not self._commissario:
      self._commissario = Commissario.get_by_user(self.c_ua.get())
    return self._commissario.nomecompleto(cmsro, myself)
  def author_title(self, cmsro, myself=False):
    if not self._commissario:
      self._commissario = Commissario.get_by_user(self.c_ua.get())
    return self._commissario.titolo(cmsro, myself)
  def author_avatar(self, cmsro, myself=False):
    if not self._commissario:
      self._commissario = Commissario.get_by_user(self.c_ua.get())
    return self._commissario.avatar(cmsro, myself)
  
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
  c_ua = model.KeyProperty()
  creato_il = model.DateTimeProperty(auto_now_add=True)
  
class UserGroup(model.Model):
  user = model.UserProperty(auto_current_user_add=True)
  group = model.KeyProperty(kind=Group)