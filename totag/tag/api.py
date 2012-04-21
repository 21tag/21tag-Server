from totag.tag.models import Team, UserProfile, Venue, UserScore, TeamScore, Event
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
import pytz

NUM_EVENTS = 10
HQ_VENUE_PK = 3
#Use this as the venue for Events without proper venue
#Such as team switching

tz = pytz.timezone('America/Chicago')

class VenueResource(ModelResource):
    #tag_owner = fields.ForeignKey(TeamResource, 'tag_owner', related_name="venue", full=True)
    class Meta:
        queryset = Venue.objects.all()
        resource_name = 'poi'

    def dehydrate(self, bundle):
        venue = Venue.objects.get(pk=bundle.obj.pk)  # check that user and profile pks are safe to assume equal

        #Get owner
        owner = {}
        try:
            owner['id'] = venue.tag_owner.pk
            owner['name'] = venue.tag_owner.name
            #print "TEAM: " + str(venue.tag_owner.pk) + " VENUE " + str(venue.pk)
            owner['points'] = TeamScore.objects.get(team=venue.tag_owner, venue=venue).score
        except Exception, e:
            #print "**** VENUE DEHYDRATE ERR " + str(e)
            owner['id'] = ""
            owner['name'] = ""
            owner['points'] = ""
        bundle.data['tag_owner'] = owner

        # Get Events
        try:
            events = Event.objects.filter(venue=venue).order_by('-time')[:NUM_EVENTS]
            eventList = []
            for e in events:
                event = {}
                event['user_id'] = e.user.pk
                event['team_id'] = e.team.pk
                event['message'] = e.message
                event['time'] = tz.localize(e.time).strftime('%Y-%m-%d %H:%M:%S %z')
                event['points'] = e.points
                eventList.append(event)
            bundle.data['events'] = eventList
        except Exception, e:
            bundle.data['events'] = []
            print e

        return bundle

class TeamResource(ModelResource):
    venues = fields.ToManyField(VenueResource, 'venues', related_name='team', full=True, blank=True, null=True)
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
        #print "*** TEAM HYDRATE: " + str(bundle.data)

        #if 'image' in bundle.data:
        #    print "image found"
        #    print bundle.data["image"]

        return bundle

    def dehydrate(self, bundle):

        #report null as empty string per 21tag convention
        if bundle.data['avatar'] == None:
            bundle.data['avatar'] = ""

        #create team with user request
        if 'user_id' in bundle.data:
            user_id = bundle.data['user_id']
            print "joining created team. user: " + str(user_id)
            bundle.data.pop('user_id')
            profile = User.objects.get(pk=user_id).get_profile()
            profile.team = Team.objects.get(pk=bundle.obj.pk)
            profile.save()

        #Remove venue.tag_owner when venue displayed as belonging to a team
        venues = bundle.data['venues']
        for index, venue in enumerate(bundle.data['venues']):
            #print "*** venue dic: " + str(venues[0].data)
            venues[index].data.pop('tag_owner')
            venues[index].data.pop('events')
        players = UserProfile.objects.filter(team__name__exact=bundle.obj.name)
        #ur = UserResource()
        plist = []
        for p in players:
            p_res = {}
            p_res['id'] = p.pk
            p_res['points'] = p.points
            try:
                user = User.objects.get(pk=p.pk)
                p_res['first_name'] = user.first_name
                p_res['last_name'] = user.last_name
                p_res['team_id'] = p.team.pk
                p_res['teamname'] = p.team.name
                p_res['fid'] = p.fid
                if p.currentVenue != None:
                    p_res['currentVenueLastTime'] = tz.localize(p.currentVenueLastPing).strftime('%Y-%m-%d %H:%M:%S %z')
                    p_res['currentVenueName'] = p.currentVenue.name
                    p_res['currentVenueId'] = p.currentVenue.pk
                else:
                    p_res['currentVenueId'] = ""
                    p_res['currentVenueLastTime'] = ""
                    p_res['currentVenueName'] = ""
            except:
                p_res['teamname'] = ""
                p_res['team_id'] = ""
                p_res['currentVenueLastTime'] = ""
                p_res['currentVenueName'] = ""
                p_res['fid'] = ""

            #to append user resource_uris
            #p_res = ur.get_resource_uri(p)
            # to append usernames instead
            #p_res = p.user.username
            plist.append(p_res)
        bundle.data['members'] = plist

        # Get Scores
        teamScores = TeamScore.objects.filter(team=bundle.obj)
        scoreList = []
        #poiList = scores.filter(poi)
        for poi in teamScores:
            score = {}
            score['poi'] = poi.venue.pk
            score['pts'] = int(poi.score)
            scoreList.append(score)
        bundle.data['poi_pts'] = scoreList

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
        #print "** hydrate: " + str(bundle.data)
        #checkin call
        if 'poi' in bundle.data:
            poi = bundle.data['poi']
            points = bundle.data['points']
            bundle.data.pop('points')
            bundle.data.pop('poi')
            #print "Checkin call @ "+str(poi)+" data:" + str(bundle.data)
            profile = User.objects.get(pk=bundle.data['id']).get_profile()
            #print "profile got"
            #using pk=bundle.obj.pk returned NoneType
            profile.checkin(poi, points)
        #team change call
        if 'new_team_id' in bundle.data:
            print "team change request"
            team_id = bundle.data['new_team_id']
            print team_id
            bundle.data.pop('new_team_id')
            profile = UserProfile.objects.get(user=bundle.obj)
            oldTeam = profile.team
            #leave team request
            if int(team_id) == 0:
                newTeam = None
            else:
                newTeam = Team.objects.get(pk=team_id)
            if oldTeam != None:
                #delete old team points
                userscores = UserScore.objects.filter(team=profile.team, user=bundle.obj)
                # deduct to-be-deleted userscore values from team scores
                for us in userscores:
                    ts = TeamScore.objects.get(team=us.team, venue=us.venue)
                    ts.score -= us.score
                    ts.save()

                UserScore.objects.filter(team=profile.team, user=bundle.obj).delete()
                oldpoints = profile.points
                profile.points = 0
                oldTeam.points = oldTeam.points - oldpoints
                oldTeam.save()
                #Generate event if user left a previously non-null team
                message = str(bundle.obj.first_name) + " " + str(bundle.obj.last_name) + " left team " + str(profile.team.name)
                Event.objects.create(venue=None, user=bundle.obj, team=profile.team, points=-oldpoints, message=message)
            #set new team
            try:
                profile.team = newTeam
            except Exception, e:
                print e
            profile.save()

        #reset fbauth call
        if 'fbauthcode' in bundle.data:
            fbauthcode = bundle.data['fbauthcode']
            bundle.data.pop('fbauthcode')
            profile = UserProfile.objects.get(user=bundle.obj)
            profile.fbauthcode = fbauthcode
            profile.save()

        return bundle

    # Prepare model data for client consumption
    def dehydrate(self, bundle):
        user = User.objects.get(pk=bundle.obj.pk)
        profile = user.get_profile()
        try:  # if user has no team, all data null. User can have team, but not yet checked in. NoneType.pk throws error
            if profile.team != None:
                bundle.data['team_id'] = profile.team.pk
                bundle.data['teamname'] = profile.team.name
            else:
                bundle.data['team_id'] = ""
                bundle.data['teamname'] = ""
            bundle.data['fid'] = profile.fid
            bundle.data['points'] = profile.points                                                # 2001-03-24 10:45:32 +0600
            if profile.currentVenue != None:
                bundle.data['currentVenueLastTime'] = tz.localize(profile.currentVenueLastPing).strftime('%Y-%m-%d %H:%M:%S -0600')
                bundle.data['currentVenueName'] = profile.currentVenue.name
                bundle.data['currentVenueId'] = profile.currentVenue.pk
            else:
                bundle.data['currentVenueId'] = ""
                bundle.data['currentVenueLastTime'] = ""
                bundle.data['currentVenueName'] = ""
        except Exception, e:
            print e
            bundle.data['currentVenueId'] = ""
            bundle.data['teamname'] = ""
            bundle.data['team_id'] = ""
            bundle.data['currentVenueLastTime'] = ""
            bundle.data['currentVenueName'] = ""
            bundle.data['fid'] = ""

        #Remove User Profile field
        #bundle.data.pop('profile')

        # Get Events
        try:
            events = Event.objects.filter(user=user).order_by('-time')[:NUM_EVENTS]
            #print events
            eventList = []
            for e in events:
                event = {}
                if e.team != None:
                    event['team_id'] = e.team.pk
                else:
                    event['team_id'] = ""
                if e.venue != None:
                    event['poi_id'] = e.venue.pk
                else:
                    event['poi_id'] = ""
                event['message'] = e.message
                event['time'] = tz.localize(e.time).strftime('%Y-%m-%d %H:%M:%S %z')
                event['points'] = e.points
                eventList.append(event)
            bundle.data['events'] = eventList
        except Exception, e:
            bundle.data['events'] = []
            print e

        # Get Scores
        scores = UserScore.objects.filter(user=bundle.obj)
        scoreList = []
        #poiList = scores.filter(poi)
        for s in scores:
            score = {}
            score['poi'] = s.venue.pk
            score['pts'] = s.score
            scoreList.append(score)
        bundle.data['poi_pts'] = scoreList
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
            #profile, created = UserProfile.objects.get_or_create(pk=bundle.obj.pk)  # check that user and profile pks are safe to assume equal
            profile = bundle.obj.get_profile()
            profile.fb_authcode = password
            profile.fid = username
            profile.save()
        except IntegrityError, e:
            print e
            raise BadRequest('That username already exists')
        return bundle
