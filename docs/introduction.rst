============
Introduction
============

Topic Trees Versus Tagging
===========================

These days, it seems that *"tagging"* is the trendy thing to provide on sites
with large amounts of contents. Tags, individual labels attached to items of
content, provide a *flat* structure for categorisation. In a wide number of
situations, experience has shown that this is all the complexity that is
needed. It's possible to provide easy searchability and qualification using
only a single layer of labels.

In more complex situations, introducing extra structure into the labels,
by grouping them into hierarchies, is very useful. Using a common name for
labels structured in a hierarchy is a bit harder, since they aren't as common
as tag-based systems. Throughout this documentation, we'll use *categories* or
*topic trees* as a descriptive name for these types of labellings.

It's obviously possible to fake hierarchies by using a flat tagging system,
simply by encoding the full name of each node in the tree into the tag name.
You could, for example, use "software/debugging" as a tag name.  Although
this works, in a fashion, operating as others do has a lot of benefits in the
web space and tagging systems do not typically use separators in tag names like
this. Your tags won't look like other people's tags if you adopt this approach
(and call your labels *tags*).

There's also a question of usability on the content creator's side of the
operation. A true hierarchy allows you to move entire subtrees at once. If you
have a whole group of topics under "software/python/", you might want to move
all those Python-related tags to live under "software/languages/python/"
instead. A normal tagging system won't understand that there's a relationship
between labels in this situation and won't relabel all the appropriate nodes
when the "python" node is moved to a new parent.

In short, tagging is not a bad labelling system. Website experiences over the
last decade has shown that. However, if you need a more structured system, it's
worth using a proper tree-like modelling scheme, rather than trying to fake the
names with tags.

Topic Trees Are Trees Plus Some Extras
=======================================

If you are in a situation where an hierarchical labelling system is
appropriate, it might seem that you are somewhat be spoilt for choice. There
are a number of tree implementations available for reuse in Django projects. At
the time of writing, probably the two most well-known examples are django-mptt_
and django-treebeard_. Both of these packages provide some well thought out
implementations of tree structures for Django models.

.. _django-mptt: http://code.google.com/p/django-mptt/
.. _django-treebeard: http://code.google.com/p/django-treebeard/

For topic trees, however, some extra work still remains to be done after you
have set up your models in an appropriate fashion. This is because you will
typically be trying to look up the topics or categories using a human-readable
name. Internally, though, the nodes in the tree won't be stored or related in
that fashion. Acacia has been developed to provide an extra layer of wrapper
functions and make those common lookup patterns (and similar manipulations)
easy.

