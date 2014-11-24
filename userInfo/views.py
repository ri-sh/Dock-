# Create your views here.
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.utils.html import escape
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
import hashlib
import os
import random
import string
import StringIO
from PIL import Image
import hashlib
import django
from userInfo.models import UserProfile, ImageHolder
from userInfo.forms import ImageUploadForm
from BlockPages.views import myBlock
import helper_functions

@csrf_exempt
def login(request, type_requested):
    """Accepts a password and either an username or email, then attempts to login user"""
    request_dict = helper_functions.get_request_dict(request, type_requested)

    username = None
    try:
        email = request_dict['email']
        username = auth.models.User.objects.get(email=email)
    except KeyError:
        username = None
    except auth.models.User.DoesNotExist:
        username = None

    try:
        if not username:    #Only try to get username if not already determined by email
            username = request_dict['username']
        password = request_dict['password']

        user = auth.authenticate(username=username, password=password)
        if (user is not None and user.is_active):
            #Correct password, so we can log them in
            auth.login(request, user)
            response = { 'success' : 1, 'user_id' : user.id }
        else:
            #Not authorized, send back error
            response = { 'success' : 0, 'error' : 'Incorrect login information.' }
    except KeyError:
        response = { 'success' : 0, 'error' : 'Incorrect login information.' }
    
    #Switch rendering based on type of view being returned
    if type_requested == 'rest':
        #Return JSONObject
        return HttpResponse(simplejson.dumps(response), mimetype='application/json')
    #elif type_requested == 'mobile':
        #Render mobile site
    elif type_requested == 'desktop':
        #Render desktop site
        if response['success'] == 0:
            return render_to_response('block_page.html', response, context_instance=RequestContext(request))
        return HttpResponseRedirect('/desktop/block/')

def logout(request, type_requested):
    """Logs out user and redirects depending on type"""
    auth.logout(request)

    response = { 'success' : 1 }
    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
    elif type_requested == 'desktop':
        return HttpResponseRedirect('/')

@csrf_exempt
def signup(request, type_requested):
    """Creates a new user (and user profile) if the data is valid (i.e. email/username not already taken)"""
    request_dict = helper_functions.get_request_dict(request, type_requested)
    
    #Make sure data is set
    response = None
    email = ''
    username = ''
    password_1 = ''
    password_2 = ''
    first_name = ''
    last_name = ''

    #Sanity checking to make sure this wasn't a get
    if request_dict == None:
        response = { 'success' : 0 }
    else:
        try:
            email = request_dict['email']
            username = email if 'username' not in request_dict else request_dict['username']
            password_1 = request_dict['password']
            password_2 = request_dict['password']
            names = request_dict['name'].split()
            if (len(names) > 1):
                first_name = names[0]
                last_name = names[1]
            elif len(names) == 1:
                first_name = names[0]
                last_name = ''
            else:
                first_name = ''
                last_name = ''
        except KeyError:
            error = ''
            if 'email' not in request_dict:
                error += 'Email not entered. '
            if 'password' not in request_dict:
                error += 'Password not entered. '
            if 'first_name' not in request_dict:
                error += 'Name not entered.\n'
            response = { 'success' : 0, 'error' : error,
                    'email' : email, 'username' : username, 'password_1' : password_1, 
                    'password_2' : password_2, 'name' : first_name + last_name}

    if not response:
        if email == u'' or username == u'' or first_name == u'':
                error = ''
                if email == '':
                    error += 'Email not entered. '
                if password_1 == '':
                    error += 'Password not entered. '
                if first_name == '':
                    error += 'Name not entered.'
                response = { 'success' : 0, 'error' : error,
                        'email' : email, 'username' : username, 'password_1' : password_1, 
                        'password_2' : password_2, 'first_name' : first_name, 'last_name' : last_name }

    #Check if email is valid
    if not response and not helper_functions.validate_email(email):
        response = { 'success' : 0, 'error' : 'Invalid email address.' }

    if not response:
        if password_1 != password_2:
            response = { 'success' : 0, 'error' : 'Passwords do not match.' }

    #Check if username or email is taken
    if not response:
        if auth.models.User.objects.filter(username=username).exists():
            response = { 'success' : 0, 'error' : 'Username already taken.' }
    if not response:
        if auth.models.User.objects.filter(email=email).exists():
            response = { 'success' : 0, 'error' : 'Email already in use.' }

    if not response:
        new_user = auth.models.User.objects.create_user(username=username, email=email, password=password_1)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.is_active = True
        new_user.save()

        #Send user e-mail containing key which is their username salted & hashed
        #key = hashlib.md5('bailey' + username).hexdigest()
        #send_mail('The Block registration', 'Hi ' + str(first_name) + ' ' + str(last_name) + 
        #        ',\n\nWelcome to The Block! ' +
        #        'Click the following link to finish signing up: http://inmyblock.com/users/' + 
        #        str(new_user.id) + '/register/' + str(key) + 
        #        '\n\n-The Block', 'no-reply@inmyblock.com'
        #        , [email], fail_silently=False)

        #Create profile for this user
        user_account = UserProfile(user=new_user)
        user_account.save()

        user = auth.authenticate(username=username, password=password_1)
        if (user is not None and user.is_active):
            #Correct password, so we can log them in
            auth.login(request, user)

        response = { 'success' : 1 }
    
    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
    elif type_requested == 'desktop':
        if response['success'] == 0:
            #Theres an error, so redisplay signup page with error text
            return render_to_response('block_page.html', response, context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect('/desktop/block/')

def confirmRegistration(request, user_id, key):
    """
    View that handles final step in email verification of new users
    """
    try:
        user = auth.models.User.objects.get(pk=user_id)
        username = user.username
        real_key = hashlib.md5('bailey' + username).hexdigest()
        if real_key == key:
            user.is_active = True
            user.save()
            response = { 'success' : 1 }
        else:
            response = { 'success' : 0, 'error' : 'Key does not match user id' }
    except auth.models.User.DoesNotExist:
        response = { 'success' : 0, 'error' : 'User id not found' }

    #Display essentially blank page with status
    return render_to_response('registration_confirmation.html', response, context_instance=RequestContext(request))

@csrf_exempt
def editProfile(request, type_requested):
    """Modifies logged in user's data"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.editProfile, template)

def getProfile(request, type_requested, user_id):
    """Returns info about specified user"""
    #Get data from model
    response = None
    try:
        user = auth.models.User.objects.get(pk=user_id)
    except auth.models.User.DoesNotExist:
        response = { 'success' : 0, 'error' : 'User does not exist' }

    if not response:
        if request.user.is_authenticated():
            response = { 'success' : 1, 'info' : user.get_profile().getProfile(request.user.id) }
        else:
            response = { 'success' : 1, 'info' : user.get_profile().getProfile() }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)

def getFriends(request, type_requested, user_id):
    """Defines view for getting a list of user's friends along with the details for each user"""
    
    #Get data from model
    response = None
    try:
        user = auth.models.User.objects.get(pk=user_id)
    except auth.models.User.DoesNotExist:
        response = { 'success' : 0, 'error' : 'User does not exist' }

    if (not response):
        if request.user.is_authenticated():
            response = { 'success' : 1, 'friends' : user.get_profile().getFriendDetails(request.user.id) }
        else:
            response = { 'success' : 1, 'friends' : user.get_profile().getFriendDetails() }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)

def getFriendRequests(request, type_requested):
    """Displays friend requests for the logged in user"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.getFriendRequests, template)

def getActivity(request, type_requested, user_id, offset=0):
    """Displays activity for the specified user"""
    try:
        offset = int(offset) #Make sure offset is an integer
    except ValueError:
        #Default it to 0
        offset = 0
    
    response = None #Sentinel value to trigger early render
    try:
        user = auth.models.User.objects.get(pk=user_id)
    except auth.models.User.DoesNotExist:
        response = { 'success' : 0, 'error' : 'User does not exist.' }

    #Get logged in user if there is one
    if request.user.is_authenticated():
        requesting_user = request.user
    else:
        requesting_user = None

    if not response:
        response = user.get_profile().getUserActivity(requesting_user, offset)

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)
    elif type_requested == 'desktop':
        return render_to_response('profile.html', response, context_instance=RequestContext(request))
    else:
        return render_to_response('profile.html', response, context_instance=RequestContext(request))

def getFriendFeed(request, type_requested, offset=0):
    """Displays the aggregate activity of all the logged in user's friends"""
    try:
        offset = int(offset) #Make sure offset is an integer
    except ValueError:
        #Default it to 0
        offset = 0

    #Get logged in user if there is one
    response = None
    if request.user.is_authenticated():
        requesting_user = request.user
    else:
        response = { 'success' : 0, 'error' : 'You must be logged in to view this page.' }

    if not response:
        response = requesting_user.get_profile().getFriendFeed(offset)

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)

@csrf_exempt
def requestFriend(request, type_requested):
    """Creates a Relationship object from logged in user to user specified"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.requestFriend, template)

@csrf_exempt
def confirmFriend(request, type_requested):
    """Modifies Relationship object between user and specified user"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.confirmFriend, template)

@csrf_exempt
def rejectFriendRequest(request, type_requested):
    """Removes relationship object between these users if it has type P"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.rejectFriendRequest, template)

@csrf_exempt
def removeFriend(request, type_requested):
    """Removes relationship object between these two users"""
    template = None
    if type_requested == 'rest':
        template = None
    return helper_functions.login_required_view(request, type_requested, UserProfile.removeFriend, template)

def search(request, type_requested, term=None, offset=0):
    """
    Searches for a user given a term containing potentially multiple words
    """

    #Get terms from term by splitting string on whitespace
    if term == None:
        response = { 'success' : 0, 'error' : 'No search term given.' }
    else:
        terms = escape(term).split()

        length = len(terms)
        if length == 0:
            response = { 'success' : 0, 'error' : 'No search term given.' }
        elif length == 1:
            #Only one word term
            results = [ result.get_profile().getInfo() for result in auth.models.User.objects.filter(Q(first_name__icontains=terms[0]) | Q(last_name__icontains=terms[0])) ]
            response = { 'success' : 1, 'matches' : results }
        else:
            #Just consider first two terms for now
            results = [ result.get_profile().getInfo() for result in auth.models.User.objects.filter(Q(first_name__icontains=terms[0], last_name__icontains=terms[1]) | Q(first_name__icontains=terms[1], last_name__icontains=terms[0])) ]
            response = { 'success' : 1, 'matches' : results }
            
    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)

@csrf_exempt
def setProfilePic(request, type_requested):
    """
    Retrieves uploaded image, creates an ImageHolder object to save the image
    and then points the logged in user's profile pic to it
    """
    response = None
    #Make sure user is logged in
    if not request.user.is_authenticated():
        response = { 'success' : 0, 'error' : 'You are not logged in.' }
    
    if not response:
        if request.method == 'POST':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                #Handle the uploaded file
                new_image = helper_functions.handleUploadedImage(request.FILES['image'], request.user.get_profile())
                request.user.get_profile().profile_pic = new_image
                request.user.get_profile().save()
                response = { 'success' : 1 }
            else:
                response = { 'success' : 0, 'error' : 'Invalid/No file given.' }
        else:
            response = { 'success' : 0, 'error' : 'No file given.' }

    if type_requested == 'rest':
        return helper_functions.dict_to_json_response(response)

@login_required(login_url="/")
def viewAccount(request):
    """
    Returns 'Account' page, where users can view and edit their account settings
    which are currently just password, name, and profile pic
    """
    if request.method != 'POST':
        return render_to_response('account.html', context_instance=RequestContext(request))

    request_dict = helper_functions.get_request_dict(request, 'desktop')

    if not request.user.is_authenticated():
        response = { 'success' : 0, 'error' : 'You are not logged in.' }
    else:
        #Modify user's info if the password is correct
        response = None
        try:
            password = request_dict['password']
        except KeyError:
            response = { 'success' : 0, 'error' : 'Password must be entered.' }
        if not response:
            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None:
                #Correct password, modify settings for values that exist
                try:
                    user.first_name = request_dict['first_name']
                except KeyError:
                    pass
                
                try:
                    user.last_name = request_dict['last_name']
                except KeyError:
                    pass

                try:
                    if request_dict['new_password'] != '':
                        user.set_password(request_dict['new_password'])
                except KeyError:
                    pass

                try:
                    setProfilePic(request, 'rest')
                except KeyError:
                    pass

                user.save()
                response = { 'success' : 1, 'saved' : 1}
            else:
                response = { 'success' : 0, 'error' : 'Incorrect password given.' }
                
    return render_to_response('account.html', response, context_instance=RequestContext(request))

def alex_paino(request):
    """
    Displays info page for me
    """
    return render_to_response('alex_paino.html', context_instance=RequestContext(request))

def tos(request):
    """
    Displays Terms of Service
    """
    return render_to_response('tos.html', context_instance=RequestContext(request))

def mobile(request):
    """
    Displays mobile site
    """
    return render_to_response('mobile.html', context_instance=RequestContext(request))

def forgotPassword(request, type_requested):
    """
    Displays form to allow user to reset password
    """
    return render_to_response('forgot_password.html', context_instance=RequestContext(request))

@csrf_exempt
def resetPassword(request, type_requested):
    """
    Resets user's password to a random value, then sends this in an email to the user
    Display's confirmation page after
    """
    request_dict = helper_functions.get_request_dict(request, type_requested)

    try:
        email = request_dict["email"]
        
        #Attempt to get user profile matching email
        user = auth.models.User.objects.get(email=email)

        #Reset their password to some random value
        new_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
        user.set_password(new_password)

        #Send them this in an email
        send_mail('New Password for The Block', 'Hi ' + str(user.get_profile().first_name) + ' ' + str(user.get_profile().last_name) +
                ',\n\nYour password has been reset. Your new password is:\n' +
                new_password + '\n\nLogin using this password at http://www.inmyblock.com/ and then create a new password using the \'Account\' page. If you have further issues, email feedback@inmyblock.com\n\n-The Block team', 'no-reply@inmyblock.com',
                [email], fail_silently=False)

        response = { 'success' : 1 }
    except KeyError:
        response = { 'success' : 0, 'error' : 'No email given' }
    except auth.models.User.DoesNotExist:
        response = { 'success' : 0, 'error' : 'No account with that email address could be found' }

    if type_requested == 'desktop':
        return render_to_response('forgot_password.html', response, context_instance=RequestContext(request))
