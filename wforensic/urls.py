from django.conf.urls.defaults import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wpf_web.views.home', name='home'),
    # url(r'^wpf_web/', include('wpf_web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'whatsapp.views.index', name='home'),
    url(r'^contacts/download$', 'whatsapp.views.contacts_download', name='download_contacts'),
    url(r'^contacts/$', 'whatsapp.views.contacts', name='contacts'),
    url(r'^contacts/(?P<key>[\-?0-9a-zS\.\@]+)$', 'whatsapp.views.contact_profile', name='contact_profile'),
    url(r'^chats/$', 'whatsapp.views.chatlist', name='chats'),
    url(r'^messages/$', 'whatsapp.views.messages', name='messages'),
    url(r'^messages/(?P<key>[\-?0-9a-zS\.\@]+)$', 'whatsapp.views.single_chat', name='single_chat'),
    url(r'^mediamsg/$', 'whatsapp.views.messages_media', name='messages_media'),
    url(r'^gpsmsg/$', 'whatsapp.views.messages_gps', name='messages_gps'),
    url(r'^favicon.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
)
