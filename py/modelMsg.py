#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys
from datetime import date, datetime, time, timedelta
import logging
import threading
import fpformat
from common import cached_property
from py.model import Commissario, Commissione, Allegato
from common import Const, Parser
from engineauth import models

from google.appengine.api import users
from google.appengine.ext.ndb import model
from google.appengine.api import memcache

class Messaggio(model.Model):
  def __init__(self, *args, **kwargs):
    self.allegati = None
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

  c_ua = model.KeyProperty(kind=models.User)
  creato_il = model.DateTimeProperty(auto_now_add=True)
  m_ua = model.KeyProperty(kind=models.User)
  modificato_il = model.DateTimeProperty(auto_now=True)


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
        cls._activities_cache_ver = 0
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

  @cached_property
  def body(self):
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      return self.root.get().note
    if self.tipo == 201 or self.tipo == 202:
      if "<p>" not in self.testo:
        return self.testo.replace("\n","<br/>")
      else:
        return self.testo

  @cached_property
  def summary(self):
    summary = ""
    if self.tipo == 101 or self.tipo == 102 or self.tipo == 103 or self.tipo == 104:
      summary = self.root.get().sommario()
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
      return len(self.testo) > 80 or self.has_allegati

  def tipodesc(self):
    return Messaggio._tipi[int(self.tipo)]

  _tipi = {101:"Ispezione",
           102:"Non Conformita",
           103:"Ispezione Dieta",
           104:"Nota",
           201:"Messaggio",
           202:"Commento"}
