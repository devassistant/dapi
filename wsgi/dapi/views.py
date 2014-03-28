# Django modules
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Our local modules
from dapi.models import Dap, MetaDap
from django.contrib.auth.models import User
from dapi.forms import *
from dapi.logic import *


def index(request):
    daps_list = MetaDap.objects.all().order_by('package_name')
    return render(request, 'dapi/index.html', {'daps_list': daps_list})

@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadDapForm(request.POST, request.FILES)
        if form.is_valid():
            errors, dname = handle_uploaded_dap(request.FILES['file'], request.user)
            if not errors:
                messages.info(request, 'Dap successfully uploaded.')
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dname, )))
            else:
                for err in errors:
                    messages.error(request, err)
    else:
        form = UploadDapForm()
    return render(request, 'dapi/upload.html', {'form': form})

def dap_devel(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if m.latest:
        return render(request, 'dapi/dap.html', {'metadap': m, 'dap': m.latest})
    else:
        raise Http404

def dap_stable(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if m.latest_stable:
        return render(request, 'dapi/dap.html', {'metadap': m, 'dap': m.latest_stable})
    else:
        raise Http404

def dap(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if m.latest_stable:
        d = m.latest_stable
    elif m.latest:
        d = m.latest
    else:
        d = None
    return render(request, 'dapi/dap.html', {'metadap': m, 'dap': d})

def dap_version(request, dap, version):
    m = get_object_or_404(MetaDap, package_name=dap)
    d = get_object_or_404(Dap, metadap=m.pk, version=version)
    return render(request, 'dapi/dap.html', {'metadap': m, 'dap': d})

def user(request, user):
    u = get_object_or_404(User, username=user)
    return render(request, 'dapi/user.html', {'u': u})

@login_required
def user_edit(request, user):
    u = get_object_or_404(User, username=user)
    if request.user.username != user and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to edit this user.')
        return HttpResponseRedirect(reverse('dapi.views.user', args=(u, )))
    if request.method == 'POST':
        form = UserForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            messages.info(request, 'User successfully edited.')
            return HttpResponseRedirect(reverse('dapi.views.user', args=(u, )))
    else:
        form = UserForm(instance=u)
    return render(request, 'dapi/user-edit.html', {'form': form, 'u': u})

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dapi.views.index'))
    try:
        n = request.GET['next']
    except KeyError:
        n = ''
    return render(request, 'dapi/login.html', {'next': n})

@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('dapi.views.index'))
