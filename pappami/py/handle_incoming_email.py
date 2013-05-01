#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

from email.utils import parseaddr
from email.header import decode_header
from datetime import date, datetime, time, timedelta

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from google.appengine.api.app_identity import *

from py.blob import *
from py.model import *

from py.post import PostHandler

class MailHandler(InboundMailHandler):

  @property
  def host(self):
    if "test" in get_application_id():
      host = "test.pappa-mi.it"
    else:
      host = "www.pappa-mi.it"
    return host

  def receive(self, message):
    logging.info("Received a message from: " + parseaddr(message.sender)[1])
    logging.info("subject: " + message.subject)
    text_bodies = message.bodies('text/plain')

    #for body in text_bodies:
    #  logging.info("body: " + body[1].decode())
    commissario = Commissario.get_by_email_lower(parseaddr(message.sender)[1].lower())
    if commissario:
      feedback = list()
      logging.info("found commissario")
      nota = Nota()
      nota.creato_da = commissario.usera
      nota.titolo = message.subject

      commissione = None
      cms = commissario.commissioni()
      if len(cms) == 0:
        feedback.append( """Non è stato possibile ricavare la Commissione a cui la segnalazione si riferisce perché non sei registrato su nessuna scuola.

Per favore modifica il tuo profilo in Pappa-Mi specificando almeno una Scuola.

Se specifichi piu' di una Scuola, ricorda di specificare nell'oggetto della mail il nome della commissione e il livello della scuola, ad esempio 'materna muzio'.\r\n""")

      if len(cms) > 1:
        subupper = nota.titolo.upper()
        for cm in cms:
          #logging.info(cm.nome.upper() + " " + cm.tipoScuola.upper() + " subject: " + subupper)
          if cm.nome.upper() in subupper and cm.tipoScuola.upper() in subupper:
            commissione = cm
      else:
        commissione = cms[0]

      if commissione is None:
        feedback.append("""Non è stato possibile ricavare la Commissione a cui la segnalazione si riferisce.

Per favore specifica nell'oggetto della mail il nome della commissione e il livello della scuola, ad esempio 'materna muzio'.\r\n""")
      else:
        nota.commissario = commissario.key
        nota.commissione = commissione.key
        self.parseMessage( nota, message, feedback)


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
          offset = i - nota.dataNota.isoweekday()
          if nota.dataNota.isoweekday() <= i:
            offset -= 7 
          nota.dataNota = nota.dataNota + timedelta(offset)
          break;

    logging.info(nota.dataNota)
    for body in message.bodies('text/plain'):
      nota.note = body[1].decode()

    nota.put()

    #allegati
    if hasattr(message, 'attachments'):
      for attach in message.attachments :
        allegato = Allegato()
        allegato.obj = nota.key
        allegato.nome = self.decode(attach[0])
        logging.info("allegato: " + allegato.nome)
        allegato_decode = attach[1].decode()
        if len(allegato_decode) > 5000000:
          logging.info("attachment too big")
          feedback.append("Non è stato possibile salvare l'allegato " + allegato.nome + " perche' troppo grande, il limite per gli allegati e' 5MB\r\n")
        elif len(allegato_decode) < 5000:
          logging.info("attachment too small")
        else:
          logging.info('uploading attachment')
          blob = Blob()
          blob.create(allegato.nome)
          allegato.blob_key = blob.write(allegato_decode)

    node = SocialNode.get_nodes_by_resource(nota.commissione)[0]
    template_values = PostHandler.create_post(node=node.key, user=nota.creato_da.get(), title=nota.titolo, content=nota.note, resources=[nota.key], attachments=nota.allegati)
    post = template_values["postlist"][0]
    
    feedback.append( """Il tuo messaggio e' stato pubblicato correttamente ed e' visibile al seguente link:

Link pubblico:
""" + "http://" + self.host + "/post/" + post.id + """

---
Pappa-Mi staff """)


    if len(feedback) > 0:
      self.sendFeedbackMail(parseaddr(message.sender)[1], post, feedback)

  def sendFeedbackMail(self, dest, post, feedback) :

    sender = "Pappa-Mi <aiuto@pappa-mi.it>"

    feedback.append("""

    --
    Pappa-Mi staff""")
    message = mail.EmailMessage()
    message.sender = sender
    message.to = dest
    message.subject = post.title
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

app = webapp.WSGIApplication([
    MailHandler.mapping()
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'))

def main():
  app.run();

if __name__ == "__main__":
  main()
