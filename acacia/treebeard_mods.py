"""
A couple of modifications to the treebeard application so that it can be used
more easily in Django's admin interface.

This module provides a new MP_Node class that can be transparently used instead
of the standard treebeard version.
"""

from django.db import connection, transaction

from treebeard import mp_tree

class MP_Node(mp_tree.MP_Node):
    """
    This class is a normal treebeard.mp_tree.MP_Node, with a couple of modified
    methods. These versions allows passing in an existing Node object when
    storing information in the tree for the first time, instead of requiring
    keyword arguments.

    The primary use-case here is allowing nodes to be used in the admin.
    """
    class Meta(mp_tree.MP_Node.Meta):
        abstract = True

    def add_child(self, *args, **kwargs):
        """
        Adds a child to the node.

        See: :meth:`treebeard.Node.add_child`

        :raise PathOverflow: when no more child nodes can be added
        """
        if not self.is_leaf() and self.node_order_by:
            # there are child nodes and node_order_by has been set
            # delegate sorted insertion to add_sibling
            return self.get_last_child().add_sibling('sorted-sibling', *args, **kwargs)

        if not args:
            # creating a new object
            newobj = self.__class__(**kwargs)
        else:
            if len(args) > 1:
                raise TypeError("Can only pass in one object argument to "
                        "add_child().")
            newobj = args[0]
        newobj.depth = self.depth + 1
        if not self.is_leaf():
            # adding the new child as the last one
            newobj.path = self._inc_path(self.get_last_child().path)
        else:
            # the node had no children, adding the first child
            newobj.path = self._get_path(self.path, newobj.depth, 1)
            if len(newobj.path) > \
                    newobj.__class__._meta.get_field('path').max_length:
                raise mp_tree.PathOverflow('The new node is too deep in the tree, try'
                                   ' increasing the path.max_length property'
                                   ' and UPDATE your  database')
        # saving the instance before returning it
        newobj.save()
        newobj._cached_parent_obj = self
        self.numchild += 1
        self.save()
        return newobj

    def add_sibling(self, pos=None, *args, **kwargs):
        """
        Adds a new node as a sibling to the current node object.

        See: :meth:`treebeard.Node.add_sibling`

        :raise PathOverflow: when the library can't make room for the
           node's new position
        """

        pos = self._fix_add_sibling_opts(pos)

        if not args:
            # creating a new object
            newobj = self.__class__(**kwargs)
        else:
            if len(args) > 1:
                raise TypeError("Can only pass in one object argument to "
                        "add_child().")
            newobj = args[0]
        newobj.depth = self.depth

        if pos == 'sorted-sibling':
            siblings = self.get_sorted_pos_queryset(
                self.get_siblings(), newobj)
            try:
                newpos = self._get_lastpos_in_path(siblings.all()[0].path)
            except IndexError:
                newpos = None
            if newpos is None:
                pos = 'last-sibling'
        else:
            newpos, siblings = None, []

        stmts = []
        _, newpath = self._move_add_sibling_aux(pos, newpos,
            self.depth, self, siblings, stmts, None, False)

        parentpath = self._get_basepath(newpath, self.depth-1)
        if parentpath:
            stmts.append(self._get_sql_update_numchild(parentpath, 'inc'))

        cursor = connection.cursor()
        for sql, vals in stmts:
            cursor.execute(sql, vals)

        # saving the instance before returning it
        newobj.path = newpath
        newobj.save()

        transaction.commit_unless_managed()
        return newobj

    @classmethod
    def add_root(cls, *args, **kwargs):
        """
        Adds a root node to the tree.

        See: :meth:`treebeard.Node.add_root`

        :raise PathOverflow: when no more root objects can be added
        """

        # do we have a root node already?
        last_root = cls.get_last_root_node()

        if last_root and last_root.node_order_by:
            # there are root nodes and node_order_by has been set
            # delegate sorted insertion to add_sibling
            return last_root.add_sibling('sorted-sibling', *args, **kwargs)

        if last_root:
            # adding the new root node as the last one
            newpath = cls._inc_path(last_root.path)
        else:
            # adding the first root node
            newpath = cls._get_path(None, 1, 1)
        if not args:
            # creating the new object
            newobj = cls(**kwargs)
        else:
            if len(args) > 1:
                raise TypeError("Can only pass in one object argument to "
                        "add_root().")
            newobj = args[0]
        newobj.depth = 1
        newobj.path = newpath
        # saving the instance before returning it
        newobj.save()
        transaction.commit_unless_managed()
        return newobj

