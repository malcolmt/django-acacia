from django import template
from django.db import models
from django.utils.html import escape

register = template.Library()

class TreeTrunkNode(template.Node):
    """
    Render the first few levels of a topic tree as an unordered HTML list.
    """
    def __init__(self, model_name, levels=2):
        super(TreeTrunkNode, self).__init__()
        app_name, model_name = model_name.rsplit(".", 1)
        self.model = models.get_model(app_name, model_name)
        if self.model is None:
            raise template.TemplateSyntaxError("Bad app or model name: %s" %
                    model_name)
        self.levels = levels

    def render(self, context):
        current_level = 0
        pieces = [u"<ul>"]
        first = True
        for node in self.model.tree.filter(level__lt=self.levels):
            diff = node.level - current_level
            if diff == 0:
                if first:
                    first = False
                else:
                    pieces.append(u"</li>")
                pieces.append(u"<li>%s" % escape(node.name))
            elif diff > 0:
                pieces.append(u"<ul>\n<li>%s" % escape(node.name))
                current_level += 1
            else:
                pieces.append(u"</li></ul></li>\n<li>%s" % escape(node.name))
                current_level -= 1
        if len(pieces) == 1:
            # No content in the tree means no output.
            return u""
        while current_level:
            pieces.append(u"</li></ul>")
            current_level -= 1
        pieces.append(u"</li>\n</ul>")
        return u"\n".join(pieces)


@register.tag
def treetrunk(dummy, token):
    """
    Called as {% treetops app.SomeModel N %} to display the first N levels of
    the Topic-derived tree class, SomeModel. The number of levels (N) can be
    omitted and defaults to 2 (root nodes and their children).
    """
    bits = token.split_contents()
    if len(bits) == 3:
        try:
            level = int(bits[2])
            if level <= 0:
                raise ValueError
        except ValueError:
            raise template.TemplateSyntaxError("Level argument ('%s') wasn't "
                    "a positive integer." % bits[2])
    elif len(bits) == 2:
        level = 2
    else:
        raise template.TemplateSyntaxError("Invalid number of arguments (%d, "
                "expected 1 or 2)." % (len(bits) - 1))
    return TreeTrunkNode(bits[1], level)

