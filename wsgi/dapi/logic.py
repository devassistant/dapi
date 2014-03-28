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


def handle_uploaded_dap(f, user):
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
        errors, dname = save_dap_to_db(dap, user)
    if errors:
        os.remove(dapfile)
    return errors, dname


def save_dap_to_db(dap, user):
    try:
        m = MetaDap.objects.get(package_name=dap.meta['package_name'])
        if m.user != user and user not in m.comaintainers.all():
            return ['We have ' + m.package_name + ' already here, but you don\'t own it.'], None
        if m.latest and dapver.compare(m.latest.version,dap.meta['version']) >= 0:
            return ['We have ' + m.package_name + ' already in the same or higher version (' + m.latest.version + '). If you want to update it, bump the version.'], None
    except MetaDap.DoesNotExist:
        m = MetaDap()
        m.package_name = dap.meta['package_name']
        m.user = user
        m.save()
    d = Dap()
    d.version = dap.meta['version']
    d.license = dap.meta['license']
    d.homepage = dap.meta['homepage']
    d.bugreports = dap.meta['bugreports']
    d.summary = dap.meta['summary']
    d.description = dap.meta['description']
    d.metadap = m
    d.save()
    for author in dap.meta['authors']:
        d.author_set.create(author=author)
    m.latest = d
    if not d.is_pre():
        m.latest_stable = d
    m.save()
    return [], m.package_name
