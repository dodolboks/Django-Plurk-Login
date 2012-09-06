from mongoengine import *
from mongoengine.django.auth import User
from datetime import datetime, date, timedelta
from django.contrib.auth import authenticate

class PlurkUser(Document):
    user = ReferenceField(User)
    oauth_token = StringField(max_length=200)
    oauth_secret = StringField(max_length=200)
    user_id = StringField(max_length=50) 
    username = StringField(max_length=50) 
        
    def __unicode__(self):
        return u'%s: %s' % (self.user, self.user_id)
    
    def authenticate(self):
        return authenticate(user_id=self.user_id)


