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
from form import *
from base import BasePage, CMCommissioniDataHandler, user_required, config, handle_404, handle_500
class PermissionHandler(BasePage):
    pass

class NodeHandler(BasePage):
  
  def post(self):
        self.response.out.write("");
  
  def get(self,node_id):
    node=model.Key("SocialNode",int(node_id))
    node_i=node.get()
    
    #if node does not exist
    if not node_i or node_i.active==False :
       
        self.response.clear() 
        self.response.set_status(404)
        template = jinja_environment.get_template('404_custom.html')
        c={"error": "Il nodo a cui stai provando ad accedere non esiste"}
        t = template.render(c)
        self.response.out.write(t)
        return
    
    latest_posts=node.get().get_latest_posts()

    for x in latest_posts: 
    
        x.commissario=Commissario.get_by_user(x.author.get())
        
        
    current_user=self.get_current_user()
    if current_user is None:
        logged=False
        is_sub=False
    else:
        logged=True
        is_sub= node.get().is_user_subscribed(current_user)
     
    #check permission
    can_post=False
    current_user=self.get_current_user()
    if current_user:
        current_user=current_user.key
        current_sub=memcache.get("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()))
        if current_sub is None:
              current_sub=SocialNodeSubscription.query(ancestor=node).filter(SocialNodeSubscription.user==current_user).get()
              memcache.add("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()),current_sub)
              
                
    if node_i.is_public:
        template_values = {
          'content': 'social/node.html',
          "user":current_user,
          "node":node_i,
          "is_sub":is_sub,
          "show_sub_button": True if not logged or not is_sub else False,
          "subscriptions": [Commissario.get_by_user(x) for x in node.get().subscription_list()],
          "citta": Citta.get_all(),
          "latest_posts":latest_posts,
          "subscription":current_sub
          }
    else:
        pass
      
    self.getBase(template_values)
    

       
    
    
class SocialTest(BasePage):
    def get(self):
    
    
     user=self.get_current_user()
     nodo=model.Key("SocialNode", 1310096,"SocialPost",1310100).get().create_reply_post("isngdsogno soirngsodi sirojnodsn", user)
     template_values = {
      'content': 'social/test.html',
      'var':nodo,
      'citta': Citta.get_all()}  
     
     
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
    
    
       
class SocialPostHandler(BasePage):
    def get(self,id):
        op=model.Key(urlsafe=id).get()
        node=op.key.parent()
        op.commissario=Commissario.get_by_user(op.author.get())
        
        if op is None:
            self.response.clear() 
            self.response.set_status(404)
            template = jinja_environment.get_template('404_custom.html')
            c={"error": "Il post a cui stai provando ad accedere non esiste"}
            t = template.render(c)
            self.response.out.write(t)
            return
        
        replies=[]
        for x in op.get_discussion():
            
            x.commissario=Commissario.get_by_user(x.author.get())
            replies.append(x)
        
        
       
        current_user=self.get_current_user()
        if current_user:
            current_user=current_user.key
            current_sub=memcache.get("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()))
            if current_sub is None:
                current_sub=SocialNodeSubscription.query(ancestor=node).filter(SocialNodeSubscription.user==current_user).get()
                memcache.add("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()),current_sub)
           
        template_values = {
                           'content': 'social/post.html',
                           'replies': replies,
                           'post': op,
                           'node':node.get(),
                           'subscription':current_sub
                                              }                    
        
    
        self.getBase(template_values)

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
                 self.response.headers["Content-Type"] = "text/xml"
                 self.response.out.write("<response>success</response>")
        
          if cmd == "unsubscribe":
                 user = model.Key("User", int(self.request.get('user'))).get()
                 node = model.Key("SocialNode", int(self.request.get('node'))).get()
             
                 node.unsubscribe_user(user)
                 self.response.headers["Content-Type"] = "text/xml"
                 self.response.out.write("<response>success</response>")
             
class SocialCreatePost(webapp.RequestHandler):
    def post(self):
       
       
       
       node=model.Key("SocialNode",int(self.request.get('node')))
       cmd = self.request.get('cmd')

       if cmd == "create_open_post":
           user=model.Key("User",int(self.request.get('user'))).get()
           node.get().create_open_post(self.request.get("content"),self.request.get("title"),user)
           self.response.headers["Content-Type"] = "text/xml"
           self.response.out.write("<response>success</response>")
           
           
       if cmd == "create_reply_post":
           user=model.Key("User",int(self.request.get('user'))).get()
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           if post is None:
              post=model.Key("SocialNode",int(self.request.get('node')), "SocialPost", int(self.request.get('post'))).get()
              memcache.add("SocialPost-"+str(self.request.get('post')),post)
           
           post.create_reply_comment(self.request.get("content"),self.request.get("title"),user)  
           self.response.headers["Content-Type"] = "text/xml"
           self.response.out.write("<response>success</response>")
           
           
       if cmd == "delete_reply_post":
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           if post is None:
               post=model.Key("SocialNode",int(self.request.get('node')), "SocialPost", int(self.request.get('post'))).get()
               memcache.add("SocialPost-"+str(self.request.get('post')),post)
           post.delete_reply_comment(int(self.request.get('reply')))
           self.response.headers["Content-Type"] = "text/xml"
           self.response.out.write("<response>success</response>")

       if cmd == "delete_open_post":
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           if post is None:
               post=model.Key("SocialNode",int(self.request.get('node')), "SocialPost", int(self.request.get('post'))).get()
           
           post.key.delete()
           memcache.delete("SocialPost-"+str(self.request.get('post')))
           self.response.headers["Content-Type"] = "text/xml"
           self.response.out.write("<response>success</response>")
               
           


app = webapp.WSGIApplication([
    ('/social/node/(\d+)', NodeHandler),
    ('/social/nodelist/', NodeListHandler),
    ('/social/post/(.*)', SocialPostHandler),
    ('/social/managepost',SocialCreatePost),
    ('/social/test', SocialTest),
    ('/social/socialmap',SocialMapHandler),
    ('/social/subscribe', SocialSubscribeHandler)
    ],
                             
    debug = True, config=config)




def main():
  app.run();

if __name__ == "__main__":
  main()
