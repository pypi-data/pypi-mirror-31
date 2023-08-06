fluentcms-twitterfeed
=====================

Twitter feed widget for django-fluent-contents_

.. image:: https://img.shields.io/pypi/v/fluentcms-twitterfeed.svg
    :target: https://pypi.python.org/pypi/fluentcms-twitterfeed/

.. image:: https://img.shields.io/github/license/bashu/fluentcms-twitterfeed.svg
    :target: https://pypi.python.org/pypi/fluentcms-twitterfeed/

.. image:: https://landscape.io/github/bashu/fluentcms-twitterfeed/develop/landscape.svg?style=flat
    :target: https://landscape.io/github/bashu/fluentcms-twitterfeed/develop

Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI:

.. code-block:: shell

    pip install fluentcms-twitterfeed


Backend Configuration
---------------------

First make sure the project is configured for django-fluent-contents_.

Then add the following settings:

.. code-block:: python

    INSTALLED_APPS += (
        'fluentcms_twitterfeed',
    )

The database tables can be created afterwards:

.. code-block:: shell

    python ./manage.py migrate

Now, the ``TwitterSearchPlugin`` and ``TwitterRecentEntriesPlugin``
can be added to your ``PlaceholderField`` and ``PlaceholderEditorAdmin`` admin screens.

Frontend Configuration
----------------------

Make sure that all plugin media files are exposed by django-fluent-contents_:

.. code-block:: html+django

    {% load fluent_contents_tags %}

    {% render_content_items_media %}

This tag should be placed at the bottom of the page, after all plugins
are rendered.  For more configuration options - e.g. integration with
django-compressor - see the `template tag documentation
<http://django-fluent-contents.readthedocs.org/en/latest/templatetags.html#frontend-media>`_.

CSS Code
~~~~~~~~

The stylesheet code is purposefully left out, since authors typically like to provide their own styling.

JavaScript Code
~~~~~~~~~~~~~~~

No configuration is required for the JavaScript integration.

By default, the plugin includes all required JavaScript code.

HTML code
~~~~~~~~~

If needed, the HTML code can be overwritten by redefining
``fluentcms_twitterfeed/recent_entries.html`` add / or ``fluentcms_twitterfeed/search.html``.

Contributing
------------

If you like this module, forked it, or would like to improve it, please let us know!
Pull requests are welcome too. :-)

.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
