from google.appengine.ext.db import djangoforms
from django import newforms

from py.model import *

class IspezioneForm(djangoforms.ModelForm):
  def clean(self):
    djangoforms.ModelForm.clean(self)
    cleaned_data = self._cleaned_data()
    pastiTotale = int(cleaned_data.get("numeroPastiTotale"))
    pastiBambini = int(cleaned_data.get("numeroPastiBambini"))
    pastiSpeciali = int(cleaned_data.get("numeroPastiBambini"))
    
    if pastiTotale < pastiBambini or pastiBambini < pastiSpeciali:
      # Only do something if both fields are valid so far.
      raise newforms.ValidationError("Il numero di pasti serviti ai bamnini deve essere minore del numero totale pasti serviti")
    
    if pastiBambini < pastiSpeciali:
      # Only do something if both fields are valid so far.
      raise newforms.ValidationError("Il numero di pasti speciali serviti deve essere minore del numero pasti serviti ai bambini")
    
    # Always return the full collection of cleaned data.
    return cleaned_data
    
  class Meta:
    model = Ispezione
    exclude = ['creato_il','creato_da','modificato_il','modificato_da','commissario']
    
  
class CommissioneForm(djangoforms.ModelForm):
  class Meta:
    model = Commissione

    