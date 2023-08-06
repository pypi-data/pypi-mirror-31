=============================
Django Chaos Features
=============================

.. image:: https://badge.fury.io/py/django-chaos-features.svg
    :target: https://badge.fury.io/py/django-chaos-features

.. image:: https://travis-ci.org/george-silva/django-chaos-features.svg?branch=master
    :target: https://travis-ci.org/george-silva/django-chaos-features

.. image:: https://codecov.io/gh/george-silva/django-chaos-features/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/george-silva/django-chaos-features

Features

Documentation
-------------

The full documentation is at https://django-chaos-features.readthedocs.io.

Quickstart
----------

Install Django Chaos Features::

    pip install django-chaos-features

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'chaos_features.apps.ChaosFeaturesConfig',
        ...
    )

Add Django Chaos Features's URL patterns:

.. code-block:: python

    from chaos_features import urls as chaos_features_urls


    urlpatterns = [
        ...
        url(r'^', include(chaos_features_urls)),
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
