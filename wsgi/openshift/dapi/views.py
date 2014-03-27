# Django modules
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import logout as auth_logout
from django.contrib import messages

# Our local modules
from dapi.models import Dap
from django.contrib.auth.models import User
from dapi.forms import UploadDapForm
from dapi.logic import *


def index(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = UploadDapForm(request.POST, request.FILES)
        if form.is_valid():
            errors, dname = handle_uploaded_dap(request.FILES['file'], request.user)
            if not errors:
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dname, )))
            else:
                for err in errors:
                    messages.error(request, err)
    else:
        form = UploadDapForm()
    daps_list = Dap.objects.all().order_by('package_name')
    return render_to_response('dapi/index.html', {'daps_list': daps_list, 'form': form, 'user': request.user}, context_instance=RequestContext(request))


def dap(request, dap):
    d = get_object_or_404(Dap, package_name=dap)
    return render_to_response('dapi/dap.html', {'dap': d})

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('dapi.views.index'))
