==================
Simple Topic Trees
==================

Basic Usage
===========

The most direct usage of Acacia's topic trees is to categorise entries in
another model. You create a ``ForeignKey`` or ``ManyToManyField`` link between
your model and ``acacia.models.Topic`` and use it to store the category (or
categories, in the latter case).

For example, to categorise a series of articles, you might have the following
model::

    from django.db import models
    from acacia import models as acacia_models

    class Author(models.Model):
        ...

    class Article(models.Model):
        title = models.CharField(max_length=150)
        author = models.ForeignKey(Author)
        text = models.FileField(upload_to="%Y%m%d")
        topics = models.ManyToManyField(acacia_models.Topic)

Working With Topics Via The Admin Interface
===========================================

Although the internals of the ``Topic`` model are fairly complex, the admin
interface is very straightforward. You can edit the name of a node in the tree
and the parent of the node.

The *name* of an individual node is the final component of the full name. Thus,
if the node's full name (path) is ``"timeframe/today/urgent"``, the name of the
node is ``"urgent"``. The parent of that node is the ``"timeframe/today"`` node.

Topic nodes are sorted lexicographically by their full name when presented in
the admin. Given the nodes, ``"pet"``, ``"pet/dog"``, ``"pet/cat"`` and
``"owners"``, they will sort in this order::

    owners
    pet
    pet/cat
    pet/dog

This makes finding the appropriate node in a list fairly straightforward.

.. admonition:: Coming Soon

    In the near future, the admin form for working with ``Topic`` objects will
    include a Javascript tree widget for even easier parent selection. With
    even a few dozen topics, the selection list can become quite long and
    unwieldy.

Selecting Topics Objects In Django Code
=======================================

.. currentmodule:: acacia.models

It will be common ``Acacia`` usage to want to select :class:`Topic` objects
using their full, human-readable names. Those names are natural candidates for
using in URLs and the like, so you need to be able to return from the string
form to the correct object or subtree of objects. This is the only reason
``Acacia`` exists as an application on top of `treebeard`_: to provide
alternative access methods.

.. _treebeard: http://code.google.com/p/django-treebeard/

The :class:`Topic` class comes with a default manager (available as
``Topic.objects``) providing some useful utility methods for this purpose. The
``get_by_full_name()`` method is the normal way of retrieving an object, given
its string form::

    Topic.objects.get_by_full_name("animal/cat")

For convenience (particularly when working with URLs), repeated separators
between name components (the ``"/"`` character) are collapsed into a single
separator. So ``animal//cat`` is the same as ``animal/cat``. Leading and
trailing separators are also ignored. Thus, ``/animal/cat/`` is also the same
as ``animal/cat``.

