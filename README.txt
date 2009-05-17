============================
Acacia -- Simple Topic Trees
============================

Acacia is a small Django application that provides hierarchical topic or
category naming. Other Django applications can then use the topic trees to
categorise articles or objects with human-readable names.

Dependencies
============

This code should run on Python 2.4 or later and Django 1.0.3 or later.

Acacia uses django-treebeard_ to provide the underlying tree implementation,
so that will need to be importable before you can use this code
(``django-treebeard`` doesn't require installation, so it only has to be on
the Python import path, not part of Django's ``INSTALLED_APPS`` setting).

.. _django-treebeard: http://code.google.com/p/django-treebeard/

More Documentation
==================

Full documentation for Acacia is available in the docs/ directory of the
source.

