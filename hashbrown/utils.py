from django.contrib.auth import get_user_model
from .models import Switch


def is_active(label, user=None):
    switch, created = Switch.objects.get_or_create(
        label=label, defaults={'globally_active': False})

    if created:
        return False

    if switch.globally_active or (
        user is not None and user.pk in get_user_model().objects.filter(
            available_switches=switch.pk).values_list('pk', flat=True)):

        return True

    else:
        return False
