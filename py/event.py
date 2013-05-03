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
from google.appengine.ext.ndb import model, Future, toplevel
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
  
  @toplevel
  def get(self):
    logging.info("EventHandler")
    if self.request.get("cmd") == "clear":
      cursor = None
      while True:
        cursor = self.clear_events(cursor)
        if not cursor:
          break;
    elif self.request.get("cmd") == "process":
      job = {}
      if self.request.get("event_cursor"):
        job.update(self.request.GET.items())
      else:
        job = {'event_cursor':None}
      job = self.process_events(job)
      logging.info("event_cursor: " + str(job.get("event_cursor")))
      if job.get("event_more"):
        self.putTask('/event', job=job)
      else:
        if self.process_notifications():
          #more notifications to process
          self.putTask('/event', job=job)

    else:
      self.startTask()

    Cache.get_cache("SocialNotification").clear_all()

    self.success()

  @classmethod
  def startTask(cls):
    cls.putTask('/event', job={})

  @classmethod
  def putTask(cls, aurl, job):
    params = {'cmd': 'process'}
    params.update(job)
    task = Task(url=aurl, params=params, method="GET")
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
    logging.info("process events: " + str(job))
    event_cursor = None
    if job.get('event_cursor') and job.get('event_cursor') != "None":
      event_cursor = Cursor(urlsafe=job['event_cursor'])

    event_batch_processed = True
    events, event_next_cursor, event_more = SocialEvent.get_by_status(0, event_cursor, limit=Const.EVENT_PROC_LIMIT)
    e_futures = list()
    n_futures = list()
    for e in events:
      logging.info("event: " + e.type)
      if e.type==SocialEvent.new_post:
        node_cursor = None
        if job.get('node_cursor_' + str(e.target.id())):
          node_cursor = Cursor(urlsafe=job.get('node_cursor_' + str(e.target.id())))
        ns, ns_next_cursor, ns_more = SocialNodeSubscription.get_by_node(e.target, cursor=node_cursor, limit=Const.EVENT_PROC_NODE_SUB_LIMIT)
        #opti
        s_futures = list()
        for s in ns:
          #logging.info("subs.user: " + s.user.get().email + " e.user: " + e.user.get().email)
          if e.user != s.user:
            #logging.info("new_post.created")
            #opti
            n_futures.append(SocialNotification.create(e.key, s.user))
            s.has_ntfy = True
            s.ntfy += 1
            #s.put()
            #opti
            s_futures.append(s.put_async())
        
        Future.wait_all(s_futures)

        if ns_more:
          logging.info("node_cursor " + str(e.target.id()) + " " + str(ns_next_cursor) + " more")
          job['node_cursor_' + str(e.target.id())] = ns_next_cursor.urlsafe()
          event_batch_processed = False
        else:
          logging.info("node_cursor " + str(e.target.id()) + " no more")
          if job.get('node_cursor_' + str(e.target.id())):
            del job['node_cursor_' + str(e.target.id())]
          e.status = 1
          #opti
          #e.put()
          e_futures.append(e.put_async())
          
      if e.type==SocialEvent.new_comment:
        #logging.info("new_comment")
        
        #opti
        s_futures = list()
        for s in SocialPostSubscription.get_by_post(e.target):
          if e.user != s.user:
            #logging.info("new_comment.created")
            #opti
            n_futures.append(SocialNotification.create(e.key, s.user))
            s.has_ntfy = True
            #s.put()
            #opti
            s_futures.append(s.put_async()) 
        
        Future.wait_all(s_futures)
        
        e.status = 1
        #opti
        #e.put()
        e_futures.append(e.put_async())

    Future.wait_all(e_futures)
    Future.wait_all(n_futures)
    
    job['event_more'] = event_more or not event_batch_processed
    if event_batch_processed and event_more:
      logging.info("event_cursor more")
      job['event_cursor'] = event_next_cursor.urlsafe()
    if event_batch_processed and not event_more and job.get('event_cursor'):
      logging.info("event_cursor no more")
      del job['event_cursor']

    return job

  @classmethod
  def clear_events(cls, cursor):
    results, next_cursor, more = SocialEvent.get_by_status(0, cursor)
    for n in SocialNotification.get_by_date(date=None):
      n.key.delete()
    return None


  @classmethod
  def process_notifications(cls, job={}):
    logging.info("process_notifications")
    user_ntfy = dict()
    #Node Subscription
    count = 0
    limit = Const.EVENT_PROC_NTFY_LIMIT
    more = False
    ns = SocialNodeSubscription.get_by_ntfy()
    #opti
    s_futures = list()
    for sub in ns:
      #logging.info("SocialNodeSub")
      notifications = user_ntfy.get(sub.user)
      if notifications is None:
        notifications = list()
        user_ntfy[sub.user] = notifications
      nt = SocialNotification.get_by_user_status(sub.user, SocialNotification.status_created)
      #opti
      n_futures = list()
      for ntfy in nt:
        notifications.append(ntfy)
        ntfy.status = SocialNotification.status_notified
        #ntfy.put()
        #opti
        n_futures.append(ntfy.put_async())
        count += 1
        if count > limit:
          more = True
          break
      #opti
      Future.wait_all(n_futures)
      if count > limit:
        break
      sub.has_ntfy = False
      sub.last_ntfy_sent = datetime.now()
      s_futures.append(sub.put_async())
    
    Future.wait_all(s_futures)

    #Post Subscriptions
    for sub in SocialPostSubscription.get_by_ntfy():
      #logging.info("SocialPostSub")
      notifications = user_ntfy.get(sub.user)
      if notifications is None:
        notifications = list()
        user_ntfy[sub.user] = notifications
      #opti
      n_futures = list()
      for ntfy in SocialNotification.get_by_user_status(sub.user, SocialNotification.status_created):
        notifications.append(ntfy)
        ntfy.status = SocialNotification.status_notified
        #ntfy.put()
        #opti
        n_futures.append(ntfy.put_async())
        count += 1
        if count > limit:
          more = True
          break
      #opti
      Future.wait_all(n_futures)  
      if count > limit:
        break
      sub.has_ntfy = False
      #sub.put()
      s_futures.append(sub.put_async())
      
    Future.wait_all(s_futures)

    logging.info("user_ntfy.len: " + str(len(user_ntfy)))
    for user in user_ntfy:
      notifications = user_ntfy.get(user)
      if len(notifications) > 0:
        cls.send_notifications_channel(user, notifications)
        cls.send_notifications_email(user, notifications)
      else:
        logging.info("user: " + user.get().email + " has no notifications")
    return more


  @classmethod
  def send_notifications_channel(cls, user, notifications):
    logging.info("Sending channel notification to user: " + user.get().email)

    for n in notifications:
      event = n.event.get()
      message = { 'type': event.type,
            'user': event.source.get().commissario.nomecompleto(Commissario.get_by_user(user.get())),
            'ntfy_num': len(notifications)
            }

      #logging.info("Notification: " + str(event.type))
      if event.type == "post":
        #message['source_id'] = str(event.source.parent().id())+"-"+str(event.source.id())
        message['source_uri'] = "/post/" + str(event.source.parent().id())+"-"+str(event.source.id())
        message['source_desc'] = "messaggio"
        #message['target_id'] = str(event.target.id())
        message['target_uri'] = "/node/" + str(event.target.id())
        message['target_desc'] = event.target.get().name
      if event.type == "comment":
        #message['source_id'] = str(event.source.parent().parent().id())+"-"+str(event.source.parent().id())+"#"+str(event.source.id())
        message['source_uri'] = "/post/" + str(event.source.parent().parent().id())+"-"+str(event.source.parent().id())+"#"+str(event.source.id())
        message['source_desc'] = "commento"
        #message['target_id'] = str(event.target.parent().id())+"-"+str(event.target.id())
        message['target_uri'] = "/post/" + str(event.target.parent().id())+"-"+str(event.target.id())
        message['target_desc'] = event.target.get().title

      json_msg = json.dumps(message)

      Channel.send_message(user.get(), json_msg)


  @classmethod
  def send_notifications_email(cls, user, notifications):
    logging.info("Sending mail notification to user: " + user.get().email)
    for n in notifications:
      logging.info("Notification: " + str(n.event.get().type))

    template = jinja_environment.get_template("ntfctn/notifications_email.html")
    logging.info("host: " + str(cls.host()))
    host = cls.host()
    html=template.render({"cmsro":Commissario.get_by_user(user.get()), "notifications":notifications, "host": host})
    
    test_emails = ['roberto.previtera@gmail.com',
           'aiuto@pappa-mi.it',
           'bob_previ@tahoo.com',
           'muriel.verweij@gmail.com',
           'roberto@pvri.com']
    
    if host == "www.pappa-mi.it" or user.get().email in test_emails:
      mail.send_mail(sender=Const.EMAIL_ADDR_NOTIFICATION,
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
      user=self.get_current_user()
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
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
