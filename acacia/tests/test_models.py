"""
Tests for the hierarchical topic structure.
"""
from django import db, test

from acacia import models, signals

class BaseTestSetup(object):
    """
    Common test support stuff, used by multiple test suites.
    """
    def setUp(self):
        """
        Load some potentially confusing topic data.

        The tests can use the fact that node "c" appears as the leaf of multiple
        similar, but different paths and that some nodes appear multiple times
        (and node "d" only appears once).
        """
        # pylint: disable-msg=R0201
        nodes = ["a/b/c",
                 "a/x/c",
                 "c/b/d",
                 "x/y/c"]

        # Intentionally not using get_or_create_by_full_name() here, since
        # that's one of the things needing testing.
        for node in nodes:
            pieces = node.split("/")
            obj = models.Topic.objects.get_or_create(name=pieces[0], level=0)[0]
            for piece in pieces[1:]:
                obj = models.Topic.objects.get_or_create(name=piece,
                        parent=obj)[0]

        self.signals = []

    def tearDown(self):
        self.signals = []

    def signal_catcher(self, sender, **kwargs):
        """
        Used to record the emission of any signal(s) during the test.
        """
        self.signals.append((sender, kwargs))


class TopicTest(BaseTestSetup, test.TestCase):
    """
    Tests for the hierarchical topic implementation.
    """


    def test_bad_full_name(self):
        """
        Tests that retrieving a non-existent full name raises the correct
        exception.
        """
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "w")
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "a/y")
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "x/y/d")
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "x/x/c")

    def test_get_by_full_name1(self):
        """
        Tests that we can correctly retrieve a node given its full name. This
        tests the simple case (where the final portion of the full name is
        unique).
        """
        node = models.Topic.objects.get_by_full_name("c/b/d")
        self.assertEquals(unicode(node), u"c/b/d")

    def test_get_by_full_name2(self):
        """
        Tests that we can correctly retrieve a node given its full name. This
        version looks for a node whose final component matches more than one
        topic, so some extra computation is required in the implementation.
        """
        node = models.Topic.objects.get_by_full_name("a/b/c")
        self.assertEquals(unicode(node), u"a/b/c")

    def test_get_by_full_name3(self):
        """
        Tests that we can correctly retrieve a node given its full name. In
        this case, we're testing the potential edge-case where the name has
        only a single component.
        """
        # Use "c" as the test here, since there's more than one Topic instance
        # with a name of "c", but only one topic whose full name is "c".
        self.assertTrue(models.Topic.objects.filter(name="c").count() > 1)
        node = models.Topic.objects.get_by_full_name("c")
        self.assertEquals(unicode(node), u"c")

    def test_get_subtree(self):
        """
        Tests that the subtree rooted at a particular node (given by full name)
        is retrieved (and sorted) correctly.
        """
        result = [unicode(obj) for obj in models.Topic.objects.get_subtree("a")]
        expected = [u"a", u"a/b", u"a/b/c", u"a/x", u"a/x/c"]
        self.assertEquals(result, expected)

    def test_name_normalisation(self):
        """
        Tests that consecutive separators in the full name are collapsed into a
        single separator (e.g. foo/bar and foo//bar are treated the same).
        """
        topic1 = models.Topic.objects.get_by_full_name("c/b/d")
        topic2 = models.Topic.objects.get_by_full_name("c//b/d")
        topic3 = models.Topic.objects.get_by_full_name("c/b/d/")
        topic4 = models.Topic.objects.get_by_full_name("/c/b/d/")
        topic5 = models.Topic.objects.get_by_full_name("///c/b/d////")
        topic6 = models.Topic.objects.get_by_full_name("c///b//d")
        self.assertEquals(topic1, topic2)
        self.assertEquals(topic2, topic3)
        self.assertEquals(topic3, topic4)
        self.assertEquals(topic4, topic5)
        self.assertEquals(topic5, topic6)

    def test_unicode(self):
        """
        Tests that the __unicode__() method displays the correct thing.
        """
        topic = models.Topic.objects.get(name="x", parent=None)
        tree = topic.get_descendants(True)
        result = [unicode(obj) for obj in tree]
        expected = [u"x", u"x/y", u"x/y/c"]
        self.assertEquals(result, expected)

    def test_change_parent(self):
        """
        Tests that setting a new parent for a node with children causes the
        children's full names to be updated appropriately.
        """
        # Move the "x" in "a/x" to be a child of "a/b" (so it becomes "a/b/x").
        target = models.Topic.objects.get_by_full_name("a/b")
        node = models.Topic.objects.get_by_full_name("a/x")
        node.move_to(target)

        # The "a/x/c" node should have been moved to "a/b/x/c" as part of this.
        models.Topic.objects.get_by_full_name("a/b/x/c")

        # It will no longer be accessible under its old name.
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "a/x/c")

    def test_simple_merge_nodes(self):
        """
        Tests that nodes merge seamlessly and the right signal is raised if one
        subtree is moved on top of another.
        """
        # Move x/y to underneath a/, which has to merge with the existing a/x/
        # subtree.
        target = models.Topic.objects.get_by_full_name("a")
        node = models.Topic.objects.get_by_full_name("x")
        old_id = node.id
        surviving_node = models.Topic.objects.get_by_full_name("a/x")
        signals.pre_merge.connect(self.signal_catcher)
        node.merge_to(target)
        signals.pre_merge.disconnect(self.signal_catcher)
        self.assertEqual(len(self.signals), 1)
        merge_pairs = self.signals[0][1]["merge_pairs"]
        self.assertEqual(len(merge_pairs), 1)
        self.assertEqual(merge_pairs[0], (old_id, surviving_node.id))

    def test_multiple_merge_nodes(self):
        """
        A merge_to() test where more there are multiple pairs of nodes that are
        merged.
        """
        models.Topic.objects.get_or_create_by_full_name("a/x/y/z")
        target = models.Topic.objects.get_by_full_name("a")
        node = models.Topic.objects.get_by_full_name("x")
        old_ids = (node.id, node.children.all()[0].id)
        pivot = models.Topic.objects.get_by_full_name("a/x/y")
        signals.pre_merge.connect(self.signal_catcher)
        node.merge_to(target)
        signals.pre_merge.disconnect(self.signal_catcher)
        self.assertEqual(len(self.signals), 1)
        merge_pairs = self.signals[0][1]["merge_pairs"]
        self.assertEqual(len(merge_pairs), 2)
        self.assertEqual(merge_pairs[0], (old_ids[0], pivot.parent_id))
        self.assertEqual(merge_pairs[1], (old_ids[1], pivot.id))
        try:
            models.Topic.objects.get_by_full_name("a/x/y/c")
        except models.Topic.DoesNotExist:
            self.fail("Node wasn't moved to correct location.")

    def test_merge_without_overlap(self):
        """
        Tests that calling merge_to() when no merge is required acts as a move.
        """
        models.Topic.objects.get_or_create_by_full_name("c/b/d/e")
        target = models.Topic.objects.get_by_full_name("a")
        node = models.Topic.objects.get_by_full_name("c/b/d")
        signals.pre_merge.connect(self.signal_catcher)
        signals.pre_move.connect(self.signal_catcher)
        node.merge_to(target)
        signals.pre_merge.disconnect(self.signal_catcher)
        self.assertEqual(len(self.signals), 1)
        signal_dict = self.signals[0][1]
        self.assertEqual(signal_dict["signal"], signals.pre_move)
        self.assertEqual(signal_dict["moving"][0][0].id, node.id)
        self.assertEqual(signal_dict["moving"][0][1].id, target.id)
        try:
            models.Topic.objects.get_by_full_name("a/d")
        except models.Topic.DoesNotExist:
            self.fail("Node wasn't moved to correct location.")
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "c/b/d")
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "c/b/d/e")

    def test_merge_moves_all_subtrees(self):
        """
        Tests that if a merge_to() call results in some merges at the top of
        the subtree, *all* unmerged children are moved correctly (descendants
        that aren't direct children of a merged node are the problematic cases).
        """
        z_child = models.Topic.objects.get_or_create_by_full_name("x/c/z")[0]
        parent = models.Topic.objects.get_by_full_name("a")
        node = models.Topic.objects.get_by_full_name("x")
        y_child = models.Topic.objects.get_by_full_name("x/y")
        node.merge_to(parent)
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "x")
        try:
            node = models.Topic.objects.get_by_full_name("a/x/c/z")
        except models.Topic.DoesNotExist:
            self.fail("Didn't move x/c/z node correctly.")
        self.assertEqual(node.id, z_child.id)
        try:
            node = models.Topic.objects.get_by_full_name("a/x/y")
        except models.Topic.DoesNotExist:
            self.fail("Didn't move x/y node correctly.")
        self.assertEqual(node.id, y_child.id)

    def test_move_is_not_merge(self):
        """
        Tests that calling move_to() for an overlapping move (creating nodes
        with duplicate full names) correctly raises an error.
        """
        target = models.Topic.objects.get_by_full_name("a")
        node = models.Topic.objects.get_by_full_name("x")
        self.assertRaises(db.IntegrityError, node.move_to, target)

    def test_create_by_full_name1(self):
        """
        Tests that creating a new node parented to an existing node using the
        full name works.
        """
        _, created = models.Topic.objects.get_or_create_by_full_name("a/b")
        self.assertEqual(created, False)
        _, created = models.Topic.objects.get_or_create_by_full_name("a/b/e")
        self.assertEqual(created, True)

    def test_create_by_full_name2(self):
        """
        Tests that creating a new node with new parents, using the full name,
        works.
        """
        _, created = models.Topic.objects.get_or_create_by_full_name("a/z/z")
        self.assertEqual(created, True)
        node = models.Topic.objects.get_by_full_name("a/z/z")
        self.assertEqual(unicode(node), u"a/z/z")

    def test_create_by_full_name3(self):
        """
        Tests that attempting to create a new node using a full name that
        already exists works as expected (the pre-existing node is returned and
        nothing new is created).
        """
        _, created = models.Topic.objects.get_or_create_by_full_name("c/b/d")
        self.assertEqual(created, False)

    def test_create_by_full_name4(self):
        """
        Tests that creating a new node with existing parents, using the full
        name, normalises the full name properly (trailing and multiple
        separators).
        """
        node, created = models.Topic.objects.get_or_create_by_full_name(
                "a///b/e//")
        self.assertEqual(created, True)
        self.assertEqual(unicode(node), u"a/b/e")

    def test_create_by_full_name5(self):
        """
        Tests that creating a new node with a new root works as expected.
        """
        _, created = models.Topic.objects.get_or_create_by_full_name("j/k/l")
        self.assertEqual(created, True)

    def test_create_duplicate_entry(self):
        """
        Tests that creating a node that already exists results in an error.
        """
        parent = models.Topic.objects.get(name="a", parent=None)
        self.assertRaises(db.IntegrityError, models.Topic.objects.create,
                name="b", parent=parent)

