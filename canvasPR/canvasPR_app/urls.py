from django.conf.urls import patterns, url

urlpatterns = patterns('',

    url(r'^$', 'canvasPR_app.views.index', name='index'),
    url(r'^index.html$', 'canvasPR_app.views.index', name='index2'),
    url(r'^lti_launch$', 'canvasPR_app.views.lti_launch', name='lti_launch'),
    url(r'^main$', 'canvasPR_app.views.main', name='main'),
    url(r'^tool_config$', 'canvasPR_app.views.tool_config', name='tool_config'),
)
