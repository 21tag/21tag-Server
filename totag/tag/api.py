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
from django.conf.urls.defaults import url
from datetime import datetime


class VenueResource(ModelResource):
    #tag_owner = fields.ForeignKey(TeamResource, 'tag_owner', related_name="venue", full=True)
    class Meta:
        queryset = Venue.objects.all()
        resource_name = 'poi'

    def dehydrate(self, bundle):
        venue = Venue.objects.get(pk=bundle.obj.pk)  # check that user and profile pks are safe to assume equal
        try:
            bundle.data['tag_owner'] = venue.tag_owner.pk

        except:
            bundle.data['teamname'] = ""


        #Remove User Profile field
        #bundle.data.pop('profile')
        print "** Dehydrate: " + str(bundle.data)
        return bundle

class TeamResource(ModelResource):
    venues = fields.ToManyField(VenueResource, 'venues', related_name='team', full=True)
    #authors = fields.ToManyField('path.to.api.resources.AuthorResource', 'author_set', related_name='entry')
    class Meta:
        queryset = Team.objects.all()
        ordering = ['points']
        resource_name = 'team'
        list_allowed_methods = ['get', 'post', 'patch']
        always_return_data = True
        # FOR DEV ONLY
        #authentication = Authentication()
        authorization = Authorization()

    def hydrate(self, bundle):

        return bundle


class UserProfileResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'userprofile'
        include_resource_uri = False
        include_absolute_url = False


class UserResource(ModelResource):
    #profile = fields.ToOneField(UserProfileResource, 'get_profile', full=True)
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'first_name', 'last_name']
        list_allowed_methods = ['get', 'post', 'patch']
        always_return_data = True
        # FOR DEV ONLY
        #authentication = Authentication()
        authorization = Authorization()
        serializer = Serializer()

 #   def override_urls(self):
 #       return [
 #           url(r"^(?P<resource_name>%s)/(?P<fid/>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
 #       ]
    def hydrate(self, bundle):
        print "** hydrate: " + str(bundle.data)
        #checkin call
        if 'poi' in bundle.data:
            poi = bundle.data['poi']
            bundle.data.pop('poi')
            print bundle.data
            profile = UserProfile.objects.get(pk=bundle.obj.pk)
            profile.checkin(poi)
        #team change call
        if 'new_team_id' in bundle.data:
            team_id = bundle.data['team_id']
            bundle.data.pop('team_id')
            profile = UserProfile.objects.get(pk=bundle.obj.pk)
            if team_id == 0:
                team = None
            else:
                team = Team.objects.get(pk=team_id)
            profile.team = team
            profile.save()
        #reset fbauth call
        if 'fbauthcode' in bundle.data:
            fbauthcode = bundle.data['fbauthcode']
            bundle.data.pop('fbauthcode')
            profile = UserProfile.objects.get(pk=bundle.obj.pk)
            profile.fbauthcode = fbauthcode
            profile.save()

        return bundle

    # Prepare model data for client consumption
    def dehydrate(self, bundle):
        profile = UserProfile.objects.get(pk=bundle.obj.pk)  # check that user and profile pks are safe to assume equal
        try:
            bundle.data['team_id'] = profile.team.pk
            bundle.data['teamname'] = profile.team.name
            bundle.data['currentVenueLastTime'] = profile.currentVenueLastPing
            bundle.data['currentVenueName'] = profile.currentVenue.name
            bundle.data['fid'] = profile.fid
        except:
            bundle.data['teamname'] = ""
            bundle.data['team_id'] = ""
            bundle.data['currentVenueLastTime'] = ""
            bundle.data['currentVenueName'] = ""
            bundle.data['fid'] = ""

        #Remove User Profile field
        #bundle.data.pop('profile')
        print "** Dehydrate: " + str(bundle.data)
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        # set facebook id as username, fbauthcode as pw
        # improve this security later
        print "obj create"
        try:
            print bundle.data
            fname, lname, username, password, email = bundle.data['firstname'], bundle.data['lastname'], bundle.data['fid'], bundle.data['fbauthcode'], bundle.data['email']
            #Else these can be passed to dehydrate
            bundle.data.pop('firstname')
            bundle.data.pop('lastname')
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
