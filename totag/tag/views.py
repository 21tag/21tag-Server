# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from models import Team, Venue
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import facebook
from models import UserProfile
from geopy.distance import distance


@login_required
@csrf_exempt
def checkin(request):
    print "method entered"
    if request.method == "POST":
        try:
            if request.user.pk == request.POST.get("user"):
                print "user " + str(request.POST.get("user"))
                print "poi " + str(request.POST.get("poi"))
                user = User.objects.get(pk=request.POST["user"])
                poi = Venue.objects.get(pk=request.POST["poi"])
                user.checkin(poi)
                return HttpResponse("checkedin")
            else:
                return HttpResponse("invalid username/password")
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


#fbtest presents the fb javascript SDK authentication route
#fblogin recieves the access token from the successful request
def fbtest(request):
    tempdic = {}
    return render_to_response('fbconnect.html', tempdic, context_instance=RequestContext(request))

#this view will create a user provided the request has a valid Facebook Auth cookie
#to replicate /adduser call
@csrf_exempt
def fblogin(request):
    user = facebook.get_user_from_cookie(request.COOKIES, "252950804781745", "af1987209aa730c3607c8bffdc9d6ef7")
    if user:
        graph = facebook.GraphAPI(user["access_token"])
        profile = graph.get_object("me")
        fid = profile["id"]
        try:
            #see if a user exists with this facebook id
            loginuser = UserProfile.objects.get(fid=fid)
            print "fb user found"
        except:
            #if not create user
            loginuser = User.objects.create_user(str(profile['first_name']) + (str(profile["id"])[5:]), "")
            loginuser.last_name = profile['last_name']
            loginuser.save()
            profile["access_token"] = user["access_token"]
            loginuser.get_profile().setFromFbResponse(profile)
            #print "new user"
            #print loginuser.get_profile().fid

    return HttpResponse("yeah")

@csrf_exempt
def login(request):
    if not request.method == "POST":
        return HttpResponse("wrong ")
    try:
        user = UserProfile.objects.get(fb_authcode=request.POST["fbauthcode"])
        return HttpResponse(str(user.fid) + " logged in.")
    except:
        return HttpResponse("nope")


@csrf_exempt
def adduser(request):
    if not request.method == "POST":
        return HttpResponse("nope")
    try:
        authcode = request.POST["fbauthcode"]
        email = request.POST["email"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        try:
            #see if a user exists with this facebook id
            loginuser = UserProfile.objects.get(fb_authcode=request.POST["fbauthcode"])
        except:
            #if not create user
            loginuser = User.objects.create_user(str(firstname) + (str(authcode)[5:]), email)
            loginuser.last_name = lastname
            loginuser.save()
            loginuser.get_profile().setEmail(email)
            loginuser.get_profile().setAuthCode(authcode)
            return HttpResponse("user added")
        #create user with credentials
    except:
        return HttpResponse("nope")
    return HttpResponse("User all ready exists")

@csrf_exempt
def resetfbauth(request):
    if not request.method == "POST":
        return HttpResponse("nope")
    try:
        profile = UserProfile.objects.get(fid=request.POST["fbid"])  # 'fbid' here and 'fid' in adduser :(
        profile.setAuthCode(request.POST["fbauthcode"])
        return HttpResponse("code reset")
    except:
        return HttpReponse("nope")

@csrf_exempt
def getteamsbyfbids(request):
    if not request.method == "POST":
        return HttpResponse("nope")
    try:
        fbids = request.POST["fbids"].split(",")
        teams = []
        fByTeam = {}
        for id in fbids:
            try:  # is fb friend on a 21tag team?
                team = (UserProfile.objects.get(fid=id).team)
                teamdic = {}
                teamdic["id"] = team.name
                teamdic["nummem"] = len(team.userprofile_set.all())
                # tally friends by team
                if not team.name in fByTeam:
                    fByTeam[team.name] = 1
                else:
                    fByTeam[team.name] += 1
                teams.append(teamdic)
            except:
                pass
        print teams
    except:
        return HttpResponse("nope")
    #Add friend tally to response dic
    for team in teams:
        team["numf"] = fByTeam[team["id"]]
    response = {}
    response["TeamData"] = teams
    return HttpResponse(json.dumps(response), mimetype="application/json")


@csrf_exempt
def createteam(request):
    if not request.method == "POST":
        return HttpResponse("nope")
    try:
        print request.POST
        try:
            newTeam = Team.objects.get(name=request.POST["team"])
            return HttpResponse("Team with given name all ready exists")
        except:
            newTeam = Team.objects.create(name=request.POST["team"])
        print newTeam
        userprofile = UserProfile.objects.get(fid=request.POST["user"])
        # Check that user is not listed as leader of original team
        if userprofile.team.leader == userprofile.user:
            userprofile.team.leader = None
            userprofile.team.save()
            print "leader status of old team updated!"
        userprofile.team = newTeam
        userprofile.save()
        newTeam.leader = userprofile.user
        newTeam.save()
    except Exception, e:
        print e
        return HttpResponse("invalid request")

    return HttpResponse("nope")

#TODO test!
@csrf_exempt
def getpoisdetails(request):
    if not request.method == "POST":
        return HttpResponse("nope")
    try:
        venues = Venue.objects.all()
        userloc = (request.POST["lat"], request.POST["lon"])
        try:
            if len(venues) > request.POST["num"]:
                venues = venues[:request.POST["num"]]
        except:
            pass
        pois = []
        for poi in venues:
            poiloc = (poi.geolat, poi.geolong)
            if distance(userloc, poiloc) < 400:
                thispoi  = {}
                thispoi["name"] = poi.name
                thispoi["zip"] = poi.zip
                thispoi["tag_playable"] = poi.tag_playable
                thispoi["geolong"] = poi.geolong
                thispoi["geolat"] = poi.geolat
                thispoi["address"] = poi.address
                #Make sure to enforce no conflicts in team venue ownership
                thispoi["tag_owner"] = poi.team_set.all()[0].name
                pois.append(thispoi)
    except Exception, e:
        print e
        return HttpResponse("invalid request")
    print pois
    return HttpResponse("nope")
