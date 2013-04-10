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
from google.appengine.api.taskqueue import Task, Queue

import webapp2 as webapp
from google.appengine.api import memcache
from google.appengine.api import mail
from datetime import date, datetime, time, timedelta
from py.model import *

from form import *
import base64
import time
from common import Const, Cache, Sanitizer, Channel

class EventHandler(BaseHandler):
    def get(self):
        logging.info("EventHandler")
        if self.request.get("cmd") == "clear":
            cursor = None
            while True:
                cursor = self.clear_events(cursor)
                if not cursor:
                    break;
        elif self.request.get("cmd") == "process":
            job = {'event_cursor':None}
            job = self.process_events(job)
            logging.info("event_cursor: " + str(job["event_cursor"]))
            if job["event_more"]:
                self.putTask('/event', job=job)
            else:
                self.process_notifications()
 
        else:
            self.startTask()
            
        Cache.get_cache("SocialNotification").clear_all()
           
        self.success()
        
    @classmethod    
    def startTask(cls):
        cls.putTask('/event', job={})
        
    @classmethod    
    def putTask(cls, aurl, job):
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
                cls.send_notifications_channel(user, notifications)
                cls.send_notifications_email(user, notifications)
            else:
                logging.info("user: " + user.get().email + " has no notifications")
                

    @classmethod
    def send_notifications_channel(cls, user, notifications):
        logging.info("Sending channel notification to user: " + user.get().email)
        
        for n in notifications:
            event = n.event.get()
            message = { 'type': event.type,
                        'user': event.source.get().commissario.nomecompleto(Commissario.get_by_user(user.get())),
                        'source_id': event.source.urlsafe(),
                        'target_id': event.target.urlsafe(),
                        'ntfy_num': len(notifications)
                        }
            
            logging.info("Notification: " + str(event.type))
            if event.type == "post":
                message['source_desc'] = "messaggio"
                message['target_desc'] = event.target.get().name
            if event.type == "comment":
                message['source_desc'] = "commento"
                message['target_desc'] = event.target.get().title
            
            json_msg = json.dumps(message)
            
            Channel.send_message(user.get(), json_msg)
            
        
    @classmethod
    def send_notifications_email(cls, user, notifications):
        logging.info("Sending notification to user: " + user.get().email)
        for n in notifications:
            logging.info("Notification: " + str(n.event.get().type))
            
        template = jinja_environment.get_template("ntfctn/notifications_email.html")
        html=template.render({"cmsro":Commissario.get_by_user(user.get()), "notifications":notifications})
        test_emails = ['roberto.previtera@gmail.com',
                       'aiuto@pappa-mi.it',
                       'bob_previ@tahoo.com',
                       'muriel.verweij@gmail.com',
                       'roberto@pvri.com']
        if user.get().email in test_emails:
            mail.send_mail(sender="Pappa-Mi <aiuto@pappa-mi.it>",
            to=user.get().email,
            subject="[Pappa-Mi] Novità",
            body="",
            html=html
            )
        #logging.info(html)        

class NotificationHandler(BasePage):

    @classmethod
    def retrieve_new_notifications(cls, user_t, date):
        return SocialNotification.get_by_user_date(user_t, date)
                   

    @classmethod
    def retrieve_notifications(cls, user_t, start_cursor):
        return SocialNotification.get_by_user(user_t, cursor=start_cursor)

    @reguser_required
    def get(self):
        user=self.get_current_user()
        cmsro = self.getCommissario(user)
        
        template_values = {
                       'content': 'ntfctn/notifications.html',
                       'user':user,
                       'last_visit': cmsro.ultimo_accesso_notifiche,
                       'notify_list': self.retrieve_new_notifications(user.key, cmsro.ultimo_accesso_notifiche)
                       
                      }
        cmsro.ultimo_accesso_notifiche = datetime.now()
        cmsro.put()
        cmsro.set_cache()
        self.getBase(template_values)

    @reguser_required
    def post(self):
        user=self.get_current_user()
        cmsro = self.getCommissario(user)
        
        response = {'response': 'success', 
                    'ntfy_num': len(self.retrieve_new_notifications(user.key, cmsro.ultimo_accesso_notifiche))}
        self.output_as_json(response)

class NotificationPaginationHandler(BaseHandler):

    def get(self):
        return self.post()
    def post(self):
            cmd=self.request.get("cmd")
            user=self.request.user
            cursor=self.request.get("cursor")
            cmsro = None
            cmsro = self.getCommissario(user)
            if cmd=="notifications":
                start_cursor = None
                cursor = self.request.get("cursor")
                logging.info(start_cursor)
                if cursor != "":
                    start_cursor = Cursor(urlsafe=cursor)
                
                notlist, next_curs, more = NotificationHandler.retrieve_notifications(user.key, start_cursor=start_cursor)

                if not notlist:                 
                    response = {'response':'no_notifications'}
                    self.output_as_json(response)
                    return
               
                template = jinja_environment.get_template("ntfctn/notification_item.html")
               
                
                template_values={
                                 'notifications':notlist,
                                 'cmsro':self.getCommissario(user),
                                 'user':user.key
                                 }
                html=template.render(template_values)
                response = {'response':'success', 'html':html, 'eof': 'false'}
                logging.info("more " + str(more))
                if more:
                    response['cursor'] = next_curs.urlsafe()
                else:
                    response["eof"] = "true"
                self.output_as_json(response)

            if cmd=="ntfy_summary":
                start_cursor = None
                cursor = self.request.get("cursor")
                logging.info(start_cursor)
                if cursor != "":
                    start_cursor = Cursor(urlsafe=cursor)
                    
                notlist, next_curs, more = NotificationHandler.retrieve_notifications(user.key, start_cursor=start_cursor)
               
                cmsro = self.getCommissario(user)
                cmsro.ultimo_accesso_notifiche = datetime.now()
                cmsro.put()
                cmsro.set_cache()
                
                while len(notlist) > 10:
                    notlist.pop()
                
                if not notlist and not next_curs:                    
                    response = {'response':'no_notifications'}
                    self.output_as_json(response)
                    return
               
                template = jinja_environment.get_template("ntfctn/notification_short_item.html")
               
                
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

app = webapp.WSGIApplication([
    ('/ntfctn/paginate', NotificationPaginationHandler),
    ('/ntfctn', NotificationHandler),
    ('/event', EventHandler),
    ],                             
    debug = True, config=config)
