from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    crossstreet = models.CharField(max_length=255)  # in iOS code, not masumi's db dump
    zip = models.IntegerField(max_length=5)
    tag_playable = models.BooleanField()
    tag_owner = models.ForeignKey(User)
    geolong = models.FloatField()
    geolat = models.FloatField()
    state = models.CharField(max_length=2)
    city = models.CharField(max_length=255)
    #at = models.CharField()  # seems like an object identifier


class Team(models.Model):
    name = models.CharField(max_length=50)
    leader = models.ForeignKey(User)
    venues = models.ManyToManyField(Venue, blank=True)
    points = models.IntegerField()


class UserProfile(models.Model):
    user = models.OneToOneField(User)

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


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance    
                                   )

post_save.connect(create_user_profile, sender=User)
