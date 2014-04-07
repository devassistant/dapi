from __future__ import division

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit.managers import TaggableManager
from social.apps.django_app.default import models as social_models

from daploader import dapver


class MetaDap(models.Model):
    '''Model represents a dap in no version.
    It holds the (meta)data related to all versions'''
    package_name = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(User)
    comaintainers = models.ManyToManyField(User, null=True, blank=True, default=None, related_name='codap_set')
    latest = models.ForeignKey('Dap', null=True, blank=True, default=None, related_name='+', on_delete=models.SET_DEFAULT)
    latest_stable = models.ForeignKey('Dap', null=True, blank=True, default=None, related_name='+', on_delete=models.SET_DEFAULT)
    tags = TaggableManager(blank=True)
    active = models.BooleanField(default=True)
    ranks = models.ManyToManyField(User, through='Rank', related_name='ranked_set', null=True, blank=True, default=None)
    reports = models.ManyToManyField(User, through='Report', related_name='reported_set', null=True, blank=True, default=None)
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


class Dap(models.Model):
    '''Model representing a specific version of a dap (of MetaDap instance)'''
    file = models.FileField(upload_to=lambda instance, filename: filename)
    metadap = models.ForeignKey(MetaDap)
    version = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200, blank=True)
    bugreports = models.CharField(max_length=200, blank=True)
    summary = models.CharField(max_length=500)
    description = models.CharField(max_length=2000, blank=True)

    def __unicode__(self):
        '''Returns dap's name followed by a dash and version'''
        return self.metadap.package_name + '-' + self.version

    def is_pre(self):
        '''Returns True if this is a pre_release'''
        return not self.version[-1].isdigit()

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


class Rank(models.Model):
    '''Rank given by one User to one MetaDap'''
    rank = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    metadap = models.ForeignKey(MetaDap)
    user = models.ForeignKey(User)

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
    reporter = models.ForeignKey(User, null=True, blank=True, default=None)
    email = models.EmailField(null=True, blank=True, default=None)
    versions = models.ManyToManyField(Dap, null=True, blank=True, default=None, related_name='report_set')
    message = models.TextField()
    solved = models.BooleanField(default=False)

    def __unicode__(self):
        '''Returns metadap name, username or e-mail and typo of report sepearted by spaces'''
        if self.reporter:
            user = self.reporter.username
        elif self.email:
            user = self.email
        else:
            user = '<anonymous>'
        return self.metadap.package_name + ' ' + user + ' ' + self.get_problem_display().split()[0].lower()


class Profile(models.Model):
    '''Additional data stored per User'''
    user = models.OneToOneField(User, primary_key=True)
    syncs = models.ManyToManyField(social_models.UserSocialAuth, null=True, blank=True, default=None)

    def __unicode__(self):
        '''Returns username'''
        return self.user.username


@receiver(post_delete, sender=Dap)
def dap_post_delete_handler(sender, **kwargs):
    '''When a dap is deleted, delete the associated file
    and refill values of latest and latest_stable to the DB.'''
    dap = kwargs['instance']
    # Delete the file
    storage, path = dap.file.storage, dap.file.path
    storage.delete(path)
    # Recalculate metadaps latest values
    m = dap.metadap
    m.latest = m._get_latest()
    m.latest_stable = m._get_latest_stable()
    m.save()


def recalculate_rank(sender, **kwargs):
    '''Recalculate the average rank and rank count in a form of handler'''
    rank = kwargs['instance']
    rank.metadap.rank_count = rank.metadap._get_rank_count()
    rank.metadap.average_rank = rank.metadap._get_average_rank()
    rank.metadap.save()


@receiver(post_save, sender=Rank)
def rank_post_save_handler(sender, **kwargs):
    '''When a rank is saved (created or updated), recalculate the average rank and rank count.'''
    recalculate_rank(sender, **kwargs)


@receiver(post_delete, sender=Rank)
def rank_post_delete_handler(sender, **kwargs):
    '''When a rank is deleted, recalculate the average rank and rank count.'''
    recalculate_rank(sender, **kwargs)
