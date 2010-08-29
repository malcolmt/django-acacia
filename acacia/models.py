"""
A hierarchical topics scheme.

The important piece here is the hierarchy. This is not tagging -- which tends
to be viewed as something flat by kids these days. We have no time for such a
shallow view of information organisation here.
"""

import mptt
from django.db import models

from acacia import managers, signals


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

    objects = managers.TopicManager()
    separator = u"/"

    class Meta:
        # pylint: disable-msg=W0232
        abstract = True
        unique_together = [("name", "parent")]

    def __unicode__(self):
        return self.full_name()

    def full_name(self):
        # pylint: disable-msg=W0201,E0203
        if (not hasattr(self, "_full_name_cache") or
                self.parent_id != self._cached_parent):
            if self.parent is not None:
                parents = self.separator.join(
                        self.get_ancestors().values_list("name", flat=True))
                self._full_name_cache = u"%s%s%s" % (parents, self.separator,
                        self.name)
            else:
                self._full_name_cache = self.name
            self._cached_parent = self.parent_id
        return self._full_name_cache

    def merge_to(self, parent):
        """
        A variant on mptt's move_to() method that merges any overlapping
        portions of the move.

        If any nodes are to be merged, a pre_merge signal is emitted before the
        move, with a list (old_id, new_id) pairs for nodes that will be merged
        rather than moved. (For efficiency reasons, no signal is emitted if no
        nodes are to be merged.)

        A pre_move signal is also emitted containing the root nodes of any
        subtrees that are being moved, but not merged, and their target parent
        node. This enables dependent apps to set up things like URL rewrites if
        they have URLs depending on topic names. (The significance of
        moved-but-not-merged is that these nodes won't have their pk values
        changed in the process.)
        """
        manager = self.__class__.objects
        try:
            merge_node = manager.get(parent=parent, name=self.name)
        except self.DoesNotExist:
            signals.pre_move.send(sender=self, moving=[(self, parent)])
            self.move_to(parent)
            return
        squash = [(self.id, merge_node.id)]
        examine = [(self, merge_node)]
        to_move = []
        while examine:
            node, merge_node = examine.pop()
            children = node.get_children()
            child_names = [obj.name for obj in children]
            conflicts = {}
            for obj in manager.filter(parent=merge_node, name__in=child_names):
                conflicts[obj.name] = obj
            for child in children:
                if child.name in conflicts:
                    squash.append((child.id, conflicts[child.name].id))
                    examine.append((child, conflicts[child.name]))
                else:
                    to_move.append((child, merge_node))
        if squash:
            signals.pre_merge.send(sender=self, merge_pairs=squash)

        if to_move:
            signals.pre_move.send(sender=self, moving=to_move)
            for child, new_parent in to_move:
                # Need to refresh the instance, as previous moves might have
                # changed the "lft" and "rght" attributes.
                new_parent = manager.get(id=new_parent.id)
                child.move_to(new_parent)
        self.delete()

class Topic(AbstractTopic):
    """
    The basic concrete class for a topic node. API details are defined by the
    AbstractTopic base class.
    """
    pass

mptt.register(Topic, order_insertion_by=["name"])

