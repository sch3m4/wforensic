
from os.path import basename
from os.path import getsize
from os import access,W_OK
from pagination import pagination
from datetime import datetime

from django.db.models import Q
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template.context import RequestContext

from wforensic.settings import CONTACTS_PER_PAGE, CHATS_PER_PAGE, MESSAGES_PER_PAGE, DATABASES
from models import WaContacts, Messages
from utils import get_latest_peers, get_top_peers, get_contacts_list, get_chat_list, get_chat_messages, get_messages_media
from utils import get_messages_gps, get_md5_file, get_sha1_file, get_activity_data, get_contacts_xml, timestamp2utc


def index(request):
    """
    Default view
    """

    try:
        wusers = WaContacts.objects.filter(is_whatsapp_user=1).count()
        nwusers = WaContacts.objects.filter(is_whatsapp_user=0).count()
        wasize = getsize(DATABASES['default']['NAME'])
        wafile = basename(DATABASES['default']['NAME'])
        wamd5 = get_md5_file(DATABASES['default']['NAME'])
        washa1 = get_sha1_file(DATABASES['default']['NAME'])
        waperm = "<b><font color=\"red\">YES (check file permissons)</font></b>" if access(DATABASES['default']['NAME'],W_OK) is True else "<b><font color=\"blue\">No</font></b>" 
    except:
        wusers = Messages.objects.using('msgstore').values('key_remote_jid').distinct().count()
        nwusers = 0
        wasize = 0
        wafile = "Not found!"
        wamd5 = "N/A"
        washa1 = "N/A"
        waperm = 'N/A'

    msgperm = "<b><font color=\"red\">YES (check file permissons)</font></b>" if access(DATABASES['msgstore']['NAME'],W_OK) is True else "<b><font color=\"blue\">No</font></b>"

    dic = {
            'whatsappusers': wusers,
            'nonwhatsappusers': nwusers,
            'activity': get_activity_data(None),
            'fromme': Messages.objects.using('msgstore').filter(key_from_me=1).count(),
            'tome': Messages.objects.using('msgstore').filter(key_from_me=0).count(),
            'latest': get_latest_peers(),
            'toppeers': get_top_peers(),
            'msgsize': getsize(DATABASES['msgstore']['NAME']),
            'msgfile': basename(DATABASES['msgstore']['NAME']),
            'msgperm': msgperm,
            'msgmd5': get_md5_file(DATABASES['msgstore']['NAME']),
            'msgsha1': get_sha1_file(DATABASES['msgstore']['NAME']),
            'wasize': wasize,
            'wafile': wafile,
            'wamd5': wamd5,
            'waperm': waperm,
            'washa1': washa1,
            }

    return render_to_response('whatsapp/index.html', dic, context_instance=RequestContext(request))


def chatlist(request):
    """
    Shows the entire chat list
    """

    chats = get_chat_list()
    chat_list = pagination(request, chats, CHATS_PER_PAGE)

    dic = {'chatlist': chat_list}
    return render_to_response('whatsapp/chatlist.html', dic, context_instance=RequestContext(request))


def messages(request):

    msgs = get_chat_messages()
    msgs_list = pagination(request, msgs, MESSAGES_PER_PAGE)

    dic = {'chatmessages': msgs_list, 'PAG_TITLE': 'Messages List'}
    return render_to_response('whatsapp/chat.html', dic, context_instance=RequestContext(request))


def contact_profile(request, key):
    """
    Shows the contact profile
    """

    ret = {}

    ret['number'] = key.split('@')[0][2:]
    ret['jid'] = key
    ret['activity'] = get_activity_data(key)
    ret['whatsapp'] = 0

    ret['messages'] = Messages.objects.using('msgstore').filter(key_remote_jid=key).count()
    tstamp = Messages.objects.using('msgstore').filter(key_remote_jid=key).values('timestamp').order_by('timestamp')[0:1][0]['timestamp']
    ret['first_seen'] = timestamp2utc(float(tstamp) / 1000)
    tstamp = Messages.objects.using('msgstore').filter(key_remote_jid=key).values('timestamp').order_by('-timestamp')[0:1][0]['timestamp']
    ret['last_seen'] = timestamp2utc(float(tstamp) / 1000)
    ret['media_messages'] = Messages.objects.using('msgstore').filter(key_remote_jid=key).exclude(media_url__isnull=True).count()
    ret['gps_messages'] = Messages.objects.using('msgstore').filter(key_remote_jid=key).exclude((Q(longitude='0.0') | Q(latitude='0.0'))).count()

    # no wa_contacts table available
    if not 'wa_contacts' in connection.introspection.table_names():
        ret['name'] = 'Not in contacts'
        ret['status'] = 'N/A'
        if ret['messages'] > 0:
            ret['whatsapp'] = 1
    else:
        ret['name'] = WaContacts.objects.filter(jid=key).values('display_name')[0]['display_name']
        ret['whatsapp'] = WaContacts.objects.filter(jid=key).values('is_whatsapp_user')[0]['is_whatsapp_user']
        ret['status'] = WaContacts.objects.filter(jid=key).values('status')[0]['status']

    return render_to_response('whatsapp/profile.html', {'contact': ret, 'activity': ret['activity']}, context_instance=RequestContext(request))


def contacts_download(request):
    """
    Generates the contact list in XML format
    """

    contacts = get_contacts_xml()
    xml = render_to_string('whatsapp/contacts.xml', {'contacts': contacts, 'date': datetime.now().replace(microsecond=0)})

    response = HttpResponse(xml, mimetype='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=contacts.xml'

    return response


def contacts(request):
    """
    Shows all contacts
    """

    contact_list = get_contacts_list()
    contacts = pagination(request, contact_list, CONTACTS_PER_PAGE)

    try:
        wusers = WaContacts.objects.filter(is_whatsapp_user=1).count()
        nwusers = WaContacts.objects.filter(is_whatsapp_user=0).count()
    except:
        wusers = Messages.objects.using('msgstore').exclude((Q(key_remote_jid=-1) | Q(key_remote_jid__startswith="Server"))).values('key_remote_jid').distinct().count()
        nwusers = 0

    dic = {
        'contactslist': contacts,
        'whatsappusers': wusers,
        'nonwhatsappusers': nwusers,
        }

    return render_to_response('whatsapp/contacts.html', dic, context_instance=RequestContext(request))


def single_chat(request, key):
    """
    Shows a single chat with a contact given by his jid (key)
    """

    msgs = get_chat_messages(key)
    msgs_list = pagination(request, msgs, MESSAGES_PER_PAGE)

    dic = {
        'chatmessages': msgs_list,
        'gps': Messages.objects.using('msgstore').exclude((Q(longitude='0.0') | Q(latitude='0.0'))),
        'media': Messages.objects.using('msgstore').exclude(media_url__isnull=True),
        'PAG_TITLE': 'Conversation'
        }

    return render_to_response('whatsapp/chat.html', dic, context_instance=RequestContext(request))


def messages_media(request):
    """
    Shows all messages containing media
    """

    msgs = get_messages_media()
    msgs_list = pagination(request, msgs, MESSAGES_PER_PAGE)

    dic = {
        'chatmessages': msgs_list,
        'PAG_TITLE': 'Messages with media data'
        }

    return render_to_response('whatsapp/chat.html', dic, context_instance=RequestContext(request))


def messages_gps(request):
    """
    Shows all messages containing GPS data
    """

    msgs = get_messages_gps()
    msgs_list = pagination(request, msgs, MESSAGES_PER_PAGE)
    dic = {
        'chatmessages': msgs_list,
        'PAG_TITLE': 'Messages with GPS Data'
        }

    return render_to_response('whatsapp/chat.html', dic, context_instance=RequestContext(request))
