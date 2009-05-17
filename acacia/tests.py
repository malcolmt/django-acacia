"""
Tests for both the local treebeard overrides and the whole hierarchical topic
structure.
"""
from django import test

import models

class BaseTestSetup(object):
    """
    Common test support stuff, used by multiple test suites.
    """
    def setUp(self):
        """
        Load some potentially confusing topic data. There are four topics here
        are:
            - a/b/c
            - a/x/c
            - c/b/d
            - x/y/c

        The tests can use the fact that node "c" appears as the leaf of three
        similar, but different paths and that some nodes appear multiple times
        (and node "d" only appears once).

        """
        content = [
                {"data": {"name": "a"},
                "children": [
                    {"data": {"name": "b"},
                    "children": [
                        {"data": {"name": "c"}},
                    ]},
                    {"data": {"name": "x"},
                    "children": [
                        {"data": {"name": "c"}},
                    ]},
                ]},
                {"data": {"name": "c"},
                "children": [
                    {"data": {"name": "b"},
                    "children": [
                        {"data": {"name": "d"}},
                    ]},
                ]},
                {"data": {"name": "x"},
                "children": [
                    {"data": {"name": "y"},
                    "children": [
                        {"data": {"name": "c"}},
                    ]},
                ]},
        ]
        models.Topic.load_bulk(content)

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
        Tests that we can correctly retrieve a node given its full name. When
        the fulli name only contains a single component, there's a third
        processing path involved and this is what's tested here.
        """
        # Use "c" as the test here, since there's more than one Topic instance
        # with a name of "c", but only one topic whose full name is "c".
        self.failUnless(models.Topic.objects.filter(name="c").count() > 1)
        node = models.Topic.objects.get_by_full_name("c")
        self.assertEquals(unicode(node), u"c")

    def test_get_subtree(self):
        """
        Tests that the subtree rooted at a particular node (given by full name)
        is retrieved correctly.
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
        self.assertEquals(topic1, topic2)
        self.assertEquals(topic3, topic2)
        self.assertEquals(topic3, topic4)

    def test_unicode(self):
        """
        Tests that the __unicode__() method displays the correct thing.
        """
        topic = models.Topic.objects.get(name="x", depth=1)
        tree = models.Topic.get_tree(topic)
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
        node.move(target, "sorted-child")

        # The "a/x/c" node should have been moved to "a/b/x/c" as part of this.
        models.Topic.objects.get_by_full_name("a/b/x/c")

        # It will no longer be accessible under its old name.
        self.assertRaises(models.Topic.DoesNotExist,
                models.Topic.objects.get_by_full_name, "a/x/c")

class TreebeardTests(BaseTestSetup, test.TestCase):
    """
    Tests for my local modification/overrides to the default treebeard
    functionality.
    """
    def test_add_instance_as_child(self):
        """
        Tests that an unsaved Topic instance can be inserted as a child of some
        other node in the tree.
        """
        root = models.Topic.get_first_root_node()
        node = models.Topic(name="new child")
        root.add_child(node)
        # The instance should be saved as part of this process.
        self.failIf(node.pk is None)
        children = [unicode(obj) for obj in root.get_children()]
        expected = [u"a/b", u"a/new child", u"a/x"]
        self.assertEquals(children, expected)

    def test_add_instance_as_root(self):
        """
        Tests that an unsaved Topic instance can be inserted as a new root node.
        """
        node = models.Topic(name="new root")
        models.Topic.add_root(node)
        # The instance should be saved as part of this process.
        self.failIf(node.pk is None)
        root = [unicode(obj) for obj in models.Topic.get_root_nodes()]
        expected = [u"a", u"c", u"new root", u"x"]
        self.assertEquals(root, expected)

