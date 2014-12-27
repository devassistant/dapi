from django.conf import settings
from django.utils.safestring import mark_safe


def type_box(request):
    if settings.SITE_URL.startswith('https://mirror'):
        css = 'warning'
        message = 'This is only a mirror of Dapi. '
        message += 'Logging in is not possible and changes from Dapi are only synced daily. '
        message += 'If possible, always use the '
        message += '<a href="http://dapi.devassistant.org/">main Dapi</a>.'
    elif settings.SITE_URL.startswith('https://staging'):
        css = 'danger'
        message = 'This is a testing version of Dapi. Please, '
        message += '<a href="http://dapi.devassistant.org/">go away</a>. '
        message += 'Do not trust any data on this website.'
    else:
        return {'type_box': ''}
    div = '<div class="alert alert-{c}">{m}</div>'.format(c=css, m=message)
    return {'type_box': mark_safe(div)}
