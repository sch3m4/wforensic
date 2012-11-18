from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'whatsapp.views.index', name='home'),
    url(r'^contacts/download$', 'whatsapp.views.contacts_download', name='download_contacts'),
    url(r'^contacts/$', 'whatsapp.views.contacts', name='contacts'),
    url(r'^contacts/(?P<key>[\-?0-9a-zS\.\@]+)$', 'whatsapp.views.contact_profile', name='contact_profile'),
    url(r'^chats/$', 'whatsapp.views.chatlist', name='chats'),
    url(r'^messages/$', 'whatsapp.views.messages', name='messages'),
    url(r'^messages/(?P<key>[\-?0-9a-zS\.\@]+)$', 'whatsapp.views.single_chat', name='single_chat'),
    url(r'^messages/(?P<key>[\-?0-9a-zS\.\@]+)/detect$', 'whatsapp.views.language_detect', name='language_detect'),
    url(r'^mediamsg/$', 'whatsapp.views.messages_media', name='messages_media'),
    url(r'^gpsmsg/$', 'whatsapp.views.messages_gps', name='messages_gps'),
    url(r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
)

handler404 = 'whatsapp.views.error404'
handler500 = 'whatsapp.views.error404'