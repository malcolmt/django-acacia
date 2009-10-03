"""
Tests for the hierarchical topic structure.
"""
from django import db, test

import models

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
        nodes = ["a/b/c",
                 "a/x/c",
                 "c/b/d",
                 "x/y/c"]
        for node in nodes:
            pieces = node.split("/")
            obj = models.Topic.objects.get_or_create(name=pieces[0], level=0)[0]
            for piece in pieces[1:]:
                obj = models.Topic.objects.get_or_create(name=piece,
                        parent=obj)[0]

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
        self.failUnless(models.Topic.objects.filter(name="c").count() > 1)
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
        self.assertEquals(topic1, topic2)
        self.assertEquals(topic2, topic3)
        self.assertEquals(topic3, topic4)
        self.assertEquals(topic4, topic5)

    def test_unicode(self):
        """
        Tests that the __unicode__() method displays the correct thing.
        """
        topic = models.Topic.objects.get(name="x", level=0)
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

    # TODO: merging nodes with common names isn't implemented yet. The
    # behaviour of this test is incorrect in any case (they shoul merge, not
    # error out).
    #def test_create_duplicate_entry(self):
    #    """
    #    Tests that an appropriate error is raised if the tree is manipulated in
    #    such a way that a duplicate full name would be created.
    #    """
    #    target = models.Topic.objects.get_by_full_name("a")
    #    node = models.Topic.objects.get_by_full_name("x")
    #    # Attempting to move "x" under "a" raises an error at the database
    #    # level because we already have an "a/x" node.
    #    self.assertRaises(db.IntegrityError, node.move_to, target)

    def test_create_by_full_name1(self):
        """
        Tests that creating a new node parented to an existing node using the
        full name works.
        """
        _, created = models.Topic.objects.get_or_create_by_full_name("a/b")
        self.failUnlessEqual(created, False)
        _, created = models.Topic.objects.get_or_create_by_full_name("a/b/e")
        self.failUnlessEqual(created, True)

    def test_create_by_full_name2(self):
        """
        Tests that creating a new node with new parents, using the full name,
        works.
        """
        _, created = models.Topic.objects.get_or_create_by_full_name("a/z/z")
        self.failUnlessEqual(created, True)
        node = models.Topic.objects.get_by_full_name("a/z/z")
        self.failUnlessEqual(unicode(node), u"a/z/z")

    def test_create_by_full_name3(self):
        """
        Tests that attempting to create a new node using a full name that
        already exists works as expected (the pre-existing node is returned and
        nothing new is created).
        """
        _, created = models.Topic.objects.get_or_create_by_full_name("c/b/d")
        self.failUnlessEqual(created, False)

    def test_create_by_full_name4(self):
        """
        Tests that creating a new node with existing parents, using the full
        name, normalises the full name properly (trailing and multiple
        separators).
        """
        node, created = models.Topic.objects.get_or_create_by_full_name(
                "a///b/e//")
        self.failUnlessEqual(created, True)
        self.failUnlessEqual(unicode(node), u"a/b/e")

