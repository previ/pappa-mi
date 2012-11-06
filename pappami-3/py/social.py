from py.base import *
from google.appengine.api import users
import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import feedparser
from google.appengine.ext.ndb import model
import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from datetime import date, datetime, time, timedelta
from gviz_api import *
from py.model import *
from form import *
import base64
import time
from base import BasePage, CMCommissioniDataHandler, reguser_required, config, handle_404, handle_500
import random
def fix_padding(string):
    lens = len(string)
    lenx = lens - (lens % 4 if lens % 4 else 4)
    try:
        result =string[:lenx]
        return result
    except: 
        pass
    
def get_current_sub(current_user,node):
    if current_user:
        current_user=current_user.key
        current_sub=memcache.get("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()))
        if current_sub is None:
              current_sub=SocialNodeSubscription.query(ancestor=node).filter(SocialNodeSubscription.user==current_user).get()
              memcache.add("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()),current_sub)
       
        return current_sub
    
class NodeHandler(BasePage):
  
  def error(self):
        self.response.clear() 
        self.response.set_status(404)
        template = jinja_environment.get_template('404_custom.html')
        c={"error": "Il nodo a cui stai provando ad accedere non esiste"}
        t = template.render(c)
        self.response.out.write(t)
        return
    
  
  def post(self):
        self.response.out.write("");
        
  def get(self,node_id):
    
   try:
    node_i=model.Key(urlsafe=node_id).get()
    node=node_i.key
       #if node does not exist
    if not node_i or node_i.active==False :
       
        self.error()
    
   
        
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
    current_sub=get_current_sub(current_user,node)
                
    template_values = {
          'content': 'social/node.html',
          "user":current_user,
          "node":node_i,
          "is_sub":is_sub,
          "show_sub_button": True if not logged or not is_sub else False,
          "subscriptions": [Commissario.get_by_user(x) for x in node.get().subscription_list(10)],
          "citta": Citta.get_all(),
          "subscription":current_sub
          }
    
      
    self.getBase(template_values)
   except:
       self.error()

       
    
    
class SocialTest(BasePage):
  def get(self):
      
      SocialUtils.generate_nodes()
    # for i in SocialComment.query().fetch(keys_only=True):
     #   i.delete()
    #  SocialUtils.generate_random_contents(self.get_current_user())
        
          
class NodeListHandler(BasePage):
  def get(self):
    geo = model.GeoPt(41.754922,12.502441)
    template_values = {
      'content': 'social/nodelist.html',
      #'nodelist': SocialNode.active_nodes(),
      #'citta': Citta.get_all(),
      'geo':geo}
        
    self.getBase(template_values)
    
    
       
class SocialPostHandler(BasePage):
   
    def error(self):
       self.response.clear() 
       self.response.set_status(404)
       template = jinja_environment.get_template('404_custom.html')
       c={"error": "Il post a cui stai provando ad accedere non esiste"}
       t = template.render(c)
       self.response.out.write(t)
       
    
    def get(self,id):
        op=model.Key(urlsafe=id).get()
        if op is None or not isinstance(op, SocialPost):
           self.error()
        node=op.key.parent()
        op.commissario=Commissario.get_by_user(op.author.get())
        replies=[]
        for x in op.get_discussion():
            
            x.commissario=Commissario.get_by_user(x.author.get())
            replies.append(x)
        
        
        current_user=self.get_current_user()
        current_sub=None
        if current_user is not None:
            current_user=current_user.key
            current_sub=memcache.get("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()))
           
            if current_sub is None:
                current_sub=SocialNodeSubscription.query(ancestor=node).filter(SocialNodeSubscription.user==current_user).get()
                memcache.add("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()),current_sub)
            
            postsub=memcache.get("SocialPostSubscription-"+str(op.key.id())+"-"+str(current_user.id()))
           
            if postsub is None:
                postsub=SocialPostSubscription.query(ancestor=op.key).filter(SocialPostSubscription.user==current_user).get()
                memcache.add("SocialPostSubscription-"+str(op.key.id())+"-"+str(current_user.id()),postsub)
         
            
        template_values = {
                           'content': 'social/post.html',
                           'replies': replies,
                           'post': op,
                           'node':node.get(),
                           'user':current_user,
                        
                           
                                              }                    
        if current_user:
            template_values['subscription']=current_sub
            template_values['postsub']=postsub
            
            
        self.getBase(template_values)

    def create_resource(self, node, user, type, url, title, content=None, res_key=None ):
        resource = SocialResource(parent=node,
                                 title=title,
                                 type=type,
                                 obj=res_key,                                
                                 )
        resource.put()
        post = resource.publish(node,content,title,user)
        
        postlist = list()
        postlist.append(post.get())
        for x in postlist: 
            x.commissario=Commissario.get_by_user(x.author.get())
        
        template_values = {
          "main":"social/pagination/post.html",
          "postlist":postlist,          
          "cmsro":self.getCommissario(user), 
          "subscription": py.social.get_current_sub(user,node),
          "user": user,
          "node":node.get()
         }
        
        return template_values
            
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
     
class SocialSubscribeHandler(SocialAjaxHandler):
       def get(self):
        user = self.get_current_user()
        
        cmd = self.request.get('cmd')
        if cmd == "subscribe":
                 node = model.Key(urlsafe=self.request.get('node')).get()
                 if node:
                     node.subscribe_user(user)
                     self.success()
                 else:
                     self.error()
        
        
        if cmd == "unsubscribe":
                 node = model.Key(urlsafe=self.request.get('node')).get()
                 if node:
                     node.unsubscribe_user(user)
                     self.success()
                 else:
                     self.error()
    
        if cmd == "subscribepost":
                
                 post = model.Key(urlsafe=self.request.get('post')).get()
                 if post:
                      post.subscribe_user(user)
                      self.success()
                 else:
                     self.error()
        
        if cmd == "unsubscribepost":
                 post = model.Key(urlsafe=self.request.get('post')).get()
                 if post:
                     post.unsubscribe_user(user)
                     
                     self.success()
                 else:
                     self.error()
              
class SocialManagePost(SocialAjaxHandler):
   
   def post(self):             
       user=self.request.user
       cmd = self.request.get('cmd')

       # create a new 'original' post
       # parameters: 'node'
       # parameters: 'title'
       # parameters: 'content'
       if cmd == "create_open_post":
           self.response.headers["Content-Type"] = "text/xml"
           node=model.Key(urlsafe=self.request.get('node')).get()
           if not node.get_subscription(user).can_post:
               self.response.out.write("<response>error</response>")
               return
           post=node.create_open_post(feedparser._sanitizeHTML(self.request.get("content"),"UTF-8"),feedparser._sanitizeHTML(self.request.get("title"),"UTF-8"),user)

           postlist = list()
           postlist.append(post.get())
           for x in postlist: 
               x.commissario=Commissario.get_by_user(x.author.get())
           
           template_values = {
               "postlist":postlist,
               "cmsro":self.getCommissario(user), 
               "subscription": get_current_sub(user,node.key),
               "user": user,
               "node":node
            }
           
           template = jinja_environment.get_template("social/pagination/post.html")

           html=template.render(template_values)
           response = {'response':'success','html':html,"cursor":''}
           self.output_as_json(response)
           
           
       # create a reply to a post
       # parameters: 'post'
       # parameters: 'content'
       if cmd == "create_reply_post":
           post=model.Key(urlsafe=self.request.get('post')).get()
           node=post.key.parent().get()
           if post:
               if not node.get_subscription(user).can_reply:
                   self.success()
                   return
           
               
           reply=post.create_reply_comment(feedparser._sanitizeHTML(self.request.get("content"),"UTF-8"),user)  

           reply.commissario=Commissario.get_by_user(reply.author.get())
           
           template_values = {
               "post":post,
               "reply":reply,
               "cmsro":self.getCommissario(user), 
               "subscription": get_current_sub(user,node.key),
               "user": user,
               "node":node
            }
           
           template = jinja_environment.get_template("social/pagination/comment.html")

           html=template.render(template_values)
           response = {'response':'success','html':html,"cursor":''}
           self.output_as_json(response)
           
           
       if cmd == "delete_reply_post":
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           if post is None:
               post=model.Key(urlsafe=self.request.get('post')).get()
               memcache.add("SocialPost-"+str(self.request.get('post')),post)
               
           #node=model.Key(urlsafe=self.request.get('node')).get()
           node=post.key.parent().get()
           
           if not node.get_subscription(user).can_admin:
               self.response.out.write("<response>error</response>")
               return
           post.delete_reply_comment(self.request.get('reply'))
           self.response.headers["Content-Type"] = "text/xml"
           self.success()

       if cmd == "delete_open_post":
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           
           if post is None:
              post=model.Key(urlsafe=self.request.get('post')).get()
              
           #node=node.get()
           node=post.key.parent().get()
           
           #check admin permissions
           if not node.get_subscription(user).can_admin:
               return    
           #delete replies
           node.delete_post(post)
           
           self.success("/social/node/"+node.key.urlsafe())

       if cmd== "reshare_open_post":          
           node=model.Key(urlsafe=self.request.get('node')).get()           
           post=memcache.get("SocialPost-"+str(self.request.get('post')))
           if post is None:
               post=model.Key(urlsafe=self.request.get('post')).get()
               memcache.add("SocialPost-"+str(self.request.get('post')),post)
               
           title=self.request.get('title')
           content=self.request.get('content')
           
           post=post.reshare(node.key,user,feedparser._sanitizeHTML(content,"UTF-8"),feedparser._sanitizeHTML(title,"UTF-8"))
           self.success("/social/post/"+post.urlsafe())
        
       if cmd == "edit_open_post":
          logging.info(self.request.get('content'))
          post=model.Key(urlsafe=self.request.get('post')).get()
          post.content=feedparser._sanitizeHTML(self.request.get("content"),"UTF-8")
          post=post.put()
          
          memcache.add("SocialPost-"+str(self.request.get('post')),post.get())
          
          if post:
              response = {'response':'success','content':post.get().content}
              self.output_as_json(response)             
          
               
       if cmd == "edit_reply_post":
           pass
       if cmd == "content_edit":
           template_values = {
                           'template': 'social/contentedit.html',
                           'post':  self.request.get('post'),
                           'node': node,
                           'user': self.get_current_user(),
                           'content': self.request.get('content'),
                           
                                              }                    
        
           template = jinja_environment.get_template(template_values["template"])
   
           self.response.write(template.render(template_values))        

       
class SocialCreateNodeHandler(BasePage):
    @reguser_required
    def get(self):  
        template_values = {
                        'content': 'social/createnode.html',
                        "citta" : Citta.get_all(),
                        
        }
        self.getBase(template_values)
        
    def post(self):
        
        node=SocialNode()
        node.name=feedparser._sanitizeHTML(self.request.get("name"),"UTF-8")
        node.description=feedparser._sanitizeHTML(self.request.get("description"),"UTF-8")
        node.default_reply=bool(self.request.get("default_reply"))
        node.default_post=bool(self.request.get("default_post"))
        node.default_admin=bool(self.request.get("default_admin"))
        node.founder=self.get_current_user().key
        logging.info(self.request.get("citta"))
        #node.resource=model.Key(urlsafe=self.request.get("citta")).get().create_resource().key
   
        
        node.put()
        
        self.redirect("/social/node/"+str(node.key.urlsafe()))


class SocialEditNodeHandler(BasePage):
        def get(self,id):  
            node=model.Key(urlsafe=id).get()
            if node is None or type(node) is not SocialNode:
                self.response.clear() 
                self.response.set_status(404)
                template = jinja_environment.get_template('404_custom.html')
                c={"error": "Il post a cui stai provando ad accedere non esiste"}
                t = template.render(c)
                self.response.out.write(t)
                return
            
            template_values = {
                            "content": 'social/editnode.html',
                            "node":node,
                            "citta" : Citta.get_all(),
                            
                            }
            
            
            
            self.getBase(template_values)
        def post(self,id):
            node=model.Key(urlsafe=self.request.get("node_id")).get()
            node.name=feedparser._sanitizeHTML(self.request.get("name"),"UTF-8")
            node.description=feedparser._sanitizeHTML(self.request.get("description"),"UTF-8")
            node.default_reply=bool(self.request.get("default_reply"))
            node.default_post=bool(self.request.get("default_post"))
            node.default_admin=bool(self.request.get("default_admin"))
            node.founder=self.get_current_user().key
            node.put()
            
            self.redirect("/social/node/"+str(node.key.id()))

class SocialPaginationHandler(SocialAjaxHandler):
        def post(self):
                cmd=self.request.get("cmd")
                user=self.request.user
                cursor=self.request.get("cursor")
                if cmd=="node":
                    if not cursor or cursor == "undefined":
                        nodelist, next_curs, more = SocialNode.query().order(-SocialNode.latest_post_date).fetch_page(10) 
                    else:
                         nodelist, next_curs, more = SocialNode.query().order(-SocialNode.latest_post_date).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))
                    template_values = {
                            "nodelist":nodelist,
                             }
                    if not nodelist or not next_curs:
                        
                        response = {'response':'no_nodes'}
                        self.output_as_json(response)
                        return
                        
                    template = jinja_environment.get_template("social/pagination/node.html")
                    
                    html=template.render(template_values)
                    response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                    self.output_as_json(response)
                 
                if cmd=="post":
                        node=model.Key(urlsafe=self.request.get("node"))
                        if not cursor or cursor == "undefined":
                            postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10) 
                        else:
                             postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))
                        
                        for x in postlist: 
    
                            x.commissario=Commissario.get_by_user(x.author.get())
                            
                            
                        template_values = {
                                "postlist":postlist,
                                 "cmsro":self.getCommissario(user), 
                                 "subscription": get_current_sub(user,node),
                                 "user": user,
                                 "node":node.get()
                                }
                        if not postlist or not next_curs:
                            
                            response = {'response':'no_posts'}
                            self.output_as_json(response)
                            return
                            
                                
                        template = jinja_environment.get_template("social/pagination/post.html")
       
                        html=template.render(template_values)
                        response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                        self.output_as_json(response)
                  
                if cmd=="post_main":
                        node=model.Key(urlsafe=self.request.get("node"))
                        if not cursor or cursor == "undefined":
                            postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10) 
                        else:
                             postlist, next_curs, more = SocialPost.query(ancestor=node).order(-SocialPost.latest_comment_date).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))
                        
                        for x in postlist: 
    
                            x.commissario=Commissario.get_by_user(x.author.get())
                            
                            
                        template_values = {
                                "postlist":postlist,
                                 "cmsro":self.getCommissario(user), 
                                 "subscription": get_current_sub(user,node),
                                 "user": user,
                                 "node":node.get()
                                }
                        if not postlist or not next_curs:
                            
                            response = {'response':'no_posts'}
                            self.output_as_json(response)
                            return
                            
                                
                        template = jinja_environment.get_template("social/pagination/post.html")
       
                        html=template.render(template_values)
                        response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                        self.output_as_json(response)
                    
                if cmd=="notifications":
                    notlist, next_curs, more = SocialProfile.retrieve_notifications(user,cursor)
                    if not notlist or not next_curs:
                            
                            response = {'response':'no_notificationss'}
                            self.output_as_json(response)
                            return
                   
                    template = jinja_environment.get_template("social/pagination/notifications.html")
                   
                    
                    template_values={
                                     'notifications':notlist,
                                  
                                     'user':user.key,
                                     }
                    html=template.render(template_values)
                    response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                    self.output_as_json(response)

                if cmd=="search_nodes":
                    nodes=[]
                    if not cursor or cursor == "undefined":
                        try:
                            results = search.Index(name="index-nodes").search(search.Query(query_string=self.request.get("query")))
                        
                            for scored_document in results:
                                nodes.append(model.Key(urlsafe=scored_document.doc_id[5:]).get())
                                
                        except search.Error:
                                logging.exception('Search failed' )
                    
                    template_values = {
                            "nodelist":nodes,
                             }
               
                        
                    template = jinja_environment.get_template("social/pagination/node.html")
                    if nodes:
                        html=template.render(template_values)
                        response = {'html':html,
                                
                                 
                                  #cursor":next_curs.urlsafe()
                                  }
                    else:
                        response={'html':"",'list':[]}
                        
                    self.output_as_json(response)
                        
class SocialSearchHandler(SocialAjaxHandler):
    def get(self):
        postlist = list()
        try:
            results = search.Index(name="index-posts").search(search.Query(query_string=self.request.get("query")))
        
            for scored_document in results:
                post = model.Key(urlsafe=scored_document.doc_id[5:]).get()
                post.commissario=Commissario.get_by_user(post.author.get())                
                postlist.append(post)
                
                
        except search.Error:
                logging.exception('Search failed' )
        
        template_values = {
            "content": "social/search.html",
            "postlist": postlist,
                 }
    
        self.getBase(template_values)
         
class SocialNotificationsListHandler(BasePage):
        @reguser_required
        def get(self):
            user=self.get_current_user()
            prof=SocialProfile.query(ancestor=user.key).get()
            
            template_values = {
                           'content': 'social/notifications.html',
                           'user':user,
                           'last_visit': prof.ultimo_accesso_notifiche
                          }
                           
            prof.ultimo_accesso_notifiche=datetime.now()
            prof.put()
            self.getBase(template_values)
            
class SocialMainHandler(BasePage):
    @reguser_required
    def get(self):
        user=self.get_current_user()
        node_list=SocialNodeSubscription.get_nodes_by_user(user,-SocialNodeSubscription.starting_date)
        node_recent=[]
        for node in SocialNode.get_most_recent():
            if node not in node_list:
                node_recent.append(node)
            if len(node_recent) >= 3:
                break
        node_active=[]
        for node in SocialNode.get_most_active():
            if node not in node_list:
                node_active.append(node)
            if len(node_active) >= 3:
                break
                    
        
        template_values = {
                        'content': 'social/main_social.html',
                        'node_list':node_list,
                        'node_active': node_active,
                        'node_recent': node_recent,
                        'user':user
        }
        self.getBase(template_values)
        
class SocialDLoadHandler(SocialAjaxHandler):
    @reguser_required
    def get(self):
        self.post()

    @reguser_required
    def post(self):
        cmd=self.request.get("cmd")
        user=self.request.user
        
        if cmd=="modal_reshare":
            template_values = {
                "my_nodelist":SocialNodeSubscription.get_nodes_by_user(user) ,
                "post":self.request.get("post")
            }
            
            template = jinja_environment.get_template("social/ajax/modal_reshare.html")
            html=template.render(template_values)
            response = {'response':'success','html':html}
            self.output_as_json(response)
        
class SocialUtils:
    @classmethod
    def generate_all_social_profiles(cls):
        users=models.User.query().fetch()
        for i in users:
            SocialProfile.create(i.key)
    @classmethod
    def generate_random_contents(cls,user):
        node=SocialNode()
        node.name="Test Node"
        node.description="Test node"
        node.put()
        for i in range(0,25):
            post=node.create_open_post("Contenuto di "+str(i),"Discussione "+str(i),user).get()
            for j in range(0,10):
                post.create_reply_comment("Commento di "+str(j),user)


    @classmethod
    def unsubscribe_all(cls):
        
        for sub in SocialPostSubscription.query().fetch():
            sub.key.delete()

    @classmethod
    def delete_nodes(cls):
        
        for node in SocialNode.query(SocialNode.latest_post==None).fetch():
            node.key.delete()
            
 
    @classmethod
    def locations_to_nodes(cls):
        
        users=models.User.query().fetch()
        
        for user in users:
            comm=Commissario.get_by_user(user)
            if comm:
                citta=comm.citta
                scuole=comm.commissioni()
                scuole=[SocialResource.get_resource(x.key) for x in scuole]
                nodes=SocialNode.query().filter(SocialNode.resource==SocialResource.get_resource(citta).key or SocialNode.resource.IN(scuole)).fetch()
                for node in nodes:
                    node.subscribe_user(user)
    @classmethod
    def generate_nodes(cls):  
        logging.info("generate_nodes.city")
        citta=Citta.get_all()
        for i in citta:
           node=SocialNode(name=i.nome,description="Gruppo di discussione sulla citta di "+i.nome,resource=i.create_resource().key)
           node.put()
        
        logging.info("generate_nodes.cm")
        commissioni=Commissione.query().fetch()
        for i in commissioni:
        
           c=i.citta.get()
           node=SocialNode(name=i.nome,description="Gruppo di discussione per la commissione della scuola "+i.nome+" di "+c.nome,resource=i.create_resource().key)
           node.put()

class SocialNewsLetter(BasePage):
    
    def get(self):
        return self.create_newsletter()
    
    def create_newsletter(self):
        user_list=Commissario.get_for_newsletter()
        nodes=SocialNode.query().fetch()
        posts_by_node={}
        newsletter_size=10
        
        titolo="Newsletter Pappa-mi"
        for node in nodes:
            logging.info("1")
            posts=SocialPost.query(ancestor=node.key).order(-SocialPost.creation_date).filter(SocialPost.creation_date>=(datetime.now()-timedelta(weeks=1))).fetch(newsletter_size/2)
            if posts:
                posts_by_node[''+str(node.key.id())]=posts
                logging.info("2")          
        logging.info("user_list: " + str(user_list.count()))          
          
        for user in user_list:
            all_posts=[]
            final_posts=[]
            my_nodes=SocialNodeSubscription.get_nodes_by_user(user.usera.get())
            for node in my_nodes:
                logging.info("3")
                if posts_by_node.has_key(''+str(node.key.id())):                
                    all_posts= all_posts+posts_by_node[''+str(node.key.id())]
            if len(all_posts)<=newsletter_size/2:
                return

            logging.info("newsletter_size: " + str(newsletter_size))          
              
                     
            for i in range(newsletter_size):
                rand=random.randint(0,len(all_posts)-1)
                final_posts.append(all_posts[rand])
            template = jinja_environment.get_template("social/newsletter.html")
            html=template.render({"posts":final_posts})
            mail.send_mail(sender="Example.com Support <example@pappa-mi.it>",
            to=user.usera.get().email,
            subject=titolo,
            body="",
            html=html
            )
            self.response.headers.add_header('content-type', 'text/html', charset='utf-8')
            self.response.out.write(html)
            
            


  
app = webapp.WSGIApplication([
    ('/social/node/(.*)', NodeHandler),
    ('/social/nodelist', NodeListHandler),
    ('/social/post/(.*)', SocialPostHandler),
    ('/social/managepost',SocialManagePost),
    ('/social/test', SocialTest),
    ('/social/socialmap',SocialMapHandler),
    ('/social/subscribe', SocialSubscribeHandler),
    ('/social/createnode', SocialCreateNodeHandler),
    ('/social/editnode/(.*)', SocialEditNodeHandler),
    ('/social/paginate', SocialPaginationHandler),
    ('/social/search', SocialSearchHandler),
    ('/social/dload', SocialDLoadHandler),
    ('/social/notifications', SocialNotificationsListHandler),
    ('/social', SocialMainHandler),
    ],
                             
    debug = True, config=config)



def main():
  app.run();

if __name__ == "__main__":
  main()
