from django.conf.urls.defaults import patterns, include, url
from tag.api import TeamResource, VenueResource, UserResource
from tastypie.api import Api
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

api_v1 = Api(api_name="v2")
api_v1.register(TeamResource())
api_v1.register(VenueResource())
api_v1.register(UserResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'totag.views.home', name='home'),
#    url(r'^api/', include(api_1.urls)),
    #API V2 endpoints
    url(r'^api/v2/getteamsbyfbids/', 'tag.views.getteamsbyfbids'),
    url(r'^api/v2/getpoisdetails/', 'tag.views.getpoisdetails'),
    url(r'^api/', include(api_v1.urls)),

    #FB auth test methods
    url(r'^fbtest/', 'tag.views.fbtest'),
    url(r'^fblogin/', 'tag.views.adduser'),

    #Point sync
    url(r'^pointsync/', 'tag.views.syncTeamPoints'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
