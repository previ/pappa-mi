#!/usr/bin/env python
#
# Copyright Pappa-Mi Org.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from py.base import *

import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import webapp2 as webapp

from google.appengine.ext.ndb import model
from google.appengine.api import memcache

from py.model import *
from event import EventHandler

def post_as_json(post, cmsro):
  return {'id': post.id,
          'author': {'id': str(post.author.id()),
                     'name': post.commissario.nomecompleto(cmsro),
                     'avatar': post.commissario.avatar(cmsro)},
          'node': {'id': str(post.key.parent().id()),
                   'name': post.key.parent().get().name},
          'ext_date': post.extended_date(),
          'title': post.title,
          'content_summary': post.content_summary,
          'content': post.content,
          'images': post.images}


class UserApiHandler(BasePage):

  @reguser_required
  def get(self):
    user = self.get_current_user()
    co = self.getCommissario()
    user_schools = list()
    for cm in co.commissioni():
      user_schools.append({'id': str(cm.key.id()),
                        'name': cm.desc()})
    user_api = {'id': str(co.usera.id()),
                'fullname': str(co.nomecompleto(None,True)),
                'schools': user_schools}
    self.output_as_json(user_api)


class NodeListApiHandler(BaseHandler):

  def get(self):
    user = self.get_current_user()
    subs = list()
    if user:
      subs = SocialNodeSubscription.get_nodes_by_user(user)

    user_nodes = list()
    for n in SocialNodeSubscription.get_nodes_by_user(user):
      user_nodes.append({'id': str(n.id),
                         'name': n.name})
    active_nodes = list()
    for n in SocialNode.get_most_active():
      active_nodes.append({'id': str(n.id),
                           'name': n.name})
    recent_nodes = list()
    for n in SocialNode.get_most_recent():
      recent_nodes.append({'id': str(n.id),
                           'name': n.name})

    response = {
      'subs_nodes': user_nodes,
      'active_nodes': active_nodes,
      'recent_nodes': recent_nodes,
      }

    self.output_as_json(response)
    
    return
  
class UserOnlineListApiHandler(BasePage):

  @reguser_required
  def get(self):
    cmsro = self.getCommissario()
    users_json = dict()
    users = memcache.get('OnlineUsers')
    if users:
      for u_i, u_t in users.iteritems():
        user = model.Key('User', int(u_i)).get()
        cmo = Commissario.get_by_user(user)
        users_json[u_i] = {'name': cmo.nomecompleto(cmsro),
                          'avatar': cmo.avatar(cmsro),
                          'last_connect': str(u_t)}
        if len(cmsro.commissioni()) > 0:
          users_json[u_i]['school'] = cmo.commissioni()[0].nome
        
    self.output_as_json(users_json)

class UserMessageApiHandler(BasePage):

  @reguser_required
  def post(self):
    current_user = self.get_current_user()
    cmsro = self.getCommissario()
    logging.info('message')
    user_id = self.request.get('user_id')
    message_text = self.request.get('message')
    users = list()
    if user_id:
      users.append(model.Key('User', int(user_id)).get())
    else:
      user_ids = memcache.get('OnlineUsers').keys() 
      for user_id in user_ids:
        if user_id != current_user.key.id():
          users.append(model.Key('User', int(user_id)).get())
        
    for user in users: 
      message = { 'type': "Message",
            'user': cmsro.nomecompleto(Commissario.get_by_user(user)),
            'message_text': message_text
            }
      json_msg = json.dumps(message)
      Channel.send_message(user, json_msg)
    
    return
      

class NodeApiHandler(BaseHandler):

  def get(self, node_id, cursor = None):
    node = None
    next_curs_key = ""
    more = False
    user = self.get_current_user()
    if node_id=="news":
      if not cursor or cursor == "undefined":
        postlist, next_curs, more = SocialPost.get_news_stream(page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
      else:
        postlist, next_curs, more = SocialPost.get_news_stream(page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=Cursor(urlsafe=cursor))
      if next_curs:
        next_curs_key = next_curs.urlsafe()
    elif node_id=="all" and user:
      if not cursor or cursor == "undefined":
        postlist, next_curs, more = SocialPost.get_user_stream(user=user, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
      else:
        postlist, next_curs, more = SocialPost.get_user_stream(user=user, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=cursor)
      next_curs_key = next_curs
    else:
      node=model.Key("SocialNode", int(node_id))

      if not cursor or cursor == "undefined":
        postlist, next_curs, more = SocialPost.get_by_node_rank(node=node, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=None)
      else:
        postlist, next_curs, more = SocialPost.get_by_node_rank(node=node, page=Const.ACTIVITY_FETCH_LIMIT, start_cursor=Cursor(urlsafe=cursor))
      if next_curs:
        next_curs_key = next_curs.urlsafe()

      if user and node.get().get_subscription(user.key):
        node.get().get_subscription(user.key).reset_ntfy()
    
    response =  { 'node_id': node_id,
                  'posts': [],
                  'next_cursor': next_curs_key
                 }
    cmsro = self.getCommissario()
    for post in postlist:
      response['posts'].append(post_as_json(post, cmsro))
    if user and node:
      user_subscription = node.get().get_subscription(user.key)
      subscription = {
        'can_admin': user_subscription.can_admin,
        'can_post': user_subscription.can_post,
        'can_comment': user_subscription.can_comment,       
      }
      response["subscription"]=subscription

    if not more:
      response['eof'] = 'true'
    self.output_as_json(response)

class PostApiHandler(BaseHandler):

  def get(self, node_id, post_id):
    cmsro = self.getCommissario()
    post = SocialPost.get_by_key(model.Key("SocialNode", int(node_id), "SocialPost", int(post_id)))
    response = post_as_json(post, cmsro)
    self.output_as_json(response)

  def post(self):
    user = self.get_current_user()
    cmsro = self.getCommissario()
    node=model.Key("SocialNode", int(self.request.get('node'))).get()

    if not node.get_subscription(user.key).can_post:
      logging.info("post not enabled")
      return
    
    clean_title = Sanitizer.text(self.request.get("title"))
    clean_content = Sanitizer.sanitize(self.request.get("content"))
    post_key=node.create_open_post(content=clean_content,title=clean_title,author=user)

    Allegato.process_attachments(self.request, post_key)

    EventHandler.startTask()

    response = post_as_json(post_key.get(), cmsro)
    self.output_as_json(response)

class MenuApiHandler(CMMenuHandler):

  @reguser_required
  def get(self, school_id, date):

    menu_api = []
    data = datetime.strptime(date,Const.DATE_FORMAT).date()
    c = model.Key("Commissione", int(school_id)).get()
    menus = self.getMenu(data, c)
    if len(menus):
      menu = self.getMenu(data, c)[0]
      menu_api = [
        { 'id': menu.primo.key.id(),
          'desc1': menu.primo.nome,
          'desc2': 'primo',
          'contents': menu.primo.ingredienti(c.tipoScuola) },
        { 'id': menu.secondo.key.id(),
          'desc1': menu.secondo.nome,
          'desc2': 'secondo',
          'contents': menu.secondo.ingredienti(c.tipoScuola)  },
        { 'id': menu.contorno.key.id(),
          'desc1': menu.contorno.nome,
          'desc2': 'contorno',
          'contents': menu.contorno.ingredienti(c.tipoScuola)  },
        { 'id': menu.dessert.key.id(),
          'desc1': menu.dessert.nome,
          'desc2': 'dessert',
          'contents': menu.dessert.ingredienti(c.tipoScuola)  }];

    self.output_as_json(menu_api)

class TestApiHandler(BaseHandler):

  @reguser_required
  def get(self):
    template_values = {
      'content': "apitest.html",
      'user': self.get_current_user(),
      'cmsro': self.getCommissario()
    }
    self.getBase(template_values)

  @reguser_required
  def post(self):
    return self.get()


app = webapp.WSGIApplication([
    ('/api/user/current', UserApiHandler),
    ('/api/node/list', NodeListApiHandler),
    ('/api/node/(.*)/stream/(.*)', NodeApiHandler),
    ('/api/post/(.*)-(.*)', PostApiHandler),
    ('/api/post/create', PostApiHandler),
    ('/api/menu/(.*)/(.*)', MenuApiHandler),
    ('/api/user/online/list', UserOnlineListApiHandler),
    ('/api/user/message', UserMessageApiHandler),
    ('/api/test', TestApiHandler),
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()
