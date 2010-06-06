"""
Custom manager for working with topic hierarchies.
"""

from django.db import models

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

        # TODO: Feels like I should be able to do this with fewer queries.
        pieces = full_name.rsplit(self.model.separator, 1)
        if len(pieces) == 1:
            return self.model.create(name=pieces[0]), True
        parent, created = self.get_or_create_by_full_name(pieces[0])
        if not pieces[1]:
            # full_name ended with a trailing separator (e.g. /foo/bar/).
            return parent, created
        node = self.create(name=pieces[-1], parent=parent)
        return node, True

