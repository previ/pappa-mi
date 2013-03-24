#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import threading
import logging
import datetime
from HTMLParser import HTMLParser
import lxml.html
from lxml.html.clean import Cleaner


class Const:
  ACTIVITY_TIME_FORMAT = "%H:%M:%S"
  ACTIVITY_DATE_FORMAT = "%d/%m/%Y"
  TIME_FORMAT = "T%H:%M:%S"
  DATE_FORMAT = "%Y-%m-%d"
  ACTIVITY_FETCH_LIMIT = 5
  ENTITY_FETCH_LIMIT = 50
  ACTIVITY_CACHE_EXP = 900
  SOCIAL_FLOOD_TIME = 5
  FLOOD_SYSTEM_ACTIVATED = False
  BASE_RANK = datetime.datetime(2008, 1, 1)
  DAY_SECONDS = 86400
  ALLOWED_TAGS = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'code',
    'em',
    'i',
    'li',
    'ol',
    'strong',
    'ul',
    'img',
    'p',
    'div',
    'br',
]
  SEARCH_LIMIT = 20


class cached_property(object):
  """A decorator that converts a function into a lazy property.
  
  The function wrapped is called the first time to retrieve the result
  and then that calculated result is used the next time you access
  the value::
  
      class Foo(object):
  
          @cached_property
          def foo(self):
              # calculate something important here
              return 42
  """
  
  _default_value = object()
  
  def __init__(self, func, name=None, doc=None):
    self.__name__ = name or func.__name__
    self.__module__ = func.__module__
    self.__doc__ = doc or func.__doc__
    self.func = func
    self.lock = threading.RLock()
  
  def __get__(self, obj, type=None):
    if obj is None:
      return self
    if not hasattr(obj, "cache"):
      #logging.info("cache.init")
      obj.cache = dict()
  
    with self.lock:
      value = obj.cache.get(self.__name__, self._default_value)
      if value is self._default_value:
        #logging.info("cache.miss")
        value = self.func(obj)
        obj.cache[self.__name__] = value
  
      return value

  def __set__(self, obj, value):
    if obj is None:
      return self
    if not hasattr(obj, "cache"):
      obj.cache = dict()
  
    with self.lock:
      if value is None and obj.cache.get(self.__name__):
        del obj.cache[self.__name__]
  
      return value
  
  def invalidate(self, obj):
    del obj.cache[self.__name__]
    


# create a subclass and override the handler methods
class Parser(HTMLParser):    

  def handle_starttag(self, tag, attrs):
    pass

  def handle_endtag(self, tag):
    pass

  def handle_data(self, data):
    self.text += str(data)
    
class Cache(object):
  
  _all_caches = dict()
  _all_lock = threading.RLock()
  
  def __init__(self, cache_name, *args, **kwargs):
    self._lock = threading.RLock()
    self._cache = dict()
    self.name=cache_name
    Cache.put_cache(self.name, self)
    super(Cache, self).__init__(*args, **kwargs) 
    
  def get(self, name):
    return self._cache.get(name)
    
  def put(self, name, obj):
    with self._lock:    
      self._cache[name] = obj
    
  def clear(self, name):
    with self._lock:    
      if self._cache.get(name):
        del self._cache[name]

  def clear_all(self):
    with self._lock:    
      self._cache.clear()
    
  @classmethod
  def get_cache(cls,name):
    cache=cls._all_caches.get(name)
    if not cache:
      cache = Cache(name)
      cls.put_cache(name, cache)
    return cache

  @classmethod
  def put_cache(cls,name, cache):
    with cls._all_lock:
      cls._all_caches[name] = cache
 
  @classmethod
  def clear_all_caches(cls):
    with cls._all_lock:
      for cache in cls._all_caches.itervalues():
        cache.clear_all()
  
  
  
class Sanitizer(object):
  sanitizer = Cleaner(allow_tags=Const.ALLOWED_TAGS, remove_unknown_tags=False)  
  texter = Cleaner(allow_tags=[''],remove_unknown_tags=False)  
  
  @classmethod
  def sanitize(cls, html):
    sanitized = cls.sanitizer.clean_html(html) 
    return sanitized

  @classmethod
  def text(cls, html):
    text = lxml.html.fromstring(html).text_content()
    return text
  