from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Switch
from .utils import is_active


class UtilsTestCase(TestCase):

    def test_is_active_without_existing_flag_creates_it(self):
        self.assertFalse(Switch.objects.filter(label='some_feature').exists())

        result = is_active('some_feature')
        self.assertFalse(result)  # flag's disabled by default
        self.assertTrue(Switch.objects.filter(label='some_feature').exists())

    def test_is_active_with_existing_disabled_flag(self):
        Switch.objects.create(label='some_feature', globally_active=False)

        self.assertFalse(is_active('some_feature'))
        self.assertEqual(
            Switch.objects.filter(label='some_feature').count(), 1)

    def test_is_active_with_existing_enabled_flag(self):
        Switch.objects.create(label='some_feature', globally_active=True)

        self.assertTrue(is_active('some_feature'))
        self.assertEqual(
            Switch.objects.filter(label='some_feature').count(), 1)

    def test_is_active_disabled_globally_for_users(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')

        Switch.objects.create(label='some_feature', globally_active=False)
        self.assertFalse(is_active('some_feature', user=user))

    def test_is_active_enabled_globally_for_users(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')

        Switch.objects.create(label='some_feature', globally_active=True)
        self.assertTrue(is_active('some_feature', user=user))

    def test_is_active_for_certain_user_with_flag_enabled(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')
        switch = Switch.objects.create(
            label='some_feature', globally_active=True)
        switch.users.add(user)

        self.assertTrue(is_active('some_feature', user=user))

    def test_is_active_for_different_user_with_flag_enabled(self):
        user_1 = get_user_model().objects.create(
            email='test@example.com', username='test')
        user_2 = get_user_model().objects.create(
            email='test@example.com', username='test')
        switch = Switch.objects.create(
            label='some_feature', globally_active=True)
        switch.users.add(user_1)

        self.assertFalse(is_active('some_feature', user=user_2))
