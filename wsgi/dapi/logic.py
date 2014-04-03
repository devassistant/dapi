from django.conf import settings

import daploader
from daploader import dapver
import logging
import os
from cStringIO import StringIO
from dapi.models import *


def handle_uploaded_dap(f, user):
    '''Check uploaded file for validity and save it to the DB if it's OK.
    Report errors if not.'''
    errors = []
    try:
        dap = daploader.Dap(f.temporary_file_path(), mimic_filename=f.name)
        out = StringIO()
        if not dap.check(output=out, network=False, level=logging.ERROR):
            errors = out.getvalue().rstrip().split('\n')
    except (daploader.DapFileError, daploader.DapMetaError) as e:
        errors = [str(e)]
    dname = None
    if not errors:
        errors, dname = save_dap_to_db(f, dap, user)
    return errors, dname


def save_dap_to_db(f, dap, user):
    '''Save the dap and it's metadata to the database'''
    try:
        m = MetaDap.objects.get(package_name=dap.meta['package_name'])
        if m.user != user and user not in m.comaintainers.all():
            return ['We have {dap} already here, but you don\'t own it.'.format(dap=m.package_name)], None
        if m.latest and dapver.compare(m.latest.version, dap.meta['version']) >= 0:
            return ['We have {dap} already in the same or higher version ({version}). If you want to update it, bump the version.'.format(dap=m.package_name, version=m.latest.version)], None
    except MetaDap.DoesNotExist:
        m = MetaDap()
        m.package_name = dap.meta['package_name']
        m.user = user
        m.save()
    d = Dap()
    for attr in ['version', 'license', 'homepage', 'bugreports', 'summary', 'description']:
        setattr(d, attr, dap.meta[attr])
    d.metadap = m
    d.file = f
    d.save()
    for author in dap.meta['authors']:
        d.author_set.create(author=author)
    m.latest = d
    if not d.is_pre():
        m.latest_stable = d
    m.save()
    return [], m.package_name


def get_rank(metadap, user):
    '''Gets the rank of given metadap and user (if available)'''
    try:
        return metadap.rank_set.get(user=user).rank
    except:
        return None
