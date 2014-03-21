from django.db import models

class Dap(models.Model):
    package_name = models.CharField(max_length=200)
    version = models.CharField(max_length=200)
    license = models.CharField(max_length=200)
    def __unicode__(self):
        return self.package_name
