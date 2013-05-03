from __future__ import absolute_import

from apiclient.discovery import build
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import httplib2
from urllib import urlencode
import json
import logging

class WindowsliveStrategy(OAuth2Strategy):

    @property
    def options(self):
        return {
            'provider': 'windowslive',
            'site_uri': 'https://apis.live.net/v5.0/me',
            'auth_uri': 'https://oauth.live.com/authorize',
            'token_uri': 'https://oauth.live.com/token',
        }

    def user_info(self, req):
        url = "https://apis.live.net/v5.0/me?{0}"# + urlencode({'access_token':req.credentials.access_token})
        #logging.info("live.1: " + url.format(urlencode({'access_token':req.credentials.access_token})))
        #res, results = self.http(req).request(url)
        results = urlfetch.fetch(url.format(urlencode({'access_token':req.credentials.access_token}))).content
        #logging.info("live.2")
        #logging.info("live.3: " + res)
        #if res.status is not 200:
        #    return self.raise_error('There was an error contacting Windows Live. '
        #                            'Please try again.')
        #logging.info("live.4: " + results)
        user = json.loads(results)
        auth_id = User.generate_auth_id(req.provider, user['id'])
        
        uinfo = {
            'auth_id': auth_id,
            'info': {
                'id': user['id'],
                'displayName': user.get('name'),
                'name': {
                    'givenName': user.get('first_name'),
                    'familyName': user.get('last_name'),
                },                
                'image': {
                    'url': ""#user.get('picture'),
                },
                'emails': [
                    {
                        'value': user.get('emails').get('preferred'),
                        'verified': True # email
                    },
                ],
            },
            'extra': {
                'raw_info': user,
                } 
            }
        return uinfo        
