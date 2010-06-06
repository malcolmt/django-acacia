============================
Acacia -- Simple Topic Trees
============================

Acacia is a small Django application that provides hierarchical topic naming.
Other Django applications can use the topic trees to categorise and retrieve
objects using human-readable names.

Documentation
=============

Full documentation for Acacia is available in the docs/ directory of the
source. It is marked up using the Sphinx documentation system — restructured
text plus some extras for inter-file connections. Running "make html" in the
docs directory is one way to create the HTML version.

Dependencies
============

This code should run on Python 2.4 or later and Django 1.2[#]_ or later.

Acacia uses django-mptt_ to provide the underlying tree implementation, so you will need that as installed Django application before being able to use django-acacia.

.. [#] To check: is there a strict 1.2 requirement, or does it also work with Django 1.1?
.. _django-mptt: http://code.google.com/p/django-mptt/

Testing
=======

Acacia uses the standard Django testing framework. Any execution of
"django-admin.py test" (or "manage.py test") in a project that has Acacia
installed will execute the Acacia tests.

To make testing in isolation easier, there is also the testing/runtests.py
script. This runs the tests in standalone mode. During development of Acacia
itself this makes things easier, as it removes the need to install Acacia into
a fake Django project merely to run the tests. Execute that script from
anywhere and it will run through all of Acacia's unittests in isolation.

