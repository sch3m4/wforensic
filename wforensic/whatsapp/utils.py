try:
    import sys
    import string
    import base64
    import hashlib
    from operator import itemgetter
    from os.path import basename, isfile
    from datetime import datetime
    from django.db import models
    from django.db.models import Q
    from django.db import connection
    from models import WaContacts, ChatList, Messages
    from wforensic.settings import LATEST_PEERS, TOP_PEERS, THUMBS_ROOT, THUMBS_URL
except ImportError, e:
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)


def timestamp2utc(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime("%Y/%m/%d %H:%M:%S")


def set_media(wa_type, data, jid, idmsg, raw = False):
    if jid[:1] == '+':
        jid = jid[1:]
    if wa_type != '0':
        path = THUMBS_ROOT + jid.replace('@','.') + '.' + str(idmsg) + '.png'
        if not isfile(path):
            try:
                if raw is False:
                    content = base64.b64decode(data)
                else:
                    content = data
            except:
                return ''
            fout = open(path, "w")
            fout.write(content)
            fout.close()
            
        return THUMBS_URL + basename(path)
    else:
        return ''


def get_md5_file(path):
    md5 = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), ''):
                md5.update(chunk)
    except:
        return 'Cannot access file'
    return md5.hexdigest()


def get_sha1_file(path):
    md5 = hashlib.sha1()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), ''):
                md5.update(chunk)
    except:
        return 'Cannot access file'
    return md5.hexdigest()


def get_latest_peers(latest=LATEST_PEERS):
    if latest > 0:
        peers = [c['key_remote_jid'] for c in Messages.objects.using('msgstore').values('key_remote_jid').exclude(Q(key_remote_jid=-1) | Q(key_remote_jid__icontains='-') | Q(key_remote_jid__startswith='Server')).annotate(models.Max('timestamp')).order_by('-timestamp__max')[:latest]]
    else:
        peers = [c['key_remote_jid'] for c in Messages.objects.using('msgstore').values('key_remote_jid').exclude(Q(key_remote_jid=-1) | Q(key_remote_jid__icontains='-') | Q(key_remote_jid__startswith='Server')).annotate(models.Max('timestamp')).order_by('-timestamp__max')]

    ret = []

    for peer in peers:
        data = Messages.objects.using('msgstore').filter(key_remote_jid=peer).values('data', '_id', 'media_wa_type','raw_data').annotate(models.Max('timestamp')).order_by('-timestamp__max')[:1][0]

        try:
            peer_data = WaContacts.objects.filter(jid=peer).values('display_name', 'status')[0]
        except:
            peer_data = {}
            peer_data['display_name'] = 'N/A'
            peer_data['status'] = 'N/A'

        newdata = {'key_remote_jid': peer,
                    'media_wa_type': data['media_wa_type'],
                    '_id': data['_id'],
                    'timestamp': timestamp2utc(float(data['timestamp__max']) / 1000),
                    'data': data['data'],
                    'display_name': peer_data['display_name'],
                    'status': peer_data['status'],
                    'number': '+' + peer.split('@')[0]
                    }
        
        if data['data'] is not None:
            newdata['img'] = set_media(data['media_wa_type'], data['data'], peer , str(data['_id']), False)
        elif data['raw_data'] is not None:
            newdata['img'] = set_media(data['media_wa_type'], data['raw_data'], peer, str(data['_id']), True)
        
        if newdata['data'] is None:
            newdata['data'] = ''

        ret.append(newdata)

    return ret


def get_top_peers(top=TOP_PEERS):
    if top > 0:
        _tmp = Messages.objects.using('msgstore').values('key_remote_jid').exclude((Q(key_remote_jid=-1) | Q(key_remote_jid__icontains='-') | Q(key_remote_jid__startswith="Server"))).annotate(models.Count('key_remote_jid')).order_by('-key_remote_jid__count')[:top]
    else:
        _tmp = Messages.objects.using('msgstore').values('key_remote_jid').exclude((Q(key_remote_jid=-1) | Q(key_remote_jid__icontains='-') | Q(key_remote_jid__startswith="Server"))).annotate(models.Count('key_remote_jid')).order_by('-key_remote_jid__count')
    ret = []
    for item in _tmp:

        try:
            _aux = WaContacts.objects.filter(jid=item['key_remote_jid']).values('number', 'display_name', 'status', 'jid')[0]
        except:
            _aux = {}
            _aux['number'] = '+' + item['key_remote_jid'].split('@')[0]
            _aux['display_name'] = "N/A"
            _aux['status'] = "N/A"
            _aux['jid'] = item['key_remote_jid']

        _aux['msgs'] = item['key_remote_jid__count']
        ret.append(_aux)
    return ret


def get_contacts_xml():

    ret = []

    # wa.db not available
    if not 'wa_contacts' in connection.introspection.table_names():
        _aux = Messages.objects.using('msgstore').values('key_remote_jid').exclude((Q(key_remote_jid=-1) | Q(key_remote_jid__icontains='-') | Q(key_remote_jid__startswith="Server"))).annotate(models.Count('key_remote_jid'))
        for item in _aux:
            item['number'] = item['key_remote_jid'].split('@')[0][2:]
            item['display_name'] = 'N/A'
            item['messages'] = item['key_remote_jid__count']
            item['whatsapp'] = "Yes"
            ret.append(item)
    else:
        _aux = WaContacts.objects.values('number', 'display_name', 'status', 'jid', 'is_whatsapp_user')
        for item in _aux:
            if item['status'] is None:
                continue
            item['messages'] = Messages.objects.using('msgstore').filter(key_remote_jid=item['jid']).count()
            if item['is_whatsapp_user']:
                item['whatsapp'] = 'Yes'
            else:
                item['whatsapp'] = 'No'
            ret.append(item)

    return ret


def get_contacts_list():

    if not 'wa_contacts' in connection.introspection.table_names():
        _list = Messages.objects.using('msgstore').exclude(Q(key_remote_jid=-1) | Q(key_remote_jid__startswith="Server") | Q(key_remote_jid__icontains='-')).values('key_remote_jid').distinct()
        _non = 1
    else:
        _list = WaContacts.objects.exclude(Q(number__isnull=True) | Q(status__isnull=True)).values('jid', 'number', 'display_name', 'status', 'is_whatsapp_user').order_by('display_name')
        _non = 0

    _ret = []
    for item in _list:
        if _non == 1:
            item['is_whatsapp_user'] = 1
            item['display_name'] = 'N/A'
            item['status'] = 'N/A'
            item['number'] = '+' + item['key_remote_jid'].split('@')[0]
            item['jid'] = item['key_remote_jid']

        try:
            item['messages'] = Messages.objects.using('msgstore').filter(key_remote_jid=item['jid']).count()
        except:
            item['messages'] = 0

        _ret.append(item)

    return _ret


def get_chat_list():
    _tmp = ChatList.objects.using('msgstore').values('key_remote_jid')
    _aux = [d['key_remote_jid'] for d in _tmp]

    _ret = []
    for item in _aux:
        if not 'wa_contacts' in connection.introspection.table_names():
            num = item.split('@')[0]
            _name = {'display_name': '', 'number': '+' + num if item[:1] in string.digits else num }
        else:
            _name = WaContacts.objects.filter(jid=item).values('display_name', 'number')[0]

        _count = Messages.objects.using('msgstore').filter(key_remote_jid=item).count()
        try:
            _tmp = Messages.objects.using('msgstore').filter(key_remote_jid=item).values('data', 'raw_data' 'media_wa_type', '_id').annotate(models.Max('timestamp')).order_by('-timestamp__max')[0]
        except:
            continue
        
        try:
            _latest = _tmp['data']
            if _latest is None:
                _latest = ''
        except:
            _latest = ''

        try:
            _tstamp = timestamp2utc(float(_tmp['timestamp__max']) / 1000)
        except Exception,e:
            print "ERROR: %s" % str(e)
            _tstamp = 'Unknown'

            set_media(_tmp['media_wa_type'], _tmp['data'], str(_tmp['_id']))

        toadd = {'jid': item, 'display_name': _name['display_name'], 'number': _name['number'], 'count': _count, 'latest': _latest, 'timestamp': _tstamp}

        if _tmp['data'] is not None:
            toadd['img'] = set_media(_tmp['media_wa_type'], _tmp['data'], item , str(_tmp['_id']), False)
        elif _tmp['raw_data'] is not None:
            toadd['img'] = set_media(_tmp['media_wa_type'], _tmp['raw_data'], item, str(_tmp['_id']), True)
            
        _ret.append(toadd)

    return _ret


def get_chat_messages(jid = None):

    if jid is not None:
        _msgs = Messages.objects.using('msgstore').filter(key_remote_jid=jid).values('media_wa_type', '_id', 'key_remote_jid', 'key_from_me', 'data', 'timestamp', 'received_timestamp', 'media_url', 'latitude', 'longitude', 'raw_data').order_by('-received_timestamp')
    else:
        _msgs = Messages.objects.using('msgstore').exclude(key_remote_jid=-1).values('media_wa_type', '_id', 'key_remote_jid', 'key_from_me', 'data', 'timestamp', 'received_timestamp', 'media_url', 'latitude', 'longitude', 'raw_data').order_by('-received_timestamp')

    _aux = []
    for item in _msgs:
        if not 'wa_contacts' in connection.introspection.table_names():
            _peer = {}
            _peer['display_name'] = '+' + item['key_remote_jid'].split('@')[0]
        else:
            _peer = WaContacts.objects.filter(jid=item['key_remote_jid']).values('display_name')[0]

        item['display_name'] = _peer['display_name']
        item['timestamp'] = timestamp2utc(float(item['timestamp']) / 1000)
        item['received_timestamp'] = timestamp2utc(float(item['received_timestamp']) / 1000)
        
        if item['data'] is not None:
            item['img'] = set_media(item['media_wa_type'], item['data'], item['key_remote_jid'], str(item['_id']), False)
        elif item['raw_data'] is not None:
            item['img'] = set_media(item['media_wa_type'], item['raw_data'], item['key_remote_jid'], str(item['_id']), True)

            
        _aux.append(item)

    return _aux


def get_messages_media():

    _msgs = Messages.objects.using('msgstore').exclude((Q(key_remote_jid=-1) | Q(media_url__isnull=True))).values('media_wa_type', '_id', 'key_remote_jid', 'key_from_me', 'data', 'raw_data', 'timestamp', 'received_timestamp', 'media_url', 'latitude', 'longitude').order_by('-timestamp')

    _aux = []
    for item in _msgs:
        if not 'wa_contacts' in connection.introspection.table_names():
            _peer = {}
            _peer['display_name'] = '+' + item['key_remote_jid'].split('@')[0]
        else:
            _peer = WaContacts.objects.filter(jid=item['key_remote_jid']).values('display_name')[0]

        item['display_name'] = _peer['display_name']
        item['timestamp'] = timestamp2utc(float(item['timestamp']) / 1000)
        item['received_timestamp'] = timestamp2utc(float(item['received_timestamp']) / 1000)
        if item['data'] is not None:
            item['img'] = set_media(item['media_wa_type'], item['data'], item['key_remote_jid'], str(item['_id']), False)
        elif item['raw_data'] is not None:
            item['img'] = set_media(item['media_wa_type'], item['raw_data'], item['key_remote_jid'], str(item['_id']), True)

        _aux.append(item)

    return _aux


def get_messages_gps():

    _msgs = Messages.objects.using('msgstore').exclude((Q(key_remote_jid=-1) | Q(longitude='0.0') | Q(latitude='0.0'))).values('media_wa_type', '_id', 'key_remote_jid', 'key_from_me', 'data', 'raw_data', 'timestamp', 'received_timestamp', 'media_url', 'latitude', 'longitude').order_by('-timestamp')

    _aux = []
    for item in _msgs:
        if not 'wa_contacts' in connection.introspection.table_names():
            _peer = {}
            _peer['display_name'] = '+' + item['key_remote_jid'].split('@')[0]
        else:
            _peer = WaContacts.objects.filter(jid=item['key_remote_jid']).values('display_name')[0]

        item['display_name'] = _peer['display_name']
        item['timestamp'] = timestamp2utc(float(item['timestamp']) / 1000)
        item['received_timestamp'] = timestamp2utc(float(item['received_timestamp']) / 1000)
        
        if item['data'] is not None:
            item['img'] = set_media(item['media_wa_type'], item['data'], item['key_remote_jid'], str(item['_id']), False)
        else:
            item['img'] = set_media(item['media_wa_type'], item['raw_data'], item['key_remote_jid'], str(item['_id']), True)
            
        _aux.append(item)

    return _aux


def get_activity_data(key=None):

    if key is None:
        peers = ChatList.objects.using('msgstore').values('key_remote_jid').exclude(Q(key_remote_jid=-1))
    else:
        peers = [{'key_remote_jid': key}]

    ret = []
    for peer in peers:
        timestamps = Messages.objects.using('msgstore').filter(key_remote_jid=peer['key_remote_jid']).values('timestamp').order_by('timestamp')
        aux = {}
        count = 0
        for time in timestamps:
            n = datetime.utcfromtimestamp(float(time['timestamp']) / 1000)
            count += 1

            key = str(n.year) + ','
            if len(str(n.month - 1)) == 1:
                key += '0' + str(n.month - 1) + ','
            else:
                key += str(n.month - 1) + ','
            if len(str(n.day)) == 1:
                key += '0' + str(n.day) + '),'
            else:
                key += str(n.day) + '),'

            try:
                aux[key] = {'data': 'Date.UTC(' + key, 'count': aux[key]['count'] + 1}
            except:
                aux[key] = {'data': 'Date.UTC(' + key, 'count': 1}

        if not 'wa_contacts' in connection.introspection.table_names():
            try:
                peer_name = "+" + str(peer['key_remote_jid']).split('@')[0]
            except:
                peer_name = "+" + peer['key_remote_jid']
        else:
            peer_name = WaContacts.objects.filter(jid=peer['key_remote_jid']).values('display_name')[0]['display_name']


        ret.append({'peer': peer_name, 'dates': sorted(aux.values(), key=itemgetter('data'))})
    return ret
