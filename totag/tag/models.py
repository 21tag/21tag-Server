from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

from tastypie.exceptions import BadRequest


class Campus(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % (self.name)


class Venue(models.Model):
    name = models.CharField(max_length=255)
    campus = models.ForeignKey(Campus)
    address = models.CharField(max_length=255)
    crossstreet = models.CharField(max_length=255)  # in iOS code, not masumi's db dump
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
        return u"%s" % (self.pk)

    def getOwner(self):
        #TODO: address ties
        top = self.venuescore_set.all().order_by('-score')[0]
        return top.team


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
        return u"%s" % (self.pk)


class VenueScore(models.Model):
    score = models.IntegerField(default=0)
    team = models.ForeignKey(Team, blank=True, null=True)
    venue = models.ForeignKey(Venue, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return u"TEAM %s AT %s WITH %s PTS" % (self.team, self.venue, self.score)

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
        if self.currentVenue == None:
            print "first checkin"
            self.currentVenue = Venue.objects.get(pk=poi)
            self.currentVenueLastPing = datetime.datetime.now()
            self.save()
            return
        try:
            print "checkin"
            checkin = Venue.objects.get(pk=poi)
            if self.currentVenue.pk != checkin.pk:
                self.currentVenue = checkin
            else:
                elapsedTime = datetime.datetime.now() - self.currentVenueLastPing
                print str(elapsedTime) + " since last checkin at this poi"
                #If it's been between 55 and 65 s since last checkin, points
                #if elapsedTime > datetime.timedelta(seconds=55) and elapsedTime < datetime.timedelta(seconds=65):
                if elapsedTime > datetime.timedelta(seconds=1) and elapsedTime < datetime.timedelta(seconds=65):
                    print "points awarded"
                    self.points += 1
                    self.team.points += 1
                    message = str(self.user.first_name)+" "+str(self.user.last_name)+" checked in at " +str(checkin.name)
                    Event.objects.create(venue=checkin, team=self.team, user=self.user, message=message)
                    venuescore, created = VenueScore.objects.get_or_create(venue=checkin, team=self.team, user=self.user)
                    venuescore.score += 1
                    venuescore.save()
                    #TODO: remove team score, have team dehydrate method tally score by venuescore objs
                    #Look into collision issues here
                    #I think there's a more proper way to increment variables
                    #When collisions are possible

                    #Check for Venue ownership change
                    top = checkin.getOwner()
                    print "top team: "+ str(top) + "my team: " + str(self.team)
                    if top == self.team:
                        #top = self.venuescore_set.all().order_by('-score')[0]
                        try:
                            teams = checkin.team_set.all()
                            print "Teams with venue: " + str(teams)
                            for t in teams:
                                t.venues.remove(checkin)
                                t.save()
                        except:
                            pass #No team previously owned venue
                        self.team.venues.add(checkin)
                        message = str(self.team)+" took over " +str(checkin.name)+"!"
                        Event.objects.create(venue=checkin, team=self.team, user=self.user, message=message)


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
    time = models.DateTimeField(default=datetime.datetime.now())

    def __unicode__(self):
        return u"%s" % (self.pk)
post_save.connect(create_user_profile, sender=User)
