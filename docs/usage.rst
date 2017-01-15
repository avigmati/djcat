=====
Usage
=====

To use djcat in a project, add it to your `INSTALLED_APPS`:

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
