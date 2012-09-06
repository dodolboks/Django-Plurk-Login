from django.conf.urls.defaults import url, patterns, include

from views import *


urlpatterns = patterns("",

    url(r'^login/plurk/$', plurk_token, name="plurk_login"),
    url(r'^login/plurk/hapus/$', hapus_plurk, name="hapus_plurk"),

    url(r'^login/plurk/oauth$', get_access_token),
)

