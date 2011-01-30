#!/usr/bin/env python
import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

class MailHandler(InboundMailHandler):
  def receive(self, message):
    logging.info("Received a message from: " + message.sender)
    logging.info("subject: " + message.subject)
    text_bodies = message.bodies('text/plain')
    for body in text_bodies:
      logging.info("body: " + body[1].decode())

def main():
  debug = os.environ['HTTP_HOST'].startswith('localhost')   

  application = webapp.WSGIApplication([
    MailHandler.mapping()
  ], debug=debug)

  run_wsgi_app(application)

if __name__ == "__main__":
  main()
