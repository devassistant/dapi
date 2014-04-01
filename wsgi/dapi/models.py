from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

from daploader import dapver

class MetaDap(models.Model):
    package_name = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(User)
    comaintainers = models.ManyToManyField(User, null=True, blank=True, default=None, related_name='codap_set')
    latest = models.ForeignKey('Dap', null=True, blank=True, default=None, related_name='+', on_delete=models.SET_DEFAULT)
    latest_stable = models.ForeignKey('Dap', null=True, blank=True, default=None, related_name='+', on_delete=models.SET_DEFAULT)
    tags = TaggableManager(blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.package_name

    def sorted_versions(self):
        return sorted([dap.version for dap in self.dap_set.all()], cmp=dapver.compare, reverse=True)

    def get_latest(self):
        versions = self.sorted_versions()
        if not versions:
            return None
        return Dap.objects.get(metadap=self, version=versions[0])

    def get_latest_stable(self):
        versions = self.sorted_versions()
        for version in versions:
            if version[-1].isdigit():
                return Dap.objects.get(metadap=self, version=version)
        return None

    def similar_active_daps(self):
        return [dap for dap in self.tags.similar_objects() if dap.active]

class Dap(models.Model):
    file = models.FileField(upload_to=lambda instance, filename: filename)
    metadap = models.ForeignKey(MetaDap)
    version = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200, blank=True)
    bugreports = models.CharField(max_length=200, blank=True)
    summary = models.CharField(max_length=500)
    description = models.CharField(max_length=2000, blank=True)

    def __unicode__(self):
        return self.metadap.package_name + '-' + self.version

    def is_pre(self):
        return not self.version[-1].isdigit()

    def delete(self):
        m = self.metadap
        super(Dap, self).delete()
        m.latest = m.get_latest()
        m.latest_stable = m.get_latest_stable()
        m.save()

    class Meta:
        unique_together = ('metadap', 'version',)


class Author(models.Model):
    dap = models.ForeignKey(Dap)
    author = models.CharField(max_length=200)

    def __unicode__(self):
        return self.author
