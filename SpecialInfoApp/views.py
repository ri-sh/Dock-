# Create your views here.
from django.contrib import auth
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from userInfo.models import UserProfile
import SpecialInfoApp.models
from django.utils.html import escape
import helper_functions

@csrf_exempt
def addInterest(request, type_requested):
    """
    Adds an interest to signed in user
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.addInterest, template)

@csrf_exempt
def addLivingLoc(request, type_requested):
    """
    Adds a living location to signed in user
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.addLivingLoc, template)

@csrf_exempt
def addSchool(request, type_requested):
    """
    Adds a school to signed in user
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.addSchool, template)

@csrf_exempt
def addWorkplace(request, type_requested):
    """
    Adds a workplace to signed in user
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.addWorkplace, template)

@csrf_exempt
def removeInterest(request, type_requested):
    """
    Removes an interest
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.removeInterest, template)

@csrf_exempt
def removeLivingLoc(request, type_requested):
    """
    Removes a living location
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.removeLivingLoc, template)

@csrf_exempt
def removeSchool(request, type_requested):
    """
    Removes a school
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.removeSchool, template)

@csrf_exempt
def removeWorkplace(request, type_requested):
    """
    Removes a workplace
    Data sent through JSON object attached to post
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.removeWorkplace, template)

def getExtraInfo(request, type_requested, user_id):
    """
    Returns all of the extra info for specified user, including interests, living locations, schools, and workplaces
    """
    response = None
    try:
        user_pro = auth.models.User.objects.get(pk=user_id).get_profile()
    except UserProfile.DoesNotExist:
        response = { 'success' : 0, 'error' : 'User does not exist.' }

    if not response:
        response = { 'success' : 1, 'extra_info' : user_pro.getInterests() + user_pro.getSchools() + user_pro.getLivingLocs() + user_pro.getWorkplaces() }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)

def searchExtraInfo(request, type_requested, extra_info_type, term):
    """
    Searches specified extra infos' entries, returning top 5 matches
    """
    term = escape(term)
    if extra_info_type == 'interests':
        results = [ interest.title for interest in SpecialInfoApp.models.Interest.objects.filter(title__icontains=term) ][0:5]
    elif extra_info_type == 'living_locs':
        results = [ living_loc.title for living_loc in SpecialInfoApp.models.LivingLoc.objects.filter(title__icontains=term) ][0:5]
    elif extra_info_type == 'schools':
        results = [ school.title for school in SpecialInfoApp.models.School.objects.filter(title__icontains=term) ][0:5]
    elif extra_info_type == 'workplaces':
        results = [ workplace.title for workplace in SpecialInfoApp.models.Workplace.objects.filter(title__icontains=term) ][0:5]

    response = None
    if len(results) == 0:
        response = { 'success' : 0, 'error' : 'No results match your term.' }
    else:
        response = { 'success' : 1, 'results' : results }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
