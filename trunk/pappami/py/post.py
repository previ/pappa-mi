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
from google.appengine.ext.ndb import model

import webapp2 as webapp
from google.appengine.api import memcache
from datetime import date, datetime, time, timedelta
from model import *
from blob import *
from event import EventHandler

from form import *
import time
from common import Const, Cache, Sanitizer, Channel

class PostHandler(BasePage):
   
    def error(self):
       self.response.clear() 
       self.response.set_status(404)
       template = jinja_environment.get_template('404_custom.html')
       c={"error": "Il post a cui stai provando ad accedere non esiste"}
       t = template.render(c)
       self.response.out.write(t)
       
    
    def get(self,id):
        post = model.Key(urlsafe=id).get()
        node = post.key.parent().get()
        
        current_user=self.get_current_user()
            
        template_values = {
                           'content': 'post/post.html',
                           'post': post,
                           'user':current_user,
                           'fullscreen': True,
        }                                
            
        self.getBase(template_values)

    @classmethod    
    def create_post(cls, node, user, title, content=None, resources=None, res_types=None, attachments=None):

        post=node.get().create_open_post(user, title, content, resources, res_types)
        
        if attachments:
            for attach in attachments:
                attach.obj = post
                attach.put()
        
        postlist = list()
        postlist.append(post.get())
        
        template_values = {
          "main":"post/post_item.html",
          "postlist":postlist,          
          "cmsro":post.get().commissario, 
          "subscription": node.get().get_subscription(user.key),
          "user": user,
          "node":node.get()
         }
        
        return template_values


class PostManageHandler(BaseHandler):
   
    def post(self):             
        user=self.request.user
        cmd = self.request.get('cmd')

        # create a new 'original' post
        # parameters: 'node'
        # parameters: 'title'
        # parameters: 'content'
        if cmd == "create_open_post":
            node=model.Key(urlsafe=self.request.get('node')).get()
            if not node.get_subscription(user.key).can_post:
                self.response.out.write("<response>error</response>")
                return
            clean_title = Sanitizer.text(self.request.get("title"))
            clean_content = Sanitizer.sanitize(self.request.get("content"))
            post_key=node.create_open_post(content=clean_content,title=clean_title,author=user)

            PostUtils.process_attachments(self.request, post_key)

            postlist = list()
            postlist.append(post_key.get())
            
            template_values = {
                "main": "post/post_item.html",
                "postlist": postlist,
                "cmsro": self.getCommissario(user), 
                "subscription": node.get_subscription(user.key),
                "user": user,
                "node": node
             }
           
            #template = jinja_environment.get_template("post/post_item.html") 
            #html=template.render(template_values)
            #response = {'response':'success','html':html,"cursor":''}
            #self.output_as_json(response)
            self.getBase(template_values)
            EventHandler.startTask()
           
           
        # create a comment to a post
        # parameters: 'post'
        # parameters: 'content'
        if cmd == "create_comment":
            post=model.Key(urlsafe=self.request.get('post')).get()
            node=post.key.parent().get()
            logging.info("content:" + self.request.get("content"))
            clean_content = Sanitizer.sanitize(self.request.get("content"))            
            comment = post.create_comment(clean_content,user)  
             
            template_values = {
                "post":post,
                "comment":comment,
                "cmsro":self.getCommissario(user), 
                "user": user
             }
            
            template = jinja_environment.get_template("post/comment.html")
 
            html=template.render(template_values)
            response = {'response':'success', 'num': str(post.comments), 'html':html,"cursor":''}
            self.output_as_json(response)
            EventHandler.startTask()
           
           
        if cmd == "delete_comment":
            comment_key = model.Key(urlsafe=self.request.get('comment'))
            post_key = comment_key.parent()              
            node = post_key.parent().get()
            
            if user.key != comment_key.get().author and not node.get_subscription(user.key).can_admin:
                self.error()
                return
            post_key.get().delete_comment(comment_key)
            self.success({'num': str(post_key.get().comments)})

        if cmd == "expand_post":
            post = model.Key(urlsafe=self.request.get('post')).get()
            template_values = {
                               'post': post,
                               'user': user,
                               "cmsro":self.getCommissario(user), 
                               'hide_comments': self.request.get('exp_comments') == 'false',
            }                                    
                
            template = jinja_environment.get_template("post/post.html")
            logging.info(self.request.get('exp_comments'))
 
            html=template.render(template_values)
            response = {'response':'success','post':post.key.urlsafe(),'html':html}
            self.output_as_json(response)

        if cmd == "collapse_post":
            post = model.Key(urlsafe=self.request.get('post')).get()
            template_values = {
                               'postlist': [post],
                               'user': user,
                               "cmsro":self.getCommissario(user), 
            }                                    
                
            template = jinja_environment.get_template("post/post_item.html")
 
            html=template.render(template_values)
            response = {'response':'success','post':post.key.urlsafe(),'html':html}
            self.output_as_json(response)

        if cmd == "delete_open_post":
            post=model.Key(urlsafe=self.request.get('post')).get()
               
            #node=node.get()
            node=post.key.parent().get()
            
            #check admin permissions
            if not post.can_admin(user):
                logging.info("not admin")
                return    
            #delete replies
            node.delete_post(post)
            logging.info("delete")
            
            self.success({'url':"/node/"+str(node.key.urlsafe())})

        if cmd == "pin_post":
           post=model.Key(urlsafe=self.request.get('post')).get()
           post.pin(days=int(self.request.get('days'))) 
           post.put()
           response = {'response':'success','post':post.key.urlsafe()}
           self.output_as_json(response)

        if cmd == "edit_post":
           post=model.Key(urlsafe=self.request.get('post')).get()
           node = post.key.parent().get()
           template_values = {
               "post":post,
               "cmsro":self.getCommissario(user), 
               "subscription": node.get_subscription(user.key),
               "user": user
            }
          
           template = jinja_environment.get_template("post/post_edit.html")

           html=template.render(template_values)
           response = {'response':'success','post':post.key.urlsafe(),'html':html}
           self.output_as_json(response)
           
        if cmd == "update_post":
           post=model.Key(urlsafe=self.request.get('post')).get()
           post.title = Sanitizer.text(self.request.get("title"))
           post.content = Sanitizer.sanitize(self.request.get("content"))
           post.put()
           node = post.key.parent().get()
                     
           PostUtils.process_attachments(self.request, post.key)
    
           post.clear_attachments()

           template_values = {
               "main": "post/post.html",
               "post": post,
               "node": node,
               "cmsro": self.getCommissario(user), 
               "subscription": node.get_subscription(user.key),
               "user": user
            }
          
           #template = jinja_environment.get_template("post/post.html")
           #html=template.render(template_values)
           #response = {'response':'success','post':post.key.urlsafe(),'html':html,"cursor":''}
           #self.output_as_json(response)
           self.getBase(template_values)
           
        if cmd=="reshare_modal":
            post=model.Key(urlsafe=self.request.get('post')).get()
            template_values = {
                "subs":SocialNodeSubscription.get_by_user(user) ,
                "post":post
            }
            
            template = jinja_environment.get_template("post/modal_reshare.html")
            html=template.render(template_values)
            response = {'response':'success','html':html}
            self.output_as_json(response)

        if cmd== "reshare_open_post":          
            node=model.Key(urlsafe=self.request.get('node')).get()           
            post=model.Key(urlsafe=self.request.get('post')).get()
                
            clean_title = Sanitizer.text(self.request.get("title"))
            clean_content = Sanitizer.sanitize(self.request.get("content"))
           
            rs_post_key=post.reshare(node.key,user,clean_content,clean_title)
            if False:
                self.success({'url': "/post/"+str(rs_post_key.urlsafe())})
            else:
                postlist = list()
                postlist.append(rs_post_key.get())
                
                template_values = {
                    "postlist":postlist,
                    "cmsro":self.getCommissario(user), 
                    "subscription": node.get_subscription(user.key),
                    "user": user,
                    "node":node
                 }
               
                template = jinja_environment.get_template("post/post_item.html")
     
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
           
            template = jinja_environment.get_template("post/voters.html")
 
            html=template.render(template_values)
                            
            response = {'response':'success', 'html':html}
            self.output_as_json(response)             

        if cmd== "reshare_list":          
            post=model.Key(urlsafe=self.request.get('post')).get()

            template_values = {
                "cmsro":self.getCommissario(user), 
                "reshares":post.reshares
             }
           
            template = jinja_environment.get_template("post/reshares.html")
 
            html=template.render(template_values)
                            
            response = {'response':'success', 'html':html}
            self.output_as_json(response)      
 
        if cmd== "author_detail":          
            post=model.Key(urlsafe=self.request.get('post')).get()

            template_values = {
                "cmsro":self.getCommissario(user), 
                "author": post.commissario,
             }
           
            template = jinja_environment.get_template("post/author.html")
 
            html=template.render(template_values)
                            
            response = {'response':'success', 'html':html}
            self.output_as_json(response)      
            
        if cmd== "post_attach_delete":          
            post=model.Key(urlsafe=self.request.get('post')).get()
            attach=model.Key(urlsafe=self.request.get('attach'))
            post.remove_attachment(attach)
                            
            self.success()             

        if cmd == "update_comment":
            comment=model.Key(urlsafe=self.request.get('comment')).get()
            post_key = comment.key.parent()
            node = post_key.parent().get()
            comment.content=Sanitizer.sanitize(self.request.get("content"))
            comment.put()
                      
            template_values = {
                "comment":comment,
                "cmsro":self.getCommissario(user), 
                "subscription": node.get_subscription(user.key),
                "user": user
             }
           
            template = jinja_environment.get_template("post/comment.html")
 
            html=template.render(template_values)
            logging.info(html)
            response = {'response':'success','comment':comment.key.urlsafe(),'html':html,"cursor":''}
            self.output_as_json(response)

        if cmd == "content_edit":
            template_values = {
                            'template': 'post/contentedit.html',
                            'post':  self.request.get('post'),
                            'node': node,
                            'user': self.get_current_user(),
                            'content': self.request.get('content'),
                            
                                               }                    
         
            template = jinja_environment.get_template(template_values["template"])
    
            self.response.write(template.render(template_values))        

class PostSubscribeHandler(BaseHandler):
    def get(self):
        user = self.get_current_user()
        cmd = self.request.get('cmd')
        if cmd == "subscribepost":
                
            post = model.Key(urlsafe=self.request.get('post')).get()
            if post:
                 post.subscribe_user(user)
                 self.success({'subscribed': 'true'})
            else:
                self.error()
    
        if cmd == "unsubscribepost":
            post = model.Key(urlsafe=self.request.get('post')).get()
            if post:
                post.unsubscribe_user(user)
                
                self.success()
            else:
                self.error()

class PostPaginationHandler(BaseHandler):

    def get(self):
        return self.post()
    
    def post(self):
        logging.info("PostPaginationHandler")
        cmd=self.request.get("cmd")
        user=self.request.user
        cursor=self.request.get("cursor")
        cmsro = None
        cmsro = self.getCommissario(user)
            
        if cmd=="post":
            node=model.Key(urlsafe=self.request.get("node")).get()
            if not cursor or cursor == "undefined":
                postlist, next_curs, more = SocialPost.get_by_node_rank(node=node.key, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
            else:
                 postlist, next_curs, more = SocialPost.get_by_node_rank(node=node.key, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=Cursor(urlsafe=cursor))
            
            template_values = {
                    "postlist":postlist,
                     "cmsro":self.getCommissario(user), 
                     "subscription": node.get_subscription(user.key),
                     "user": user,
                     "node":node
                    }                    
                    
            template = jinja_environment.get_template("post/post_item.html")

            html=template.render(template_values)
            response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
            if more == False:
                response['eof'] = 'true'

            self.output_as_json(response)
          
        if cmd=="post_main":
            node=None
            next_curs_key=None
            node_urlsafe=self.request.get("node")
            more = False
            if node_urlsafe=="news":                                            
                if not cursor or cursor == "undefined":
                    postlist, next_curs, more = SocialPost.get_news_stream(page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
                else:
                    postlist, next_curs, more = SocialPost.get_news_stream(page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=Cursor(urlsafe=cursor))
                if next_curs:
                    next_curs_key = next_curs.urlsafe()
            elif node_urlsafe=="all":                                            
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
                
                if user and node.get().get_subscription(user.key):
                    node.get().get_subscription(user.key).reset_ntfy()
                
            template_values = {
                    "postlist":postlist,
                    "cmsro":cmsro, 
                    "user": user
                    }
            
            if user and node:
                template_values["subscription"]=node.get().get_subscription(user.key)
                                        
            template = jinja_environment.get_template("post/post_item.html")

            html=template.render(template_values)
            response = {'response':'success','html':html,"cursor":next_curs_key}
            if not more:
                response['eof'] = 'true'
            self.output_as_json(response)
                                        
class PostUtils:    
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


app = webapp.WSGIApplication([
    ('/post/manage',PostManageHandler),
    ('/post/subscribe', PostSubscribeHandler),
    ('/post/paginate', PostPaginationHandler),
    ('/post/(.*)', PostHandler),
    ],                             
    debug = True, config=config)

