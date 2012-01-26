#!/usr/bin/env python

import wsgiref.handlers
import os
import facebook
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class BaseHandler(webapp.RequestHandler):
  def get(self):
    self.API_KEY = '63acc8b9bce03aaa3fbfaa14fe4d4e8a'# YOUR API KEY
    self.SECRET_KEY = 'e57edc34abb15fece9abcc7b00d39735'# YOUR SECRET KEY
    self.facebookapi = facebook.Facebook(self.API_KEY, self.SECRET_KEY)

    if not self.facebookapi.check_connect_session(self.request):
      self.tpl('login.html')
      return

    try:
      self.user = self.facebookapi.users.getInfo(
        [self.facebookapi.uid],
        ['uid', 'name'])[0]
    except facebook.FacebookError:
      self.tpl('login.html')
      return

    self.get_secure()

  def tpl(self, tpl_file, vars = {}):
      vars['apikey'] = self.API_KEY
      path = os.path.join(os.path.dirname(__file__), 'templates/py/' + tpl_file)
      self.response.out.write(template.render(path, vars))

class MainHandler(BaseHandler):
  def get_secure(self):
    template_values = {
      'name': self.user['name'],
      'uid': self.user['uid']
    }

    self.tpl('index.html', template_values)

def main():
  application = webapp.WSGIApplication([('/fb', MainHandler)], debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

