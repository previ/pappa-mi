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
  user = cmsro.usera.get() if cmsro else None
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
          'resource': resources_as_json(post),
          'images': post.images,
          'attachments': attachments_as_json(post),
          'votes': len(post.votes),
          'comments': post.comments,
          'canadmin': post.can_admin(user),
          'canvote': post.can_vote(user),
          'cancomment': post.can_comment(user)}

def comment_as_json(comment, cmsro):
  user = cmsro.usera.get() if cmsro else None
  return {'id': comment.key.urlsafe(),
          'author': {'id': str(comment.author.id()),
                     'name': comment.commissario.nomecompleto(cmsro),
                     'avatar': comment.commissario.avatar(cmsro)},
          'ext_date': comment.extended_date(),
          'content': comment.content,
          'votes': comment.votes}

def vote_as_json(vote, cmsro):
  user = cmsro.usera.get() if cmsro else None
  return {'id': vote.key.urlsafe(),
          'author': {'id': str(vote.author.id),
                     'name': vote.author.nomecompleto(cmsro),
                     'avatar': vote.author.avatar(cmsro)},
          }

def resources_as_json(post):
  resources = list()
  for r in post.resources:
    resources.append({'id': r.id(),
                      'desc': (r.get().title if r.get().restype == "post" else r.get().sommario()),
                      'url': '/post/'+post.id}) 
  return resources

def attachments_as_json(post):
  attachments = list()
  for a in post.attachments:
    att = {'id': a.key.id(),
           'desc': a.nome,
           'url': a.path}
    if a.isImage():
      att['imgthumb'] = a.imgthumb
    attachments.append(att) 
  return attachments

class UserApiHandler(BaseHandler):

  def get(self):
    user = self.get_current_user()
    user_api = {'id': 0,
                'fullname': 'Ospite',
                'type': 'O',
                'avatar': "/img/default_avatar.png",
                'city': 1364003,
                'schools': [{'id': 2212, 'name': 'Muzio Primaria'}]}
    if user:
      co = self.getCommissario()
      user_schools = list()
      for cm in co.commissioni():
        user_schools.append({'id': str(cm.key.id()),
                          'name': cm.desc()})
      user_api = {'id': str(co.usera.id()),
                  'fullname': str(co.nomecompleto(None,True)),
                  'firstname': str(co.nome),
                  'lastname': str(co.cognome),
                  'type': 'C' if co.stato == 1 else "G",
                  'avatar': str(co.avatar(co,48)),
                  'city': co.citta.id(),
                  'schools': user_schools}
    self.output_as_json(user_api)

  @reguser_required  
  def post(self):
    cmsro = self.getCommissario()
    userprofile = JSON.decode(self.request.get('userprofile'))
    if userprofile.get('firstname'):
      cmsro.nome = userprofile.get('firstname')
    if userprofile.get('lastname'):
      cmsro.cognome = userprofile.get('lastname')
      
    if userprofile.get('schools'):
      old = list()
      for cm in cmsro.commissioni():
        old.append(cm.key)
      old = set(old)

      new = list()
      for s in userprofile.get('schools'):
        new.append(model.Key("Commissione", int(s['id'])))
      new = set(new)

      todel = old - new
      toadd = new - old

      for cm_key in todel:
        commissione = cm_key.get()
        cmsro.unregister(commissione)
        node = SocialNode.get_by_resource(cm_key)[0]
        if node:
          node.unsubscribe_user(cmsro.usera.get())

      for cm_key in toadd:
        commissione = cm_key.get()
        cmsro.register(commissione)
        node = SocialNode.get_by_resource(cm_key)[0]
        if node:
          node.subscribe_user(cmsro.usera.get())
          if commissione.zona:
            nodes = SocialNode.get_by_name(commissione.citta.get().nome + " - Zona " + str(commissione.zona))
            if len(nodes) > 0:
              nodes[0].subscribe_user(cmsro.usera.get())


      cmsro.setCMDefault()
    cmsro.put()
    return self.get()
      

class NodeListApiHandler(BaseHandler):

  def get(self):
    user = self.get_current_user()
    user_nodes = list()
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
  
class UserOnlineListApiHandler(BaseHandler):

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

class MessageSendApiHandler(BaseHandler):

  @reguser_required
  def post(self):
    messages = memcache.get('Messages')
    if not messages:
      messages = dict()
    current_user = self.get_current_user()
    cmsro = self.getCommissario()
    user_id = self.request.get('user_id')
    message_text = self.request.get('message')
    logging.info('user_id: ' + str(user_id) + ' message: ' + message_text)
    users = list()
    if user_id:
      users.append(model.Key('User', int(user_id)).get())
      users.append(self.get_current_user())
    else:
      user_ids = memcache.get('OnlineUsers').keys() 
      for user_id in user_ids:
        users.append(model.Key('User', int(user_id)).get())
        
    for user in users: 
      message = { 'type': "message",
            'user': cmsro.nomecompleto(Commissario.get_by_user(user)),
            'body': message_text
            }
      messages[user.key.id()] = message
      json_msg = json.dumps(message)
      logging.info(json_msg)
      Channel.send_message(user, json_msg)
    memcache.set('Messages', messages)
    return
      
class MessageListApiHandler(BaseHandler):

  @reguser_required
  def get(self):
    messages = memcache.get('Messages')
    if messages:
      pass

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
    elif node_id=="all" and not user:
      postlist = list()
      next_curs=None
      more = False
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

    response = {'response':'success','post':post_as_json(post, cmsro)}    
    self.output_as_json(response)

  @reguser_required
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

    response = {'response':'success','post':post_as_json(post_key.get(), cmsro)}    
    self.output_as_json(response)

class PostVoteApiHandler(BaseHandler):

  @reguser_required
  def post(self, node_id, post_id):
    user = self.get_current_user()
    cmsro = self.getCommissario()
    post = SocialPost.get_by_key(model.Key("SocialNode", int(node_id), "SocialPost", int(post_id)))
    
    vote = int(self.request.get('vote'))
    post.vote(vote, user)
    
    response = {'response':'success', 'key': post.key.urlsafe(), 'votes':str(len(post.votes)), 'vote': vote}
    self.output_as_json(response)
  
  def get(self, node_id, post_id):
    post = SocialPost.get_by_key(model.Key("SocialNode", int(node_id), "SocialPost", int(post_id)))
    
    votes = list();
    for v in post.votes:
      votes.append(vote_as_json(v, self.getCommissario()))
      
    response = {'response':'success', 'votes': votes}
    self.output_as_json(response)
    

class PostCommentApiHandler(BaseHandler):

  def get(self, node_id, post_id):
    post = SocialPost.get_by_key(model.Key("SocialNode", int(node_id), "SocialPost", int(post_id)))
    
    comments = list();
    for c in post.comment_list:
      comments.append(comment_as_json(c, self.getCommissario()))
      
    response = {'response':'success', 'comments': comments}
    self.output_as_json(response)
      
  @reguser_required  
  def post(self, node_id, post_id):
    user = self.get_current_user()
    cmsro = self.getCommissario()
    post = SocialPost.get_by_key(model.Key("SocialNode", int(node_id), "SocialPost", int(post_id)))
    
    clean_content = Sanitizer.sanitize(self.request.get("content"))
    comment = post.create_comment(clean_content,user)

    EventHandler.startTask()
    
    response = {'response':'success', 'comments': [comment_as_json(comment, self.getCommissario())] }
    self.output_as_json(response)

class PostReshareApiHandler(BaseHandler):

  @reguser_required
  def post(self, node_id, post_id):
    user = self.get_current_user()
    cmsro = self.getCommissario()
    node=model.Key("SocialNode", int(self.request.get('node'))).get()
    post = SocialPost.get_by_key(model.Key("SocialNode", int(node_id), "SocialPost", int(post_id)))
    
    clean_title = Sanitizer.text(self.request.get("title"))
    clean_content = Sanitizer.sanitize(self.request.get("content"))

    rs_post_key=post.reshare(node.key,user,clean_content,clean_title)
    
    EventHandler.startTask()    

    response = {'response':'success','post':post_as_json(rs_post_key.get(), cmsro)}
    self.output_as_json(response)

class MenuApiHandler(CMMenuHandler):

  def get(self, school_id, date):

    menu_api = []
    data = datetime.strptime(date,Const.DATE_FORMAT).date()
    c = model.Key("Commissione", int(school_id)).get()
    menus = self.getMenu(data, c)
    if len(menus) > 0 and menus[0].primo.key:
      menu = menus[0]
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

class DishApiHandler(CMMenuHandler):

  def get(self, dish_id, school_id):
    details = dict()
    factors = {'Materna': 0.625,
               'Primaria': 0.875,
               'Secondaria': 1.0}
    factor = 1.0
    if school_id:
      cm = model.Key('Commissione', int(school_id)).get()
      factor = factors[cm.tipoScuola]
    piatto = model.Key("Piatto", int(dish_id)).get()
    details['dish'] = piatto.nome
    details['components'] = piatto.ingredienti(cm.tipoScuola)
    json.dump(details, self.response.out)

class CityListApiHandler(BaseHandler):

  def get(self):

    cities = memcache.get("City")
    if not cities:
      cities = list()
      cs = Citta.get_all()
      for c in cs:
        cities.append({'id': str(c.key.id()), 'name':c.nome})

      memcache.add("City", cities)

    self.output_as_json(cities)   
    return

class SchoolListApiHandler(BaseHandler):

  def get(self, city_id):

    schools = memcache.get("Schools-" + city_id)
    if not schools:
      schools = list()
      cms = Commissione.get_by_citta(model.Key('Citta', int(city_id)))
      for cm in cms:
        schools.append({'id': str(cm.key.id()), 'name':cm.nome + ' - ' + cm.tipoScuola})

      memcache.add("Schools-" + city_id, schools)

    self.output_as_json(schools)   
    return

class ConfigApiHandler(BaseHandler):

  def get(self):
    config = {'apihost': 'api.pappa-mi.it',
              'apiversion': '1.0',
              'appname': 'Pappa-Mi',
              'veespoproduction': 'YES'}
    self.output_as_json(config)

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
    ('/api/post/(.*)-(.*)/vote', PostVoteApiHandler),
    ('/api/post/(.*)-(.*)/comment', PostCommentApiHandler),
    ('/api/post/(.*)-(.*)/reshare', PostReshareApiHandler),
    ('/api/post/(.*)-(.*)', PostApiHandler),
    ('/api/post/create', PostApiHandler),
    ('/api/menu/(.*)/(.*)', MenuApiHandler),
    ('/api/dish/(.*)/(.*)', DishApiHandler),
    ('/api/user/online/list', UserOnlineListApiHandler),
    ('/api/message/send', MessageSendApiHandler),
    ('/api/message/list', MessageListApiHandler),
    ('/api/city/list', CityListApiHandler),    
    ('/api/school/(.*)/list', SchoolListApiHandler),    
    ('/api/config', ConfigApiHandler),
    ('/api/test', TestApiHandler),
  ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500

def main():
  app.run();

if __name__ == "__main__":
  main()
