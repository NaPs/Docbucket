Docbucket README
================

Docbucket is a web application used to ease the management of the personnal
paperwork. It provide a way to create, index and manage "searchable" PDF files.

.. image:: https://raw.github.com/NaPs/Docbucket/master/artworks/screenshot.png
   :align: center

Setup
-----

Docbucket is packaged for the Debian Wheezy distro, but since its a standard
Django application, it should be easy to install it on any other distro.

Install the Docbucket package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add these lines in your ``/etc/apt/source.list`` file::

    deb http://debian.tecknet.org/debian wheezy tecknet
    deb-src http://debian.tecknet.org/debian wheezy tecknet

Add the Tecknet repositories key in your keyring:

    # wget http://debian.tecknet.org/debian/public.key -O - | apt-key add -

Update and install the *docbucket* package::

    # aptitude update
    # aptitude install docbucket

The installation procedure will configure the database (SQLite by default) and
collect all static files in the ``/var/lib/docbucket/`` directory.

Optional: Install memcached
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Memcached can be used by Docbucket to cache the images thumbnails. Install the
Memcached daemon and the Python client library::

    # aptitude install memcached python-memcache

To configure Docbucket to use Memcached daemon as cache backend, add the
following lines to your ``/etc/docbucket.conf`` file::

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        }
    }

Configure Gunicorn
~~~~~~~~~~~~~~~~~~

The next step is to configure gunicorn to serve the docbucket application, in
the ``/etc/gunicorn.d/`` directory, copy the ``docbucket.example`` file
to ``docbucket``::

    # cd /etc/gunicorn.d
    # cp docbucket.example docbucket

You can customize the file to add or change Gunicorn options such as the http
listening port (by default 9001) or the number of workers to start.

Restart the Gunicorn daemon to start Docbucket::

    # service gunicorn restart

Configure the web server
~~~~~~~~~~~~~~~~~~~~~~~~

The last thing to do is to configure a web server to reverse proxify the
Docbucket application, and to serve statics. Here is an example for nginx::

    # cat /etc/nginx/site-enabled/docbucket
    server {
        location / {
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass http://127.0.0.1:9001/;
            proxy_redirect default;
        }

        location /static {
            alias /var/lib/docbucket/static;
        }

        location /media {
            alias /var/lib/docbucket/media;
        }
    }

Strongly recommended: Setup backups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Backups are almost mandatory if you store important documents into your
Docbucket instance. Docbucket provide a backup tool which can help you to
secure your documents.

The backup command will export all the content of the database and each PDF
into a zip file. To create a backup file, execute the following command::

    $ docbucketadm backup /path/to/the/backup.zip

To restore a backup file, use the following comand::

    $ docbucketadm restore /path/to/the/backup.zip

.. note::
   The restore process will *NOT* clean the existing documents, so you can use
   it to exchange documents between instances.

Contribute
----------

You can send your pull-request for Docbucket through Github:

    https://github.com/NaPs/Docbucket

I also accept well formatted git patches sent by email.

Feel free to contact me for any question/suggestion/patch: <antoine@inaps.org>.