==============
feincms3-sites
==============

.. image:: https://travis-ci.org/matthiask/feincms3-sites.svg?branch=master
   :target: https://travis-ci.org/matthiask/feincms3-sites

Multisite support for `feincms3 <https://feincms3.readthedocs.io>`_.

This app allows running a feincms3 site on several domains, with
separate page trees etc. on each (if so desired).

The default behavior allows to match a single host. The advanced options
fieldset in the administration panel allows specifying your own regex,
which is matched against the host. There can be at most one default
site.


Installation and usage
======================

- ``pip install feincms3-sites``
- Add ``feincms3_sites`` to ``INSTALLED_APPS`` and run ``./manage.py
  migrate``
- Your page model should extend ``feincms3_sites.models.AbstractPage``
  instead of ``feincms3.pages.AbstractPage``. The only difference is
  that our ``AbstractPage`` has an additional ``site`` foreign key, and
  path uniqueness is enforced per-site.
- If you're using feincms3 apps currently, replace
  ``feincms3.apps.apps_middleware`` with
  ``feincms3_sites.middleware.apps_middleware`` in your ``MIDDLEWARE``.
  Otherwise, you may want to add
  ``feincms3_sites.middleware.site_middleware`` near the top.
- Uses of ``apps_urlconf()`` in your own code (improbable!) have to be
  replaced by ``feincms3_sites.middleware.apps_urlconf_for_site(site)``.
- ``Page.objects.active()`` does not automatically filter by site,
  you'll have to do this yourself in your views code, navigation
  template tags etc. The site instance (if any could be found) is always
  available as ``request.site``.
- If you want to automatically redirect requests to the current site,
  insert ``feincms3_sites.middleware.redirect_to_site_middleware`` after
  one of the other middleware referenced above. You may also set
  ``SecurityMiddleware``'s ``SECURE_SSL_REDIRECT = True`` to enforce
  SSL. In this case, insert ``redirect_to_site_middleware`` before the
  ``SecurityMiddleware``.
- It is possible to define a default language per site. If this sounds
  useful to you, replace ``django.middleware.locale.LocaleMiddleware``
  with ``feincms3_sites.middleware.default_language_middleware``.


