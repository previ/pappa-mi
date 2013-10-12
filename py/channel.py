import os
import cgi
import logging
from datetime import date, datetime, time, timedelta

import webapp2 as webapp
from google.appengine.api import memcache

from base import BasePage, config

class ChannelConnectHandler(BasePage):

  def post(self):
    client_id = self.request.get("from")
    logging.info(client_id + " " + self.request.path)
    users = memcache.get('OnlineUsers')
    user_id = client_id.split('.')[1]
    
    if not users:
      users = dict()
    users[user_id] = datetime.now()
    memcache.set('OnlineUsers', users)
    

class ChannelDisconnectHandler(BasePage):

  def post(self):
    client_id = self.request.get("from")
    logging.info(client_id + " " + self.request.path)
    users = memcache.get('OnlineUsers', dict())
    user_id = client_id.split('.')[1]
    if not users:
      users = dict()
    if users.get(user_id):
      del users[user_id]
    memcache.set('OnlineUsers', users)

app = webapp.WSGIApplication([
    ('/_ah/channel/connected/', ChannelConnectHandler),
    ('/_ah/channel/disconnected/', ChannelDisconnectHandler),
    ], debug=os.environ['HTTP_HOST'].startswith('localhost'), config=config)


def main():
  app.run();

if __name__ == "__main__":
  main()
