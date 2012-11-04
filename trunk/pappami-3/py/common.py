#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import threading
import logging
from HTMLParser import HTMLParser

class Const:
  ACTIVITY_TIME_FORMAT = "%H:%M:%S"
  ACTIVITY_DATE_FORMAT = "%d/%m/%Y"
  TIME_FORMAT = "T%H:%M:%S"
  DATE_FORMAT = "%Y-%m-%d"
  ACTIVITY_FETCH_LIMIT = 20
  ENTITY_FETCH_LIMIT = 50
  ACTIVITY_CACHE_EXP = 900
  SOCIAL_FLOOD_TIME = 5
  FLOOD_SYSTEM_ACTIVATED = True

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
    
    