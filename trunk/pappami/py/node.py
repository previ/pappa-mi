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
from gviz_api import *
from py.model import *
from py.blob import *

import py.PyRSS2Gen

from form import *
import base64
import time
from common import Const, Cache, Sanitizer, Channel

class NodeHandler(BaseHandler):

  def error(self):
        self.response.clear()
        self.response.set_status(404)
        template = jinja_environment.get_template('404_custom.html')
        c={"error": "Il nodo a cui stai provando ad accedere non esiste"}
        t = template.render(c)
        self.response.out.write(t)
        return

  def get(self,node_id):
      node=model.Key('SocialNode', long(node_id)).get()

      user=self.get_current_user()

      template_values = {
            'content': 'node/node.html',
            "cmsro":self.getCommissario(user),
            "user":user,
            "node":node,
            }

      self.getBase(template_values)

  def post(self, node_id):
      self.get(node_id)

class NodeListHandler(BaseHandler):

  def get(self):
    user = self.get_current_user()
    subs = list()
    if user:
        subs = SocialNodeSubscription.get_nodes_by_user(user)

    template_values = {
      'content': 'node/nodelist.html',
      'subs_nodes': subs,
      'active_nodes': SocialNode.get_most_active(),
      'recent_nodes': SocialNode.get_most_recent(),
      }

    self.getBase(template_values)

class NodeSubscribeHandler(BaseHandler):
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
                self.success({'subscribed': 'false'})
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

class NodeCreateHandler(BaseHandler):
    @reguser_required
    def get(self):
      template_values = {
        'content': 'node/createnode.html',
        "citta" : Citta.get_all(),

      }
      self.getBase(template_values)

    def post(self):
      node=SocialNode()
      node.name=Sanitizer.text(self.request.get("name"))
      node.description=Sanitizer.sanitize(self.request.get("description"))
      node.default_comment=bool(self.request.get("default_comment"))
      node.default_post=bool(self.request.get("default_post"))
      node.default_admin=bool(self.request.get("default_admin"))
      node.founder=self.get_current_user().key
      node.init_rank()
      logging.info(self.request.get("citta"))
      #node.resource=model.Key(urlsafe=self.request.get("citta")).get().create_resource().key

      node.put()

      self.redirect("/node/"+str(node.key.id()))


class NodeEditHandler(BaseHandler):
    def get(self,id):
      logging.info(str(id))
      node=model.Key("SocialNode", long(id)).get()
      if node is None or type(node) is not SocialNode:
        self.response.clear()
        self.response.set_status(404)
        template = jinja_environment.get_template('404_custom.html')
        c={"error": "Il post a cui stai provando ad accedere non esiste"}
        t = template.render(c)
        self.response.out.write(t)
        return

      template_values = {
                      "content": 'node/editnode.html',
                      "node":node,
                      "citta" : Citta.get_all(),

                      }

      self.getBase(template_values)

    def post(self,id):
      logging.info(id)
      node=model.Key("SocialNode", long(id)).get()

      node.name = Sanitizer.text(self.request.get("name"))
      node.description = Sanitizer.sanitize(self.request.get("description"))
      node.default_comment = bool(self.request.get("default_comment"))
      node.default_post = bool(self.request.get("default_post"))
      node.default_admin = bool(self.request.get("default_admin"))
      if self.request.get('city'):
        if self.request.get('city') != "0":
          node.set_resource('Citta', model.Key("Citta", int(self.request.get('city')))) 
        else:
          node.set_resource('Citta', None) 
      if self.request.get('cm'):
        node.set_resource('Commissione', model.Key("Commissione", int(self.request.get('cm'))))
      else:
        node.set_resource('Commissione', None) 

      Allegato.process_attachments(self.request, node.key)

      node.put()

      self.redirect("/node/"+str(node.key.id()))

class NodePaginationHandler(BaseHandler):

    def get(self):
        return self.post()
    def post(self):
            cmd=self.request.get("cmd")
            user=self.request.user
            cursor=self.request.get("cursor")
            cmsro = None
            cmsro = self.getCommissario(user)

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

                template = jinja_environment.get_template("node/node_item.html")

                html=template.render(template_values)
                response = {'response':'success','html':html,"cursor":next_curs.urlsafe()}
                self.output_as_json(response)

            if cmd=="node_main":
                node = None
                node_key_str = self.request.get("node")
                self.get_context()['node'] = node_key_str
                self.set_context()
                node_name = self.request.get("node_name")
                if node_key_str != "all" and node_key_str != "news":
                    node = model.Key(urlsafe=self.request.get("node")).get()
                    node_name = node.name


                template_values = {
                        "node":node,
                        "node_key":node_key_str,
                        "node_name":node_name,
                        "user": user,
                        "cmsro": cmsro,
                        "admin": users.is_current_user_admin()
                        }

                if node and user:
                    template_values["subscription"]=node.get_subscription(user.key)
                if user:
                    template_values["node_list"]=SocialNodeSubscription.get_nodes_by_user(user)

                template = jinja_environment.get_template("node/node_em.html")

                html=template.render(template_values)
                response = {'response':'success','html':html}
                self.output_as_json(response)

            if cmd=="search_nodes":
              nodes=[]
              if not cursor or cursor == "undefined":
                try:
                  results = search.Index(name="index-nodes").search(search.Query(query_string=self.request.get("query")))

                  for scored_document in results:
                    nodes.append(model.Key("SocialNode", long(scored_document.doc_id[5:])).get())

                except search.Error:
                  logging.exception('Search failed' )

              template_values = {
                      "nodelist":nodes,
                       }

              template = jinja_environment.get_template("node/node_item.html")
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


                template = jinja_environment.get_template("node/node_item.html")
                if nodes:
                    html=template.render(template_values)
                    response = {'html':html,


                              #cursor":next_curs.urlsafe()
                              }
                else:
                    response={'html':"",'list':[]}

                self.output_as_json(response)

class NodeFeedHandler(BasePage):

  def get(self, node_id):

    node=model.Key('SocialNode', long(node_id)).get()
    postlist, next_curs, more = SocialPost.get_by_node_rank(node=node.key, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
    items = list()

    for post in postlist:
      items.append(py.PyRSS2Gen.RSSItem(title = post.title,
                        description = post.content_summary,
                        guid = py.PyRSS2Gen.Guid("http://" + self.getHost() + "/post/" + str(node.key.id()) + "-" + str(post.key.id())),
                        pubDate = post.created.strftime("%a, %d %b %Y %H:%M:%S +0100")))


    rss = py.PyRSS2Gen.RSS2( title = "Pappa-Mi - " + node.name,
                             link = "http://" + self.getHost() + "/node/" + str(node.key.id()) + "/rss",
                             description = node.description,
                             items = items)

    expires_date = datetime.utcnow() + timedelta(1)
    expires_str = expires_date.strftime("%d %b %Y %H:%M:%S GMT")
    self.response.headers.add_header("Expires", expires_str)
    self.response.out.write(rss.to_xml())

app = webapp.WSGIApplication([
  ('/node/create', NodeCreateHandler),
  ('/node/edit/(.*)', NodeEditHandler),
  ('/node/list', NodeListHandler),
  ('/node/paginate', NodePaginationHandler),
  ('/node/subscribe', NodeSubscribeHandler),
  ('/node/(.*)/rss', NodeFeedHandler),
  ('/node/(.*)', NodeHandler),
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
