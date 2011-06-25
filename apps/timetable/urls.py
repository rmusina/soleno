from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'timetables.views.user_timetable', name='user_timetable'),
)