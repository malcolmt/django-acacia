============================
Acacia -- Simple Topic Trees
============================

Acacia is a small Django application that provides hierarchical topic or
category naming. Other Django applications can then use the topic trees to
categorise articles or objects with human-readable names. For example::

    root_1
        root_1/child_1
        root_1/child_2
    root_2
        root_2/child_1
            root_2/child_1/grandchild_1
        root_2/child_2

Each model instance in this application is one node in the hierarchy, defining
only the name for that node (which is the parent's name plus the node's
individual name). Further information could be added to the nodes through
subclassing.

Individual node names can be reused in multiple places in the tree, which is
where this system provides an advantage over tagging. It allows you to create
"debugging" nodes under both "software/" and "hardware/" and have them remain
distinct.

Admin Support
=============

The topic tree can be edited directly in the admin interface. Admin users can
create new node names and reparent existing nodes directly.

(Coming soon: nifty Javascript manipulation)

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

Further documentation, containing information about usage, extending the
nodes, using the hierarchy with multiple models, and providing easy use with
other applications in the admin application is coming soon. The current code
is an initial dump of what I've been working with.

Eager early adopters can probably work out most of the extensions themselves
in any case, using intermediate many-to-many tables and model inheritance in
appropriate places to provide extensions.

