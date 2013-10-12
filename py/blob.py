from __future__ import with_statement
from google.appengine.api import files

from py.base import *

import os
import cgi
import logging
import urllib
from datetime import date, datetime, time, timedelta
import wsgiref.handlers
import mimetypes

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers

class Blob:
    #file_name = None
    #blob_key = None
    #blob_reader = None
    #mime_type = None

    def create(self, filename):
        # Create the file
        self.mime_type = mimetypes.guess_type(filename)[0]
        if not self.mime_type:
            self.mime_type = "application/octet-stream"
        self.file_name = files.blobstore.create(mime_type=self.mime_type)

    def open(self,key):
        self.blob_key = key
        self.blob_reader = blobstore.BlobReader(self.blob_key)


    def write(self,data):
        # Open the file and write to it
        with files.open(self.file_name, 'a') as f:
            f.write(data)

        # Finalize the file. Do this before attempting to read it.
        files.finalize(self.file_name)

        # Get the file's blob key
        self.blob_key = files.blobstore.get_blob_key(self.file_name)

        return self.blob_key

    def read(self):
        # Open the file and write to it
        value = self.blob_reader.read()
        return value

    def mime(self):
        return self.mime_type
    
    def size(self):
        return blobstore.BlobInfo.get(self.blob_key).size

class BlobHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self):
        blob_key = self.request.get("key")
        #logging.info("blob_key: " + str(blob_key))
        blob_info = blobstore.BlobInfo.get(blob_key)
        if not blob_info:
            logging.info("blog.404")
            self.error(404)
        else:
            #logging.info("blog.200")
            self.send_blob(blob_info)


app = webapp.WSGIApplication([
    ('/blob/get', BlobHandler)], debug=os.environ['HTTP_HOST'].startswith('localhost'))

#app.error_handlers[404] = handle_404
#app.error_handlers[500] = handle_500

