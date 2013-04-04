import os
import cgi
import logging

import webapp2 as webapp

from base import BasePage, config

class ChannelHandler(BasePage):
    
  def post(self):
    client_id = self.request.get("from")
    logging.info(client_id + " " + self.request.path)


app = webapp.WSGIApplication([
    ('/_ah/channel/connected/', ChannelHandler),
    ('/_ah/channel/disconnected/', ChannelHandler),
    ],                             
    debug = True, config=config)

def main():
  app.run();

if __name__ == "__main__":
  main()
