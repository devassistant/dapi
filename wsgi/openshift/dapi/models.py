from django.db import models

class Dap(models.Model):
    package_name = models.CharField(max_length=200)
    version = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    homepage = models.CharField(max_length=200,blank=True)
    bugreports = models.CharField(max_length=200,blank=True)
    summary = models.CharField(max_length=500)
    description = models.CharField(max_length=2000,blank=True)
    def __unicode__(self):
        return self.package_name

class Author(models.Model):
    dap = models.ForeignKey(Dap)
    author = models.CharField(max_length=200)
    def __unicode__(self):
        return self.author
