from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from totag.tag.models import Team, Venue, Campus, UserProfile, VenueScore, Event

admin.site.register(Team)
admin.site.register(Venue)
admin.site.register(Campus)
admin.site.register(VenueScore)
admin.site.unregister(User)
admin.site.register(Event)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)
