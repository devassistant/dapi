from django.db import models


class Dap(models.Model):
    package_name = models.CharField(max_length=200, unique=True)
    version = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200, blank=True)
    bugreports = models.CharField(max_length=200, blank=True)
    summary = models.CharField(max_length=500)
    description = models.CharField(max_length=2000, blank=True)

    def __unicode__(self):
        return self.package_name

    def link(self):
        return 'daps/' + self.package_name + '-' + self.version + '.dap'


class Author(models.Model):
    dap = models.ForeignKey(Dap)
    author = models.CharField(max_length=200)

    def __unicode__(self):
        return self.author
