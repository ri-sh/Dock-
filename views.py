# Create your views here.
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def home(request):
    """
    Displays desktop homepage or redirects to mobile webpage if on mobile device
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect('/desktop/block/')
    return render_to_response('index.html', context_instance=RequestContext(request))
