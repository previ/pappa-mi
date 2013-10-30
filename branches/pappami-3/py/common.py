#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import threading
import logging
from datetime import timedelta, tzinfo, datetime
from HTMLParser import HTMLParser
import lxml.html
from lxml.html.clean import Cleaner
from google.appengine.api import channel, memcache


class Const:
  ACTIVITY_TIME_FORMAT = "%H:%M:%S"
  ACTIVITY_DATE_FORMAT = "%d/%m/%Y"
  TIME_FORMAT = "T%H:%M:%S"
  DATE_FORMAT = "%Y-%m-%d"
  ACTIVITY_FETCH_LIMIT = 10
  ENTITY_FETCH_LIMIT = 50
  ACTIVITY_CACHE_EXP = 900
  SOCIAL_FLOOD_TIME = 5
  FLOOD_SYSTEM_ACTIVATED = False
  BASE_RANK = datetime(2008, 1, 1)
  DAY_SECONDS = 86400
  EVENT_PROC_LIMIT=2
  EVENT_PROC_NODE_SUB_LIMIT = 200
  EVENT_PROC_NTFY_LIMIT = 100
  ALLOWED_TAGS = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'code',
    'em',
    'i',
    'iframe',
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
  EVENT = True
  EMAIL_ADDR_MAIN = "'Pappa-Mi' <aiuto@pappa-mi.it>"
  EMAIL_ADDR_NOTIFICATION = "'Pappa-Mi - Notifiche' <aiuto@pappa-mi.it>"


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
      obj.cache = dict()

    with self.lock:
      value = obj.cache.get(self.__name__, self._default_value)
      if value is self._default_value:
        value = self.func(obj)
        obj.cache[self.__name__] = value

      return value

  def __set__(self, obj, value):
    if obj is None:
      return self
    if not hasattr(obj, "cache"):
      obj.cache = dict()

    with self.lock:
      if value is None and obj.cache.get(self.__name__) is not None:
        del obj.cache[self.__name__]

      return value


class memcached_property(object):
  """A decorator that converts a function into a lazy property.

  The function wrapped is called the first time to retrieve the result
  and then that calculated result is used the next time you access
  the value::

      class Foo(object):

          @memcached_property
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

    with self.lock:
      value = memcache.get(str(obj.id) + "-" + self.__name__)
      if value is None:
        value = self.func(obj)
        memcache.set(str(obj.id) + "-" + self.__name__, value)

      return value

  def __set__(self, obj, value):
    if obj is None:
      return self

    with self.lock:
      if value is None and memcache.get(str(obj.id) + "-" + self.__name__) is not None:
        memcache.delete(str(obj.id) + "-" + self.__name__)

      return value

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
    self.name=cache_name
    self._lock = threading.RLock()
    self._cache = dict()
    self._version = memcache.get(self.name + "-version")
    if not self._version:
      memcache.set(self.name + "-version", 0)
      self._version = 0
    Cache.put_cache(self.name, self)
    super(Cache, self).__init__(*args, **kwargs)

  def get(self, name):
    return self._cache.get(name)

  def put(self, name, obj):
    with self._lock:
      self._cache[name] = obj
      #self._version += 1
      #memcache.incr(self.name + "-version") #non è necessario invalidare la cache su una put, la versione va gestita in modo esplicito 

  def clear(self, name):
    with self._lock:
      if self._cache.get(name):
        del self._cache[name]
        self._version += 1
        memcache.incr(self.name + "-version")

  def clear_all(self):
    with self._lock:
      self._cache.clear()
      self._version += 1
      memcache.incr(self.name + "-version")

  def check_version(self):
    global_version = memcache.get(self.name + "-version")
    return self._version != global_version

  @classmethod
  def get_cache(cls,name):
    cache=cls._all_caches.get(name)
    if not cache or cache.check_version():
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
  sanitizer = Cleaner(allow_tags=Const.ALLOWED_TAGS, remove_unknown_tags=False, embedded=False, frames=False)
  texter = Cleaner(allow_tags=[''],remove_unknown_tags=False)

  @classmethod
  def sanitize(cls, html):
    sanitized = ""
    if html and len(html) > 0:
      sanitized = cls.sanitizer.clean_html(html)
    return sanitized

  @classmethod
  def text(cls, html):
    text = ""
    if html and len(html) > 0:
      text = lxml.html.fromstring(html).text_content()
    return text

  @classmethod
  def images(cls, html):
    images = list()
    try:
      for img in lxml.html.fromstring(html).iter('img'):
        #logging.info(str(img))
        images.append(img.get('src'))
    except Exception:
      pass

    return images


class Channel(object):

  @classmethod
  def get_by_user(cls, user):
    #channel_key = 'pappa-mi.' + str(user.key.id())
    #channel = memcache.get(channel_key)
    #if not channel:
      #channel = channel.create_channel('pappa-mi.' + str(user.key.id()), duration_minutes=30)
      #memcache.add('pappa-mi.' + str(user.key.id(), channel), 1800)
    if not hasattr(user, "channel"):
      user.channel = channel.create_channel('pappa-mi.' + str(user.key.id()))
    return user.channel

  @classmethod
  def send_message(cls, user, message):
    channel.send_message('pappa-mi.' + str(user.key.id()), message)

ZERO = timedelta(0)
HOUR = timedelta(hours=1)

# Last Sunday in March, which is the first Sunday on or after Mar 24.
DSTSTART_CET = datetime(1, 3, 24, 2)
# and ends at 2am (DST time; 1am standard time) on the last Sunday of Oct.
DSTEND_CET = datetime(1, 10, 24, 1)

def first_sunday_on_or_after(dt):
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += timedelta(days_to_go)
    return dt

class CETimeZone(tzinfo):

    def __init__(self):
        self.stdoffset = timedelta(hours=1) #GMT+1
        self.reprname = "Europe/Rome"
        self.stdname = "CET"
        self.dstname = "CET"

    def __repr__(self):
        return self.reprname

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return ZERO
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.

        start = first_sunday_on_or_after(DSTSTART_CET.replace(year=dt.year))
        end = first_sunday_on_or_after(DSTEND_CET.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return HOUR
        else:
            return ZERO
