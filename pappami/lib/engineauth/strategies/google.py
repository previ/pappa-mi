from __future__ import absolute_import

from apiclient.discovery import build
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy
from google.appengine.api import memcache
import httplib2
import json
import logging

class GoogleStrategy(OAuth2Strategy):

    @property
    def options(self):
        return {
            'provider': 'google',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
        }

    def user_info(self, req):
        url = "https://www.googleapis.com/oauth2/v1/userinfo?access_token=" +\
              req.credentials.access_token
        res, results = self.http(req).request(url)
        if res.status is not 200:
            return self.raise_error('There was an error contacting Google. '
                                    'Please try again.')
        user = json.loads(results)
        auth_id = User.generate_auth_id('google', user['id'], 'userinfo')
        
        uinfo = {
            'auth_id': auth_id,
            'info': {
                'id': user['id'],
                'displayName': user.get('name'),
                'givenName': user.get('given_name'),
                'familyName': user.get('family_name'),
                'image': {
                    'url': user.get('picture'),
                },
                'emails': [
                    {
                        'value': user.get('email'), # email
                        'verified': True # email                        
                    },
                ],
            },
            'extra': {
                'raw_info': user,
                } 
            }

        return uinfo        
