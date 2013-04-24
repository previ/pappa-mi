try:
  from xml.etree import ElementTree # for Python 2.5 users
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import gdata.alt.appengine
import atom
import getopt
import sys
import string
import time
import logging

class Calendario:
  calendar_service = None
  calendar = None

  def logon(self, user, password):
    self.calendar_service = gdata.calendar.service.CalendarService()
    self.calendar_service = gdata.alt.appengine.run_on_appengine(self.calendar_service, deadline=10)
    self.calendar_service.email = user
    self.calendar_service.password = password
    self.calendar_service.source = 'Pappa-Mi-1.0'
    self.calendar_service.ProgrammaticLogin()

  def printOwn(self):
    feed = self.calendar_service.GetOwnCalendarsFeed()
    print feed.title.text
    for i, a_calendar in enumerate(feed.entry):
      logging.info("calendar: " + a_calendar.title.text)

  def create(self, title):
    self.calendar = gdata.calendar.CalendarListEntry()
    self.calendar.title = atom.Title(text=title)
    self.calendar.summary = atom.Summary(text="Calendario Commissione Mensa " + title)
    self.calendar.where = gdata.calendar.Where(value_string='Milano')
    self.calendar.timezone = gdata.calendar.Timezone(value='Europe/Rome')
    self.calendar.hidden = gdata.calendar.Hidden(value='false')
    j = 3
    while True:
      if j < 1:
        logging.error("unable to insert calendar")
        break
      try:
        self.calendar = self.calendar_service.InsertCalendar(new_calendar=self.calendar)
      except gdata.service.RequestError, inst:
        thing = inst[0]
        if thing['status'] == 302:
          j = j - 1
          time.sleep(2.0)
          continue
        elif thing['status'] == 403:
          j = j - 1
          time.sleep(5.0)
          continue
        else:
          raise
      except:
        raise
      break
    if self.calendar.title.text != title:
      self.calendar.title = atom.Title(text=title)
      self.update()

  def update(self):
    j = 3
    while True:
      if j < 1:
        logging.error("unable to update calendar")
        break
      try:
        self.calendar = self.calendar_service.UpdateCalendar(calendar=self.calendar)
      except gdata.service.RequestError, inst:
        thing = inst[0]
        if thing['status'] == 302:
          j = j - 1
          time.sleep(2.0)
          continue
        elif thing['status'] == 403:
          j = j - 1
          time.sleep(5.0)
          continue
        else:
          raise
      except:
        raise
      break

  def load(self, calId):
    self.calendar = gdata.calendar.CalendarListEntry()
    self.calendar.id = atom.Id(text="https://www.google.com/calendar/feeds/default/allcalendars/full/"+calId)

  def share(self, user_email):
    rule = gdata.calendar.CalendarAclEntry()
    rule.scope = gdata.calendar.Scope(value=user_email, scope_type='user')
    roleValue = 'http://schemas.google.com/gCal/2005#%s' % ('editor')
    rule.role = gdata.calendar.Role(value=roleValue)
    aclUrl = "https://www.google.com/calendar/feeds/" + self.GetId() + "/acl/full"
    j = 3
    while True:
      if j < 1:
        logging.error("unable to share calendar to " + str(user_email))
        break
      try:
        returned_rule = self.calendar_service.InsertAclEntry(rule, aclUrl)
      except gdata.service.RequestError, inst:
        thing = inst[0]
        if thing['status'] == 302:
          j = j - 1
          time.sleep(2.0)
          continue
        elif thing['status'] == 403:
          j = j - 1
          time.sleep(5.0)
          continue
        else:
          raise
      except:
        raise
      break
    #logging.info(self.GetId())

  def unShare(self, user_email):
    uri = "http://www.google.com/calendar/feeds/" + self.GetId() + "/acl/full/user:" + user_email
    self.calendar_service.GetCalendarAclEntry(uri)
    j = 3
    while True:
      if j < 1:
        logging.error("unable to share calendar to " + str(user_email))
        break
      try:
        entry = self.calendar_service.GetCalendarAclEntry(uri)
        self.calendar_service.DeleteAclEntry(entry.GetEditLink().href)
      except gdata.service.RequestError, inst:
        thing = inst[0]
        if thing['status'] == 302:
          j = j - 1
          time.sleep(2.0)
          continue
        elif thing['status'] == 403:
          j = j - 1
          time.sleep(5.0)
          continue
        else:
          raise
      except:
        raise
      break
    #logging.info(self.GetId())

  def GetId(self):
    calId = self.calendar.id.text
    return calId[calId.find("/full/") + len("/full/"): len(calId)]
