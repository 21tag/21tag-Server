from django.conf.urls.defaults import patterns, include, url
from tag.api import TeamResource, VenueResource
from tastypie.api import Api

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

api_1 = Api(api_name="v1")
api_1.register(TeamResource())
api_1.register(VenueResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'totag.views.home', name='home'),
    url(r'^api/', include(api_1.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
