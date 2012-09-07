Django Plurk Login
==================

simple django plurk login apps. this apps is refactored from our `Bukucinta.com <http://bukucinta.com>`_. code base and not ready yet. please dont use it.

**Author:** `Ali kusnadi <http://twitter.com/dodolboks>`_.

Install
-------

* Add ``PLURK_APP_KEY``, and ``PLURK_APP_SECRET`` in ``settings.py``::

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



