try:
    import base64
    import hashlib
    import sys
    from operator import itemgetter
    from os.path import basename,isfile
    from datetime import datetime
    from django.db import models
    from django.db.models import Q
    from models import WaContacts,ChatList,Messages
    from wforensic.settings import LATEST_PEERS,TOP_PEERS,THUMBS_ROOT,THUMBS_URL
except ImportError,e:
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)

def timestamp2utc(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime ("%Y/%m/%d %H:%M:%S")

def set_media(wa_type,data,idmsg):
        if wa_type != '0':
            path = THUMBS_ROOT + idmsg + '.png'
            if isfile(path):
                THUMBS_URL + basename(path)
            else:
                try:
                    content = base64.b64decode(data)
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
        with open(path,'rb') as f:
            for chunk in iter(lambda: f.read(8192), ''):
                md5.update(chunk)
    except:
        return 'Cannot access file'
    return md5.hexdigest()

def get_sha1_file(path):
    md5 = hashlib.sha1()
    try:
        with open(path,'rb') as f:
            for chunk in iter(lambda: f.read(8192), ''):
                md5.update(chunk)
    except:
        return 'Cannot access file'
    return md5.hexdigest()

def get_latest_peers():
    peers = [c['key_remote_jid'] for c in Messages.objects.using('msgstore').values('key_remote_jid').exclude(Q(key_remote_jid=-1) | Q( key_remote_jid__icontains='-') | Q(key_remote_jid__startswith = 'Server') ).annotate(models.Max('timestamp')).order_by('-timestamp__max')[:LATEST_PEERS]]
    ret = []

    for peer in peers:
        data = Messages.objects.using('msgstore').filter(key_remote_jid = peer).values('data','_id','media_wa_type').annotate(models.Max('timestamp')).order_by('-timestamp__max')[:1][0]

        try:
            peer_data = WaContacts.objects.filter(jid=peer).values('display_name')[0]
        except:
            peer_data = {}
            peer_data['display_name'] = peer.split('@')[0][2:]

        display_name = peer_data['display_name']

        newdata = {'key_remote_jid': peer,
                    'media_wa_type': data['media_wa_type'],
                    '_id': data['_id'],
                    'timestamp': timestamp2utc(float(data['timestamp__max'])/1000),
                    'img': set_media(data['media_wa_type'],data['data'],str(data['_id'])),
                    'data': data['data'],
                    'display_name': display_name,
                    }

        ret.append(newdata)

    return ret

def get_top_peers():
    _tmp = Messages.objects.using('msgstore').values('key_remote_jid').exclude((Q(key_remote_jid = -1) |Q(key_remote_jid__icontains='-') | Q(key_remote_jid__startswith="Server"))).annotate(models.Count('key_remote_jid')).order_by('-key_remote_jid__count')[:TOP_PEERS]
    ret = []
    for item in _tmp:

        try:
            _aux = WaContacts.objects.filter(jid = item['key_remote_jid']).values('number','display_name','status','jid')[0]
        except:
            _aux = {}
            _aux['number'] = item['key_remote_jid'].split('@')[0][2:]
            _aux['display_name'] = "Not in contacts"
            _aux['status'] = "N/A"
            _aux['jid'] = item['key_remote_jid']


        _aux['msgs'] = item['key_remote_jid__count']
        ret.append(_aux)
    return ret

def get_contacts_list():

    try:
        _list = WaContacts.objects.exclude(number__isnull = True).values('jid','number','display_name','status','is_whatsapp_user').order_by('display_name')
	_non = len(_list)  # to raise the exception (if wa_contacts table does not exists, the line above does not raise any exception, DJango bug? )
    except:
        _list = Messages.objects.using('msgstore').exclude( Q(key_remote_jid = -1) | Q(key_remote_jid__startswith="Server") | Q( key_remote_jid__icontains = '-' ) ).values('key_remote_jid').distinct()
	_non = 0

    _ret = []
    for item in _list:
        if not _non:
            item['is_whatsapp_user'] = 1
            item['display_name'] = 'Not in contacts'
            item['status'] = 'N/A'
            item['number'] = item['key_remote_jid'].split('@')[0][2:]
            item['jid'] = item['key_remote_jid']

        try:
            item['messages'] = Messages.objects.using('msgstore').filter(key_remote_jid = item['jid']).count()
        except:
            item['messages'] = 0
        _ret.append(item)

    return _ret

def get_chat_list():
    _tmp = ChatList.objects.using('msgstore').values('key_remote_jid')
    _aux = [d['key_remote_jid'] for d in _tmp]

    _ret = []
    for item in _aux:
        try:
            _name = WaContacts.objects.filter(jid = item).values('display_name','number')
        except:
            _name = {'display_name': item.split('@')[0],'number':item}

        _count = Messages.objects.using('msgstore').filter(key_remote_jid = item).count()

        _tmp = Messages.objects.using('msgstore').filter(key_remote_jid = item).values('data','media_wa_type','_id').annotate(models.Max('timestamp')).order_by('-timestamp__max')
        try:
            _latest = _tmp[0]['data']
        except:
            _latest=''

        try:
            _tstamp = timestamp2utc(float(_tmp[0]['timestamp__max'])/1000)
        except:
            _tstamp='Unknown'

        try:
            _ret.append({'jid': item ,'display_name': _name[0]['display_name'],'number':_name[0]['number'],'count': _count, 'latest': _latest,'timestamp': _tstamp , 'img': set_media(_tmp[0]['media_wa_type'],_tmp[0]['data'],str(_tmp[0]['_id']))})
        except:
            _ret.append({'jid': item ,'display_name': '+' + item.split('@')[0],'number': '+' + item.split('@')[0],'count': _count, 'latest': _latest,'timestamp': _tstamp , 'img': ''})

    return _ret

def get_chat_messages(jid = None):

    if jid is not None:
        _msgs = Messages.objects.using('msgstore').filter(key_remote_jid = jid).values('media_wa_type','_id','key_remote_jid','key_from_me','data','timestamp','received_timestamp','media_url','latitude','longitude').order_by('-timestamp')
    else:
        _msgs = Messages.objects.using('msgstore').exclude(key_remote_jid = -1).values('media_wa_type','_id','key_remote_jid','key_from_me','data','timestamp','received_timestamp','media_url','latitude','longitude').order_by('-timestamp')

    _aux = []
    for item in _msgs:
        try:
            _peer = WaContacts.objects.filter(jid = item['key_remote_jid']).values('display_name')[0]
        except:
            _peer = {}
            _peer['display_name'] = '+' + item['key_remote_jid'].split('@')[0]

        item['display_name'] = _peer['display_name']
        item['timestamp'] = timestamp2utc(float(item['timestamp'])/1000)
        item['received_timestamp'] = timestamp2utc(float(item['received_timestamp'])/1000)
        item['img'] = set_media(item['media_wa_type'],item['data'],str(item['_id']))
        _aux.append(item)

    return _aux

def get_messages_media():

    _msgs = Messages.objects.using('msgstore').exclude((Q(key_remote_jid = -1) | Q(media_url__isnull = True))).values('media_wa_type','_id','key_remote_jid','key_from_me','data','timestamp','received_timestamp','media_url','latitude','longitude').order_by('-timestamp')

    _aux = []
    for item in _msgs:
        try:
            _peer = WaContacts.objects.filter(jid = item['key_remote_jid']).values('display_name')[0]
        except:
            _peer = {}
            _peer['display_name'] = '+' + item['key_remote_jid'].split('@')[0]

        item['display_name'] = _peer['display_name']
        item['timestamp'] = timestamp2utc(float(item['timestamp'])/1000)
        item['received_timestamp'] = timestamp2utc(float(item['received_timestamp'])/1000)
        item['img'] = set_media(item['media_wa_type'],item['data'],str(item['_id']))
        _aux.append(item)

    return _aux

def get_messages_gps():

    _msgs = Messages.objects.using('msgstore').exclude((Q(key_remote_jid = -1) | Q(longitude = '0.0') | Q(latitude = '0.0'))).values('media_wa_type','_id','key_remote_jid','key_from_me','data','timestamp','received_timestamp','media_url','latitude','longitude').order_by('-timestamp')

    _aux = []
    for item in _msgs:
        try:
            _peer = WaContacts.objects.filter(jid = item['key_remote_jid']).values('display_name')[0]
        except:
            _peer = {}
            _peer['display_name'] = '+' + item['key_remote_jid'].split('@')[0]

        item['display_name'] = _peer['display_name']
        item['timestamp'] = timestamp2utc(float(item['timestamp'])/1000)
        item['received_timestamp'] = timestamp2utc(float(item['received_timestamp'])/1000)
        item['img'] = set_media(item['media_wa_type'],item['data'],str(item['_id']))
        _aux.append(item)

    return _aux

def get_activity_data(key=None):

    if key is None:
        peers = ChatList.objects.using('msgstore').values('key_remote_jid').exclude(Q(key_remote_jid = -1))
    else:
        peers = [{'key_remote_jid': key}]

    ret = []
    for peer in peers:
        timestamps = Messages.objects.using('msgstore').filter(key_remote_jid = peer['key_remote_jid']).values('timestamp').order_by('timestamp')
        aux = {}
        count = 0
        for time in timestamps:
            n = datetime.utcfromtimestamp(float(time['timestamp'])/1000)
            count += 1

            key = str(n.year) + ','
            if len(str(n.month-1)) == 1:
                key += '0' + str(n.month-1) + ','
            else:
                key += str(n.month-1) + ','
            if len(str(n.day)) == 1:
                key += '0' + str(n.day) + '),'
            else:
                key += str(n.day) + '),'

            try:
                aux[key] = {'data': 'Date.UTC(' + key , 'count': aux[key]['count'] + 1 }
            except:
                aux[key] = {'data': 'Date.UTC(' + key , 'count': 1 }

        try:
            peer_name = WaContacts.objects.filter(jid = peer['key_remote_jid']).values('display_name')[0]['display_name']
        except:
            try:
                peer_name = str(peer['key_remote_jid']).split('@')[0]
            except:
                peer_name = peer['key_remote_jid']

        ret.append({'peer': peer_name , 'dates': sorted(aux.values(),key=itemgetter('data')) })
    return ret
