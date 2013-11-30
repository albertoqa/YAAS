from django.conf.urls import patterns, include, url
from YAASApp.views import *
from django.views.decorators.csrf import csrf_exempt

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    #url(r'^', include('YAASApp.urls')),
    (r'^home/$', home),
    (r'^createuser/$', register),
    (r'^login/$', login),
    (r'^logout/$', logout),
    (r'^edituser/$',edit_user_info),
    (r'^addauction/$',add_auction),
    (r'^saveauction/$',save_auction),
    (r'^editauction/(?P<id>\w+)/$', edit_auction),
    (r'^saveeditedauction/(?P<id>\w+)/$',save_edited_auction),
    (r'^canceledit/(?P<id>\w+)/$',canceledit),
    (r'^auction/(?P<id>\w+)/$', view_auction),
    (r'^banauction/(?P<id>\w+)/$', ban_auction),
    (r'^changelang/$', changelang),
    (ur'^search/(\w+)/$', search),
    (ur'^search/$', search),
    (r'^bidauction/(?P<id>\w+)/$', bid_auction),



    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    (ur'^api/v1/search/$', apisearch),
    (ur'^api/v1/search/(\w+)/$', apisearch),

    (ur'^api/v2/bid/(?P<id>\w+)/$', apibid),



    url(r'^admin/', include(admin.site.urls)),
)
