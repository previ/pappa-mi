#!/usr/bin/env python
import os
import logging

from py.model import *
from email.utils import parseaddr
from email.header import decode_header
from datetime import date, datetime, time, timedelta
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

class MailHandler(InboundMailHandler):
  def receive(self, message):
    logging.info("Received a message from: " + parseaddr(message.sender)[1])
    logging.info("subject: " + message.subject)
    text_bodies = message.bodies('text/plain')
    #for body in text_bodies:
    #  logging.info("body: " + body[1].decode())
    commissario = Commissario.all().filter("user",users.User(parseaddr(message.sender)[1])).get()    
    if commissario:
      logging.info("found commissario")
      decoded_subject = message.subject.decode()
      if len(decode_header(message.subject)) > 0 and len(decode_header(message.subject)[0]) > 1:
        decoded_subject = decode_header(message.subject)[0]
        decoded_subject = decoded_subject[0].decode(decoded_subject[1])
      
      commissione = None
      cms = commissario.commissioni()
      logging.info("commissioni: " + str(len(cms)))
      if len(cms) > 1:
        subupper = decoded_subject.upper()
        for cm in cms:
          if cm.nome.upper() in subupper and cm.tipoScuola.upper() in subupper:
            commissione = cm
      else:
        commissione = cms[0]
      if commissione:
        nota = Nota()
        nota.titolo = decoded_subject
        nota.commissario = commissario
        nota.commissione = commissione
        nota.dataNota = datetime.now().date()
        if nota.titolo.lower().find("ieri") >= 0:
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
        
        #allegati
        for attach in message.attachments:
          logging.info("allegato: " + attach[0])
          allegato = Allegato()
          allegato.obj = nota          
          allegato.titolo = attach[0]
          if len(attach[1].decode()) > 1000000:
            logging.info("attachment too big")
          else:
            allegato.dati = db.Blob(attach[1].decode())
            allegato.put()

def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
    MailHandler.mapping()
  ], debug=debug)

  run_wsgi_app(application)

if __name__ == "__main__":
  main()
