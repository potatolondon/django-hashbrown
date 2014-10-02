from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Switch


def is_active(label, user=None):
    defaults = getattr(settings, 'HASHBROWN_SWITCH_DEFAULTS', {})

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

    if switch.globally_active or (
        user is not None and user.pk in get_user_model().objects.filter(
            available_switches=switch.pk).values_list('pk', flat=True)):

        return True

    else:
        return False
