from django.conf import settings
from dapi import models

from devassistant import dapi
from devassistant.dapi import dapver
import logging
import os
try:
    import cStringIO as sio
except ImportError:
    import io as sio


def handle_uploaded_dap(f, user):
    '''Check uploaded file for validity and save it to the DB if it's OK.
    Report errors if not.'''
    errors = []
    out = sio.StringIO()
    logger = logging.getLogger(f.name)
    handler = logging.StreamHandler(out)
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    try:
        dap = dapi.Dap(f.temporary_file_path(), mimic_filename=f.name)
        if not dap.check(network=False, logger=logger):
            errors = out.getvalue().rstrip().split('\n')
    except (dapi.DapFileError, dapi.DapMetaError) as e:
        errors = [str(e)]
    dname = None
    if not errors:
        errors, dname = save_dap_to_db(f, dap, user)
    return errors, dname


def save_dap_to_db(f, dap, user):
    '''Save the dap and it's metadata to the database'''
    try:
        m = models.MetaDap.objects.get(package_name=dap.meta['package_name'])
        if m.user != user and user not in m.comaintainers.all():
            return (
                ['We have {dap} already here, but you don\'t own it.'.format(dap=m.package_name)],
                None
            )
        if m.latest and dapver.compare(m.latest.version, dap.meta['version']) >= 0:
            return (
                ['We have {dap} already in the same or higher version ({version}). '
                    'If you want to update it, bump the version.'
                    .format(dap=m.package_name, version=m.latest.version)],
                None
            )
        if not m.active:
            return (
                ['We have {dap} already here, but it\'s not active.'.format(dap=m.package_name)],
                None
            )
    except models.MetaDap.DoesNotExist:
        m = models.MetaDap()
        m.package_name = dap.meta['package_name']
        m.user = user
        m.save()
    d = models.Dap()
    for attr in ['version', 'license', 'homepage', 'bugreports', 'summary', 'description']:
        setattr(d, attr, dap.meta[attr])
    d.sha256sum = dap.sha256sum
    d.metadap = m
    d.file = f
    d.save()
    for author in dap.meta['authors']:
        d.author_set.create(author=author)
    for dependency in dap.meta['dependencies']:
        dependency = dependency.replace(' ', '')  # remove spaces to make this canonical
        d.dependency_set.create(dependency=dependency)
    d.has_assistants = False
    for assistant in dap.list_assistants():
        d.assistant_set.create(assistant=assistant)
        if assistant.startswith('assistants/'):
            d.has_assistants = True
    d.save()
    for platform in dap.meta['supported_platforms']:
        try:
            p = models.Platform.objects.get(platform=platform)
        except models.Platform.DoesNotExist:
            p = models.Platform(platform=platform)
            p.save()
        p.dap_set.add(d)
        p.save()
    m.latest = d
    if not d.is_pre():
        m.latest_stable = d
    m.save()
    models.Dap.generate_dependencies_metafile()
    return [], m.package_name


def get_rank(metadap, user):
    '''Gets the rank of given metadap and user (if available)'''
    try:
        return metadap.rank_set.get(user=user).rank
    except:
        return None
