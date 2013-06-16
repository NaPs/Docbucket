from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = patterns('',
    url(r'^$', 'docbucket.views.home', name='home'),
    url(r'^create/(?P<compiler>.+)$', 'docbucket.views.create', name='create'),
    url(r'^list/$', 'docbucket.views.list', name='list'),
    url(r'^list/(?P<tag_name>.+)/$', 'docbucket.views.list', name='list-tag'),
    url(r'^show/(?P<doc_id>\d+)/$', 'docbucket.views.show', name='show'),
    url(r'^search/$', 'docbucket.views.search', name='search'),
    url(r'^_thumbnail/file/(?P<identifier>.+)$', 'docbucket.views.thumbnail', {'type': 'file'}, name='thumbnail-file'),
    url(r'^_thumbnail/document/(?P<identifier>\d+)$', 'docbucket.views.thumbnail', {'type': 'document'}, name='thumbnail-document'),
    url(r'^_document/(?P<doc_id>\d+)', 'docbucket.views.ajax_document', name='ajax_document'),
    url(r'^_tags/', 'docbucket.views.ajax_tags', name='ajax_tags')
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)