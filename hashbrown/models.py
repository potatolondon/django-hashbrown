from django.db import models

from .compat import User


class Switch(models.Model):

    label = models.CharField(max_length=200, unique=True)
    description = models.TextField(
        help_text='Short description of what this switch is doing', blank=True)
    globally_active = models.BooleanField(default=False)

    users = models.ManyToManyField(
        User, null=True, related_name='available_switches', blank=True)

    class Meta:
        verbose_name_plural = u'switches'

    def __unicode__(self):
        return self.label
