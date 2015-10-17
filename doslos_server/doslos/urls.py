from django.conf.urls import patterns, url
from doslos.views import select_level, questionnaire, post_questionnaire

urlpatterns = patterns(
    '',
    url(r'^$', select_level, name='select_level'),
    url(r'^questionnaire/(?P<level_id>\d+)/$', questionnaire, name='questionnaire'),
    url(r'^questionnaire/(?P<level_id>\d+)/post/$', post_questionnaire, name='post_questionnaire'),
)
