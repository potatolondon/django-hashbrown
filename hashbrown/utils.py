from django.conf import settings


SETTINGS_KEY = 'HASHBROWN_SWITCH_DEFAULTS'


def is_active(label, user=None):
    from .models import Switch

    defaults = get_defaults()

    globally_active = defaults[label].get(
        'globally_active',
        False) if label in defaults else False

    description = defaults[label].get(
        'description',
        '') if label in defaults else ''

    switch, created = Switch.objects.get_or_create(
        label=label, defaults={
            'globally_active': globally_active,
            'description': description,
        })

    if created:
        return switch.globally_active

    if (switch.globally_active or (
            user and not user.is_anonymous() and
            user.available_switches.filter(pk=switch.pk).exists())):
        return True
    return False


def get_defaults():
    return getattr(settings, SETTINGS_KEY, {})
