from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import models as auth_models
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from haystack import forms as haystack_forms
from haystack import query as haystack_query
from rest_framework import viewsets, permissions, mixins
from taggit import models as taggit_models
from dapi import forms
from dapi import logic
from dapi import models
from dapi import serializers


def index(request):
    '''The homepage, currentl lists top and most ranked daps'''
    top_rated = models.MetaDap.objects.filter(active=True).order_by(
        '-average_rank',
        '-rank_count',
    )[:10]
    most_rated = models.MetaDap.objects.filter(active=True).order_by(
        '-rank_count',
        '-average_rank',
    )[:10]
    recent = models.MetaDap.objects.filter(active=True).order_by('-pk')[:10]
    tags = taggit_models.Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).exclude(num_times=0).order_by('-num_times')[:10]
    return render(request, 'dapi/index.html', {
        'top_rated': top_rated,
        'most_rated': most_rated,
        'recent': recent,
        'tags': tags
    })


def tag(request, tag):
    '''Lists all daps of given tag'''
    t = get_object_or_404(taggit_models.Tag, slug=tag)
    all_tagged_daps = models.MetaDap.objects.filter(
        tags__slug__in=[tag],
        active=True,
    ).order_by('-average_rank', '-rank_count')
    paginator = Paginator(all_tagged_daps, 10)
    page = request.GET.get('page')
    try:
        daps_list = paginator.page(page)
    except PageNotAnInteger:
        daps_list = paginator.page(1)
    except EmptyPage:
        daps_list = paginator.page(paginator.num_pages)
    return render(request, 'dapi/tag.html', {'daps_list': daps_list, 'tag': t})


@login_required
def upload(request):
    '''Upload a dap form'''
    if request.method == 'POST':
        form = forms.UploadDapForm(request.POST, request.FILES)
        if form.is_valid():
            errors, dname = logic.handle_uploaded_dap(request.FILES['file'], request.user)
            if not errors:
                messages.success(request, 'Dap successfully uploaded.')
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dname, )))
            else:
                form.errors['file'] = form.error_class(errors)
    else:
        form = forms.UploadDapForm()
    return render(request, 'dapi/upload.html', {'form': form})


def dap_devel(request, dap):
    '''Display latest version of dap, even if that's devel'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    rank = logic.get_rank(m, request.user)
    reports = m.report_set.filter(solved=False)
    if m.latest:
        return render(request, 'dapi/dap.html', {
            'metadap': m,
            'dap': m.latest,
            'similar': m.similar_active_daps()[:5],
            'rank': rank,
            'reports': reports,
        })
    else:
        raise Http404


def dap_stable(request, dap):
    '''Display latest stable version of dap'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    rank = logic.get_rank(m, request.user)
    reports = m.report_set.filter(solved=False)
    if m.latest_stable:
        return render(request, 'dapi/dap.html', {
            'metadap': m,
            'dap': m.latest_stable,
            'similar': m.similar_active_daps()[:5],
            'rank': rank,
            'reports': reports,
        })
    else:
        raise Http404


def dap(request, dap):
    '''Display latest stable version of dap, or latest devel if no stable is available'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    rank = logic.get_rank(m, request.user)
    reports = m.report_set.filter(solved=False)
    if m.latest_stable:
        d = m.latest_stable
    elif m.latest:
        d = m.latest
    else:
        d = None
    return render(request, 'dapi/dap.html', {
        'metadap': m,
        'dap': d,
        'similar': m.similar_active_daps()[:5],
        'rank': rank,
        'reports': reports,
    })


def dap_version(request, dap, version):
    '''Display a particular version of dap'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    d = get_object_or_404(models.Dap, metadap=m.pk, version=version)
    rank = logic.get_rank(m, request.user)
    reports = m.report_set.filter(solved=False)
    return render(request, 'dapi/dap.html', {
        'metadap': m,
        'dap': d,
        'similar': m.similar_active_daps()[:5],
        'rank': rank,
        'reports': reports,
    })


@login_required
def dap_admin(request, dap):
    '''Administrate dap's comaintainers, transfer it to other user, (de)activate it or delete it'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    if request.user != m.user and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to administrate this dap.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    cform = forms.ComaintainersForm(instance=m)
    tform = forms.TransferDapForm(instance=m)
    aform = forms.ActivationDapForm(instance=m)
    dform = forms.DeleteDapForm()
    if request.method == 'POST':
        if 'cform' in request.POST:
            cform = forms.ComaintainersForm(request.POST, instance=m)
            if cform.is_valid():
                cform.save()
                m.comaintainers.remove(m.user)
                messages.success(request, 'Comaintainers successfully saved.')
                return HttpResponseRedirect(reverse('dapi.views.dap_admin', args=(dap, )))
        if 'tform' in request.POST:
            olduser = m.user
            tform = forms.TransferDapForm(request.POST, instance=m)
            if tform.is_valid():
                if dap == request.POST['verification']:
                    tform.save()
                    m.comaintainers.add(olduser)
                    m.comaintainers.remove(m.user)
                    messages.success(request, 'Dap {dap} successfully transfered.'.format(dap=dap))
                    return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
                else:
                    tform.errors['verification'] = \
                        tform.error_class(['You didn\'t enter the dap\'s name correctly.'])
        if 'aform' in request.POST:
            aform = forms.ActivationDapForm(request.POST, instance=m)
            if aform.is_valid():
                if dap == request.POST['verification']:
                    aform.save()
                    messages.success(request, 'Dap {dap} successfully {de}activated.'
                                     .format(dap=dap, de='' if m.active else 'de'))
                    return HttpResponseRedirect(reverse('dapi.views.dap_admin', args=(dap, )))
                else:
                    aform.errors['verification'] = \
                        aform.error_class(['You didn\'t enter the dap\'s name correctly.'])
        if 'dform' in request.POST:
            dform = forms.DeleteDapForm(request.POST)
            if dform.is_valid():
                if dap == request.POST['verification']:
                    m.delete()
                    messages.success(request, 'Dap {dap} successfully deleted.'.format(dap=dap))
                    return HttpResponseRedirect(reverse('dapi.views.index'))
                else:
                    dform.errors['verification'] = \
                        dform.error_class(['You didn\'t enter the dap\'s name correctly.'])
    return render(request, 'dapi/dap-admin.html', {
        'cform': cform,
        'tform': tform,
        'aform': aform,
        'dform': dform,
        'dap': m,
    })


@login_required
def dap_leave(request, dap):
    '''If you are the comaintainer of a dap, here you resign'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    if request.user == m.user:
        messages.error(request, 'You cannot leave this dap. First, transfer it to someone else.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    if not request.user in m.comaintainers.all():
        messages.error(request, 'You cannot leave this dap, you are not it\'s comaintainer.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    if request.method == 'POST':
        form = forms.LeaveDapForm(request.POST)
        if form.is_valid():
            if dap == request.POST['verification']:
                m.comaintainers.remove(request.user)
                messages.success(request, 'Successfully leaved {dap}.'.format(dap=dap))
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
            else:
                form.errors['verification'] = \
                    form.error_class(['You didn\'t enter the dap\'s name correctly.'])
    else:
        form = forms.LeaveDapForm()
    return render(request, 'dapi/dap-leave.html', {'form': form, 'dap': m})


@login_required
def dap_version_delete(request, dap, version):
    '''Delete a particular version of a dap'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    d = get_object_or_404(models.Dap, metadap=m.pk, version=version)
    if request.user != m.user and not request.user in m.comaintainers.all() \
       and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to delete versions of this dap.')
        return HttpResponseRedirect(reverse('dapi.views.dap_version', args=(dap, version)))
    if request.method == 'POST':
        form = forms.DeleteVersionForm(request.POST)
        if form.is_valid():
            wrong = False
            if dap != request.POST['verification_name']:
                form.errors['verification_name'] = \
                    form.error_class(['You didn\'t enter the dap\'s name correctly.'])
                wrong = True
            if version != request.POST['verification_version']:
                form.errors['verification_version'] = \
                    form.error_class(['You didn\'t enter the version correctly.'])
                wrong = True
            if not wrong:
                d.delete()
                messages.success(request, 'Successfully deleted {dap}.'.format(dap=d))
                return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    else:
        form = forms.DeleteVersionForm()
    return render(request, 'dapi/dap-version-delete.html', {'form': form, 'dap': d})


@login_required
def dap_tags(request, dap):
    '''Manage dap's tags'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    if request.user != m.user and not request.user in m.comaintainers.all() \
       and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to change tags of this dap.')
        return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    if request.method == 'POST':
        data = request.POST.copy()
        try:
            data['tags'] = data['tags'].lower() + ','
        except KeyError:
            pass
        form = forms.TagsForm(data, instance=m)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tags successfully saved.')
            return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    else:
        form = forms.TagsForm(instance=m)
        if form['tags'].value():
            data = {'tags': ', '.join([tagged.tag.name for tagged in form['tags'].value()])}
        else:
            data = {'tags': ''}
        form = forms.TagsForm(data, instance=m)
    return render(request, 'dapi/dap-tags.html', {'form': form, 'dap': m})


@login_required
def dap_rank(request, dap, rank):
    '''Rank a given dap with given rank. Use 0 to unrank.'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    rank = int(rank)
    if rank:
        r, c = request.user.rank_set.get_or_create(metadap=m, defaults={'rank': rank})
        if not c:
            r.rank = rank
            r.save()
        messages.success(request, 'Successfully ranked {dap} with {rank}'
                         .format(dap=dap, rank=rank))
    else:
        try:
            request.user.rank_set.get(metadap=m).delete()
        except Rank.DoesNotExist:
            pass
        messages.success(request, 'Successfully unranked {dap}'.format(dap=dap))
    return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))


def dap_report(request, dap):
    '''Report an evil dap'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    if request.user.is_authenticated():
        formclass = forms.ReportForm
    else:
        formclass = forms.ReportAnonymousForm
    if request.method == 'POST':
        form = formclass(m, request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            if request.user.is_authenticated():
                r.reporter = request.user
            r.save()
            form.save_m2m()
            if not settings.DEBUG:
                to = []
                if m.user.email:
                    to.append(m.user.email)
                for admin in settings.ADMINS:
                    to.append(admin[1])
                send_mail('Dap {dap} reported as evil'.format(dap=dap),
                          '''Hi, dap {dap} was reported as evil.
                          See {link} for more information.'''
                          .format(dap=dap,
                                  link=request.build_absolute_uri(
                                      reverse('dapi.views.dap_reports', args=(dap, ))
                                  )),
                          'no-reply@rhcloud.com',
                          to, fail_silently=False)
            messages.success(request, 'Dap successfully reported.')
            return HttpResponseRedirect(reverse('dapi.views.dap', args=(dap, )))
    else:
        form = formclass(m)
    return render(request, 'dapi/dap-report.html', {'form': form, 'dap': m})


def dap_reports(request, dap):
    '''List reports of given dap'''
    m = get_object_or_404(models.MetaDap, package_name=dap)
    if request.user.is_staff:
        reports = m.report_set.order_by('solved')
    else:
        reports = m.report_set.filter(solved=False)
    return render(request, 'dapi/dap-reports.html', {'dap': m, 'reports': reports})


@login_required
def report_toggle_solve(request, report_id):
    '''Mark solved reports unsolved and vice versa'''
    if not request.user.is_staff:
        raise Http404
    r = get_object_or_404(models.Report, id=report_id)
    r.solved = not r.solved
    r.save()
    messages.success(request, 'Successfully toggled the report')
    return HttpResponseRedirect(reverse('dapi.views.dap_reports', args=(r.metadap.package_name, )))


def user(request, user):
    '''Display the user profile'''
    u = get_object_or_404(auth_models.User, username=user)
    return render(request, 'dapi/user.html', {'u': u})


@login_required
def user_edit(request, user):
    '''Edit the user profile'''
    u = get_object_or_404(auth_models.User, username=user)
    if request.user.username != user and not request.user.is_superuser:
        messages.error(request, 'You don\'t have permissions to edit this user.')
        return HttpResponseRedirect(reverse('dapi.views.user', args=(user, )))
    uform = forms.UserForm(instance=u)
    pform = forms.ProfileSyncForm(instance=u.profile)
    dform = forms.DeleteUserForm()
    if request.method == 'POST':
        if 'uform' in request.POST:
            uform = forms.UserForm(request.POST, instance=u)
            if uform.is_valid():
                uform.save()
                messages.success(request, 'User {u} successfully saved.'.format(u=user))
                return HttpResponseRedirect(reverse('dapi.views.user_edit', args=(u, )))
        if 'pform' in request.POST:
            pform = forms.ProfileSyncForm(request.POST, instance=u.profile)
            if pform.is_valid():
                pform.save()
                messages.success(request, 'Sync settings successfully saved.')
                return HttpResponseRedirect(reverse('dapi.views.user_edit', args=(u, )))
        if 'dform' in request.POST:
            dform = forms.DeleteUserForm(request.POST)
            if dform.is_valid():
                if user == request.POST['verification']:
                    u.delete()
                    messages.success(request, 'Successfully deleted {user}.'.format(user=user))
                    return HttpResponseRedirect(reverse('dapi.views.index'))
                else:
                    dform.errors['verification'] = \
                        dform.error_class(['You didn\'t enter the username correctly.'])
    return render(request, 'dapi/user-edit.html', {
        'uform': uform,
        'pform': pform,
        'dform': dform,
        'u': u,
    })


def login(request):
    '''In another world, this would be a log in form.
    Here it just contains backend links.'''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dapi.views.index'))
    try:
        n = request.GET['next']
    except KeyError:
        n = ''
    return render(request, 'dapi/login.html', {'next': n})


@login_required
def logout(request):
    '''Logs out the user'''
    auth_logout(request)
    return HttpResponseRedirect(reverse('dapi.views.index'))


def terms(request):
    '''Terms and conditions'''
    return render(request, 'dapi/terms.html')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    '''API endpoint that allows users to be viewed'''
    queryset = auth_models.User.objects.all()
    lookup_field = 'username'
    serializer_class = serializers.UserSerializer


class MetaDapViewSet(viewsets.ReadOnlyModelViewSet):
    '''API endpoint that allows metadaps to be viewed

    A metadap stores the information about a dap across all it's versions'''
    queryset = models.MetaDap.objects.all()
    lookup_field = 'package_name'
    serializer_class = serializers.MetaDapSerializer


class DapViewSet(viewsets.ReadOnlyModelViewSet):
    '''API endpoint that allows daps to be viewed

    A dap represents one dap in a specific version'''
    queryset = models.Dap.objects.all()
    lookup_field = 'nameversion'
    serializer_class = serializers.DapSerializer

    def get_object(self, queryset=None):
        '''Returns the object the view is displaying'''
        if queryset is None:
            queryset = self.filter_queryset(self.get_queryset())

        nv = self.kwargs.get('nameversion', None)
        nv = nv.split('-')
        dap = '-'.join(nv[:-1])
        version = nv[-1]

        m = get_object_or_404(models.MetaDap, package_name=dap)
        obj = get_object_or_404(models.Dap, metadap=m.pk, version=version)

        self.check_object_permissions(self.request, obj)

        return obj


class SearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    '''API endpoint that allows to search for a metadap. Just add **?q=_query_** to the URL.'''
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.SearchResultSerializer

    def get_queryset(self, *args, **kwargs):
        # This will return a dict of the fount things
        request = self.request
        results = haystack_query.EmptySearchQuerySet()

        if request.GET.get('q'):
            form = haystack_forms.ModelSearchForm(request.QUERY_PARAMS,
                                                  searchqueryset=None, load_all=True)

            if form.is_valid():
                query = form.cleaned_data['q']
                results = form.search()
        else:
            form = haystack_forms.ModelSearchForm(searchqueryset=None, load_all=True)

        return results
