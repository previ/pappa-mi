import cloudstorage as gcs

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

class BlobCloud:

    bucket_name = "/" + app_identity.get_default_gcs_bucket_name()
    server_base_url = "http://storage.googleapis.com"

    def create(self, blob_name, filename_orig, content_type):
		self.blob_name = blob_name
		self.filename_orig = filename_orig
		self.content_type = content_type
		
		write_retry_params = gcs.RetryParams(backoff_factor=1.1)
		self.gcs_file = gcs.open((self.bucket_name + self.blob_name).encode('utf8'),
							'w',
							content_type=content_type,
							options={ 'x-goog-acl': 'public-read', 'x-goog-meta-filename': filename_orig.encode('utf8')},
							retry_params=write_retry_params)
		return blob_name
 
    def open(self, blob_name):
		self.blob_name = blob_name
		blob_stat = gcs.stat(self.bucket_name + self.blob_name)
		self.filename_orig = blob_stat.metadata["x-goog-meta-filename"]
		self.content_type = blob_stat.content_type
		self.blob_size = blob_stat.st_size
		self.gcs_file = gcs.open(self.bucket_name + blob_name, 'r')

    def write(self, data):
		self.gcs_file.write(data)
		self.gcs_file.close()

    def read(self):
		data = [self.blob_size]
		self.gcs_file.read(data)
		self.gcs_file.close()
		return data

    def content_type(self):
        return self.content_type
    
    def size(self):
        return self.blob_size

    def get_blob_key(self):
        key = blobstore.create_gs_key("/gs" + self.bucket_name + self.blob_name)
        return blobstore.BlobKey(key)
		            
    @classmethod
    def get_serving_url(cls, key="", name="", size=None):
        if size:
            return images.get_serving_url(blob_key=key, size=size)
        else:
            return cls.server_base_url + str(cls.bucket_name) + str(name)
            #return "/blob/" + str(key)

class BlobHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, key):
        logging.info("key: " + key)
        blob_info = blobstore.BlobInfo.get(key)
        if not blob_info:
            logging.info("blog.404")
            self.error(404)
        else:
            #logging.info("blog.200")
            self.send_blob(blob_info)


app = webapp.WSGIApplication([
    ('/blob/(.*)', BlobHandler)], debug=os.environ['HTTP_HOST'].startswith('localhost'))


