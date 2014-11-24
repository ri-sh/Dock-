# Create your views here.
from django.contrib import auth
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from userInfo.models import UserProfile
from MessagesApp.models import ThreadMembership, Thread
import helper_functions

@csrf_exempt
def sendNewMessage(request, type_requested):
    """Creates a new thread and initial message"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.sendNewMessage, template)

@csrf_exempt
def sendReply(request, type_requested):
    """Creates a new message in the specified thread"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.createReply, template)

def getThreads(request, type_requested):
    """Retrieves a list of dictionary objects containing ThreadInfo for the most recent threads"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.getThreads, template)

def getNumUnreadMessages(request, type_requested):
    """Returns number of unread messages for this user, wrapped in a dictionary object"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.numUnreadMessages, template)

def getThread(request, type_requested, thread_id):
    """Returns most recent messages from specified thread"""
    request_dict = helper_functions.get_request_dict(request, type_requested)

    #Make sure user is logged in
    response = None
    if not request.user.is_authenticated():
        response = { 'success' : 0, 'error' : 'You are not logged in.' }
    
    if not response:
        #Make sure thread exists
        if Thread.objects.filter(pk=thread_id).exists():
            thread = Thread.objects.get(pk=thread_id)
        else:
            response = { 'success' : 0, 'error' : 'Thread does not exist' }

    if not response:
        if ThreadMembership.objects.filter(user=request.user.get_profile(), thread=thread).exists():
            #Set has_been_read to True
            tm = ThreadMembership.objects.get(user=request.user.get_profile(), thread=thread)
            tm.has_been_read = True
            tm.save()
            response = { 'success' : 1, 'thread' : thread.getThread(), 'recipients' : [ recip.user.getInfo() for recip in ThreadMembership.objects.filter(thread=thread) ] }
        else:
            response = { 'success' : 0, 'error' : 'You do not have permission to view this thread.' }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
