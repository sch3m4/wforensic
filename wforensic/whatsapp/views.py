from os.path import basename
from os.path import getsize
from django.db.models import Q
from django.shortcuts import render_to_response
from wforensic.settings import CONTACTS_PER_PAGE,CHATS_PER_PAGE,MESSAGES_PER_PAGE,DATABASES
from pagination import pagination
from django.template.context import RequestContext
from models import WaContacts,Messages
from utils import get_latest_peers,get_top_peers,get_contacts_list,get_chat_list,get_chat_messages,get_messages_media,get_messages_gps,get_md5_file,get_sha1_file,get_activity_data

def index(request):
    
    try:
        wusers = WaContacts.objects.filter(is_whatsapp_user = 1).count()
        nwusers = WaContacts.objects.filter(is_whatsapp_user = 0).count()
        wasize = getsize(DATABASES['default']['NAME'])
        wafile = basename(DATABASES['default']['NAME'])
        wamd5 = get_md5_file(DATABASES['default']['NAME'])
        washa1 = get_sha1_file(DATABASES['default']['NAME'])
    except:
        wusers = Messages.objects.using('msgstore').values('key_remote_jid').distinct().count()
        nwusers = 0
        wasize = 0
        wafile = "Not found!"
        wamd5 = "N/A"
        washa1 = "N/A"
    
    dic = {
            'whatsappusers': wusers,
            'nonwhatsappusers': nwusers,
            'activity': get_activity_data(None),
            'fromme': Messages.objects.using('msgstore').filter(key_from_me = 1).count(),
            'tome': Messages.objects.using('msgstore').filter(key_from_me = 0).count(),
            'latest': get_latest_peers(),
            'toppeers': get_top_peers(),
            'msgsize': getsize(DATABASES['msgstore']['NAME']),
            'msgfile': basename(DATABASES['msgstore']['NAME']),
            'msgmd5': get_md5_file(DATABASES['msgstore']['NAME']),
            'msgsha1': get_sha1_file(DATABASES['msgstore']['NAME']),
            'wasize': wasize,
            'wafile': wafile,
            'wamd5': wamd5,
            'washa1': washa1,
            }

    return render_to_response('whatsapp/index.html',dic,context_instance=RequestContext(request))

def chatlist(request):
    
    
    chats = get_chat_list()
    chat_list = pagination(request,chats,CHATS_PER_PAGE)
    
    dic = {'chatlist': chat_list}
    return render_to_response('whatsapp/chatlist.html',dic,context_instance=RequestContext(request))

def messages(request):
    
    
    msgs = get_chat_messages()
    msgs_list = pagination(request,msgs,MESSAGES_PER_PAGE)
    
    dic = {'chatmessages': msgs_list,'PAG_TITLE': 'Messages List' }
    return render_to_response('whatsapp/chat.html',dic,context_instance=RequestContext(request))
        
def contacts(request):
    
    
    contact_list = get_contacts_list()
    contacts = pagination(request,contact_list,CONTACTS_PER_PAGE)
    
    try:
        wusers = WaContacts.objects.filter(is_whatsapp_user = 1).count()
        nwusers = WaContacts.objects.filter(is_whatsapp_user = 0).count()
    except:
        wusers = Messages.objects.using('msgstore').values('key_remote_jid').distinct().count()
        nwusers = 0

    dic = {'contactslist': contacts,
                'whatsappusers': wusers,
                'nonwhatsappusers': nwusers,
                }
    
    return render_to_response('whatsapp/contacts.html',dic,context_instance=RequestContext(request))

def single_chat(request,key):
    
    
    msgs = get_chat_messages(key)
    msgs_list = pagination(request,msgs,MESSAGES_PER_PAGE)
    
    dic = {'activity': get_activity_data(key),
                'chatmessages': msgs_list,
                'gps': Messages.objects.using('msgstore').exclude((Q(longitude = '0.0') | Q(latitude = '0.0'))),
                'media': Messages.objects.using('msgstore').exclude(media_url__isnull = True),
                'PAG_TITLE': 'Conversation'
                }
    return render_to_response('whatsapp/chat.html',dic,context_instance=RequestContext(request))

def messages_media(request):
    
    
    msgs = get_messages_media()
    msgs_list = pagination(request,msgs,MESSAGES_PER_PAGE)
    dic = {'chatmessages': msgs_list,'PAG_TITLE': 'Messages with media data'}
    
    return render_to_response('whatsapp/chat.html',dic,context_instance=RequestContext(request))

def messages_gps(request):
    
    
    msgs = get_messages_gps()
    msgs_list = pagination(request,msgs,MESSAGES_PER_PAGE)
    dic = {'chatmessages': msgs_list,'PAG_TITLE': 'Messages with GPS Data'}
    
    return render_to_response('whatsapp/chat.html',dic,context_instance=RequestContext(request))