# Django modules
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from taggit.models import Tag

# Our local modules
from dapi.models import Dap, MetaDap
from django.contrib.auth.models import User
from dapi.forms import *
from dapi.logic import *


def index(request):
    daps_list = MetaDap.objects.filter(active=True).order_by('package_name')
    return render(request, 'dapi/index.html', {'daps_list': daps_list})

def tag(request, tag):
    t = get_object_or_404(Tag, slug=tag)
    daps_list = MetaDap.objects.filter(tags__slug__in=[tag], active=True).order_by('package_name')
    return render(request, 'dapi/index.html', {'daps_list': daps_list, 'tag': t})

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
                form.errors['file'] = errors
    else:
        form = UploadDapForm()
    return render(request, 'dapi/upload.html', {'form': form})

def dap_devel(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if m.latest:
        return render(request, 'dapi/dap.html', {'metadap': m, 'dap': m.latest, 'similar': m.similar_active_daps()[:5]})
    else:
        raise Http404

def dap_stable(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if m.latest_stable:
        return render(request, 'dapi/dap.html', {'metadap': m, 'dap': m.latest_stable, 'similar': m.similar_active_daps()[:5]})
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
    return render(request, 'dapi/dap.html', {'metadap': m, 'dap': d, 'similar': m.similar_active_daps()[:5]})

def dap_version(request, dap, version):
    m = get_object_or_404(MetaDap, package_name=dap)
    d = get_object_or_404(Dap, metadap=m.pk, version=version)
    return render(request, 'dapi/dap.html', {'metadap': m, 'dap': d, 'similar': m.similar_active_daps()[:5]})

@login_required
def dap_admin(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if request.user != m.user and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to administrate this dap.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    cform = ComaintainersForm(instance=m)
    tform = TransferDapForm(instance=m)
    aform = ActivationDapForm(instance=m)
    dform = DeleteDapForm()
    if request.method == 'POST':
        if 'cform' in request.POST:
            cform = ComaintainersForm(request.POST, instance=m)
            if cform.is_valid():
                cform.save()
                m.comaintainers.remove(m.user)
                messages.info(request, 'Comaintainers successfully saved.')
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
        if 'tform' in request.POST:
            olduser = m.user
            tform = TransferDapForm(request.POST, instance=m)
            if tform.is_valid():
                if dap == request.POST['verification']:
                    tform.save()
                    m.comaintainers.add(olduser)
                    m.comaintainers.remove(m.user)
                    messages.info(request, 'Dap {dap} successfully transfered.'.format(dap=dap))
                    return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
                else:
                    tform.errors['verification'] = ['You didn\'t enter the dap\'s name correctly.']
        if 'aform' in request.POST:
            aform = ActivationDapForm(request.POST, instance=m)
            if aform.is_valid():
                if dap == request.POST['verification']:
                    aform.save()
                    messages.info(request, 'Dap {dap} successfully {de}activated.'.format(dap=dap,de='' if m.active else 'de'))
                    return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
                else:
                    aform.errors['verification'] = ['You didn\'t enter the dap\'s name correctly.']
        if 'dform' in request.POST:
            dform = DeleteDapForm(request.POST)
            if dform.is_valid():
                if dap == request.POST['verification']:
                    m.delete()
                    messages.info(request, 'Dap {dap} successfully deleted.'.format(dap=dap))
                    return HttpResponseRedirect(reverse('dapi.views.index'))
                else:
                    dform.errors['verification'] = ['You didn\'t enter the dap\'s name correctly.']
    return render(request, 'dapi/dap-admin.html', {'cform': cform, 'tform': tform, 'aform': aform, 'dform': dform, 'dap': m})

@login_required
def dap_leave(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if request.user == m.user:
        messages.error(request, 'You cannot leave this dap. First, transfer it to someone else.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    if not request.user in m.comaintainers.all():
        messages.error(request, 'You cannot leave this dap, you are not it\'s comaintainer.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    if request.method == 'POST':
        form = LeaveDapForm(request.POST)
        if form.is_valid():
            if dap == request.POST['verification']:
                m.comaintainers.remove(request.user)
                messages.info(request, 'Successfully leaved {dap}.'.format(dap=dap))
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
            else:
                form.errors['verification'] = ['You didn\'t enter the dap\'s name correctly.']
    else:
        form = LeaveDapForm()
    return render(request, 'dapi/dap-leave.html', {'form': form, 'dap': m})

@login_required
def dap_version_delete(request, dap, version):
    m = get_object_or_404(MetaDap, package_name=dap)
    d = get_object_or_404(Dap, metadap=m.pk, version=version)
    if request.user != m.user and not request.user in m.comaintainers.all() and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to delete versions of this dap.')
        return HttpResponseRedirect(reverse('dapi.views.dap_version', args=(dap, version)))
    if request.method == 'POST':
        form = DeleteVersionForm(request.POST)
        if form.is_valid():
            wrong = False
            if dap != request.POST['verification_name']:
                form.errors['verification_name'] = ['You didn\'t enter the dap\'s name correctly.']
                wrong = True
            if version != request.POST['verification_version']:
                form.errors['verification_version'] = ['You didn\'t enter the version correctly.']
                wrong = True
            if not wrong:
                d.delete()
                messages.info(request, 'Successfully deleted {dap}.'.format(dap=d))
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    else:
        form = DeleteVersionForm()
    return render(request, 'dapi/dap-version-delete.html', {'form': form, 'dap': d})

@login_required
def dap_tags(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if request.user != m.user and not request.user in m.comaintainers.all() and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to change tags of this dap.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    if request.method == 'POST':
        data = request.POST.copy()
        try:
            data['tags'] += ','
        except KeyError:
            pass
        form = TagsForm(data, instance=m)
        if form.is_valid():
            form.save()
            messages.info(request, 'Tags successfully saved.')
            return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    else:
        form = TagsForm(instance=m)
        if form['tags'].value():
            data = {'tags': ', '.join([tagged.tag.name for tagged in form['tags'].value()])}
            form = TagsForm(data, instance=m)
    return render(request, 'dapi/dap-tags.html', {'form': form, 'dap': m})

@login_required
def dap_delete(request, dap):
    m = get_object_or_404(MetaDap, package_name=dap)
    if request.user.username != m.user and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to delete this dap.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))

    else:
        form = DeleteDapForm()
    return render(request, 'dapi/dap-delete.html', {'form': form, 'm': m})

def user(request, user):
    u = get_object_or_404(User, username=user)
    return render(request, 'dapi/user.html', {'u': u})

@login_required
def user_edit(request, user):
    u = get_object_or_404(User, username=user)
    if request.user.username != user and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to edit this user.')
        return HttpResponseRedirect(reverse('dapi.views.user', args=(user, )))
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
