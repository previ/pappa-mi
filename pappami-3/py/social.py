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
from py.model import *
from form import CommissarioForm
from base import BasePage, CMCommissioniDataHandler, user_required, config, handle_404, handle_500
class PermissionHandler(BasePage):
    pass

class NodeHandler(BasePage):
  
  def get(self,node_id):
    
    node=model.Key("SocialNode",int(node_id))
    current_user=self.get_current_user()
    template_values = {
      'content': 'social/node.html',
      "node":node.get(),
      "is_sub":False if self.get_current_user() is None else node.get().is_user_subscribed(current_user),
      "subscriptions": [Commissario.query( Commissario.usera==x.key).fetch() for x in node.get().subscription_list()],
      "citta": Citta.get_all(),
      "latest_posts":node.get().get_latest_posts()}
 
    disc=model.Key("SocialNode", 1310019,"SocialPost",1310040).get().get_discussion()
    self.getBase(template_values)
    
    
class SocialTest(BasePage):
    def get(self):
    
     template_values = {
      'content': 'social/test.html',
      
      'citta': Citta.get_all()}  
     
     nodo= SocialNode()
     nodo.name="aegfisong"
     nodo.put()
     nodo.create_open_post("agfsngoisn",self.get_current_user())
     
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