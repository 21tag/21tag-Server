# Create your views here.
from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from models import Team, Venue
from django.views.decorators.csrf import csrf_exempt

#need to test
@csrf_exempt
def checkin(request):
    if request.method == "POST":
        try:
            print "user " + str(request.POST.get("user"))
            print "poi " + str(request.POST.get("poi"))
            user = User.objects.get(pk=request.POST["user"])
            poi = Venue.objects.get(pk=request.POST["poi"])
            user.checkin(poi)
            return HttpResponse("checkedin")
        except Exception, e:
            print e
    return HttpResponse("malformed request")


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

@csrf_exempt
def getPoiDetails(request):
    if request.method == "POST":
        print request.POST["poi"]
        try:
            venue = [Venue.objects.get(pk=request.POST["poi"])]
        except Exception, e:
            venue = None
            print "error " + str(e)
    else:
        venue = Venue.objects.all()
        print "nonPOST " + str(len(venue))
    response = {}
    venues = []
    for v in venue:
        tdic = {}
        tdic["id"] = v.name
        tdic["zip"] = v.zip
        tdic["tag_playable"] = v.tag_playable
        tdic["geolong"] = v.geolong
        tdic["geolat"] = v.geolat
        tdic["state"] = v.state
        tdic["city"] = v.city
        venues.append(tdic)
    response["poi"] = venues
    return HttpResponse(json.dumps(response), mimetype="application/json")

@csrf_exempt
def standings(request):
    if request.method == "POST":
        print request.POST["num"]
        try:
            num = request.POST["num"]
        except Exception, e:
            venue = None
            print "error " + str(e)
    else:
        num = request.GET.get("num", 10)
        print "nonPOST "
    team = Team.objects.order_by('-points')[:num]
    response = {}
    teams = []
    for t in team:
        tpdic = {}  # {t: <team data except pts>, p: <points>}  Ugh!
        tdic = {}   # { team data }
        tdic["id"] = t.name
        if t.leader != None:
            tdic["leader"] = t.leader.pk
        users = []
        #Get all users on team
        for user in User.objects.filter(team__name__exact=t.name):
            users.append(user.pk)
        tdic["users"] = users
        venues = []
        for venue in t.venues.all():
            venues.append(venue.pk)
        tdic["venues"] = venues

        tpdic["t"] = tdic
        tpdic["p"] = t.points

        teams.append(tpdic)
    response["teams"] = teams
    return HttpResponse(json.dumps(response), mimetype="application/json")
