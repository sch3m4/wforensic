from django.db import models
from django.forms import ModelForm, Textarea


class AndroidMetadata(models.Model):
    locale = models.TextField(blank=True)

    class Meta:
        db_table = u'android_metadata'


class WaContacts(models.Model):
    """
    Contact model
    """
    _id = models.IntegerField(primary_key=True, blank=True)
    jid = models.TextField()
    is_whatsapp_user = models.IntegerField()
    is_iphone = models.IntegerField()
    status = models.TextField(blank=True)
    number = models.TextField(blank=True)
    raw_contact_id = models.IntegerField(null=True, blank=True)
    display_name = models.TextField(blank=True)
    phone_type = models.IntegerField(null=True, blank=True)
    phone_label = models.TextField(blank=True)
    unseen_msg_count = models.IntegerField(null=True, blank=True)
    photo_ts = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'wa_contacts'


class Messages(models.Model):
    """
    Message model
    """
    _id = models.IntegerField(primary_key=True, blank=True)
    key_remote_jid = models.TextField()
    key_from_me = models.IntegerField(null=True, blank=True)
    key_id = models.TextField()
    status = models.IntegerField(null=True, blank=True)
    needs_push = models.IntegerField(null=True, blank=True)
    data = models.TextField(blank=True)
    timestamp = models.IntegerField(null=True, blank=True)
    media_url = models.TextField(blank=True)
    media_mime_type = models.TextField(blank=True)
    media_wa_type = models.TextField(blank=True)
    media_size = models.IntegerField(null=True, blank=True)
    media_name = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    thumb_image = models.TextField(blank=True)
    remote_resource = models.TextField(blank=True)
    received_timestamp = models.IntegerField(null=True, blank=True)
    send_timestamp = models.IntegerField(null=True, blank=True)
    receipt_server_timestamp = models.IntegerField(null=True, blank=True)
    receipt_device_timestamp = models.IntegerField(null=True, blank=True)
    raw_data = models.TextField(blank=True)

    class Meta:
        db_table = u'messages'


class ChatList(models.Model):
    """
    Chat list model
    """
    _id = models.IntegerField(primary_key=True, blank=True)
    key_remote_jid = models.TextField(unique=True, blank=True)
    message_table_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = u'chat_list'
