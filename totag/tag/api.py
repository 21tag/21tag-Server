from totag.tag.models import Team, UserProfile, Venue
from tastypie import fields
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie.serializers import Serializer


class TeamResource(ModelResource):
    class Meta:
        queryset = Team.objects.all()
        ordering = ['points']
        resource_name = 'team'
        list_allowed_methods = ['get', 'post']
        # FOR DEV ONLY
        #authentication = Authentication()
        authorization = Authorization()

    def dehydrate(self, bundle):
        players = UserProfile.objects.filter(team__name__exact=bundle.obj.name)
        ur = UserResource()

        plist = []
        for p in players:
            p_res = ur.get_resource_uri(p)
            # to append usernames instead
            #p_res = p.user.username
            plist.append(p_res)
        bundle.data['members'] = plist
        return bundle

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['first_name', 'last_name']
        list_allowed_methods = ['get', 'post']
        # FOR DEV ONLY
        #authentication = Authentication()
        authorization = Authorization()
        serializer = Serializer()

    def dehydrate(self, bundle):
        profile = UserProfile.objects.get(pk=bundle.obj.pk)
        bundle.data['team'] = profile.team.pk
        bundle.data['teamname'] = profile.team.name
        bundle.data['currentVenueTime'] = profile.currentVenueTime
        bundle.data['currentVenueLastTime'] = profile.currentVenueLastTime
        bundle.data['currentVenueName'] = profile.currentVenueName
        return bundle


class VenueResource(ModelResource):
    class Meta:
        queryset = Team.objects.all()
        resource_name = 'poi'
