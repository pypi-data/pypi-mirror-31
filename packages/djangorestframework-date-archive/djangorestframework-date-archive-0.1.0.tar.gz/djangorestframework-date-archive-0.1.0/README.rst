djangorestframework-date-archive
======================================

|build-status-image| |pypi-version|

Overview
--------

Django date view archive for rest framework

Requirements
------------

-  Python (3.6)
-  Django REST Framework (3.8)

Installation
------------

Install using ``pip``\ …

.. code:: bash

    $ pip install djangorestframework-date-archive

Example
-------

rest_framework_date_archive provides your drf model viewsets with a read-only date archive similar to that of django.

The archive can be accessed through the following urls:

.. code:: python
    items\\archive\\year\\
    items\\archive\\year\\month\\
    items\\archive\\year\\month\day\\

Setting things up is pretty easy:

Your model manager must include a queryset that inherit from ``DateArchiveMixin``.
The name of the field with which the data is archived is specified by the class attribute date_field:

.. code:: python

   class BlogQueryset(DateArchiveMixin,
                      models.QuerySet):
       date_field = 'date'


   class Blog(models.Model):
       date = models.DateField()
       content = models.TextField(default='')

       objects = BlogQueryset.as_manager()

Your model viewset must inherit from ``DateArchiveView``:

.. code:: python

    class BlogViewSet(DateArchiveView,
                      ModelViewSet):
        model = Blog
        queryset = Blog.objects.all()
        serializer_class = BlogSerializer

And you must register your urls with the ``DateArchiveRouter``:

.. code:: python

    router = DateArchiveRouter()
    router.register('blogs', BlogViewSet)


Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with runtests.

.. code:: bash

    $ ./runtests.py

You can use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

Documentation
-------------

To build the documentation, you’ll need to install ``mkdocs``.

.. code:: bash

    $ pip install mkdocs

To preview the documentation:

.. code:: bash

    $ mkdocs serve
    Running at: http://127.0.0.1:8000/

To build the documentation:

.. code:: bash

    $ mkdocs build

.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://secure.travis-ci.org/PJCampi/django-rest-framework-date-archive.svg?branch=master
   :target: http://travis-ci.org/PJCampi/django-rest-framework-date-archive?branch=master
.. |pypi-version| image:: https://img.shields.io/pypi/v/djangorestframework-date-archive.svg
   :target: https://pypi.python.org/pypi/djangorestframework-date-archive
