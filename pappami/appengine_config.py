#!/usr/bin/env python
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import sys
ON_DEV = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
if 'lib' not in sys.path:
    sys.path[0:0] = ['lib']

if 'py' not in sys.path:
    sys.path[0:0] = ['py']

#########################################
# Remote_API Authentication configuration.
#
# See google/appengine/ext/remote_api/handler.py for more information.
# For datastore_admin datastore copy, you should set the source appid
# value.  'HTTP_X_APPENGINE_INBOUND_APPID', ['trusted source appid here']
#
remoteapi_CUSTOM_ENVIRONMENT_AUTHENTICATION = (
    'HTTP_X_APPENGINE_INBOUND_APPID', ['test-pappa-mi'])

#def webapp_add_wsgi_middleware(app):
    #from google.appengine.ext.appstats import recording
    #app = recording.appstats_wsgi_middleware(app)
    #return app
	

engineauth = {
    # Login uri. The user will be returned here if an error occures.
    'login_uri': '/', # default 'login/'
    # The user is sent here after successfull authentication.
    'success_uri': '/',
    'secret_key': 'CHANGE_TO_A_SECRET_KEY',
    # Change to provide a subclassed model
    'user_model': 'engineauth.models.User',
}

engineauth['provider.google'] = {
    'client_id': '610506648671.apps.googleusercontent.com',
    'client_secret': '_oIxbi9__8RR8mG8bl40dByM',
    'api_key': 'AIzaSyDK9TuhnLfxxE1h16ar_B6Gztb0bkmBSuQ',
    'scope': 'https://www.googleapis.com/auth/userinfo.email',
    }

engineauth['provider.github'] = {
    'client_id': '7c9a74ca5fd7bdb149c2',
    'client_secret': 'a6dbb9f8db8f881290db3bdc32c8f2ac3d5b2535',
    }

engineauth['provider.linkedin'] = {
    'client_id': 'jfsgpazuxzb2',
    'client_secret': 'LxGBTeCpQlb4Ad2R',
    }

engineauth['provider.twitter'] = {
    'client_id': 'l8nfb1saEW4mlTOARqunKg',
    'client_secret': 'LCQweRuuGndhtNWihnwiDxs9npkNRII8GAgpGkYFi5c',
    }


if ON_DEV:
    # Facebook settings for Development
    FACEBOOK_APP_KEY = '343417275669983'
    FACEBOOK_APP_SECRET = 'fec59504f33b238a5d7b5f3b35bd958a'
else:
    # Facebook settings for Production
    FACEBOOK_APP_KEY = '109551039166233'
    FACEBOOK_APP_SECRET = 'f929abbc0c5092164df693d047f880ec'

engineauth['provider.facebook'] = {
    'client_id': FACEBOOK_APP_KEY,
    'client_secret': FACEBOOK_APP_SECRET,
    'scope': 'email',
    }
    
def webapp_add_wsgi_middleware(app):
    from engineauth import middleware
    return middleware.AuthMiddleware(app)
