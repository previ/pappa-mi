from __future__ import absolute_import

from apiclient.discovery import build
from engineauth.models import User
from engineauth.strategies.oauth2 import OAuth2Strategy
from google.appengine.api import memcache
import httplib2
import logging

class GoogleStrategy(OAuth2Strategy):

    @property
    def options(self):
        return {
            'provider': 'google',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://accounts.google.com/o/oauth2/token',
        }

    def service(self, **kwargs):
        name = kwargs.get('name', 'oauth2')
        version = kwargs.get('version', 'v2')
        return build(name, version, http=httplib2.Http(memcache))

    def user_info(self, req):
        user = self.service().userinfo().get().execute(self.http(req))
        logging.info("GoogleStrategy.2: " + user.get('id'))
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
                    },
                ],
            },
            'extra': {
                'raw_info': user,
                } 
            }
        return uinfo        
