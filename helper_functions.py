#General helper functions
from django.contrib import auth
from django.utils import simplejson
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import os
import StringIO
from PIL import Image
import hashlib
import django
import re
import datetime
from boto.s3.connection import S3Connection

#Define AWS keys here
AWS_ACCESS_KEY_ID = 'AKIAIEX5CZIM6WWDY67Q'
AWS_SECRET_ACCESS_KEY = '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'

def get_request_dict(request, type_requested):
    """Get dictionary from request (either posted or in raw json form)"""
    if request.method == 'GET':
        return None
    if (type_requested == 'rest'):
        return simplejson.loads(request.raw_post_data)
    else:
        return request.POST

def dict_to_json_response(response):
    """Takes in a dictionary object, serializes it into JSON and returns it as an HttpResponse"""
    return HttpResponse(simplejson.dumps(response), mimetype='application/json')

def login_required_view(request, type_requested, method, template, redirect=None):
    """Generic view for a view that has to check for authentication first"""
    request_dict = get_request_dict(request, type_requested)

    #Make sure user is logged in
    response = None
    if not request.user.is_authenticated():
        response = { 'success' : 0, 'error' : 'You are not logged in.' }
    
    if not response:
        response = method(request.user.get_profile(), request_dict)

    #Switch rendering based on type
    if type_requested == 'rest':
        return dict_to_json_response(response)
    if type_requested == 'desktop':
        if redirect is not None:
            return HttpResponseRedirect(redirect)
        elif template is not None:
            return render_to_response(template, response, conext_instance=RequestContext(request))
        else:
            return render_to_response('base.html', response, conext_instance=RequestContext(request))
    
def my_strftime(date_time):
    """Returns string formatted in a uniform way based on received datetime object"""
    return '' if date_time == None else date_time.strftime("%A, %d %B %Y %I:%M%p")

def inverse_my_strftime(date_string):
    """
    Returns a datetime object created from the passed in string which has been
    formatted according to my_strftime
    """
    try:
        date_time = datetime.datetime.strptime(date_string, "%A, %d %B %Y %I:%M%p")
        return date_time
    except ValueError:
        return None

def relative_timestamp(date):
    """
    Returns a human readable difference between the time given and now
    i.e. "5 minutes ago", "27 seconds ago", etc.
    """
    diff = datetime.datetime.now() - date
    s = diff.seconds
    if diff.days > 7:
        if diff.days > 13:
            return '{0} weeks ago'.format(diff.days/7)
        else:
            return '{0} week ago'.format(diff.days/7)
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s/60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s/3600)

def validate_email(email):
    """
    Checks if the email address given is valid
    """
    return re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", email)

def handleUploadedImage(image, user):
    """
    Saves image object along with a thumbnail of the image
    Returns the image object created
    """
    from userInfo.models import ImageHolder
    image_file = StringIO.StringIO(image.read())
    real_image = Image.open(image_file)

    #TODO test this
    #Get connection to theblock bucket
    s3 = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = s3.get_bucket('theblock')

    #Get dimensions of image
    (width, height) = real_image.size
    #Calculate new, scaled dimensions (i.e. maximum dimensions for full size image)
    (width, height) = scaleDimensions(width, height, longest_side=700)

    #Convert it to RGB to make it look better
    real_image = real_image.convert("RGB")
    resized_image = real_image.resize((width, height))

    image_file = StringIO.StringIO()
    resized_image.save(image_file, 'JPEG')
    filename = hashlib.md5(image_file.getvalue()).hexdigest() + '.jpg'

    #Save to disk
    image_file = open(os.path.join('/tmp', filename), 'w')
    resized_image.save(image_file, 'JPEG')
    #image_file = open(os.path.join('/tmp', filename), 'r')
    #content = django.core.files.File(image_file)

    prof_pic = ImageHolder(creator=user, handle=filename)
    prof_pic.save() #Just to generate id
    #Save the full size image in "Images" directory with filename = <prof_pic.id>.jpg
    key = bucket.new_key('images/' + str(prof_pic.id) + '.jpg')
    key.set_contents_from_filename(os.path.join('/tmp', filename))
    key.set_acl('public-read')
    
    #Do this all again for thumbnail
    #Get dimensions of image
    (width, height) = real_image.size
    #Calculate new, scaled dimensions (i.e. maximum dimensions for full size image)
    (width, height) = scaleDimensions(width, height, longest_side=45)

    #Convert it to RGB to make it look better
    real_image = real_image.convert("RGB")
    resized_image = real_image.resize((width, height), Image.ANTIALIAS)

    image_file = StringIO.StringIO()
    resized_image.save(image_file, 'JPEG')
    filename = hashlib.md5(image_file.getvalue()).hexdigest() + '.jpg'

    #Save to disk
    image_file = open(os.path.join('/tmp', filename), 'w')
    resized_image.save(image_file, 'JPEG')
    #image_file = open(os.path.join('/tmp', filename), 'r')
    #content = django.core.files.File(image_file)
    
    #Save thumbnail in "Images/Thumbnails" directory with same name as fullsize
    key = bucket.new_key('images/Thumbnails/' + str(prof_pic.id) + '.jpg')
    key.set_contents_from_filename(os.path.join('/tmp', filename))
    key.set_acl('public-read')

    prof_pic.handle = str(prof_pic.id) + '.jpg'
    prof_pic.save()

    return prof_pic

def scaleDimensions(width, height, longest_side):
    if width > height:
        if width > longest_side:
            ratio = longest_side*1./width
            return (int(width*ratio), int(height*ratio))
    elif height > longest_side:
        ratio = longest_side*1./height
        return (int(width*ratio), int(height*ratio))
    return (width, height)

def computeXY(latitude, longitude):
    """
    Calculates the x and y coordinates for the block containing given coordinates
    Returns a tuple of the form (x_coord, y_coord)
    """
    #Assume 90 km == 1 degree longitude and 111 km == 1 degree latitude for now
    #We want 400 m by 400 m squares for the blocks
    x_coord = int(225 * longitude)
    y_coord = int(277.5 * latitude)

    return (x_coord, y_coord)
