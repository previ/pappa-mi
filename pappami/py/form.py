#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import fixpath
from wtforms.ext.appengine.ndb import model_form
from wtforms.validators import ValidationError
from py.model import *

class IspezioneForm(model_form(model=Ispezione, exclude=['creato_il','creato_da','modificato_il','modificato_da','commissario','lavaggioFinale','contornoCottura','anno','stato',"commissione"])):

  def validate_dataIspezione(form, field):
    dataIspezione = field.data
    
    if Ispezione.get_by_cm_data_turno(form.commissione, dataIspezione, form.turno.data).get() :
      logging.info("Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.")
      raise ValidationError("Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.")
  
    if dataIspezione.isoweekday() > 5 :
      logging.info("L'ispezione deve essere fatta in un giorno feriale")
      raise ValidationError("L'ispezione deve essere fatta in un giorno feriale")
  
    age = (date.today() - dataIspezione).days
    #if age > 60 :
    #  raise ValidationError("Non e' ammesso inserire schede di Ispezione effettuate in date antecedenti di 60 giorni o oltre")
  
    if age < 0 :
      logging.info("Non è ammesso inserire schede di Ispezione effettuate in date successive alla data odierna")
      raise ValidationError("Non è ammesso inserire schede di Ispezione effettuate in date successive alla data odierna")
    
  def validate_pastiTotale(form, field):
    pastiTotale = int(form.numeroPastiTotale.data)
    pastiBambini = int(form.numeroPastiBambini.data)
    pastiSpeciali = int(form.numeroPastiSpeciali.data)
    
    if pastiTotale < pastiBambini or pastiBambini < pastiSpeciali:
      raise ValidationError("Il numero di pasti serviti ai bambini deve essere minore del numero totale pasti serviti")
    
    if pastiBambini < pastiSpeciali:
      raise ValidationError("Il numero di pasti speciali serviti deve essere minore del numero pasti serviti ai bambini")


    
class NonconformitaForm(model_form(model=Nonconformita, exclude=['creato_il','creato_da','modificato_il','modificato_da','commissario','anno','stato',"commissione"])):
  def validate_dataNonconf(form, field):
    dataNonconf = field.data
    logging.info(dataNonconf)
    if Nonconformita.get_by_cm_data_turno(cm=form.commissione, data=dataNonconf, turno=form.turno.data).count() > 10 :
      logging.info("Esistona gia' 10 Non Conformita' per questa commissione con la stessa data e turno.")
      raise ValidationError("Esiste gia' 10 segnalazioni di Non Conformita' per questa commissione con la stessa data e turno.")

    logging.info("1")
    if dataNonconf.isoweekday() > 5 :
      logging.info("La scheda di Non Conformita' deve essere fatta in un giorno feriale")
      raise ValidationError(u"La scheda di Non Conformita' deve essere fatta in un giorno feriale")

    age = (date.today() - dataNonconf).days
    #if age > 60 :
    #  raise ValidationError(u"Non e' ammesso inserire schede di Non Conformita' effettuate in date antecedenti di 60 giorni o oltre")

    if age < 0 :
      logging.info("Non è ammesso inserire schede di Non Conformità effettuate in date successive alla data odierna")
      raise ValidationError(u"Non è ammesso inserire schede di Non Conformità effettuate in date successive alla data odierna")


class DietaForm(model_form(model=Dieta, exclude=['creato_il','creato_da','modificato_il','modificato_da','commissario','anno','stato',"commissione"])):

  def validate_dataIspezione(form, field):
    dataIspezione = field.data
    if Dieta.get_by_cm_data_turno_tipo(form.commissione, dataIspezione, form.turno.data, form.tipoDieta.data).get() :
      raise ValidationError("Esiste gia una scheda di ispezione Diete per questa commissione con la stessa data e turno e tipo di dieta.")
  
    if dataIspezione.isoweekday() > 5 :
      raise ValidationError("L'ispezione deve essere fatta in un giorno feriale")
  
    age = (date.today() - dataIspezione).days
    #if age > 60 :
    #  raise ValidationError("Non e' ammesso inserire schede di Ispezione effettuate in date antecedenti di 60 giorni o oltre")
  
    if age < 0 :
      raise ValidationError("Non è ammesso inserire schede di Ispezione effettuate in date successive alla data odierna")
  

class NotaForm(model_form(model=Nota, exclude=['creato_il','creato_da','modificato_il','modificato_da','commissario','anno','stato',"commissione"])):
  def validate_dataNota(form, field):
    dataNota = field.data

    if dataNota.isoweekday() > 5 :
      raise ValidationError(u"La Nota deve far riferimento a un giorno feriale")

    age = (date.today() - dataNota).days
    #if age > 60 :
    #  raise ValidationError(u"Non e' ammesso inserire schede di Non Conformita' effettuate in date antecedenti di 60 giorni o oltre")

    if age < 0 :
      raise ValidationError(u"Non è ammesso inserire note in date successive alla data odierna")
       
class CommissioneForm(model_form(Commissione)):
  class Meta:
    model = Commissione

class CommissarioForm(model_form(model=Commissario, exclude=['creato_il','creato_da','modificato_il','modificato_da', 'avatar_data', 'citta', 'privacy', 'notify'])):  
  stored = False
    
    