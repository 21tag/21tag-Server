from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime

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
    tag_owner = models.ForeignKey(User)
    geolong = models.FloatField()
    geolat = models.FloatField()
    state = models.CharField(max_length=2)
    city = models.CharField(max_length=255)
    #at = models.CharField()  # seems like an object identifier

    def __unicode__(self):
        return u"%s at %s" % (self.name, self.address)


class Team(models.Model):
    name = models.CharField(max_length=50)
    #Integrate Campus functionality 
    campus = models.ForeignKey(Campus, blank=True, null=True)
    #motto = models.CharField(max_length=255)
    #avatar = models.FileField()
    leader = models.ForeignKey(User, blank=True, null=True)
    venues = models.ManyToManyField(Venue, blank=True)
    points = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s and the %ss" % (self.leader, self.name)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    campus = models.ForeignKey(Campus, blank=True, null=True)
    gender = models.CharField(blank=True, max_length=1)  # m /f
    phone = models.IntegerField(blank=True, max_length=11, null=True)
    fid = models.IntegerField(blank=True, max_length=255, null=True)
    fb_authcode = models.CharField(blank=True, max_length=255)
    team = models.ForeignKey(Team, blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    currentVenueId = models.CharField(blank=True, max_length=255)
    currentVenueName = models.CharField(blank=True, max_length=255)
    currentVenueTime = models.DateTimeField(blank=True, null=True)
    currentVenueLastTime = models.DateTimeField(blank=True, null=True)

    def setFromFbResponse(self, resp):
        self.gender = resp["gender"][:1]
        self.fid = resp["id"]
        self.fb_authcode = resp["access_token"]
        self.save()

    def setAuthCode(self, authcode):
        self.fb_authcode = authcode
        self.save()

    def checkin(self, poi):
        if self.currentVenueID != poi.pk:
            self.currentVenueID = poi.pk
            self.currentVenueName = poi.name
            self.currentVenueTime = datetime.datetime.now()
        elif datetime.datetime.now() - self.currentVenueLastTime > datetime.timedelta(minutes=1):
            self.points += 1
        self.currentVenueLastTime = datetime.datetime.now()
        self.save()
        #Start timeout counter?

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
