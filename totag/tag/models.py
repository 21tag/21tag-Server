from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

from tastypie.exceptions import BadRequest

CHECKIN_MAX = 60 * 6  # seconds without checkin until "checked out"
CHECKIN_MIN = 30  # fundamental time b/t checkins to award 1 pt
CHECKIN_PTS = 5  # pts per checkin


class Campus(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % (self.name)


class Venue(models.Model):
    name = models.CharField(max_length=255)
    campus = models.ForeignKey(Campus, blank=True, null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    crossstreet = models.CharField(max_length=255, null=True, blank=True)  # in iOS code, not masumi's db dump
    zip = models.IntegerField()
    tag_playable = models.BooleanField()
    tag_owner = models.ForeignKey('Team', null=True, blank=True)
    geolong = models.FloatField()
    geolat = models.FloatField()
    state = models.CharField(max_length=2)
    city = models.CharField(max_length=255)
    #at = models.CharField()  # seems like an object identifier

    def __unicode__(self):
        #return u"%s at %s" % (self.name, self.address)
        return u"%s %s" % (self.pk, self.name)


    #returns pk of team on top and changes self.tag_owner if needed
    def getOwner(self):
        #TODO: address ties
        try:
            top = self.teamscore_set.all().order_by('-score')[0]
            print "get Owner top for " + str(self.pk) + " :" + str(top)

            # If Venue owner is null, set it to top team
            if self.tag_owner == None:
                self.tag_owner = top.team
                # Set venue to be owned by top team
                top.team.venues.add(self)
                self.save()
            # Set Venue tag owner if ownership change occured
            elif top.team != self.tag_owner:
                # Remove venue from previous Team's venue list
                self.tag_owner.venues.remove(self)
                # Set this venue's owner to new Team
                self.tag_owner = top.team
                self.save()
                # Add this venue to the new Team's venue list
                top.team.venues.add(self)
        except Exception, e:
            print "get owner error: " + str(e)
            #No owner yet
            return 0
        return top.team.pk


class Team(models.Model):
    name = models.CharField(max_length=50)
    #Integrate Campus functionality 
    campus = models.ForeignKey(Campus, blank=True, null=True)
    motto = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to="team_avatars/", blank=True, null=True)
    leader = models.ForeignKey(User, blank=True, null=True)
    venues = models.ManyToManyField(Venue, blank=True, null=True)
    points = models.IntegerField(default=0)
    #remove points and venues

    def __unicode__(self):
        return u"%s %s" % (self.pk, self.name)

class TeamScore(models.Model):
    score = models.IntegerField(default=0)
    team = models.ForeignKey(Team)
    venue = models.ForeignKey(Venue)

    def __unicode__(self):
        return u"TEAM %s AT %s WITH %s PTS" % (self.team, self.venue, self.score)

#TODO: rename UserScore
class UserScore(models.Model):
    score = models.IntegerField(default=0)
    team = models.ForeignKey(Team)
    venue = models.ForeignKey(Venue)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u"USER %s TEAM %s AT %s WITH %s PTS" % (self.user, self.team, self.venue, self.score)

    #Auto increments teamScore
    def addScore(self, score):
        self.score += score
        self.team.points += score
        self.team.save()
        #Test to see if self.team must be explicitly saved
        self.save()
        teamscore = TeamScore.objects.get(team=self.team, venue=self.venue)
        teamscore.score += score
        teamscore.save()


    def save(self, *args, **kwargs):
        teamscore, created = TeamScore.objects.get_or_create(team=self.team, venue=self.venue)

        super(UserScore, self).save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    campus = models.ForeignKey(Campus, blank=True, null=True)
    gender = models.CharField(blank=True, max_length=1)  # m /f
    phone = models.IntegerField(blank=True, max_length=11, null=True)
    fid = models.BigIntegerField(blank=True, max_length=255, null=True)
    fb_authcode = models.CharField(blank=True, max_length=255)
    team = models.ForeignKey(Team, blank=True, null=True)
    points = models.IntegerField(default=0, blank=True, null=True)
    currentVenue = models.ForeignKey(Venue, blank=True, null=True)
    currentVenueLastPing = models.DateTimeField(blank=True, null=True)

    def setFromFbResponse(self, resp):
        self.gender = resp["gender"][:1]
        self.fid = resp["id"]
        self.fb_authcode = resp["access_token"]
        self.save()

    def setAuthCode(self, authcode):
        self.fb_authcode = authcode
        self.save()

    def checkin(self, poi, points):

        try:
            checkin = Venue.objects.get(pk=poi)
            #If first checkin or expired time
            #if justDoIt or self.currentVenue.pk != checkin.pk or self.currentVenue == None or (datetime.datetime.now() - self.currentVenueLastPing > datetime.timedelta(seconds=CHECKIN_MAX)):
            #    print "first checkin"
            #    self.currentVenue = Venue.objects.get(pk=poi)
            #    self.currentVenueLastPing = datetime.datetime.now()
            #    self.save()
            #    message = str(self.user.first_name) + " " + str(self.user.last_name) + " checked in at " + str(self.currentVenue.name)
            #    Event.objects.create(venue=self.currentVenue, team=self.team, user=self.user, message=message)
            #else:

            # If first checkin, self.CurrentVenue and currentVenueLastPing will be null
            # First indicates this state
            first = False
            if self.currentVenueLastPing == None:
                elapsedTime = datetime.timedelta(seconds=CHECKIN_MIN)
                print "first checkin"
                first = True
            else:
                elapsedTime = datetime.datetime.now() - self.currentVenueLastPing
                print str(elapsedTime) + " since last checkin"

            #If it's been between 55 and 65 s since last checkin, points
            #if elapsedTime > datetime.timedelta(seconds=55) and elapsedTime < datetime.timedelta(seconds=65):
            #if elapsedTime > datetime.timedelta(seconds=CHECKIN_MIN) and elapsedTime < datetime.timedelta(seconds=CHECKIN_MAX):

            #New behavior: A checkin represents 5m of checked in time
            if elapsedTime >= datetime.timedelta(seconds=CHECKIN_MIN):

                if first:
                    message = str(self.user.first_name) + " " + str(self.user.last_name) + " checked in at " + str(checkin.name)
                    Event.objects.create(points=points, venue=self.currentVenue, team=self.team, user=self.user, message=message)
                elif self.currentVenue.pk != checkin.pk:
                    message = str(self.user.first_name) + " " + str(self.user.last_name) + " checked in at " + str(self.currentVenue.name)
                    Event.objects.create(points=points, venue=self.currentVenue, team=self.team, user=self.user, message=message)

                self.currentVenue = Venue.objects.get(pk=poi)
                self.currentVenueLastPing = datetime.datetime.now()
                print str(points) + " points awarded"
                oldOwner = checkin.getOwner()

                self.points += points
                self.team.points += points
                userscore, created = UserScore.objects.get_or_create(venue=checkin, team=self.team, user=self.user)
                userscore.addScore(points)  # auto adds teamScore
                userscore.save()

                #TODO: remove team score, have team dehydrate method tally score by venuescore objs
                #Look into collision issues here
                #I think there's a more proper way to increment variables
                #When collisions are possible
                #Check for Venue ownership change
                newOwner = checkin.getOwner()
                if oldOwner != newOwner:
                    print "team takeover!"
                    message = str(self.team.name) + " took over " + str(checkin.name) + "!"
                    Event.objects.create(points=0, venue=checkin, team=self.team, user=self.user, message=message)
                print "top team: " + str(newOwner) + "my team: " + str(self.team)
                if newOwner == self.team:
                    #top = self.venuescore_set.all().order_by('-score')[0]
                    try:
                        teams = checkin.team_set.all()
                        print "Teams with venue: " + str(teams)
                        #  This should be handled by getOwner(), but in case latent bad data exists:
                        for t in teams:
                            t.venues.remove(checkin)
                        t.save()  # Don't think this is actually needed after remove
                    except Exception, e:
                        print 'team owner removal error: ' + str(e)

                    self.team.venues.add(checkin)

                self.save()
            else:
                print "checkin time req not met"
        except Exception, e:
            print e
            raise BadRequest
        #Start timeout counter?

    # If the User is created through the admin interface
    # UserProfile is created via admin inline form. So 
    # Assume that's the cause of any exception here
    def save(self, *args, **kwargs):
        try:
            existing = UserProfile.objects.get(user=self.user)
            self.id = existing.id
        except UserProfile.DoesNotExist:
            pass
        return super(UserProfile, self).save(*args, **kwargs)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Event(models.Model):
    venue = models.ForeignKey(Venue, blank=True, null=True)  #for user leaving team
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    message = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.pk)
post_save.connect(create_user_profile, sender=User)
