#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

from py.model import *
from py.site import *

from email.utils import parseaddr
from email.header import decode_header
from datetime import date, datetime, time, timedelta
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail

class MailHandler(InboundMailHandler):
  site = None
  host = "test.pappa-mi.it"
  path = None

  def __init__(self):
    super(InboundMailHandler, self).__init__()
    username = Configurazione.all().filter("nome", "attach_user").get().valore
    password = Configurazione.all().filter("nome", "attach_password").get().valore
    site = Configurazione.all().filter("nome", "attach_site").get().valore
    self.path = Configurazione.all().filter("nome", "attach_path").get().valore
    self.site = Site(username, password, site)    

  def receive(self, message):
    logging.info("Received a message from: " + parseaddr(message.sender)[1])
    logging.info("subject: " + self.decode(message.subject))
    text_bodies = message.bodies('text/plain')
    #for body in text_bodies:
    #  logging.info("body: " + body[1].decode())
    commissario = Commissario.all().filter("user",users.User(parseaddr(message.sender)[1])).get()    
    if commissario:
      feedback = list()
      logging.info("found commissario")
      nota = Nota()
      nota.titolo = self.decode(message.subject)
      
      commissione = None
      cms = commissario.commissioni()
      logging.info("commissioni: " + str(len(cms)))
      if len(cms) == 0:
        feedback.append( """Non è stato possibile ricavare la Commissione a cui la segnalazione si riferisce perché non sei registrato su nessuna scuola.
        
Per favore modifica il tuo profilo in Pappa-Mi specificando almeno una Scuola.
        
Se specifichi piu' di una Scuola, ricorda di specificare nell'oggetto della mail il nome della commissione e il livello della scuola, ad esempio 'materna muzio'.\r\n""")
        
      if len(cms) > 1:
        subupper = nota.titolo.upper()
        for cm in cms:
          if cm.nome.upper() in subupper and cm.tipoScuola.upper() in subupper:
            commissione = cm
      else:
        commissione = cms[0]

      if commissione is None:
        feedback.append("""Non è stato possibile ricavare la Commissione a cui la segnalazione si riferisce.

Per favore specifica nell'oggetto della mail il nome della commissione e il livello della scuola, ad esempio 'materna muzio'.\r\n""")
      else:
        nota.commissario = commissario
        nota.commissione = commissione
        self.parseMessage( nota, message, feedback)
          
          
      if len(feedback) > 0:
        self.sendFeedbackMail(parseaddr(message.sender)[1], nota, feedback)

  def parseMessage(self, nota, message, feedback):
    
    tags = list()
    nota.dataNota = datetime.now().date()
    if nota.titolo.lower().find("ieri") >= 0:
      nota.dataNota = nota.dataNota + timedelta(-1)
      if nota.dataNota.isoweekday() == 0 :
        nota.dataNota = nota.dataNota + timedelta(-2)
      if nota.dataNota.isoweekday() == 6 :
        nota.dataNota = nota.dataNota + timedelta(-1)
    else:
      i = 0
      for giorno in ["luned","marted","mercoled","gioved","venerd"]:
        i = i + 1
        if nota.titolo.lower().find(giorno) >= 0:
          nota.dataNota = nota.dataNota - timedelta(nota.dataNota.isoweekday()-i)
          break;
        
    for body in message.bodies('text/plain'):
      nota.note = body[1].decode()

    nota.put()
      
    # tags
    s = nota.note.find("#")
    while s >= 0:
      e = nota.note.find(" ",s+1)
      if e < 0:
        e = len(nota.note)
      tag = Tag()
      tag.tag = nota.note[s+1:e]
      tag.obj = nota
      tag.put()
      s = nota.note.find("#",e)

    logging.info('uploading')        
         
    #allegati
    if hasattr(message, 'attachments'):
      for attach in message.attachments :
        allegato = Allegato()
        allegato.obj = nota
        allegato.nome = self.decode(attach[0])
        logging.info("allegato: " + allegato.nome)
        allegato_decode = attach[1].decode()
        if len(allegato_decode) > 1000000:
          logging.info("attachment too big")
          feedback.append("Non è stato possibile salvare l'allegato " + allegato.nome + " perche' troppo grande, il limite per gli allegati e' 1MB\r\n")
        elif len(allegato_decode) < 5000: 
          logging.info("attachment too small")
        else:
          allegato.path = self.site.uploadDoc(allegato_decode, str(nota.key().id()) + "_" + allegato.nome, allegato.contentType(), self.path)
          allegato.put()
         
    linkpath="genitore"
    if nota.commissario.isCommissario():
      linkpath="commissario"
    
    feedback.append( """Il tuo messaggio e' stato pubblicato correttamente ed e' visibile ai seguenti link:
      
Link per utenti registrati:
""" + "http://" + self.host + "/"+linkpath+"/nota?cmd=open&key="+str(nota.key()) + """
    
Link pubblico:
""" + "http://" + self.host + "/public/nota?cmd=open&key="+str(nota.key()) + """
    
---
Pappa-Mi staff """)
                  
  def sendFeedbackMail(self, dest, nota, feedback) :
  
    sender = "Pappa-Mi <aiuto@pappa-mi.it>"

    feedback.append("""
    
    --
    Pappa-Mi staff""")
    message = mail.EmailMessage()
    message.sender = sender
    message.to = dest
    message.subject = nota.titolo
    body = ""
    for f in feedback:
      body = body + f
    message.body = body

    logging.info("sending mail to: " + message.to)
    message.send()
            
  def decode(self, text):
    if len(decode_header(text)) > 0 and len(decode_header(text)[0]) > 1 and decode_header(text)[0][0] is not None and decode_header(text)[0][1] is not None:
      decoded_text = decode_header(text)[0]
      decoded_text = decoded_text[0].decode(decoded_text[1])
    else:
      decoded_text = text.decode('utf-8')
    return decoded_text
  
def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
    MailHandler.mapping()
  ], debug=debug)

  run_wsgi_app(application)

if __name__ == "__main__":
  main()
