from py.base import *

import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers

from google.appengine.ext.ndb import model
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail

from gviz_api import *
from model import *
from form import CommissarioForm
from base import BasePage, CMCommissioniDataHandler, user_required, config, handle_404, handle_500


class PermissionHandler(BasePage):
    pass

class NodeHandler(BasePage):
  @user_required
  def get(self,node_id):
    
    node=model.Key("SocialNode",int(node_id))
    template_values = {
      'content': 'social/node.html',
      "node":node.get(),
      "is_subscribed": node.is_user_subscribed(users.get_current_user()), 
      'citta': Citta.get_all()}
    self.getBase(template_values)
    
    
class SocialTest(BasePage):
    def get(self):
     template_values = {
      'content': 'social/test.html',
      'citta': Citta.get_all()}
     

     self.getBase(template_values)
    
        
class NodeListHandler(BasePage):
  def get(self):
    template_values = {
      'content': 'social/nodelist.html',
      'nodelist': SocialNode.query(),
      'citta': Citta.get_all()}
     

    self.getBase(template_values)
    
    
       
class PostHandler(BasePage):
    pass

    
    
app = webapp.WSGIApplication([
    ('/social/node/(\d+)', NodeHandler),
    ('/social/nodelist/', NodeListHandler),
    ('/social/post', PostHandler),
    ('/social/test',SocialTest)
    ],
                             
    debug = True, config=config)


def main():
  app.run();

if __name__ == "__main__":
  main()