#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from datetime import date, datetime, time, timedelta
import logging
import fpformat
from py.model import Commissario

from google.appengine.api import users
from google.appengine.ext import db

TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%d/%m/%Y"

class Messaggio(db.Model):
  root = db.ReferenceProperty(db.Model, collection_name="children_all_set")
  par = db.ReferenceProperty(db.Model, collection_name="children_set")
  tipo = db.IntegerProperty()
  livello = db.IntegerProperty()
  pop = db.IntegerProperty()
  titolo = db.StringProperty(indexed=False)
  testo = db.TextProperty(indexed=False)
  
  creato_da = db.UserProperty(auto_current_user_add=True)
  creato_il = db.DateTimeProperty(auto_now_add=True)
  modificato_da = db.UserProperty(auto_current_user=True)
  modificato_il = db.DateTimeProperty(auto_now=True)
  
  commissario = None
  
  __tags__ = None

  def likes(self):
    return self.voto_reference_set.count()
  def canvote(self):
    canvote = True
    for p_voto in self.voto_reference_set:
      if p_voto.creato_da == users.get_current_user():
        canvote = False
        break;
      
    return canvote
  def data(self):
    delta = datetime.now() - self.creato_il
    if delta.days == 0 and delta.seconds < 3600:
      return str(delta.seconds / 60) + " minuti fa"
    elif delta.days == 0 and delta.seconds < 3600*24:
      return str(delta.seconds / 3600) + " ore fa"
    else:
      return "il " + datetime.strftime(self.creato_il, DATE_FORMAT + " alle " + TIME_FORMAT)
  def author(self):
    if not self.commissario:
      self.commissario = Commissario.all().filter("user", self.modificato_da).get()
    return self.commissario.nomecompleto()
  def author_title(self):
    if not self.commissario:
      self.commissario = Commissario.all().filter("user", self.modificato_da).get()
    return self.commissario.titolo()
  def author_avatar(self):
    if not self.commissario:
      self.commissario = Commissario.all().filter("user", self.modificato_da).get()
    return self.commissario.avatar()

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
      return self.root.commissione.desc() + " - " + self.tipodesc() + " del " + datetime.strftime(self.root.data(), DATE_FORMAT)
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
        s = self.testo[0:77] + " ..."
      else:
        s = self.testo
        
      return s
    
  
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
  
  def size(self):
    return self.numRef
    

class TagObj(db.Model):
  tag = db.ReferenceProperty(Tag,collection_name="tagobj_reference_set")
  obj = db.ReferenceProperty(db.Model,collection_name="tagobj_reference_set" )
  
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
