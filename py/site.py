#!/usr/bin/env python
import os
import logging
import fixpath

import gdata.sites.client
import gdata.data

import StringIO

class Site:

  username = ""
  password = ""
  site = ""
  client = None

  def __init__(self, username, password, site):
    self.username = username
    self.password = password
    self.site = site
    self.client = gdata.sites.client.SitesClient(source='Pappa-Mi-1.0', domain="pappa-mi.it", site=site)
    self.client.ClientLogin(self.username, self.password, self.client.source);

  def uploadDoc(self, upload_data, upload_name, upload_type, path):

    uri = '%s?path=%s' % (self.client.MakeContentFeedUri(), path )

    feed = self.client.GetContentFeed(uri=uri)
    ms = gdata.data.MediaSource( file_handle=StringIO.StringIO(upload_data), content_length=len(upload_data), content_type=upload_type)
    attachment = self.client.UploadAttachment(ms, feed.entry[0], title=upload_name)
    logging.info( 'Uploaded. View it at: ' + attachment.GetAlternateLink().href)

    return attachment.GetAlternateLink().href
