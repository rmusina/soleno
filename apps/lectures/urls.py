from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'lectures.views.lecture_list', name='lecture_list'),
    url(r'^create/$', 'lectures.views.lecture_create', name='lecture_create'),               
    url(r'^lecture/(?P<lecture_id>[\w\._-]+)/$', 'lectures.views.lecture_detail', name='lecture_detail'),
    url(r'^lecture/(?P<lecture_id>[\w\._-]+)/session/$', 'lectures.views.lecture_session', name='lecture_session'),
    url(r'^lecture/(?P<lecture_id>[\w\._-]+)/session/new$', 'lectures.views.lecture_session_new', name='lecture_session_new'),
    url(r'^lecture/(?P<lecture_id>[\w\._-]+)/session/updates$', 'lectures.views.lecture_session_updates', name='lecture_session_updates'),
    url(r'^lecture/(?P<lecture_id>[\w\._-]+)/session/keywords$', 'lectures.views.lecture_session_keywords', name='lecture_session_keywords'),
    #url(r'^lecture/(?P<lecture_hash>[\w\._-]+)/notes/(?P<username>[\w\._-]+)$', '', name='lecture_session'),
    #url(r'^lecture/(?P<lecture_hash>[\w\._-]+)/featured$', '', name='lecture_session'),  
)