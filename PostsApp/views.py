# Create your views here.
from django.contrib import auth
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from userInfo.models import UserProfile
from PostsApp.models import Post
import helper_functions

@csrf_exempt
def createPost(request, type_requested):
    """
    Creates a new post from this user to specified user
    """
    template = None
    redirect = None
    if type_requested == 'rest':
        template = None
    elif type_requested == 'desktop':
        redirect = "/desktop/block/"
    return helper_functions.login_required_view(request, type_requested, UserProfile.createPost, template, redirect)

@csrf_exempt
def createComment(request, type_requested, comment_type):
    """
    Creates a new comment for specified post or event
    """
    template = None
    redirect = None
    if type_requested == 'rest':
        template = None
    elif type_requested == 'desktop':
        #Change redirect based on whether this is a post comment or event comment
        if comment_type == 'posts':
            try:
                post_id = helper_functions.get_request_dict(request, type_requested)["post_id"]
                redirect = "/desktop/posts/" + post_id + "/comments/"
            except KeyError:
                redirect = "/desktop/block/"
        else:
            try:
                event_id = helper_functions.get_request_dict(request, type_requested)["event_id"]
                redirect = "/desktop/block/events/" + event_id
            except KeyError:
                redirect = "/desktop/block/"
        
    if comment_type == 'posts':
        return helper_functions.login_required_view(request, type_requested, UserProfile.createPostComment, template, redirect)
    else:
        return helper_functions.login_required_view(request, type_requested, UserProfile.createEventComment, template, redirect)

def getComments(request, type_requested, post_id, offset=0):
    """
    Gets a list of comments for given post
    """
    try:
        offset = int(offset) #Make sure its an integer
    except ValueError:
        #Default it to 0
        offset = 0

    response = None
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        response = { 'success' : 0, 'error' : 'Post does not exist.' }

    #TODO maybe check if user has permission to view this

    if not response:
        #Get comments according to offset
        if len(post.comment_set.all()) >= offset + 10:
            comments = [ comment.getDetail() for comment in post.comment_set.all()[len(post.comment_set.all())-1*(offset+10):len(post.comment_set.all())-1*offset] ]
        else:
            comments = [ comment.getDetail() for comment in post.comment_set.all()[0:len(post.comment_set.all())-1*offset] ]
        response = { 'success' : 1, 'comments' : comments, 'post' : post.getDetail() }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
    elif type_requested == 'desktop':
        return render_to_response('comments.html', response, context_instance=RequestContext(request))
