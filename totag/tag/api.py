from totag.tag.models import Team, UserProfile, Venue
from tastypie import fields
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication, Authentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL
from tastypie.serializers import Serializer
from tastypie.exceptions import BadRequest
from django.db import IntegrityError


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

# Not needed
#class UserProfileResource(ModelResource):
#    class Meta:
#        queryset = UserProfile.objects.all()
#        resource_name = 'userprofile'
#        include_resource_uri = False
#        include_absolute_url = False

class UserResource(ModelResource):
    #profile = fields.OneToOneField(UserProfileResource, 'get_profile', full=True)
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
        profile = UserProfile.objects.get(pk=bundle.obj.pk)  # check that user and profile pks are safe to assume equal
        bundle.data['team'] = profile.team.pk
        bundle.data['teamname'] = profile.team.name
        bundle.data['currentVenueTime'] = profile.currentVenueTime
        bundle.data['currentVenueLastTime'] = profile.currentVenueLastTime
        bundle.data['currentVenueName'] = profile.currentVenueName
        return bundle


    def obj_create(self, bundle, request=None, **kwargs):
        # set facebook id as username, fbauthcode as pw
        # improve this security later
        try:
            fname, lname, username, password, email = bundle.data['firstname'], bundle.data['lastname'], bundle.data['fid'], bundle.data['fbauthcode'], bundle.data['email']
        except:
            raise BadRequest('Incomplete user data')
        try:
            bundle.obj = User.objects.create_user(username, email, password)
            bundle.obj.first_name = fname
            bundle.obj.last_name = lname
            bundle.obj.save()
            profile = UserProfile.objects.get(pk=bundle.obj.pk)  # check that user and profile pks are safe to assume equal
            profile.fb_authcode = password
            profile.fid = username
            profile.save()
        except IntegrityError, e:
            print e
            raise BadRequest('That username already exists')
        return bundle


class VenueResource(ModelResource):
    class Meta:
        queryset = Team.objects.all()
        resource_name = 'poi'
