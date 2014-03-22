import daploader
import logging
import os
from cStringIO import StringIO

try:
    UPLOADDIR = os.path.join(os.environ['OPENSHIFT_DATA_DIR'],'upload')
except KeyError:
    UPLOADDIR = 'upload'

def handle_uploaded_dap(f):
    errors = []
    dapfile = os.path.join(UPLOADDIR,f.name)
    if os.path.isfile(dapfile):
        return ['Oops. We already have '+f.name+' here. If you are the owner and you want to update it, bump the version.']
    destination = open(dapfile, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    try:
        dap = daploader.Dap(dapfile)
        out = StringIO()
        if not dap.check(output=out,network=False,level=logging.ERROR):
            errors = out.getvalue().rstrip().split('\n')
    except (daploader.DapFileError, daploader.DapMetaError) as e:
        errors = [str(e)]
    if errors:
        os.remove(dapfile)
    else:
        errors = save_dap_to_db(dap)
    return errors

def save_dap_to_db(dap):
    from dapi.models import *
    try:
        d = Dap.objects.get(package_name=dap.meta['package_name'])
        if d.version >= dap.meta['version']:
            return ['We have '+d.package_name+' already in the same or higher version. If you are the owner, bump the version.']
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
    # TODO remove old authors
    for author in dap.meta['authors']:
        d.author_set.create(author=author)
    return []
