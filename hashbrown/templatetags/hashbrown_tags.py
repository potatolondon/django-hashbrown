from django import template
from ..utils import is_active

register = template.Library()


@register.tag
def ifswitch(parser, token):
    bits = token.split_contents()

    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires an argument" % bits[0])

    name = bits[1]

    try:
        user = bits[2]
    except IndexError:
        user = None

    nodelist_true = parser.parse(('else', 'endifswitch'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifswitch',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return SwitchNode(nodelist_true, nodelist_false, name, user)


class SwitchNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, name, user):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.name = template.Variable(name)

        if user:
            self.user = template.Variable(user)
        else:
            self.user = None

    def render(self, context):
        if self.user:
            user = self.user.resolve(context)
        else:
            user = None

        if not is_active(self.name.resolve(context), user):
            return self.nodelist_false.render(context)

        return self.nodelist_true.render(context)
