"""
A hierarchical topics scheme.

The important piece here is the hierarchy. This is not tagging -- which tends
to be viewed as something flat by the kids these days.
"""

from django.db import models

import treebeard_mods


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
        normalised_path = sep.join(pieces)
        return self.get(full_name=normalised_path)

    def get_subtree(self, full_name):
        """
        Returns a list containing the tag with the given full name and all tags
        with this tag as an ancestor. The first item in the list will be the
        tag with the passed in long name.

        Raises Tag.DoesNotExist if there is no tag with 'long_name'.
        """
        return self.model.get_tree(self.get_by_full_name(full_name))


class AbstractTopic(treebeard_mods.MP_Node):
    """
    A node in a hierarchical storage tree, representing topics of some kind.
    The name of the topic is the name of the parent, followed by the node's
    name (with a configurable separator in between).

    This is an abstract base class to allow for including attributes other than
    just the name via inheritance.
    """
    name = models.CharField(max_length=50)
    # Denormalise things a bit so that full name lookups are fast.
    full_name = models.CharField(max_length=512, db_index=True)

    node_order_by = ["name"]
    separator = "/"

    objects = TopicManager()

    class Meta(treebeard_mods.MP_Node.Meta):
        abstract = True

    def __unicode__(self):
        if not hasattr(self, "full_name") or not self.full_name:
            self._set_full_name()
        return self.full_name

    @models.permalink
    def get_absolute_url(self):
        return ("topic", [unicode(self)])

    def _set_full_name(self):
        if self.depth == 1:
            self.full_name = self.name
        else:
            parent = self.separator.join(
                    list(self.get_ancestors().values_list("name", flat=True)))
            self.full_name = "%s%s%s" % (parent, self.separator, self.name)

    def save(self, *args, **kwargs):
        """
        Updates the full_name attribute prior to saving (incurs an extra lookup
        query on each save, but saving is much less common than retrieval).
        """
        self._set_full_name()
        return super(AbstractTopic, self).save(*args, **kwargs)

class Topic(AbstractTopic):
    """
    The basic concrete class for a topic node. API details are defined by the
    AbstractTopic base class.
    """
    pass

