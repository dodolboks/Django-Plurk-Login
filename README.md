Django Plurk Login
==================

simple django plurk login apps


Install
-------

* Add ``django_plurk_login`` to ``INSTALLED_APPS`` in ``settings.py``::

    INSTALLED_APPS = (
        # other apps
        "django_plurk_login",
    )

* Add ``django_plurk_login`` to ``INSTALLED_APPS`` in ``settings.py``::

    AUTHENTICATION_BACKENDS = (
        # other auth
        'django_plurk_login.auth.PlurkAuth'
    )
* Add ``django_plurk_login`` url in Url ::
   urlpatterns = patterns('',
        url("^login/plurk/", include("django_plurk_login.url")),
   )

