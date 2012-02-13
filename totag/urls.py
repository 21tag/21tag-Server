from django.conf.urls.defaults import patterns, include, url
from tag.api import TeamResource, VenueResource
from tastypie.api import Api

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#api_1 = Api(api_name="v1")
#api_1.register(TeamResource())
#api_1.register(VenueResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'totag.views.home', name='home'),
#    url(r'^api/', include(api_1.urls)),
    url(r'^getteam', 'tag.views.getTeam'),
    url(r'^checkin', 'tag.views.checkin'),
    url(r'^getpoidetails', 'tag.views.getPoiDetails'),
    url(r'^standings', 'tag.views.standings'),
    url(r'^login', 'tag.views.login'),
    url(r'^adduser', 'tag.views.adduser'),
    url(r'^resetfbauth', 'tag.views.resetfbauth'),
    url(r'^getteamsbyfbids', 'tag.views.getteamsbyfbids'),

    #FB auth test methods
    url(r'^fbtest/', 'tag.views.fbtest'),
    url(r'^fblogin/', 'tag.views.adduser'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
