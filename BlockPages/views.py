# Create your views here.
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from userInfo.models import UserProfile
from BlockPages.models import BlockEvent
from BlockPages.models import BlockPage
from userInfo.forms import ImageUploadForm
import helper_functions

@csrf_exempt
def updateBlock(request, type_requested):
    """
    Updates logged in user's block using POSTed coordinates
    """
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.updateCurrentBlock, template)

def myBlock(request, type_requested='desktop', offset=0, num_results=10):
    """
    Returns activity for user's current block
    """
    #Make sure user is logged in
    response = None
    if not request.user.is_authenticated():
        response = { 'success' : 0 }
    
    if not response:
        response = request.user.get_profile().getBlockActivity(offset=offset)

    #Switch rendering based on type
    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
    elif type_requested == 'desktop':
        return render_to_response('block_page.html', response, context_instance=RequestContext(request))

@csrf_exempt
def createEvent(request, type_requested='desktop'):
    """
    Creates a block event if user is logged in and post is not empty
    """
    #Check if they actually tried to create an event
    if request.method != 'POST':
        #They are just viewing page for the first time, display empty form
        return render_to_response('create_event.html', context_instance=RequestContext(request))

    request_dict = helper_functions.get_request_dict(request, type_requested)

    response = None
    if not request.user.is_authenticated():
        response = { 'success' : 0, 'error' : 'You are not logged in.' }
    else:
        title = ''
        description = ''
        duration = ''
        location = ''
        try:
            title = request_dict['title']
            description = request_dict['description'] if 'description' in request_dict else ''
            duration = request_dict['duration']
            location = request_dict['location']
        except KeyError:
            error = ''
            if 'title' not in request_dict:
                error += 'No title entered. '
            if 'description' not in request_dict:
                error += 'No description entered. '
            if 'duration' not in request_dict:
                error += 'No duration given. '
            if 'location' not in request_dict:
                error += 'No location given. '
            response = { 'success' : 0, 'error' : error, 'title' : title, 
                    'description' : description, 'duration' : duration, 
                    'location' : location }

        if not response:
            if title == '' or duration == '' or location == '':
                error = ''
                if title == '':
                    error += 'No title entered. '
                if description == '':
                    error += 'No description entered. '
                if duration == '':
                    error += 'No duration given. '
                if location == '':
                    error += 'No location given. '
                response = { 'success' : 0, 'error' : error, 'title' : title, 
                        'description' : description, 'duration' : duration, 
                        'location' : location }

        if not response:
            #Check if there was an image uploaded
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    new_image = helper_functions.handleUploadedImage(request.FILES['image'], request.user.get_profile())
                    new_event = BlockEvent(block_page=request.user.get_profile().current_block, author=request.user.get_profile(), duration=duration, event_title=title, description=description, location=location, image=new_image)
                except KeyError:
                    #Create new block event
                    new_event = BlockEvent(block_page=request.user.get_profile().current_block, author=request.user.get_profile(), duration=duration, event_title=title, description=description, location=location)

            else:
                #Create new block event
                new_event = BlockEvent(block_page=request.user.get_profile().current_block, author=request.user.get_profile(), duration=duration, event_title=title, description=description, location=location)

            #Save new event
            new_event.save()

            #Set user as attending event
            request.user.get_profile().events.add(new_event)
            request.user.get_profile().save()

            response = { 'success' : 1 }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
    elif type_requested == 'desktop':
        if response['success'] == 0:
            #There's an error; redisplay create block page with error text
            return render_to_response('create_event.html', response, context_instance=RequestContext(request))
        else:
            #It was successful, redirect back to Block page
            return HttpResponseRedirect('/desktop/block/')

@csrf_exempt
def attending(request, type_requested):
    """
    Creates entry in 'attending' join table to signify that the logged in user
    is attending the posted event
    This is only going to be called asynchronously
    """
    template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.attendingEvent, template)

def eventPage(request, type_requested, event_id, offset=0):
    """
    Gets info on event for given event_id
    """
    try:
        event = BlockEvent.objects.get(pk=event_id)
        if request.user.is_authenticated():
            response = event.getComments(offset=offset, user=request.user.get_profile())
        else:
            response = event.getComments(offset=offset)

    except BlockEvent.DoesNotExist:
        response = { 'success' : 0, 'error' : 'Event does not exist.' }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
    elif type_requested == 'desktop':
        return render_to_response('block_event.html', response, context_instance=RequestContext(request))

@csrf_exempt
def currentBlock(request, type_requested, offset=0, num_results=10):
    """
    Gets the Block feed for the posted latitude and longitude
    To be used as a preview pane
    """
    request_dict = helper_functions.get_request_dict(request, type_requested)

    try:
        #Get Block corresponding to POSTed lat/long
        (x, y) = helper_functions.computeXY(request_dict['latitude'], request_dict['longitude'])
        current_block = BlockPage.objects.get(x_coordinate=x, y_coordinate=y)
        response = current_block.getActivity(offset=offset)
    except KeyError:
        response = { 'success' : 0, 'error' : 'Latitude and longitude were not passed in' }
    except BlockPage.DoesNotExist:
        response = { 'success' : 0, 'error' : 'There is nothing posted for the current block' }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
