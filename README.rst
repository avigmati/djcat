=============================
djcat
=============================

.. image:: https://badge.fury.io/py/djcat.png
    :target: https://badge.fury.io/py/djcat

.. image:: https://travis-ci.org/avigmati/djcat.png?branch=master
    :target: https://travis-ci.org/avigmati/djcat

Simply app for creating catalog.

Documentation
-------------

The full documentation is at https://djcat.readthedocs.io.

Quickstart
----------

Install djcat::

    pip install djcat

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'djcat.apps.DjcatConfig',
        ...
    )

Add djcat's URL patterns:

.. code-block:: python

    from djcat import urls as djcat_urls


    urlpatterns = [
        ...
        url(r'^', include(djcat_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
