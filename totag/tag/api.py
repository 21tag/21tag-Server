from totag.tag.models import Team, UserProfile, Venue
from tastypie import fields
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL


class TeamResource(ModelResource):
    class Meta:
        queryset = Team.objects.all()
        resource_name = 'getteam'

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'getuser'

class VenueResource(ModelResource):
    class Meta:
        queryset = Team.objects.all()
        resource_name = 'venue'
