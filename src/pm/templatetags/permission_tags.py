from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_user_perm(context, user, project):
    try:
        if hasattr(user, 'get_all_permissions'):
            func = getattr(user, 'get_all_permissions')
            return func(project)
        return None
    except Exception as e:
        return None


@register.tag(name='hasperm')
def permission(parser, token):
    try:
        tag_name, username, perm, object = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 4 arguments" % token.contents.split()[0])

    if not (perm[0] == perm[-1] and perm[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument perm should be in quotes" % token.contents.split()[0])

    nodelist = parser.parse(('endhasperm',))
    parser.delete_first_token()
    return PermissionNode(nodelist, username, perm, object)


class PermissionNode(template.Node):
    def __init__(self, nodelist, username, perm, object):
        self.nodelist = nodelist
        self.username = username
        self.perm = perm
        self.object = object

    def render(self, context):
        user = template.Variable(self.username).resolve(context)
        object = template.Variable(self.object).resolve(context)

        content = self.nodelist.render(context)
        
        if hasattr(user, 'has_perm'):
            func = getattr(user, 'has_perm')
            if func(self.perm[1:-1], object):
                return content 
        return ""

