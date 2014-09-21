from django.db import models
from django.conf import settings


class Switch(models.Model):

    label = models.CharField(max_length=200)
    desciption = models.TextField(
        help_text='Short description of what this switch is doing', blank=True)
    globally_active = models.BooleanField(default=False)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True)

    def __unicode__(self):
        return self.label
