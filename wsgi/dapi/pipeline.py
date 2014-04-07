from dapi import models


def create_profile(strategy, request, user=None, is_new=False, *args, **kwargs):
    '''Create a profile for newly created user'''
    if not user or not is_new:
        return None

    profile = models.Profile(user=user)
    profile.save()

    return {
        'is_new': True,
        'user': user
    }


def auto_sync(strategy, request, user=None, is_new=False, *args, **kwargs):
    '''Enable sync of data for newly created user'''
    if not user or not is_new:
        return None

    social = kwargs.get('social') or strategy.storage.user.get_social_auth(
        strategy.backend.name,
        uid
    )

    if social:
        user.profile.syncs.add(social)

    return {
        'user': user
    }


def user_details(strategy, details, response, user=None, *args, **kwargs):
    '''Update user details using data from provider if the user wants it.'''
    if user:
        social = kwargs.get('social') or strategy.storage.user.get_social_auth(
            strategy.backend.name,
            uid
        )
        if social in user.profile.syncs.all():
            changed = False  # flag to track changes
            protected = strategy.setting('PROTECTED_USER_FIELDS', [])
            keep = ('username', 'id', 'pk') + tuple(protected)

            for name, value in details.items():
                # do not update username, it was already generated
                # do not update configured fields if user already existed
                if name not in keep and hasattr(user, name):
                    if value and value != getattr(user, name, None):
                        try:
                            setattr(user, name, value)
                            changed = True
                        except AttributeError:
                            pass

            if changed:
                strategy.storage.user.changed(user)
