from django.conf.urls.defaults import url, patterns, include

from views import *

urlpatterns = patterns("",

    url(r'^$', plurk_token, name="plurk_login"),
    url(r'^plurk/hapus/$', hapus_plurk, name="hapus_plurk"),

    url(r'^plurk/oauth$', get_access_token),
)

