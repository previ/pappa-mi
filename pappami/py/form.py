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
    if age > 15 :
      raise newforms.ValidationError("Non e' ammesso inserire schede di Ispezione effettuate in date antecedenti di 15 giorni o oltre")

    if age < 0 :
      raise newforms.ValidationError("Non e' ammesso inserire schede di Ispezione effettuate in date successive alla data odierna")

    t1 = cleaned_data.get("arrivoTermiche")
    t2 = cleaned_data.get("aperturaTermiche")
    t3 = cleaned_data.get("primoInizioDist")
    t4 = cleaned_data.get("primoFineDist")
    t5 = cleaned_data.get("secondoInizioDist")
    t6 = cleaned_data.get("secondoFineDist")
    t7 = cleaned_data.get("finePasto")
    
    if t1 > t2 :
      raise newforms.ValidationError("L'ora di apertura termiche deve essere successiva all'ora di arrivo termiche")
    if t2 > t3 :
      raise newforms.ValidationError("L'ora di inizio distribuzione primo piatto deve essere successiva all'ora di apertura termiche")
    if t3 > t4 :
      raise newforms.ValidationError("L'ora di fine distribuzione primo piatto deve essere successiva all'ora di inizio distribuzione primo piatto")
    if t4 > t5 :
      raise newforms.ValidationError("L'ora di inizio distribuzione secondo piatto deve essere successiva all'ora di fine distribuzione primo piatto")
    if t5 > t6 :
      raise newforms.ValidationError("L'ora di fine distribuzione secondo piatto deve essere successiva all'ora di inizio distribuzione secondo piatto")
    if t6 > t7 :
      raise newforms.ValidationError("L'ora di fine pasto deve essere successiva all'ora di fine distribuzione secondo piatto")

    # Always return the full collection of cleaned data.
    return cleaned_data
    
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
    #if age > 15 :
    #  raise newforms.ValidationError(u"Non e' ammesso inserire schede di Non Conformita' effettuate in date antecedenti di 15 giorni o oltre")

    if age < 0 :
      raise newforms.ValidationError(u"Non e' ammesso inserire schede di Non Conformita' effettuate in date successive alla data odierna")

    # Always return the full collection of cleaned data.
    return cleaned_data
  class Meta:
    model = Nonconformita
    exclude = ['creato_il','creato_da','modificato_il','modificato_da','commissario']

class CommissioneForm(djangoforms.ModelForm):
  class Meta:
    model = Commissione

    