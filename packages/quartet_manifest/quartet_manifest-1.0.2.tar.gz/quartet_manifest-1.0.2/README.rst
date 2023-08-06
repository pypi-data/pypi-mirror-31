=============================
quartet_manifest
=============================

.. image:: https://gitlab.com/serial-lab/quartet_manifest/badges/master/pipeline.svg
    :target: https://gitlab.com/serial-lab/quartet_manifest/commits/master

.. image:: https://gitlab.com/serial-lab/quartet_manifest/badges/master/coverage.svg
    :target: https://gitlab.com/serial-lab/quartet_manifest/commits/master

Reports back QU4RTET configuration and capabilities to quartet-ui.

Documentation
-------------

Dependencies
____________
First, make sure you have Django_ and the `Django Rest Framework`_ installed and
you have an active project started.  See the Django and Django Rest Framework
documentation below if you are unfamiliar with this process.

.. _Django: https://docs.djangoproject.com
.. _Django Rest Framework: http://www.django-rest-framework.org/


Modfiy settings.py
__________________

To use quartet_manifest in a project, first, add it to your `INSTALLED_APPS`:

.. code-block::text

    INSTALLED_APPS = (
        ...
        'rest_framework',
        'quartet_manifest',
        ...
    )

Add the URL patterns
____________________

In your project's `urls.py`, add quartet_manifest's URL patterns:

.. code-block::python

    from quartet_manifest import urls as quartet_manifest_urls


    urlpatterns = [
        ...
        path('manifest/', include('quartet_manifest.urls')),
        ...
    ]

Test the URL
____________
Navigate to the configured host/port and url using the structure below:

http://[your host name]:[your port]/manifest/quartet-manifest/?format=json

You should get a return value as below

.. code-block::javascript

    [..."rest_framework","quartet_manifest","quartet_epcis"...]

