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
from datetime import date, datetime, time, timedelta
from gviz_api import *
from py.model import *
from form import CommissarioForm
from base import BasePage, CMCommissioniDataHandler, user_required, config, handle_404, handle_500
class PermissionHandler(BasePage):
    pass

class NodeHandler(BasePage):
  
  def get(self,node_id):
    
    node=model.Key("SocialNode",int(node_id))
    node_i=node.get()
    node_i.set_position(45.1,12.2)
    
    #if node does not exist
    if not node_i or node_i.active==False :
       
        self.response.clear() 
        self.response.set_status(404)
        template = jinja_environment.get_template('404_custom.html')
        c={"error": "Il nodo a cui stai provando ad accedere non esiste"}
        t = template.render(c)
        self.response.out.write(t)
        return
    
    latest_post=node.get().get_latest_posts()
    logging.info(latest_post)
    for x in latest_post: 
    
        x.commissario=Commissario.get_by_user(x.author.get())
        
        
    current_user=self.get_current_user()
    is_sub= node.get().is_user_subscribed(current_user)
    template_values = {
      'content': 'social/node.html',
      "user":current_user,
      "node":node_i,
      "is_sub":is_sub,
      "show_sub_button": True if self.get_current_user() is None or not is_sub else False,
      "subscriptions": [Commissario.query( Commissario.usera==x.key).fetch() for x in node.get().subscription_list()],
      "citta": Citta.get_all(),
      "latest_posts":latest_post}
      
    self.getBase(template_values)
    
    
class SocialTest(BasePage):
    def get(self):
    
     template_values = {
      'content': 'social/test.html',
     
      'citta': Citta.get_all()}  
     
     nodo= model.Key("SocialNode",1310060)
     nodo=nodo.get()
     nodo.create_open_post("agfsngoisn",self.get_current_user())
     
     self.getBase(template_values)
    
        
class NodeListHandler(BasePage):
  def get(self):
    geo = model.GeoPt(41.754922,12.502441)
    template_values = {
      'content': 'social/nodelist.html',
      'nodelist': SocialNode.active_nodes(),
      'citta': Citta.get_all(),
       'geo':geo}
        
    
    self.getBase(template_values)
    
    
       
class PostHandler(BasePage):
    pass

class SocialMapHandler(webapp.RequestHandler):
      
  def get(self): 
    cursor = self.request.get("cur")

    offset = 0
    if self.request.get("offset"):
      offset = int(self.request.get("offset"))    

    if self.request.get("cmd") == "all":
      markers = memcache.get("markers_social_all"+str(offset))
      if(markers == None):
          
        nodes = SocialNode.get_all_cursor(cursor)
          
        limit = Const.ENTITY_FETCH_LIMIT
        i = 0
        markers_list = list()
        try:
          for c in nodes :
            i += 1
            if i >= limit:
              break
            if c.geo:
              mark = '<marker key="' + str(c.key.id()) + '" name="' + c.name + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon)
              mark += '" />\n'              
              markers_list.append(mark)
        except:
          logging.error("Timeout")
        if i >= limit:
          markers = "<markers cur='" + nodes.cursor_after().to_websafe_string() + "'>\n"
        else:
          markers = "<markers>\n"
          
        markers = markers + "".join(markers_list) + "</markers>"
        
        memcache.add("markers_all"+str(offset), markers)
      
      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)      
    else:
      markers = memcache.get("markers_social"+str(offset))
      if(markers == None):
          
        nodes = SocialNode.get_active_cursor(cursor)

        limit = Const.ENTITY_FETCH_LIMIT
        i = 0
        markers_list = list()
        try:
          for c in commissioni :
            i += 1
            if i >= limit:
              break
            if c.geo :
                mark = '<marker key="' + str(c.key.id()) + '" name="' + c.name + '"' + ' lat="' + str(c.geo.lat) + '" lon="' + str(c.geo.lon)
                mark += '" />\n'              
                markers_list.append(mark)
        except:
          raise
          logging.error("Timeout")
          
        #logging.info(markers_list)
        if i >= limit:
          markers = "<markers cur='" + nodes.cursor_after().to_websafe_string() + "'>\n"
        else:
          markers = "<markers>\n"
          
        markers = markers + "".join(markers_list) + "</markers>"
        memcache.add("markers_social"+str(offset), markers)
      
      #logging.info(markers)
      self.response.headers["Content-Type"] = "text/xml"
      self.response.out.write(markers)
     
class SocialSubscribeHandler(webapp.RequestHandler):
       def get(self):
           
          cmd = self.request.get('cmd')
          if cmd == "subscribe":
                 user = model.Key("User", int(self.request.get('user'))).get()
                 node = model.Key("SocialNode", int(self.request.get('node'))).get()
                 node.subscribe_user(user)
                 
                 self.response.out.write("Success")
        
          if cmd == "unsubscribe":
                 user = model.Key("User", int(self.request.get('user'))).get()
                 node = model.Key("SocialNode", int(self.request.get('node'))).get()
                 logging.info(node)
                 logging.info(user)
                 node.unsubscribe_user(user)
                 self.response.out.write("Success")
             
                
app = webapp.WSGIApplication([
    ('/social/node/(\d+)', NodeHandler),
    ('/social/nodelist/', NodeListHandler),
    ('/social/post', PostHandler),
    ('/social/test',SocialTest),
    ('/social/socialmap',SocialMapHandler),
    ('/social/subscribe', SocialSubscribeHandler)
    ],
                             
    debug = True, config=config)


def main():
  app.run();

if __name__ == "__main__":
  main()
