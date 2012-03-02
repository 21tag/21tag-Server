from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

from tastypie.exceptions import BadRequest

CHECKIN_MAX = 65  # seconds without checkin until "checked out"
CHECKIN_MIN = 5  # fundamental time b/t checkins to award 1 pt

class Campus(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % (self.name)


class Venue(models.Model):
    name = models.CharField(max_length=255)
    campus = models.ForeignKey(Campus)
    address = models.CharField(max_length=255)
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


    #returns pk of team on top
    def getOwner(self):
        #TODO: address ties
        try:
            top = self.teamscore_set.all().order_by('-score')[0]
            print "get Owner top for " + str(self.pk) + " :" + str(top)
            #Set Venue tag owner if ownership change occured
            if top.team != self.tag_owner:
                self.tag_owner = top.team
                self.save()
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
    #avatar = models.FileField()
    leader = models.ForeignKey(User, blank=True, null=True)
    venues = models.ManyToManyField(Venue, blank=True)
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
        teamscore = TeamScore.objects.get(team=self.team, venue=self.venue)
        teamscore.score += score
        teamscore.save()
        self.save()

    def save(self, *args, **kwargs):
        teamscore, created = TeamScore.objects.get_or_create(team=self.team, venue=self.venue)

        super(UserScore, self).save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    campus = models.ForeignKey(Campus, blank=True, null=True)
    gender = models.CharField(blank=True, max_length=1)  # m /f
    phone = models.IntegerField(blank=True, max_length=11, null=True)
    fid = models.IntegerField(blank=True, max_length=255, null=True)
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

    def checkin(self, poi):
        #If first checkin, self.CurrentVenue will be null

        try:
            print "checkin"
            checkin = Venue.objects.get(pk=poi)
            #If first checkin or expired time
            if self.currentVenue.pk != checkin.pk or self.currentVenue == None or (datetime.datetime.now() - self.currentVenueLastPing > datetime.timedelta(seconds=CHECKIN_MAX)):
                print "first checkin"
                self.currentVenue = Venue.objects.get(pk=poi)
                self.currentVenueLastPing = datetime.datetime.now()
                self.save()
                message = str(self.user.first_name) + " " + str(self.user.last_name) + " checked in at " + str(self.currentVenue.name)
                Event.objects.create(venue=self.currentVenue, team=self.team, user=self.user, message=message)
            else:
                elapsedTime = datetime.datetime.now() - self.currentVenueLastPing
                print str(elapsedTime) + " since last checkin at this poi"
                #If it's been between 55 and 65 s since last checkin, points
                #if elapsedTime > datetime.timedelta(seconds=55) and elapsedTime < datetime.timedelta(seconds=65):
                if elapsedTime > datetime.timedelta(seconds=CHECKIN_MIN) and elapsedTime < datetime.timedelta(seconds=CHECKIN_MAX):
                    print "points awarded"
                    oldOwner = checkin.getOwner()

                    self.points += 1
                    self.team.points += 1
                    userscore, created = UserScore.objects.get_or_create(venue=checkin, team=self.team, user=self.user)
                    userscore.addScore(1)  # auto adds teamScore
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
                        Event.objects.create(venue=checkin, team=self.team, user=self.user, message=message)
                    print "top team: " + str(newOwner) + "my team: " + str(self.team)
                    if newOwner == self.team:
                        #top = self.venuescore_set.all().order_by('-score')[0]
                        try:
                            teams = checkin.team_set.all()
                            print "Teams with venue: " + str(teams)
                            for t in teams:
                                t.venues.remove(checkin)
                                t.save()
                        except Exception, e:
                            print 'team owner removal error: ' + str(e)

                        self.team.venues.add(checkin)



                #default = 55
                if elapsedTime > datetime.timedelta(seconds=1):
                    self.currentVenueLastPing = datetime.datetime.now()
            self.save()
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
    venue = models.ForeignKey(Venue)
    user = models.ForeignKey(User)
    team = models.ForeignKey(Team)
    message = models.CharField(max_length=255)
    points = models.IntegerField(default=1)
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.pk)
post_save.connect(create_user_profile, sender=User)
