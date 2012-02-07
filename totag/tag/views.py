# Create your views here.
from django.http import HttpResponse
import json
from django.contrib.auth.models import User
from models import Team
import string

def getTeam(request):
	team = Team.objects.all()
	#jdilly = jsonpickle.encode(team)
	#response -> {"teams":[...]}
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
	json_response = json.dumps(response)
	return HttpResponse(json_response, content_type="text/plain")
