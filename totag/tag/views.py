# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from models import Team, Venue, UserScore, TeamScore, UserProfile, Event
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import facebook
from geopy.distance import distance
from forms import UploadFileForm
import datetime
import pytz

tz = pytz.timezone('America/Chicago')

def time(request):
    t = datetime.datetime.now()
    return HttpResponse(tz.localize(t).strftime('%Y-%m-%d %H:%M:%S %z'))

@csrf_exempt
def uploadavatar(request):
    print "upload avatar request"
    #print "upload file " + str(request.META.CONTENT_TYPE)
    if request.method == 'POST':
        if "team_id" in request.POST:
            print "team id got: " + str(request.POST["team_id"])
            try:
                myteam = Team.objects.get(pk=request.POST["team_id"])
            except:
                return HttpResponse('invalid team')
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print "valid form"
            myteam.avatar = request.FILES['image']
            myteam.save()
            return HttpResponse('cool')
        else:
            return HttpResponse('POST form validation failed. ' + str(form.errors))
    else:
        print request.method
        form = UploadFileForm()
    return HttpResponse('invalid request type')

@csrf_exempt
def userfromfid(request):
    if not request.method == "GET":
        return HttpResponse("nope")
    response = {}
    try:
        response['id'] = UserProfile.objects.get(fid=request.GET.get("fid")).user.pk
    except Exception, e:
        print "id from fid error: "+ str(e)
        response['id'] = None
    return HttpResponse(json.dumps(response), mimetype="application/json")

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
def syncTeamPoints(request):
    teams = Team.objects.all()
    for team in teams:
        users = UserScore.objects.filter(team=team)
        teams = TeamScore.objects.filter(team=team)
        utally = 0
        for u in users:
            utally += u.score
        ttally = 0
        for t in teams:
            ttally += t.score
        print str(team.name) + " u:" + str(utally) + " t:" + str(ttally)
    return HttpResponse("points synced")

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
    print "/login POST: " + str(request.POST)
    try:
        user = UserProfile.objects.get(fb_authcode=request.POST["fbauthcode"])
        return HttpResponse(str(user.fid) + " logged in.")
        print "logged in"
    except:
        #When running on 21tag.com use fbauthcode to query fb for account
        #creation data
        #User.objects.create_user(request.POST[""])
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
                print id
                team = (UserProfile.objects.get(fid=id).team)
                teamdic = {}

                teamdic["name"] = team.name
                teamdic["nummem"] = len(team.userprofile_set.all())
                #vestigal fields
                teamdic["id"] = team.pk
                teamdic["name"] = team.name

                # tally friends by team
                if not team.id in fByTeam:
                    fByTeam[team.id] = 1
                else:
                    fByTeam[team.id] += 1
                teams.append(teamdic)
            except Exception, e:
                pass
                #print e
    except Exception, e:
        print e
        return HttpResponse("nope")
    #Add friend tally to response dic
    for team in teams:
        team["numf"] = fByTeam[team["id"]]
    response = {}
    response["TeamData"] = teams
    print response
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

# Hey Chris!
# Check this ouuuuut!

# Distance cutoff between targer lat/lon and venue lat/lon
# Check units with geopy docs
THRESHOLD_DISTANCE = 0.25  # in miles

# Number of venues to return
RESPONSE_LENGTH = 30
from operator import itemgetter


@csrf_exempt
def getpoisdetails(request):

    if request.method == "POST":
        return HttpResponse("nope")
    try:
        #print request.GET["lat"]
        #print request.GET["lon"]
        venues = Venue.objects.all()

        # Target coordinates
        userloc = (request.GET["lat"], request.GET["lon"])

        # Array of venues (dictionaries) within distance
        pois = []

        for poi in venues:

            # Venue coordinates
            poiloc = (poi.geolat, poi.geolong)
            distance_from_user = distance(userloc, poiloc).miles

            # Calculate distance between target and venue
            # See http://code.google.com/p/geopy/wiki/GettingStarted#Calculating_distances
            # Check the units of distance(), that could be the problem :)
            if distance_from_user < THRESHOLD_DISTANCE:

                # Prepare JSON Venue response for this venue
                eventList = []
                try:
                    events = Event.objects.filter(venue=poi).order_by('-time')[:10]
                    for e in events:
                        event = {}
                        event["message"] = e.message
                        event["points"] = e.points
                        if e.team != None:
                            event["team_id"] = e.team.pk
                        else:
                            event["team_id"] = ""
                        event["time"] = tz.localize(e.time).strftime('%Y-%m-%d %H:%M:%S %z')
                        event["user_id"] = e.user.pk
                        eventList.append(event)
                except Exception, e:
                    event = {}
                    #print "poidetails err " + str(e)
                thispoi = {}
                thispoi["events"] = eventList
                thispoi["id"] = poi.id
                thispoi["name"] = poi.name
                thispoi["zip"] = poi.zip
                thispoi["tag_playable"] = poi.tag_playable
                thispoi["geolong"] = poi.geolong
                thispoi["geolat"] = poi.geolat
                thispoi["address"] = poi.address
                thispoi["crossstreet"] = poi.crossstreet
                thispoi["city"] = poi.city
                thispoi["state"] = poi.state
                thispoi["distance"] = float(distance_from_user)
                #Make sure to enforce no conflicts in team venue ownership
                tag_owner = {}
                try:
                    tag_owner["id"] = poi.tag_owner.pk
                    tag_owner["name"] = poi.tag_owner.name
                    tag_owner["points"] = poi.tag_owner.points
                except:
                    tag_owner["id"] = ""
                    tag_owner["name"] = ""
                    tag_owner["points"] = ""
                thispoi["tag_owner"] = tag_owner
                pois.append(thispoi)
        # The iOS client requets 10 responses, I believe
        # But we're not using this input for now
        # RESPONSE_LENGTH = int(request.GET["num"])

        # Perform a sort or something sweet before
        pois = sorted(pois, key=itemgetter('distance'))
        pois = pois[:RESPONSE_LENGTH]
    except Exception, e:
        print e
        return HttpResponse("invalid request")
    container = {}
    meta = {}
    meta['total_count'] = len(pois)
    meta['previous'] = ""
    meta['next'] = ""
    container["meta"] = meta
    container["objects"] = pois
    #print pois
    return HttpResponse(json.dumps(container), mimetype="application/json")

    # Thoughts:
    # Check the return type of geopy's distance()
    # Add the distance b/t target and venue to
    # thispoi{} dic and sort pois[] by pois[thispoi[distance]]

@csrf_exempt
def deletefromteam(request):
    if not request.method == "POST":
        return HttpResponse("nope")
    print "/deletefromteam POST: " + str(request.POST)
    try:
        profile = UserProfile.objects.get(fid=request.POST["user"])
        print profile.team.name.lower()
        if profile.team.name.lower() == request.POST["team"].lower():
            profile.team = None
            profile.save()
            return HttpResponse("yeah")
        else:
            return HttpResponse("team does not exist")
    except Exception, e:
        print e
        return HttpResponse("nope")

@csrf_exempt
def addtoteam(request):
    if not request.method == "POST":
        return HttpResponse("nope")
    try:
        team = Team.objects.get(name=request.POST["team"])
        user = UserProfile.objects.get(fid=request.POST["user"])
        user.team = team
        user.save()
        return HttpResponse("yeah")
    except Exception, e:
        print e
        return HttpResponse("nope")
