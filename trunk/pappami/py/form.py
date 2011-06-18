#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext.db import djangoforms
from django import newforms
import logging

from py.model import *

class IspezioneForm(djangoforms.ModelForm):
  def clean(self):
    super(IspezioneForm,self).clean()
    cleaned_data = self._cleaned_data()
    #for f in cleaned_data:
      #logging.info("data: %s, %s", f, cleaned_data.get(f))
    pastiTotale = int(cleaned_data.get("numeroPastiTotale"))
    pastiBambini = int(cleaned_data.get("numeroPastiBambini"))
    pastiSpeciali = int(cleaned_data.get("numeroPastiSpeciali"))
    
    if pastiTotale < pastiBambini or pastiBambini < pastiSpeciali:
      raise newforms.ValidationError("Il numero di pasti serviti ai bambini deve essere minore del numero totale pasti serviti")
    
    if pastiBambini < pastiSpeciali:
      raise newforms.ValidationError("Il numero di pasti speciali serviti deve essere minore del numero pasti serviti ai bambini")

    if Ispezione.all().filter("dataIspezione",cleaned_data.get("dataIspezione")).filter("commissione",cleaned_data.get("commissione")).filter("turno",cleaned_data.get("turno")).count() > 0 :
      raise newforms.ValidationError("Esiste gia una scheda di ispezione per questa commissione con la stessa data e turno.")

    if cleaned_data.get("dataIspezione").isoweekday() > 5 :
      raise newforms.ValidationError("L'ispezione deve essere fatta in un giorno feriale")

    age = (date.today() - cleaned_data.get("dataIspezione")).days
    #if age > 60 :
    #  raise newforms.ValidationError("Non e' ammesso inserire schede di Ispezione effettuate in date antecedenti di 60 giorni o oltre")

    if age < 0 :
      raise newforms.ValidationError("Non è ammesso inserire schede di Ispezione effettuate in date successive alla data odierna")

    # Always return the full collection of cleaned data.
    return cleaned_data

  #dataIspezione = djangoforms.DateField(blank=True)
  
  class Meta:
    model = Ispezione
    exclude = ['creato_il','creato_da','modificato_il','modificato_da','commissario']
    
class NonconformitaForm(djangoforms.ModelForm):
  def clean(self):
    super(NonconformitaForm,self).clean()
    cleaned_data = self._cleaned_data()
    #for f in cleaned_data:
      #logging.info("data: %s, %s", f, cleaned_data.get(f))

    if Nonconformita.all().filter("dataNonconf",cleaned_data.get("dataNonconf")).filter("commissione",cleaned_data.get("commissione")).filter("turno",cleaned_data.get("turno")).filter("tipo",cleaned_data.get("tipo")).count() > 0 :
      raise newforms.ValidationError("Esiste gia' una scheda di Non Conformita' per questa commissione con la stessa data e turno.")

    if cleaned_data.get("dataNonconf").isoweekday() > 5 :
      raise newforms.ValidationError(u"La scheda di Non Conformita' deve essere fatta in un giorno feriale")

    age = (date.today() - cleaned_data.get("dataNonconf")).days
    #if age > 60 :
    #  raise newforms.ValidationError(u"Non e' ammesso inserire schede di Non Conformita' effettuate in date antecedenti di 60 giorni o oltre")

    if age < 0 :
      raise newforms.ValidationError(u"Non è ammesso inserire schede di Non Conformità effettuate in date successive alla data odierna")

    # Always return the full collection of cleaned data.
    return cleaned_data

  class Meta:
    model = Nonconformita
    exclude = ['creato_il','creato_da','modificato_il','modificato_da','commissario']

class DietaForm(djangoforms.ModelForm):
  def clean(self):
    super(DietaForm,self).clean()
    cleaned_data = self._cleaned_data()
    #for f in cleaned_data:
      #logging.info("data: %s, %s", f, cleaned_data.get(f))

    if Dieta.all().filter("dataIspezione",cleaned_data.get("dataIspezione")).filter("commissione",cleaned_data.get("commissione")).filter("turno",cleaned_data.get("turno")).filter("tipoDieta",cleaned_data.get("tipo")).count() > 0 :
      raise newforms.ValidationError("Esiste già una scheda di Ispezione Diete per questa commissione con la stessa data e turno.")

    if cleaned_data.get("dataIspezione").isoweekday() > 5 :
      raise newforms.ValidationError(u"La scheda di Ispezione deve essere fatta in un giorno feriale")

    age = (date.today() - cleaned_data.get("dataIspezione")).days
    #if age > 60 :
    #  raise newforms.ValidationError(u"Non e' ammesso inserire schede di Non Conformita' effettuate in date antecedenti di 60 giorni o oltre")

    if age < 0 :
      raise newforms.ValidationError(u"Non è ammesso inserire schede di Ispezione effettuate in date successive alla data odierna")

    # Always return the full collection of cleaned data.
    return cleaned_data
  class Meta:
    model = Dieta
    exclude = ['creato_il','creato_da','modificato_il','modificato_da','commissario']

class NotaForm(djangoforms.ModelForm):
  def clean(self):
    super(NotaForm,self).clean()
    cleaned_data = self._cleaned_data()
    #for f in cleaned_data:
      #logging.info("data: %s, %s", f, cleaned_data.get(f))

    if cleaned_data.get("dataNota").isoweekday() > 5 :
      raise newforms.ValidationError(u"La Nota deve far riferimento a un giorno feriale")

    age = (date.today() - cleaned_data.get("dataNota")).days
    #if age > 60 :
    #  raise newforms.ValidationError(u"Non e' ammesso inserire schede di Non Conformita' effettuate in date antecedenti di 60 giorni o oltre")

    if age < 0 :
      raise newforms.ValidationError(u"Non è ammesso inserire note in date successive alla data odierna")
   
    # Always return the full collection of cleaned data.
    return cleaned_data
  class Meta:
    model = Nota
    exclude = ['commissario']
    
class CommissioneForm(djangoforms.ModelForm):
  class Meta:
    model = Commissione

    