"""
A hierarchical topics scheme.

The important piece here is the hierarchy. This is not tagging -- which tends
to be viewed as something flat by the kids these days.
"""

from django.db import models

import mptt


class TopicManager(models.Manager):
    """
    Some useful methods that operate on topics as a whole. Mostly for locating
    information about a Topic based on its full name.
    """
    def get_by_full_name(self, full_name):
        """
        Returns the topic with the given full name.

        Raises Topic.DoesNotExist if there is no tag with 'full_name'.
        """
        # Ensure foo//bar is the same as foo/bar. Nice to have.
        sep = self.model.separator
        pieces = [o for o in full_name.split(sep) if o]
        for candidate in self.filter(level=len(pieces)-1, name=pieces[-1]):
            parents = candidate.get_ancestors().values_list("name", flat=True)
            if list(parents) == pieces[:-1]:
                return candidate
        raise self.model.DoesNotExist

    def get_subtree(self, full_name):
        """
        Returns a list containing the tag with the given full name and all tags
        with this tag as an ancestor. The first item in the list will be the
        tag with the passed in long name.

        Raises Topic.DoesNotExist if there is no tag with 'long_name'.
        """
        return self.get_by_full_name(full_name).get_descendants(True)

    def get_or_create_by_full_name(self, full_name):
        """
        Retrieves a topic with the given full_name. If the topic doesn't exist,
        it is created (along with all the necessary parent topics). This is
        analogous to Django's get_or_create() manager method, with additional
        logic to handle long names.

        Returns a pair: the topic object and a boolean flag indicating whether
        or not a new object was created.
        """
        try:
            node = self.get_by_full_name(full_name)
            return node, False
        except self.model.DoesNotExist:
            pass

        # TODO: Feels like I should be able to do this with less queries.
        pieces = full_name.rsplit(self.model.separator, 1)
        if len(pieces) == 1:
            return self.model.create(name=pieces[0]), True
        parent, created = self.get_or_create_by_full_name(pieces[0])
        if not pieces[1]:
            # full_name ended with a trailing separator (e.g. /foo/bar/).
            return parent, created
        node = self.create(name=pieces[-1], parent=parent)
        return node, True


class AbstractTopic(models.Model):
    """
    A node in a hierarchical storage tree, representing topics of some kind.
    The name of the topic is the name of the parent, followed by the node's
    name (with a configurable separator in between).

    This is an abstract base class to allow for including attributes other than
    just the name via inheritance.
    """
    name = models.CharField(max_length=50)
    parent = models.ForeignKey("self", null=True, blank=True,
            related_name="children")
    # The level of this node in the tree it belongs to (used by mptt).
    level = models.PositiveIntegerField()

    objects = TopicManager()
    separator = u"/"

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.full_name()

    def full_name(self):
        if not hasattr(self, "_full_name_cache"):
            if self.level:
                parents = self.separator.join(
                        self.get_ancestors().values_list("name", flat=True))
                self._full_name_cache = u"%s%s%s" % (parents, self.separator,
                        self.name)
            else:
                self._full_name_cache = self.name
        return self._full_name_cache

    # FIXME: Implement this in a reasonable fashion for mptt-based trees.
    ##def move_to(self, target, pos=None, update_funcs=()):
    ##    """
    ##    Moves current node and all descendents to a new position in the tree.

    ##    If "update_funcs" is given, it's a list of callables that are passed
    ##    child nodes as the first argument. Subclasses can use this list to add
    ##    their own hooks for things needing updating after moves.
    ##    """
    ##    # A little runtime efficiency is sacrificed here for the sake of code
    ##    # simplicity. The default treebeard move() method uses custom SQL to
    ##    # update the paths on all the children. This class has to also update
    ##    # all the full_name attributes. The latter is done as a separate query
    ##    # for each child, on the grounds that moving is far less common than
    ##    # reading for these types of hierarchies.
    ##    super(AbstractTopic, self).move(target, pos)

    ##    # After call to super's move(), "self" no longer has valid path
    ##    # information, so have to refetch the data from the database.
    ##    for node in self.__class__.objects.get(pk=self.pk).get_tree():
    ##        # FIXME: Since I already know the ancestor names at this point,
    ##        # being able to pass them into _set_full_name() would be an
    ##        # improvement.
    ##        node._set_full_name()
    ##        for func in update_funcs:
    ##            func(node)
    ##        node.save()

class Topic(AbstractTopic):
    """
    The basic concrete class for a topic node. API details are defined by the
    AbstractTopic base class.
    """
    pass

mptt.register(Topic, order_insertion_by=["name"])

