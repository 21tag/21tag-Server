# Create your views here.
from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from models import Team
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def getTeam(request):
    if request.method == "POST":
        print request.POST["team"]
        try:
            team = [Team.objects.get(name=str(request.POST["team"]))]
        except Exception, e:
            team = None
            print "error " + str(e)
    else:
        team = Team.objects.all()
    response = {}
    teams = []
    for t in team:
        tdic = {}
        tdic["id"] = t.name
        users = []
        #Get all users on team
        for user in User.objects.filter(team__name__exact=t.name):
            users.append(user.pk)
        tdic["users"] = users
        venues = []
        for venue in t.venues.all():
            venues.append(venue.pk)
        tdic["venues"] = venues
        teams.append(tdic)
    response["teams"] = teams
    return HttpResponse(json.dumps(response), mimetype="application/json")
