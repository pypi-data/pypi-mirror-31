WARapidPro
==========

Wassup Integration for RapidPro.

::

    pip install -e '.[dev]'


::

    docker run praekeltfoundation/rapidpro-engage:latest


Setting up the application
~~~~~~~~~~~~~~~~~~~~~~~~~~

All environment variables for ``rapidpro-docker`` apply here.

Add `warapidpro` to `EXTRA_INSTALLED_APPS` in your environment variables.

You will also need at least 1 celery instance running. Use the command to run the worker:
``/venv/bin/celery --beat --app=temba worker --loglevel=INFO --queues=celery,msgs,flows,handler --max-tasks-per-child=10``

Note: that you should give your web application between 1-2GB of RAM in order to avoid uWSGI worker failures.

Get a oAuth client id and a client secret from https://wassup.p16n.org/oauth/applications/ or create a new one at https://wassup.p16n.org/oauth/applications/.
`Client type` should be `confidential` and `Authorization grant type` should be `authorization code`.

Make sure to setup the redirect uris correctly for your installation. These should be formatted as follows::

    https://<your domain>/channels/claim/wad/
    https://<your domain>/channels/claim/wag/


Environment Variables
~~~~~~~~~~~~~~~~~~~~~

- ``WASSUP_AUTH_URL`` defaults to ``https://wassup.p16n.org``
- ``WASSUP_AUTH_CLIENT_ID`` as per above.
- ``WASSUP_AUTH_CLIENT_SECRET`` as per above.


