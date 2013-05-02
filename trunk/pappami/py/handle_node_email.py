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
#from py.sendmail import SendMail

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
    logging.info("Received a message from: " + parseaddr(message.sender)[1] + " to: " + parseaddr(message.to)[1])
    logging.info("subject: " + message.subject)
    text_bodies = message.bodies('text/plain')
    html_bodies = message.bodies('text/html')
    
    feedback = list()    
    content = ""
    for body in html_bodies:
      content = Sanitizer.sanitize(body[1].decode())
    if content == "":
      for body in text_bodies:
        content = Sanitizer.text("<p>"+body[1].decode()+"</p>")
      
    to = parseaddr(message.to)[1]

    node_id = None
    if "node" in to:
      node_id = to[5:to.find('@')]
      logging.info(node_id)
    
    node = model.Key("SocialNode", int(node_id)).get()

    user = None
    commissario = Commissario.get_by_email_lower(parseaddr(message.sender)[1].lower())
    if commissario:
      user = commissario.usera
      
    #allegati
    attachments = list()
    if hasattr(message, 'attachments'):
      for attach in message.attachments :
        allegato = Allegato()
        #allegato.obj = nota.key
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
      attachments.append(allegato)
    
    template_values = PostHandler.create_post(node=node.key, user=commissario.usera.get(), title=message.subject, content=content, resources=[], attachments=attachments)
    post = template_values["postlist"][0]
    
    feedback.append( """Il tuo messaggio e' stato pubblicato correttamente ed e' visibile al seguente link:

Link pubblico:
""" + "http://" + self.host + "/post/" + post.id + """

""")


    if len(feedback) > 0:
      sender = "'Pappa-Mi - " + node.name + " <node-" + str(node.key.id()) + "@pappa-mi.it>"
      self.sendFeedbackMail( sender, parseaddr(message.sender)[1], post, feedback)
      #SendMail().send_mail(sender=message.sender, to=parseaddr(message.sender)[1], subject=post.title, text_body=feedback)

  def sendFeedbackMail(self, sender, dest, post, feedback) :

    feedback.append("""

    --
    Pappa-Mi staff""")
    message = mail.EmailMessage()
    message.sender = sender
    message.to = dest
    message.subject = "[Pappa-Mi] - " + post.title
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

