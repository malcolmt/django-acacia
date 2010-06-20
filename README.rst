======================================
Acacia — Simple Topic Trees For Django
======================================

Acacia is a small Django application that provides hierarchical topic naming.
Other applications can use the topic trees to categorise and retrieve objects
using human-readable names.

Full documentation is available in the ``docs/`` directory of the source. It is
marked up using the Sphinx documentation system — restructured text plus some
extras for inter-file connections. Running ``make html`` in the docs directory
is the simplest way to create the HTML version.

Dependencies
============

This code should run on Python 2.4 or later and Django 1.2 [*]_ or later.

The underlying tree implementation is provided by django-mptt_. Any project
using django-acacia, also needs to include django-mptt.

.. [*] To check: is there a strict 1.2 requirement, or does it also work with Django 1.1?
.. _django-mptt: http://code.google.com/p/django-mptt/

Testing
=======

Acacia can be tested with the standard Django testing framework. That is, any
run of ``django-admin.py test`` (or ``manage.py test``) in a project that has
Acacia installed will execute the tests.

In addition, to make testing in isolation easier, the ``testing/runtests.py``
script is provided. This removes the need to install Acacia into a fake Django
project merely to run the tests during development work. Execute the script
from anywhere and it will run through all of Acacia’s unittests in isolation.

