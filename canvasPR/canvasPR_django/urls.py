from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bootstrap_lti.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^lti_tools/canvasPR_app/', include('canvasPR_app.urls', namespace="canvasPR_app")),
    url(r'^lti_tools/auth_error/', 'canvasPR_django.views.lti_auth_error', name='lti_auth_error'),
)
