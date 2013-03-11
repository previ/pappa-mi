#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
from google.appengine.api.taskqueue import Task, Queue

import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import mail
from datetime import date, datetime, time, timedelta
from gviz_api import *
from py.model import *
from py.blob import *

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
      current_sub=node_i.get_subscription(current_user)
                  
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
 

       
    
    
class SocialTest(BasePage):
  def get(self):
      
      SocialUtils.generate_nodes()
    # for i in SocialComment.query().fetch(keys_only=True):
     #   i.delete()
    #  SocialUtils.generate_random_contents(self.get_current_user())
        
          
class NodeListHandler(BasePage):
  def get(self):
    #geo = model.GeoPt(41.754922,12.502441)
    template_values = {
      'content': 'social/nodelist.html',
      'nodelist': SocialNode.get_most_active()
      #'citta': Citta.get_all(),
      }
        
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
        post = model.Key(urlsafe=id).get()
        if post is None or not isinstance(post, SocialPost):
            self.error()
        node = post.key.parent()
        
        current_user=self.get_current_user()
        current_sub=None
        if current_user is not None:
            current_user=current_user.key
            current_sub=memcache.get("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()))
           
            if current_sub is None:
                current_sub=SocialNodeSubscription.query(ancestor=node).filter(SocialNodeSubscription.user==current_user).get()
                memcache.add("SocialNodeSubscription-"+str(node.id())+"-"+str(current_user.id()),current_sub)
            
            postsub=memcache.get("SocialPostSubscription-"+str(post.key.id())+"-"+str(current_user.id()))
           
            if postsub is None:
                postsub=SocialPostSubscription.query(ancestor=post.key).filter(SocialPostSubscription.user==current_user).get()
                memcache.add("SocialPostSubscription-"+str(post.key.id())+"-"+str(current_user.id()),postsub)
         
            
        template_values = {
                           'content': 'social/post.html',
                           'post': post,
                           'user':current_user,
        }                    
        if current_user:
            template_values['subscription']=current_sub
            template_values['postsub']=postsub
            
            
        self.getBase(template_values)

    @classmethod    
    def create_post(cls, node, user, title, content=None, resources=None, res_types=None, attachments=None):

        post=node.get().create_open_post(user, title, content, resources, res_types)
        
        if attachments:
            for attach in nc.attachments:
                attach.obj = post
                attach.put()
        
        postlist = list()
        postlist.append(post.get())
        
        template_values = {
          "main":"social/pagination/post.html",
          "postlist":postlist,          
          "cmsro":post.get().commissario, 
          "subscription": node.get().get_subscription(user),
          "user": user,
          "node":node.get()
         }
        
        return template_values

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
        #for x in postlist: 
        #    x.commissario=Commissario.get_by_user(x.author.get())
        
        template_values = {
          "main":"social/pagination/post.html",
          "postlist":postlist,          
          "cmsro":self.getCommissario(user), 
          "subscription": node.get().get_subscription(user),
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
                sub = node.subscribe_user(user)
                self.success({'subscribed': 'true',
                                  'ntfy_period': str(sub.ntfy_period)})
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

        if cmd == "set_ntfy_period":
            node = model.Key(urlsafe=self.request.get('node')).get()
            if node:
                ns = node.subscriptions[user.key]
                if ns:
                    ns.ntfy_period = int(self.request.get('ntfy_period'))
                    ns.put()
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
            post_key=node.create_open_post(content=feedparser._sanitizeHTML(self.request.get("content"),"UTF-8"),title=feedparser._sanitizeHTML(self.request.get("title"),"UTF-8"),author=user)

            SocialUtils.process_attachments(self.request, post_key)

            postlist = list()
            postlist.append(post_key.get())
            
            template_values = {
                "postlist":postlist,
                "cmsro":self.getCommissario(user), 
                "subscription": node.get_subscription(user),
                "user": user,
                "node":node
             }
           
            template = jinja_environment.get_template("social/pagination/post.html")
 
            html=template.render(template_values)
            response = {'response':'success','html':html,"cursor":''}
            self.output_as_json(response)
           
           
        # create a comment to a post
        # parameters: 'post'
        # parameters: 'content'
        if cmd == "create_comment":
            post=model.Key(urlsafe=self.request.get('post')).get()
            node=post.key.parent().get()
            logging.info("content:" + self.request.get("content"))
            comment = post.create_comment(feedparser._sanitizeHTML(self.request.get("content"),"UTF-8"),user)  
             
            template_values = {
                "post":post,
                "comment":comment,
                "cmsro":self.getCommissario(user), 
                "user": user
             }
            
            template = jinja_environment.get_template("social/pagination/comment.html")
 
            html=template.render(template_values)
            response = {'response':'success','html':html,"cursor":''}
            self.output_as_json(response)
           
           
        if cmd == "delete_comment":
            comment_key = model.Key(urlsafe=self.request.get('comment'))
            post_key = comment_key.parent()              
            node = post_key.parent().get()
            
            if user.key != comment_key.get().author and not node.get_subscription(user).can_admin:
                self.error()
                return
            post_key.get().delete_comment(comment_key)
            self.success()

        if cmd == "expand_post":
            post = model.Key(urlsafe=self.request.get('post')).get()
            template_values = {
                               'main': 'social/post.html',
                               'post': post,
                               'user': user,
                               "cmsro":self.getCommissario(user), 
            }                                    
                
            template = jinja_environment.get_template("social/post.html")
 
            html=template.render(template_values)
            response = {'response':'success','post':post.key.urlsafe(),'html':html}
            self.output_as_json(response)

        if cmd == "delete_open_post":
            post=model.Key(urlsafe=self.request.get('post')).get()
               
            #node=node.get()
            node=post.key.parent().get()
            
            #check admin permissions
            if not node.get_subscription(user).can_admin:
                return    
            #delete replies
            node.delete_post(post)
            
            self.success({'url':"/social/node/"+str(node.key.urlsafe())})

        if cmd == "edit_post":
           post=model.Key(urlsafe=self.request.get('post')).get()
           node = post.key.parent().get()
           template_values = {
               "post":post,
               "cmsro":self.getCommissario(user), 
               "subscription": node.get_subscription(user),
               "user": user
            }
          
           template = jinja_environment.get_template("social/ajax/post_edit.html")

           html=template.render(template_values)
           response = {'response':'success','post':post.key.urlsafe(),'html':html}
           self.output_as_json(response)
           
        if cmd == "update_post":
           post=model.Key(urlsafe=self.request.get('post')).get()
           post.content=feedparser._sanitizeHTML(self.request.get("content"),"UTF-8")
           post.put()
           node = post.key.parent().get()
                     
           SocialUtils.process_attachments(self.request, post.key)
    
           post.clear_attachments()

           template_values = {
               "post":post,
               "node":node,
               "cmsro":self.getCommissario(user), 
               "subscription": node.get_subscription(user),
               "user": user
            }
          
           template = jinja_environment.get_template("social/post.html")

           html=template.render(template_values)
           response = {'response':'success','post':post.key.urlsafe(),'html':html,"cursor":''}
           self.output_as_json(response)
           

        if cmd== "reshare_open_post":          
            node=model.Key(urlsafe=self.request.get('node')).get()           
            post=model.Key(urlsafe=self.request.get('post')).get()
                
            title=self.request.get('title')
            content=self.request.get('content')
            
            rs_post_key=post.reshare(node.key,user,feedparser._sanitizeHTML(content,"UTF-8"),feedparser._sanitizeHTML(title,"UTF-8"))
            if False:
                self.success({'url': "/social/post/"+str(rs_post_key.urlsafe())})
            else:
                postlist = list()
                postlist.append(rs_post_key.get())
                
                template_values = {
                    "postlist":postlist,
                    "cmsro":self.getCommissario(user), 
                    "subscription": node.get_subscription(user),
                    "user": user,
                    "node":node
                 }
               
                template = jinja_environment.get_template("social/pagination/post.html")
     
                html=template.render(template_values)
                response = {'response':'success','html':html,"cursor":'', 'post': rs_post_key.urlsafe()}
                self.output_as_json(response)
                
        
        if cmd== "vote_post":          
            post=model.Key(urlsafe=self.request.get('post')).get()
            vote = int(self.request.get('vote'))
            post.vote(vote, self.get_current_user())
                            
            response = {'response':'success', 'post': post.key.urlsafe(), 'votes':str(len(post.votes))}
            self.output_as_json(response)             

        if cmd== "vote_list":          
            post=model.Key(urlsafe=self.request.get('post')).get()

            template_values = {
                "cmsro":self.getCommissario(user), 
                "votes":post.votes
             }
           
            template = jinja_environment.get_template("social/pagination/voters.html")
 
            html=template.render(template_values)
                            
            response = {'response':'success', 'html':html}
            self.output_as_json(response)             

        if cmd== "reshare_list":          
            post=model.Key(urlsafe=self.request.get('post')).get()

            template_values = {
                "cmsro":self.getCommissario(user), 
                "reshares":post.reshares
             }
           
            template = jinja_environment.get_template("social/pagination/reshares.html")
 
            html=template.render(template_values)
                            
            response = {'response':'success', 'html':html}
            self.output_as_json(response)      
            
        if cmd== "post_attach_delete":          
            post=model.Key(urlsafe=self.request.get('post')).get()
            attach=model.Key(urlsafe=self.request.get('attach'))
            post.remove_attachment(attach)
                            
            response = {'response':'success'}
            self.output_as_json(response)             

        if cmd == "update_comment":
            comment=model.Key(urlsafe=self.request.get('comment')).get()
            post_key = comment.key.parent()
            node = post_key.parent().get()
            comment.content=feedparser._sanitizeHTML(self.request.get("content"),"UTF-8")
            comment.put()
                      
            template_values = {
                "comment":comment,
                "cmsro":self.getCommissario(user), 
                "subscription": node.get_subscription(user),
                "user": user
             }
           
            template = jinja_environment.get_template("social/pagination/comment.html")
 
            html=template.render(template_values)
            logging.info(html)
            response = {'response':'success','comment':comment.key.urlsafe(),'html':html,"cursor":''}
            self.output_as_json(response)

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
        node.default_comment=bool(self.request.get("default_comment"))
        node.default_post=bool(self.request.get("default_post"))
        node.default_admin=bool(self.request.get("default_admin"))
        node.founder=self.get_current_user().key
        node.init_rank()
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
        node.default_comment=bool(self.request.get("default_comment"))
        node.default_post=bool(self.request.get("default_post"))
        node.default_admin=bool(self.request.get("default_admin"))
        node.founder=self.get_current_user().key
        node.init_rank()
        node.put()
        
        self.redirect("/social/node/"+str(node.key.id()))

class SocialPaginationHandler(SocialAjaxHandler):

    def get(self):
        return self.post()
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
                node=model.Key(urlsafe=self.request.get("node")).get()
                if not cursor or cursor == "undefined":
                    postlist, next_curs, more = SocialPost.get_by_node_rank(node=node.key, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
                else:
                     postlist, next_curs, more = SocialPost.get_by_node_rank(node=node.key, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=Cursor(urlsafe=cursor))
                
                #for x in postlist: 
                #    x.commissario=Commissario.get_by_user(x.author.get())
                    
                    
                template_values = {
                        "postlist":postlist,
                         "cmsro":self.getCommissario(user), 
                         "subscription": node.get_subscription(user),
                         "user": user,
                         "node":node
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
                node=None
                next_curs_key=None
                node_urlsafe=self.request.get("node")
                if node_urlsafe=="all":                                            
                    if not cursor or cursor == "undefined":
                        postlist, next_curs, more = SocialPost.get_user_stream(user=user, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
                    else:
                        postlist, next_curs, more = SocialPost.get_user_stream(user=user, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=cursor)
                    next_curs_key = next_curs
                else:
                    node=model.Key(urlsafe=self.request.get("node"))
                    
                    if not cursor or cursor == "undefined":
                        postlist, next_curs, more = SocialPost.get_by_node_rank(node=node, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
                    else:
                        postlist, next_curs, more = SocialPost.get_by_node_rank(node=node, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=Cursor(urlsafe=cursor))
                    if next_curs:
                        next_curs_key = next_curs.urlsafe()
                    
                    if node.get().get_subscription(user):
                        node.get().get_subscription(user).reset_ntfy()
                    
                template_values = {
                        "postlist":postlist,
                        "cmsro":self.getCommissario(user), 
                        "user": user
                        }
                
                if node:
                    template_values["subscription"]=node.get().get_subscription(user)
                    
                if len(postlist) == 0:
                    
                    response = {'response':'no_posts'}
                    self.output_as_json(response)
                    return                        
                        
                template = jinja_environment.get_template("social/pagination/post.html")

                html=template.render(template_values)
                response = {'response':'success','html':html,"cursor":next_curs_key}
                self.output_as_json(response)
                                        
            if cmd=="notifications":
                
                notlist, next_curs, more = SocialNotificationHandler.retrieve_notifications(user.key, start_cursor=None)
                for n in notlist:
                    logging.info(n)

                if not notlist:                 
                    response = {'response':'no_notifications'}
                    self.output_as_json(response)
                    return
               
                template = jinja_environment.get_template("social/pagination/notifications.html")
               
                
                template_values={
                                 'notifications':notlist,
                                 'cmsro':self.getCommissario(user),
                                 'user':user.key
                                 }
                html=template.render(template_values)
                response = {'response':'success','html':html}
                if more:
                    response['cursor'] = next_curs.urlsafe()
                self.output_as_json(response)

            if cmd=="ntfy_summary":
                start_cursor = None
                if cursor or cursor != "undefined":
                    start_cursor = Cursor(urlsafe=cursor)
                    
                notlist, next_curs, more = SocialNotificationHandler.retrieve_notifications(user.key, start_cursor=start_cursor)

                if not notlist and not next_curs:                    
                    response = {'response':'no_notifications'}
                    self.output_as_json(response)
                    return
               
                template = jinja_environment.get_template("social/pagination/notifications.html")
               
                
                template_values={
                                 'notifications':notlist,                                  
                                 'user':user.key,
                                 'cmsro':self.getCommissario(user)
                                 }
                html=template.render(template_values)
                next_curs_str = None
                if next_curs:
                    next_curs_str = next_curs.urlsafe()
                response = {'response':'success','html':html,"cursor":next_curs_str}
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
                
                if cmd=="browse_nodes":
                    nodes= list()
                    if not cursor or cursor == "undefined":
                        try:
                            for n in SocialNode.get_most_active():
                                nodes.append(n)
                                if len(nodes) > 50:
                                    break
                                
                        except search.Error:
                                logging.exception('Browse failed' )
                    
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
    

class SocialNotificationHandler(SocialAjaxHandler):
    def get(self):
        logging.info("SocialNotificationHandler")
        if self.request.get("cmd") == "clear":
            cursor = None
            while True:
                cursor = SocialNotificationHandler.clear_events(cursor)
                if not cursor:
                    break;
        elif self.request.get("cmd") == "process":
            job = {'event_cursor':None}
            job = SocialNotificationHandler.process_events(job)
            logging.info("event_cursor: " + str(job["event_cursor"]))
            if job["event_more"]:
                self.putTask('/social/event', job=job)
            else:
                self.process_notifications()
 
        else:
            self.putTask('/social/event', job={})
            
        Cache.get_cache("SocialNotification").clear_all()
           
        self.success()
        
    def startTask(self):
        self.putTask('/social/event', job={})
        
    def putTask(self, aurl, job):
      task = Task(url=aurl, params={'cmd': 'process', "job": job}, method="GET")
      queue = Queue()
      queue.add(task)
            
    """
    process events as a batch
    input: 
      event_cursor
      node_cursor_<node_id>
      for every event in batch(defined by cursor) do:
        if event is a new post:
          process subscription in batch(definied by none_cursor_id), if batch size > limit, do not save event state, else mark event as processed 
    """
    @classmethod
    def process_events(cls, job):
        event_cursor = job['event_cursor']
        events, event_next_cursor, event_more = SocialEvent.get_by_status(0, event_cursor)
        for e in events:
            logging.info("event: " + e.type)
            if e.type==SocialEvent.new_post:
                node_cursor = job.get('node_cursor_' + str(e.target.id()))
                ns, ns_next_cursor, ns_more = SocialNodeSubscription.get_by_node(e.target, cursor=node_cursor)
                for s in ns:
                    logging.info("subs.user: " + s.user.get().email + " e.user: " + e.user.get().email)
                    if e.user != s.user:
                        logging.info("new_post.created")
                        SocialNotification.create(e.key, s.user)
                        s.has_ntfy = True
                        s.ntfy += 1
                        s.put()
                if ns_more:
                    job['node_cursor_' + str(e.target.id())] = ns_next_cursor
                else:
                    e.status = 1
                    e.put()
            if e.type==SocialEvent.new_comment:
                logging.info("new_comment")
                for s in SocialPostSubscription.get_by_post(e.target):
                    logging.info("s: " + str(s))
                    if e.user != s.user:
                        logging.info("new_comment.created")
                        SocialNotification.create(e.key, s.user)
                        s.has_ntfy = True
                        s.put()
                e.status = 1
                e.put()
        job['event_more'] = event_more 
        job['event_cursor'] = event_next_cursor
        return job

    @classmethod
    def clear_events(cls, cursor):
        results, next_cursor, more = SocialEvent.get_by_status(0, cursor)
        for n in SocialNotification.get_by_date(date=None):
            n.key.delete()
        return None
        
        
    @classmethod
    def retrieve_new_notifications_(cls,user_t, date):
        nodes_list=SocialNodeSubscription.get_nodes_keys_by_user(user_t)
        posts_list=SocialPostSubscription.get_posts_keys_by_user(user_t)
        
        sources_list=nodes_list+posts_list
        logging.info(sources_list)
        c = 0
        for n in SocialNotification.query().filter(SocialNotification.author_key!=user_t.key,SocialNotification.source_key.IN(sources_list)).order(SocialNotification.author_key).order(-SocialNotification.date).fetch():
            if n.date < date:
                break;
            c += 1
        return c

    @classmethod
    def retrieve_new_notifications(cls, user_t, date):
        return SocialNotification.get_by_user_date(user_t, date)
                   

    @classmethod
    def retrieve_notifications_(self,user_t,cursor):
      nodes_list=SocialNodeSubscription.get_nodes_keys_by_user(user_t)
      posts_list=SocialPostSubscription.get_posts_keys_by_user(user_t)
      
      
      sources_list=nodes_list+posts_list
      logging.info(sources_list)
      if not cursor or cursor == "undefined":
          return SocialNotification.query().order(SocialNotification.author_key).filter(SocialNotification.author_key!=user_t.key,SocialNotification.source_key.IN(sources_list)).order(-SocialNotification.date).order(SocialNotification._key).fetch_page(10)
      else:
          return SocialNotification.query().order(SocialNotification.author_key).filter(SocialNotification.author_key!=user_t.key,SocialNotification.source_key.IN(sources_list)).order(-SocialNotification.date).order(SocialNotification._key).fetch_page(10, start_cursor=Cursor(urlsafe=cursor))

    @classmethod
    def retrieve_notifications(cls, user_t, start_cursor):
        return SocialNotification.get_by_user(user_t, cursor=start_cursor)
    
    @classmethod
    def process_notifications(cls):
        logging.info("process_notifications")
        user_ntfy = dict()
        
        #Node Subscription
        for sub in SocialNodeSubscription.get_by_ntfy():
            logging.info("SocialNodeSub")
            notifications = user_ntfy.get(sub.user)
            if notifications is None:
                notifications = list()
                user_ntfy[sub.user] = notifications
            for ntfy in SocialNotification.get_by_user_status(sub.user, SocialNotification.status_created):
                notifications.append(ntfy)
                ntfy.status = SocialNotification.status_notified
                ntfy.put()
                logging.info("SocialNotification")
            sub.has_ntfy = False
            sub.last_ntfy_sent = datetime.now()
            sub.put()

        #Post Subscriptions
        for sub in SocialPostSubscription.get_by_ntfy():
            logging.info("SocialPostSub")
            notifications = user_ntfy.get(sub.user)
            if notifications is None:
                notifications = list()
                user_ntfy[sub.user] = notifications
            for ntfy in SocialNotification.get_by_user_status(sub.user, SocialNotification.status_created):
                notifications.append(ntfy)
                ntfy.status = SocialNotification.status_notified
                ntfy.put()
                logging.info("SocialNotification")
            sub.has_ntfy = False
            sub.put()
        
        logging.info("user_ntfy.len: " + str(len(user_ntfy)))
        for user in user_ntfy:
            notifications = user_ntfy.get(user)
            if len(notifications) > 0:
                cls.send_notifications_email(user, notifications)
            else:
                logging.info("user: " + user.get().email + " has no notifications")
                
        
    @classmethod
    def send_notifications_email(cls, user, notifications):
        logging.info("Sending notification to user: " + user.get().email)
        for n in notifications:
            logging.info("Notification: " + str(n.event.get().type))
            
        template = jinja_environment.get_template("social/notifications_email.html")
        html=template.render({"cmsro":Commissario.get_by_user(user.get()), "notifications":notifications})
        mail.send_mail(sender="Pappa-Mi <aiuto@pappa-mi.it>",
        to=user.get().email,
        subject="[Pappa-Mi] Novità",
        body="",
        html=html
        )
        #self.response.headers.add_header('content-type', 'text/html', charset='utf-8')
        #self.response.out.write(html)
        #logging.info(html)
    
        
            
        
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
            cmsro = self.getCommissario(user)
            
            template_values = {
                           'content': 'social/notifications.html',
                           'user':user,
                           'last_visit': cmsro.ultimo_accesso_notifiche,
                           'notify_list': SocialNotificationHandler.retrieve_new_notifications(user.key, cmsro.ultimo_accesso_notifiche)
                           
                          }
            cmsro.ultimo_accesso_notifiche = datetime.now()
            cmsro.put()
            cmsro.set_cache()
            self.getBase(template_values)
            
class SocialMainHandler(BasePage):
    @reguser_required
    def get(self):
        user=self.get_current_user()
        subs = SocialNodeSubscription.get_by_user(user,-SocialNodeSubscription.starting_date)
        node_list = []
        for sub in subs:
            node_list.append(sub.key.parent().get())
        node_recent=[]
        for node in SocialNode.get_most_recent():
            if node not in node_list:
                node_recent.append(node)
            if len(node_recent) >= 5:
                break
        node_active=[]
        for node in SocialNode.get_most_active():
            if node not in node_list:
                node_active.append(node)
            if len(node_active) >= 5:
                break
            
        cmsro = self.getCommissario(user)
        last_access = cmsro.ultimo_accesso_notifiche
        if not last_access:
            last_access = datetime.now()
        cmsro.ultimo_accesso_notifiche = datetime.now()
        if last_access - cmsro.ultimo_accesso_notifiche > timedelta(60):
            cmsro.put()
            cmsro.set_cache()
            
        logging.info("node_list")
        for n in node_list:
            logging.info(n.name)
        logging.info("node_recent")
        for n in node_recent:
            logging.info(n.name)
        logging.info("node_active")
        for n in node_active:
            logging.info(n.name)
        template_values = {
                        'content': 'social/main_social.html',
                        'subs':subs,
                        'node_list':node_list,
                        'node_active': node_active,
                        'node_recent': node_recent,
                        'user':user,
                        'notifications': str(len(SocialNotificationHandler.retrieve_new_notifications(user.key, last_access)))
        }
        self.getBase(template_values)

    @reguser_required
    def post(self):
        return self.get()
        
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
                "subs":SocialNodeSubscription.get_by_user(user) ,
                "post":self.request.get("post")
            }
            
            template = jinja_environment.get_template("social/ajax/modal_reshare.html")
            html=template.render(template_values)
            response = {'response':'success','html':html}
            self.output_as_json(response)
        
class SocialUtils:
    
    @classmethod
    def process_attachments(cls, request, obj):
        for att in request.POST.getall('attach_file'):
            if hasattr(att, "filename"):
                if len(att.value) < 10000000 :
                    attachment = Allegato()
                    attachment.nome = att.filename
                    blob = Blob()
                    blob.create(attachment.nome)
                    attachment.blob_key = blob.write(att.value)
                    attachment.obj = obj
                    attachment.put()
                else:
                    logging.info("attachment is too big.")
        for att_key in request.POST.getall('attach_delete'):
            model.Key(urlsafe=att_key).delete()
        
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
        node.init_rank()
        node.put()
        for i in range(0,25):
            post=node.create_open_post("Contenuto di "+str(i),"Discussione "+str(i),user).get()
            for j in range(0,10):
                post.create_comment("Commento di "+str(j),user)


    @classmethod
    def unsubscribe_all(cls):
        
        for sub in SocialPostSubscription.query().fetch():
            sub.key.delete()

    @classmethod
    def delete_nodes(cls):
        
        for node in SocialNode.query().fetch():
            node.key.delete()
            
 
    @classmethod
    def locations_to_nodes(cls):
        
        for c in Commissario.get_all():
            for node in SocialNode.query().filter(SocialNode.resource==c.citta).fetch():
                node.subscribe_user(c.usera.get())
            for cm in c.commissioni():
                for node in SocialNode.query().filter(SocialNode.resource==cm.key).fetch():
                    node.subscribe_user(c.usera.get())
                    
    @classmethod
    def generate_nodes(cls):  
        logging.info("generate_nodes.city")
        citta=Citta.get_all()
        for i in citta:
            if len(SocialNode.get_nodes_by_resource(i.key)) == 0:
                node=SocialNode(name=i.nome,description="Gruppo di discussione sulla citta di "+i.nome,resource=[i.key], res_type=["city"])
                node.init_rank()
                node.put()
        
        logging.info("generate_nodes.cm")
        commissioni=Commissione.query().fetch()
        for i in commissioni:
            if len(SocialNode.get_nodes_by_resource(i.key)) == 0:
                logging.info(i.nome)
                c=i.citta.get()
                node=SocialNode(name=i.tipoScuola + " " + i.nome,
                                description="Gruppo di discussione per la scuola " + i.tipoScuola + " " + i.nome + " di " + c.nome, resource=[i.key], res_type=["commission"])
                node.init_rank()
                node.put()

    @classmethod
    def msg_to_post(cls):
        tags_mapping = {"salute", "Salute",
                        "educazione alimentare", "Educazione alimentare",
                        "commissioni mensa", "Commissioni Mensa",
                        "rassegna stampa", "Generale"}
        for tag, node_name in tags_mapping:
            node = SoacialNode.get_by_name(node_name)
            tags_mapping[tag] = node
        for m in Messaggio.get_all():
            post = None
            if m.tipo in [101,102,103,104]:
                #dati
                node = SocialNode.query().filter(SocialNode.resource==m.grp).fetch().get()
                post=node.create_open_post(m.c_ua, m.title, m.body, [m.par], [m.par.get().restype])
            elif m.tipo == 201:
                #messaggi
                node = None
                if len(m.tags) > 0:
                    node = tags_mapping(m.tags[0])
                if not tag:
                    node = node_default
                post=node.create_open_post(m.c_ua, m.title, m.body, [], [])
            if m.commenti:
                for mc in Messaggio.get_by_parent(m.key):
                    post.create_comment(mc.body, mc.c_ua)
                
            for a in m.get_allegati(m.key):
                a.obj = post.key
                a.put()
            for v in Voto.get_by_msg(m):
                v.obj = post.key
                v.put()             
            

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
            subs = SocialNodeSubscription.get_by_user(user.usera.get())
            for sub in subs:
                logging.info("3")
                if posts_by_node.has_key(''+str(sub.parent().id())):                
                    all_posts= all_posts+posts_by_node[''+str(sub.parent().id())]
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
    ('/social/event', SocialNotificationHandler),
    ('/social', SocialMainHandler),
    ],
                             
    debug = True, config=config)



def main():
  app.run();

if __name__ == "__main__":
  main()
