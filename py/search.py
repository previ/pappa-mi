#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from py.base import *
import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
from google.appengine.ext.ndb import model

import webapp2 as webapp
from datetime import date, datetime, time, timedelta
from py.model import *

from common import Const, Cache, Sanitizer, Channel

class SearchHandler(BaseHandler):
  def post(self):
    postlist = list()
    found = 0
    offset = 0
    limit = Const.SEARCH_LIMIT
    try:
      query = self.request.get("query")

      if self.request.get("author"):
        query += " author:" + self.request.get("author")
      if self.request.get("node"):
        query += " node:" + self.request.get("node")
      if self.request.get("resources"):
        query += " resources:" + self.request.get("resources")
      if self.request.get("attach"):
        query += " attach:" + self.request.get("attach")
      if self.request.get("date_from"):
        query += " date>=" + self.request.get("date_from")
      if self.request.get("date_to"):
        query += " date<=" + self.request.get("date_to")
      if self.request.get("offset"):
        offset = int(self.request.get('offset'))

      logging.info("offset: " + str(offset))
      options = search.QueryOptions(
        limit=limit,
        offset=offset)

      results = search.Index(name="index-posts").search(search.Query(query_string=query, options=options))
      found = results.number_found

      for scored_document in results:
        post = model.Key(urlsafe=scored_document.doc_id[5:]).get()
        postlist.append(post)


    except search.Error:
        logging.exception('Search failed' )

    template_values = {
      "content": "search.html",
      "query": self.request.get("query"),
      "author": self.request.get("author"),
      "node": self.request.get("node"),
      "resources": self.request.get("resources"),
      "attach": self.request.get("attach"),
      "date_from": self.request.get("date_from"),
      "date_to": self.request.get("date_to"),
      "author": self.request.get("author"),
      "advanced": self.request.get("advanced"),
      "offset": offset,
      "lim": limit,
      "found": found,
      "postlist": postlist,
        }

    self.getBase(template_values)

  def get(self):
    limit = Const.SEARCH_LIMIT
    template_values = {
      "content": "search.html",
      "lim": limit,
        }

    self.getBase(template_values)

app = webapp.WSGIApplication([
  ('/search', SearchHandler),
  ],
  debug = os.environ['HTTP_HOST'].startswith('localhost'), config=config)
