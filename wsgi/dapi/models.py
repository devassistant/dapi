from django.db import models
from django.contrib.auth.models import User

from daploader import dapver

class MetaDap(models.Model):
    package_name = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(User)
    comaintainers = models.ManyToManyField(User, null=True, blank=True, default=None, related_name='codap_set')
    latest = models.ForeignKey('Dap', null=True, blank=True, default=None, related_name='+')
    latest_stable = models.ForeignKey('Dap', null=True, blank=True, default=None, related_name='+')

    def __unicode__(self):
        return self.package_name

    def sorted_versions(self):
        return sorted([dap.version for dap in self.dap_set.all()], cmp=dapver.compare, reverse=True)

class Dap(models.Model):
    metadap = models.ForeignKey(MetaDap)
    version = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200, blank=True)
    bugreports = models.CharField(max_length=200, blank=True)
    summary = models.CharField(max_length=500)
    description = models.CharField(max_length=2000, blank=True)

    def __unicode__(self):
        return self.metadap.package_name + '-' + self.version

    def link(self):
        return '/download/' + self.__unicode__() + '.dap'

    def is_pre(self):
        return not self.version[-1].isdigit()

    class Meta:
        unique_together = ('metadap', 'version',)


class Author(models.Model):
    dap = models.ForeignKey(Dap)
    author = models.CharField(max_length=200)

    def __unicode__(self):
        return self.author
