from django import template
from django.db import connection

register = template.Library()


class GotContactsDB(template.Node):

    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        if not 'wa_contacts' in connection.introspection.table_names():
            context[self.varname] = 0
        else:
            context[self.varname] = 1

        return ''


@register.tag
def gotcontactsdb(parser, token):
    return GotContactsDB('gotcontacts')
