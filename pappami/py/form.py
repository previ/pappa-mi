from google.appengine.ext.db import djangoforms
from django import newforms
import logging

from py.model import *

class IspezioneForm(djangoforms.ModelForm):
  def clean(self):
    super(IspezioneForm,self).clean()
    cleaned_data = self._cleaned_data()
    for f in cleaned_data:
      logging.info("data: %s, %s", f, cleaned_data.get(f))
    pastiTotale = int(cleaned_data.get("numeroPastiTotale"))
    pastiBambini = int(cleaned_data.get("numeroPastiBambini"))
    pastiSpeciali = int(cleaned_data.get("numeroPastiBambini"))
    
    if pastiTotale < pastiBambini or pastiBambini < pastiSpeciali:
      raise newforms.ValidationError("Il numero di pasti serviti ai bambini deve essere minore del numero totale pasti serviti")
    
    if pastiBambini < pastiSpeciali:
      raise newforms.ValidationError("Il numero di pasti speciali serviti deve essere minore del numero pasti serviti ai bambini")

    if Ispezione.all().filter("dataIspezione",cleaned_data.get("dataIspezione")).filter("commissione",cleaned_data.get("commissione")).count() > 0 :
      raise newforms.ValidationError("Esiste gia una scheda di ispezione per quesa data e questa commissione.")

    if cleaned_data.get("dataIspezione").isoweekday() > 5 :
      raise newforms.ValidationError("L'ispezione deve essere fatta in un giorno feriale")
    
    # Always return the full collection of cleaned data.
    return cleaned_data
    
  class Meta:
    model = Ispezione
    exclude = ['creato_il','creato_da','modificato_il','modificato_da','commissario']
    
  
class CommissioneForm(djangoforms.ModelForm):
  class Meta:
    model = Commissione

    