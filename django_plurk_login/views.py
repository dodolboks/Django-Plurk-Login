import datetime
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect, HttpResponse
import random
from urllib2 import urlopen
import urllib
from models import PlurkUser
import oauth2 as oauth
from django.utils import simplejson as json
from django.utils.encoding import smart_str
import re

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

from mongoengine.django.auth import User
from django.contrib.auth import authenticate, logout as auth_logout
import urlparse
from cgi import parse_qs

OAUTH_REQUEST_TOKEN = 'http://www.plurk.com/OAuth/request_token'
OAUTH_ACCESS_TOKEN = 'http://www.plurk.com/OAuth/access_token'
AUTH_AUTHORIZE_URL = 'http://www.plurk.com/OAuth/authorize?oauth_token=%s'
OAUTH_REQUEST_TOKEN_URL = 'http://www.plurk.com/OAuth/request_token'
OAUTH_ACCESS_TOKEN_URL = 'http://www.plurk.com/OAuth/access_token'

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
REDIRECT_FIELD_NAME = 'next'


def login(request, user, apps, token=None):
    if user is None:
        user = request.user

    
    user.last_login = datetime.datetime.now()
    user.save()

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            request.session.flush()
    else:
        request.session.cycle_key()

    request.session[SESSION_KEY] = user.id
    request.session[BACKEND_SESSION_KEY] = user.backend
    if hasattr(request, 'user'):
        request.user = user


def _get_next(request):
    """
    Returns a url to redirect to after the login
    """
    if 'next' in request.session:
        next = request.session['next']
        del request.session['next']
        #return next
    elif 'next' in request.GET:
        next = request.GET.get('next')
    elif 'next' in request.POST:
        next =  request.POST.get('next')
    else:
        next = '/' #getattr(settings, 'LOGIN_REDIRECT_URL', '/')

    if next is None:
       return '/'
    else:
       return next
    
def hapus_plurk(request):
    user = request.user
    if user.is_authenticated():
         social_profile = PlurkUser.objects.get(user=user)
         social_profile.delete()
       return HttpResponseRedirect("/user/edit/")


def plurk_token(request):
    request.session['next'] = _get_next(request)
    consumer = oauth.Consumer(settings.PLURK_APP_KEY, settings.PLURK_APP_SECRET)
    client = oauth.Client(consumer)
    params = { 'oauth_signature_method': 'HMAC-SHA1',
				   'oauth_nonce': oauth.generate_nonce(),
				   'oauth_timestamp': oauth.generate_timestamp() }
    req = oauth.Request.from_consumer_and_token(consumer=consumer,
	http_method='GET', http_url=OAUTH_REQUEST_TOKEN,
	parameters=params, is_form_encoded=True)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)
    response, content = client.request(OAUTH_REQUEST_TOKEN, method='GET', headers=req.to_header())
    #request.session['request_token'] = dict(parse_qsl(content))
    content = dict(parse_qsl(content))
    request.session['request_token'] = content
    go = 'http://www.plurk.com/OAuth/authorize?oauth_token=%s' % content['oauth_token']
    return HttpResponseRedirect(go) 

def get_access_token(request):
        oauth_token = request.session['request_token']['oauth_token']
        oauth_token_secret = request.session['request_token']['oauth_token_secret']
        oauth_verifier = request.GET.get('oauth_verifier')
        consumer = oauth.Consumer(settings.PLURK_APP_KEY, settings.PLURK_APP_SECRET)
        token = oauth.Token(oauth_token, oauth_token_secret)
        client = oauth.Client(consumer, token)
        params = {
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': oauth.generate_timestamp(),
            'oauth_token': oauth_token,
            'oauth_token_secret': oauth_token_secret,
            'oauth_verifier': oauth_verifier,
        }
        req = oauth.Request.from_consumer_and_token(consumer=consumer, 
              token=token, http_method='POST', http_url=OAUTH_ACCESS_TOKEN_URL, 
              parameters=params, is_form_encoded=True)
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)

        response, content = client.request(OAUTH_ACCESS_TOKEN_URL, method='POST', 
                            headers=req.to_header())
        content = dict(parse_qsl(content))
        print content
        del request.session['request_token']
        url = 'http://www.plurk.com/APP/Profile/getOwnProfile' 
        return getUsers(request, url, content['oauth_token'], content['oauth_token_secret']) 


def _get(url, oauth_token, oauth_token_secret):
        consumer = oauth.Consumer(settings.PLURK_APP_KEY, settings.PLURK_APP_SECRET)
        token = oauth.Token(oauth_token, oauth_token_secret)
        client = oauth.Client(consumer, token)
        params = {
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': oauth.generate_timestamp(),
            'oauth_token': oauth_token
        }

        req = oauth.Request.from_consumer_and_token(consumer=consumer, 
              token=token, http_method='GET', http_url=url, parameters=params)
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)

        response, content = client.request(url, method='GET', headers=req.to_header())

        return content


def getUsers(request, api_url, oauth_token, oauth_token_secret):
    consumer = oauth.Consumer(settings.PLURK_APP_KEY, settings.PLURK_APP_SECRET)
    token = oauth.Token(oauth_token, oauth_token_secret)
    client = oauth.Client(consumer, token)
    params = { 'oauth_signature_method': 'HMAC-SHA1',
				   'oauth_nonce': oauth.generate_nonce(),
				   'oauth_timestamp': oauth.generate_timestamp(),
				   'oauth_token': oauth_token }
    req = oauth.Request.from_consumer_and_token(consumer=consumer, token=token,
				   http_method='GET', http_url=api_url, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
    #response, content = client.request(api_url, method=method, headers=req.to_header())
    #content = dict(parse_qsl(content))
    response, content = client.request(api_url, method='GET', headers=req.to_header())
    #if response['status'] != '200':
     #  raise Exception(content)

    content = json.loads(content)
    content = content["user_info"]
    user = request.user
    if user.is_authenticated():
       try:
           dono = PlurkUser.objects.get(username=content["nick_name"])
           return HttpResponse("mohon maap akun sudah di daftarkan")
       except PlurkUser.DoesNotExist:
           plurk = PlurkUser(username=content["nick_name"].lower())
           plurk.user_id = str(content["id"])
           plurk.user = request.user
           plurk.oauth_token = oauth_token
           plurk.oauth_secret = oauth_token_secret
           plurk.save()
       return HttpResponseRedirect(_get_next(request)) 
    else:
      try:
          plurk_user = PlurkUser.objects.get(username=content["nick_name"])
          user = plurk_user.authenticate()
          login(request, user, 'plurk')
          return HttpResponseRedirect(_get_next(request))
                 
      except PlurkUser.DoesNotExist:
        username = content["nick_name"].lower()
        username =  re.sub(r'([^a-zA-Z0-9_-]*)', '', username)
        try:   
          User.objects.get(username=username)
          d = User.objects.only('username')
          while True:
            ran = random.randint(0, 1000)
            username = username+str(ran)
            if not username in d:
               break
        except User.DoesNotExist:
            pass

        user = User(username=username)
        if user.display_name is None:  
              user.display_name = content["full_name"]     

        user.display_name = username
        user.save()
        plurk = PlurkUser(username=content["nick_name"])
        plurk.user_id = str(content["id"])
        plurk.user = user
        plurk.oauth_token = oauth_token
        plurk.oauth_secret = oauth_token_secret
        plurk.save()
        user = plurk.authenticate()
        login(request, user, 'plurk')
        return HttpResponseRedirect(_get_next(request)) 
      
def callAPI(oauth_token, oauth_token_secret, data):
    api_url = 'http://www.plurk.com/APP/Timeline/plurkAdd'
    body = urllib.urlencode(data)
    consumer = oauth.Consumer(settings.PLURK_APP_KEY, settings.PLURK_APP_SECRET)
    token = oauth.Token(oauth_token, oauth_token_secret)
    client = oauth.Client(consumer, token)
    params = { 'oauth_signature_method': 'HMAC-SHA1',
				   'oauth_nonce': oauth.generate_nonce(),
				   'oauth_timestamp': oauth.generate_timestamp(),
				   'oauth_token': oauth_token }
    req = oauth.Request.from_consumer_and_token(consumer=consumer, token=token,
				   http_method='POST', http_url=api_url, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
    response, content = client.request(api_url, method='POST', headers=req.to_header(), body=data)
    print "sukses"
    print content
    print response
    return (response, content)

def getFriendsPlurk(oauth_token, oauth_token_secret, body):
    from plurk_oauth.PlurkAPI import PlurkAPI
    #body = urllib.urlencode(body)
    plurk = PlurkAPI(settings.PLURK_APP_KEY, settings.PLURK_APP_SECRET)
    plurk.authorize(oauth_token, oauth_token_secret)
    dd = plurk.callAPI('/APP/FriendsFans/getFriendsByOffset', body)
    return dd
    
    #return None

