from __future__ import division

from devassistant.dapi import dapver
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.core import urlresolvers
from django.core import validators
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from social.apps.django_app.default import models as social_models
from taggit import managers as taggit_managers
from rest_framework.authtoken.models import Token
from django.conf import settings
import os


class MetaDap(models.Model):
    '''Model represents a dap in no version.
    It holds the (meta)data related to all versions'''
    package_name = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(auth_models.User)
    comaintainers = models.ManyToManyField(auth_models.User, null=True, blank=True,
                                           default=None, related_name='codap_set')
    latest = models.ForeignKey('Dap', null=True, blank=True, default=None, related_name='+',
                               on_delete=models.SET_DEFAULT)
    latest_stable = models.ForeignKey('Dap', null=True, blank=True, default=None,
                                      related_name='+', on_delete=models.SET_DEFAULT)
    tags = taggit_managers.TaggableManager(blank=True)
    active = models.BooleanField(default=True)
    ranks = models.ManyToManyField(auth_models.User, through='Rank', related_name='ranked_set',
                                   null=True, blank=True, default=None)
    reports = models.ManyToManyField(auth_models.User, through='Report',
                                     related_name='reported_set', null=True,
                                     blank=True, default=None)
    average_rank = models.FloatField(null=True, blank=True, default=None)
    rank_count = models.IntegerField(default=0)

    def __unicode__(self):
        '''Returns package name'''
        return self.package_name

    def sorted_versions(self):
        '''Returns a sorted list of version strings by the rules defined in daploader'''
        return sorted([dap.version for dap in self.dap_set.all()], cmp=dapver.compare, reverse=True)

    def _get_latest(self):
        '''Returns the dap with the latest version (if any).
        The latest attribute should be used to obtain this value from DB.'''
        versions = self.sorted_versions()
        if not versions:
            return None
        return Dap.objects.get(metadap=self, version=versions[0])

    def _get_latest_stable(self):
        '''Returns the dap with the latest stable version (if any).
        The latest_stable attribute should be used to obtain this value from DB.'''
        versions = self.sorted_versions()
        for version in versions:
            if version[-1].isdigit():
                return Dap.objects.get(metadap=self, version=version)
        return None

    def similar_active_daps(self):
        '''Returns active daps with similar tags'''
        return [dap for dap in self.tags.similar_objects() if dap.active]

    def similar_active_daps_api(self):
        '''Dirty trick to return API links of similar daps'''
        return [settings.SITE_URL +
                urlresolvers.reverse('metadap-detail', args=(dap.package_name, ))
                for dap in self.similar_active_daps()]

    def _get_average_rank(self):
        '''Calculates the average rank of the dap.
        The average_rank attribute should be used to obtain this value from DB.'''
        total = 0
        for rank in self.rank_set.all():
            total += rank.rank
        if not total:
            return None
        return total / self.rank_set.count()

    def _get_rank_count(self):
        '''Gets the count of ranks of the dap.
        The rank_count attribute should be used to obtain this value from DB.'''
        return self.rank_set.count()

    def get_unsolved_reports_count(self):
        '''Gets the number of active reports'''
        return self.report_set.filter(solved=False).count()

    def get_human_link(self, absolute=True):
        '''Gets the link to website, where the latest dap lives'''
        link = urlresolvers.reverse('dapi.views.dap', args=(self.package_name, ))
        if absolute:
            return settings.SITE_URL + link
        return link


class Dap(models.Model):
    '''Model representing a specific version of a dap (of MetaDap instance)'''
    file = models.FileField(upload_to=lambda instance, filename: filename)
    metadap = models.ForeignKey(MetaDap)
    version = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200, blank=True)
    bugreports = models.CharField(max_length=200, blank=True)
    summary = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    sha256sum = models.CharField(max_length=64)
    supported_platforms = models.ManyToManyField('Platform', null=True, blank=True,
                                                 default=None, related_name='dap_set')
    has_assistants = models.BooleanField(default=True)

    def __unicode__(self):
        '''Returns dap's name followed by a dash and version'''
        return self.metadap.package_name + '-' + self.version

    def is_pre(self):
        '''Returns True if this is a pre_release'''
        return not self.version[-1].isdigit()

    def is_latest(self):
        '''Whether the Dap is latest version of it's MetaDap.'''
        return self == self.metadap.latest

    def is_latest_stable(self):
        '''Whether the Dap is latest stable version of it's MetaDap.'''
        return self == self.metadap.latest_stable

    def get_authors(self):
        '''Returns the list of authors as strings'''
        return [author.author for author in self.author_set.all()]

    def get_dependencies(self):
        '''Returns the list of dependencies as strings'''
        return [dependency.dependency for dependency in self.dependency_set.all()]

    def get_supported_platforms(self):
        '''Returns the list of supported platforms as strings'''
        return [platform.platform for platform in self.supported_platforms.all()]

    def bugreports_link(self):
        '''Returns URL to add to bugreports link'''
        if '://' not in self.bugreports:
            return 'mailto:' + self.bugreports
        else:
            return self.bugreports

    def get_human_link(self, absolute=True):
        '''Gets the link to website, where this dap lives'''
        link = urlresolvers.reverse('dapi.views.dap_version',
                                    args=(self.metadap.package_name, self.version))
        if absolute:
            return settings.SITE_URL + link
        return link

    @classmethod
    def generate_dependencies_metafile(cls):
        '''Generates the file that lists the dependencies'''
        dest = os.path.join(settings.MEDIA_ROOT, 'meta.txt')
        with open(dest, 'w') as f:
            for d in Dap.objects.all():
                f.write(str(d))
                if d.dependency_set.exists():
                    f.write('; depends (')
                    deps = [str(dep) for dep in d.dependency_set.all()]
                    f.write(', '.join(deps))
                    f.write(')')
                f.write('\n')

    class Meta:
        unique_together = ('metadap', 'version',)


class Author(models.Model):
    '''Author field of dap's metadata.
    It allows to associate more authors to one dap.
    More authors of the same name and address are kept in the DB, but that's OK.'''
    dap = models.ForeignKey(Dap)
    author = models.CharField(max_length=200)

    def __unicode__(self):
        '''Returns name and e-mail address (value of author field)'''
        return self.author


class Assistant(models.Model):
    '''Assistant or snippet contained in a dap.
    It allows to associate more assistants to one dap.'''
    dap = models.ForeignKey(Dap)
    assistant = models.CharField(max_length=200)

    def __unicode__(self):
        '''Returns the assistant pseudo path'''
        return self.assistant


class Dependency(models.Model):
    '''Dependency field of dap's metadata.
    It allows to associate more dependencies to one dap.'''
    dap = models.ForeignKey(Dap)
    dependency = models.CharField(max_length=250)

    def __unicode__(self):
        '''Returns dependency string'''
        return self.dependency


class Platform(models.Model):
    '''Supported platform field of dap's metadata.
    It allows to associate more platforms to one dap
    For each platform, only one DB filed is created.'''
    platform = models.CharField(max_length=32, unique=True)

    def __unicode__(self):
        '''Returns platform name'''
        return self.platform


class Rank(models.Model):
    '''Rank given by one User to one MetaDap'''
    rank = models.IntegerField(
        validators=[
            validators.MaxValueValidator(5),
            validators.MinValueValidator(1)
        ]
    )
    metadap = models.ForeignKey(MetaDap)
    user = models.ForeignKey(auth_models.User)

    def __unicode__(self):
        '''Returns metadap name, username and rank, in this order, separated by spaces'''
        return self.metadap.package_name + ' ' + self.user.username + ' ' + str(self.rank)

    class Meta:
        unique_together = ('metadap', 'user',)


class Report(models.Model):
    '''Model that stores info about evil daps reported'''
    LEGAL = 'l'
    MALWARE = 'm'
    HATE = 'h'
    SPAM = 's'
    TYPE_CHOICES = (
        (LEGAL, 'Legal (copyright issues, non-free or patented content...)'),
        (MALWARE, 'Malware (this dap tries to break my system or leak my data)'),
        (HATE, 'Hate (racism, sexism, adult content, etc)'),
        (SPAM, 'Spam or advertising'),
    )
    problem = models.CharField(max_length=1, choices=TYPE_CHOICES)
    metadap = models.ForeignKey(MetaDap)
    reporter = models.ForeignKey(auth_models.User, null=True, blank=True, default=None,
                                 on_delete=models.SET_DEFAULT)
    email = models.EmailField(null=True, blank=True, default=None)
    versions = models.ManyToManyField(Dap, null=True, blank=True, default=None,
                                      related_name='report_set')
    message = models.TextField()
    solved = models.BooleanField(default=False)

    def __unicode__(self):
        '''Returns metadap name, username or e-mail and typ of report sepearted by spaces'''
        if self.reporter:
            user = self.reporter.username
        elif self.email:
            user = self.email
        else:
            user = '<anonymous>'
        return self.metadap.package_name + ' ' + user + ' ' + \
            self.get_problem_display().split()[0].lower()


class Profile(models.Model):
    '''Additional data stored per User'''
    user = models.OneToOneField(auth_models.User, primary_key=True)
    syncs = models.ManyToManyField(social_models.UserSocialAuth, null=True,
                                   blank=True, default=None)

    def __unicode__(self):
        '''Returns username'''
        return self.user.username

    def get_social_username(self, provider):
        '''Get the username of this user on given social auth provider, if any'''
        try:
            usa = social_models.UserSocialAuth.objects.get(user=self.user, provider=provider)
            return usa.extra_data['username']
        except (social_models.UserSocialAuth.DoesNotExist, KeyError):
            return None

    def get_social_url(self, provider):
        '''Get the URL of this user on given social auth provider, if any'''
        username = self.get_social_username(provider)
        if not username:
            return None
        try:
            url = getattr(settings, 'SOCIAL_AUTH_{provider}_PROFILE_LINK'
                          .format(provider=provider.upper()))
        except AttributeError:
            return None
        return url.format(username=username)

    def fedora_username(self):
        '''If the user uses Fedora to login, return his FAS username'''
        return self.get_social_username('fedora')

    def github_username(self):
        '''If the user uses Github to login, return his Github username'''
        return self.get_social_username('github')

    def get_human_link(self, absolute=True):
        '''Gets the link to website, where this user lives'''
        link = urlresolvers.reverse('dapi.views.user', args=(self.user.username, ))
        if absolute:
            return settings.SITE_URL + link
        return link


@receiver(signals.post_delete, sender=Dap)
def dap_post_delete_handler(sender, **kwargs):
    '''When a dap is deleted, delete the associated file
    and refill values of latest and latest_stable to the DB.
    Regenerate the file with dependencies as well'''
    dap = kwargs['instance']
    # Delete the file
    storage, path = dap.file.storage, dap.file.path
    storage.delete(path)
    # Recalculate metadaps latest values
    m = dap.metadap
    m.latest = m._get_latest()
    m.latest_stable = m._get_latest_stable()
    m.save()
    # Regenerate the file
    Dap.generate_dependencies_metafile()


def recalculate_rank(sender, **kwargs):
    '''Recalculate the average rank and rank count in a form of handler'''
    rank = kwargs['instance']
    rank.metadap.rank_count = rank.metadap._get_rank_count()
    rank.metadap.average_rank = rank.metadap._get_average_rank()
    rank.metadap.save()


@receiver(signals.post_save, sender=Rank)
def rank_post_save_handler(sender, **kwargs):
    '''When a rank is saved (created or updated), recalculate the average rank and rank count.'''
    recalculate_rank(sender, **kwargs)


@receiver(signals.post_delete, sender=Rank)
def rank_post_delete_handler(sender, **kwargs):
    '''When a rank is deleted, recalculate the average rank and rank count.'''
    recalculate_rank(sender, **kwargs)


@receiver(signals.pre_delete, sender=auth_models.User)
def user_pre_delete_handler(sender, **kwargs):
    '''When an user is deleted, save his e-mail address to his former reports.'''
    user = kwargs['instance']
    for report in user.report_set.all():
        report.email = user.email
        report.save()

@receiver(signals.post_save, sender=auth_models.User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    '''When an user is created, assign a token to him/her'''
    if created:
        Token.objects.create(user=instance)
