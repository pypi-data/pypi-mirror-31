Ragtag Auth for Sentry
======================

An SSO provider for Sentry which enables Ragtag authentication.

Install
-------

::

    $ pip install https://github.com/ragtagopen/sentry-auth-ragtag/archive/master.zip

Setup
-----

Create a new application under your organization in Ragtag ID. Enter the **Authorization
callback URL** as the prefix to your Sentry installation:

::

    https://example.sentry.com


Once done, grab your API keys and drop them in your ``sentry.conf.py``:

.. code-block:: python

    RAGTAG_APP_ID = ""

    RAGTAG_API_SECRET = ""
