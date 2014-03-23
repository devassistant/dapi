import daploader
from daploader import dapver
import logging
import os
from cStringIO import StringIO
from dapi.models import *

try:
    UPLOADDIR = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'upload')
except KeyError:
    UPLOADDIR = 'upload'


def handle_uploaded_dap(f):
    errors = []
    dapfile = os.path.join(UPLOADDIR, f.name)
    if os.path.isfile(dapfile):
        return ['Oops. We already have ' + f.name + ' here. If you are the owner and you want to update it, bump the version.'], None
    destination = open(dapfile, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    try:
        dap = daploader.Dap(dapfile)
        out = StringIO()
        if not dap.check(output=out, network=False, level=logging.ERROR):
            errors = out.getvalue().rstrip().split('\n')
    except (daploader.DapFileError, daploader.DapMetaError) as e:
        errors = [str(e)]
    dname = None
    if not errors:
        errors, dname = save_dap_to_db(dap)
    if errors:
        os.remove(dapfile)
    return errors, dname


def save_dap_to_db(dap):
    try:
        d = Dap.objects.get(package_name=dap.meta['package_name'])
        if dapver.compare(d.version,dap.meta['version']) >= 0:
            return ['We have ' + d.package_name + ' already in the same or higher version. If you are the owner, bump the version.'], None
        # keep the old .dap file as a backup
    except Dap.DoesNotExist:
        d = Dap()
    d.package_name = dap.meta['package_name']
    d.version = dap.meta['version']
    d.license = dap.meta['license']
    d.homepage = dap.meta['homepage']
    d.bugreports = dap.meta['bugreports']
    d.summary = dap.meta['summary']
    d.description = dap.meta['description']
    d.save()
    for author in d.author_set.all():
        author.delete()
    for author in dap.meta['authors']:
        d.author_set.create(author=author)
    return [], d.package_name
