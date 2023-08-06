|Python| |Django| |License| |PyPI| |Build Status| |Coverage Status|

Django-Celery-GrowthMonitor
===========================

A Django helper to monitor jobs running Celery tasks

Features
--------

-  Utilities to track progress of Celery tasks via in-database jobs

Requirements
------------

-  `Python <https://www.python.org/>`__ >= 3.4
-  `Django <https://www.djangoproject.com/>`__ >= 1.8
-  `Celery <http://www.celeryproject.org/>`__ >= 4.0.2
-  `echoices <https://github.com/mbourqui/django-echoices>`__ >= 2.5.0
-  `autoslugged <https://github.com/mbourqui/django-autoslugged>`__ >=
   2.0.0

Installation
------------

Using PyPI
~~~~~~~~~~

1. Run ``pip install django-celery-growthmonitor``

Using the source code
~~~~~~~~~~~~~~~~~~~~~

1. Make sure ```pandoc`` <http://pandoc.org/index.html>`__ is installed
2. Run ``./pypi_packager.sh``
3. Run
   ``pip install dist/django_celery_growthmonitor-x.y.z-[...].wheel``,
   where ``x.y.z`` must be replaced by the actual version number and
   ``[...]`` depends on your packaging configuration

Usage
-----

.. code:: DJango

    ('state', echoices.fields.make_echoicefield(default=celery_growthmonitor.models.AJob.EStates.CREATED, echoices=celery_growthmonitor.models.AJob.EStates, editable=False)),
    ('status', echoices.fields.make_echoicefield(default=celery_growthmonitor.models.AJob.EStatuses.ACTIVE, echoices=celery_growthmonitor.models.AJob.EStatuses, editable=False)),

.. code:: Django

    from .celery import app

    @app.task
    def my_task(holder: JobHolder, *args):
        job = holder.get_job()
        # Some processing
        return holder.pre_serialization()

Helpers
~~~~~~~

Admin
^^^^^

.. code:: Django

    from django.contrib import admin

    from celery_growthmonitor.admin import AJobAdmin

    @admin.register(MyJob)
    class MyJobAdmin(AJobAdmin):
        fields = AJobAdmin.fields + ('my_extra_field',)
        readonly_fields = AJobAdmin.readonly_fields + ('my_extra_field',)

.. |Python| image:: https://img.shields.io/badge/Python-3.4,3.5,3.6-blue.svg?style=flat-square
   :target: /
.. |Django| image:: https://img.shields.io/badge/Django-1.8,1.9,1.10,1.11-blue.svg?style=flat-square
   :target: /
.. |License| image:: https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square
   :target: /LICENSE
.. |PyPI| image:: https://img.shields.io/pypi/v/django_celery_growthmonitor.svg?style=flat-square
   :target: https://pypi.org/project/django-celery-growthmonitor
.. |Build Status| image:: https://travis-ci.org/mbourqui/django-celery-growthmonitor.svg?branch=master
   :target: https://travis-ci.org/mbourqui/django-celery-growthmonitor
.. |Coverage Status| image:: https://coveralls.io/repos/github/mbourqui/django-celery-growthmonitor/badge.svg?branch=master
   :target: https://coveralls.io/github/mbourqui/django-celery-growthmonitor?branch=master


