from django import template
from django.db.models import Q
from wforensic.whatsapp.models import WaContacts,ChatList,Messages

register = template.Library()

class LoadHeader(template.Node):

    def __init__(self,varname):
        self.varname = varname
    
    def render(self,context):
        try:
            contacts = WaContacts.objects.count()
        except:
            contacts = Messages.objects.using('msgstore').values('key_remote_jid').distinct().count()
        
        ctx = {
               'contacts': contacts,
               'messages': Messages.objects.using('msgstore').count(),
               'chats': ChatList.objects.using('msgstore').count(),
               'gps': Messages.objects.using('msgstore').exclude((Q(longitude = '0.0') | Q(latitude = '0.0'))).count(),
               'media': Messages.objects.using('msgstore').exclude(media_url__isnull = True).count()
               }
               
        context[self.varname] = ctx
        return ''

@register.tag
def gettemplateheader(parser,token):
    _var = 'theader'
    return LoadHeader(_var)
