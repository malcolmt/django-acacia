# coding: utf-8
"""
Tests for the custom template acacia template tags.
"""

from django import template, test

from acacia import models


def setup_from_node_strings(nodes):
    """
    Convert a list of node names into a populated model hierarchy.
    """
    for node in nodes:
        models.Topic.objects.get_or_create_by_full_name(node)

def convert(template_string):
    compiled = template.Template(template_string)
    return compiled.render(template.Context({}))

class TreeTrunkErrorTests(test.TestCase):
    def test_invalid_app_name(self):
        self.assertRaises(template.TemplateSyntaxError, convert,
                "{% load acacia %}{% treetrunk bad.Topic %}")

    def test_invalid_model_name(self):
        self.assertRaises(template.TemplateSyntaxError, convert,
                "{% load acacia %}{% treetrunk acacia.BadName %}")

    def test_non_integer_level_value(self):
        self.assertRaises(template.TemplateSyntaxError, convert,
                "{% load acacia %}{% treetrunk acacia.Topic bad %}")

    def test_negative_level_value(self):
        self.assertRaises(template.TemplateSyntaxError, convert,
                "{% load acacia %}{% treetrunk acacia.Topic -1 %}")

    def test_zero_level_value(self):
        self.assertRaises(template.TemplateSyntaxError, convert,
                "{% load acacia %}{% treetrunk acacia.Topic 0 %}")

    def test_too_many_arguments(self):
        self.assertRaises(template.TemplateSyntaxError, convert,
                "{% load acacia %}{% treetrunk acacia.Topic 2 extra %}")

    def test_too_few_arguments(self):
        self.assertRaises(template.TemplateSyntaxError, convert,
                "{% load acacia %}{% treetrunk %}")


class TreeTrunkMiscTests(test.TestCase):
    def test_empty_tree(self):
        """
        No content should result in nothing being inserted into the template,
        not an empty unordered list element.
        """
        self.failIf(convert("{% load acacia %}{% treetrunk acacia.Topic %}"))

    def test_html_sensitive_content(self):
        setup_from_node_strings([">/&amp;/<"])
        output = convert("{% load acacia %}{% treetrunk acacia.Topic 5 %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>&gt;
                <ul><li>&amp;amp;
                    <ul><li>&lt;</li></ul>
                </li></ul>
            </li></ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot     %s\n\nExpected %s" %
                (output, expected))


class TreeTrunkSingleRootTests(test.TestCase):
    def setUp(self):
        nodes = [
                "root1/child1/grandchild1",
                "root1/child1/grandchild2",
                "root1/child2/grandchild1",
                "root1/child2/grandchild2",
                "root1/child3/grandchild1",
        ]
        setup_from_node_strings(nodes)

    def test_single_level(self):
        output = convert("{% load acacia %}{% treetrunk acacia.Topic 1 %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>root1</li>
            </ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot     %s\n\nExpected %s" %
                (output, expected))

    def test_two_levels(self):
        output = convert("{% load acacia %}{% treetrunk acacia.Topic 2 %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>root1
                <ul><li>child1</li>
                    <li>child2</li>
                    <li>child3</li>
                </ul></li>
            </ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot      %s\n\nExpected %s" %
                (output, expected))

    def test_three_levels(self):
        output = convert("{% load acacia %}{% treetrunk acacia.Topic 3 %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>root1
                <ul><li>child1
                    <ul><li>grandchild1</li>
                        <li>grandchild2</li></ul></li>
                    <li>child2
                    <ul><li>grandchild1</li>
                        <li>grandchild2</li></ul></li>
                    <li>child3
                    <ul><li>grandchild1</li></ul></li>
                </ul></li>
            </ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot      %s\n\nExpected %s" %
                (output, expected))

    def test_more_levels_than_nodes(self):
        output = convert("{% load acacia %}{% treetrunk acacia.Topic 10 %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>root1
                <ul><li>child1
                    <ul><li>grandchild1</li>
                        <li>grandchild2</li></ul></li>
                    <li>child2
                    <ul><li>grandchild1</li>
                        <li>grandchild2</li></ul></li>
                    <li>child3
                    <ul><li>grandchild1</li></ul></li>
                </ul></li>
            </ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot      %s\n\nExpected %s" %
                (output, expected))

    def test_default_level(self):
        output = convert("{% load acacia %}{% treetrunk acacia.Topic %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>root1
                <ul><li>child1</li>
                    <li>child2</li>
                    <li>child3</li>
                </ul></li>
            </ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot      %s\n\nExpected %s" %
                (output, expected))


class TreeTrunkFullContentTests(test.TestCase):
    def setUp(self):
        nodes = [
                "root1/child1/grandchild1",
                "root1/child1/grandchild2",
                "root1/child1/grandchild3",
                "root1/child2/grandchild1",
                "root1/child2/grandchild2",
                "root1/child3/grandchild1",
                "root1/child4",
                "root2/child1/grandchild1",
                "root2/child2/grandchild1",
                "root2/child2/grandchild2/other",
                "root3"
        ]
        setup_from_node_strings(nodes)

    def test_one_level(self):
        output = convert("{% load acacia %}{% treetrunk acacia.Topic 1 %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>root1</li>
                <li>root2</li>
                <li>root3</li>
            </ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot      %s\n\nExpected %s" %
                (output, expected))

    def test_three_levels(self):
        output = convert("{% load acacia %}{% treetrunk acacia.Topic 3 %}")
        output = output.replace("\n", "")
        expected = """
            <ul>
                <li>root1
                <ul><li>child1
                    <ul><li>grandchild1</li>
                        <li>grandchild2</li>
                        <li>grandchild3</li></ul></li>
                    <li>child2
                    <ul><li>grandchild1</li>
                        <li>grandchild2</li></ul></li>
                    <li>child3
                    <ul><li>grandchild1</li></ul></li>
                    <li>child4</li>
                </ul></li>
                <li>root2
                <ul><li>child1
                    <ul><li>grandchild1</li></ul></li>
                    <li>child2
                    <ul><li>grandchild1</li>
                        <li>grandchild2</li></ul></li>
                </ul></li>
                <li>root3</li>
            </ul>""".replace("\n", "").replace(" ", "")
        self.assertEqual(output, expected, "\nGot      %s\n\nExpected %s" %
                (output, expected))

