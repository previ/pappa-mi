#!/usr/bin/env python

import wsgiref.handlers
import os
import logging

import webapp2 as webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from ndb import model

from py.facebook import *
from py.base import BasePage
from py.model import Commissario

class MainHandler(webapp.RequestHandler):
  def get(self):
    user = get_user_from_cookie(self.request.cookies, '63acc8b9bce03aaa3fbfaa14fe4d4e8a', 'e57edc34abb15fece9abcc7b00d39735')
    template_values = dict()
    template_values["apikey"] = '63acc8b9bce03aaa3fbfaa14fe4d4e8a'
    logging.info(user)
    if user:
      graph = facebook.GraphAPI(user["access_token"])
      profile = graph.get_object("me")
      friends = graph.get_connections("me", "friends")
      picture = graph.get_connections("me", "picture")
      logging.info(profile)
      logging.info(picture)
      template_values["profile"] = profile
      template_values["picture"] = picture
    path = os.path.join(os.path.dirname(__file__), '../templates/fb/index.html')
    self.response.out.write(template.render(path, template_values))
        
  
class LoginHandler(webapp.RequestHandler):
  def get(self):    
    template_values = {
    }
    path = os.path.join(os.path.dirname(__file__), '../templates/fb/login2.html')
    self.response.out.write(template.render(path, template_values))

class SaveUserInfoHandler(BasePage):
  def post(self):
    commissario = self.getCommissario(users.get_current_user())
    commissario.avatar_url = self.request.get("picture")
    commissario.put()
    
    
app = webapp.WSGIApplication([
    ('/fb', MainHandler),
    ('/fb/login', LoginHandler),
    ('/fb/save', SaveUserInfoHandler)
    ], debug=os.environ['HTTP_HOST'].startswith('localhost'))

def main():
  app.run();

if __name__ == "__main__":
  main()