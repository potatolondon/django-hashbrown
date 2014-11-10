from django.core.management import call_command
from django.db import IntegrityError
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase
from django.test.utils import override_settings

import hashbrown
from .compat import get_user_model
from .models import Switch
from .testutils import switches


HASHBROWN_SWITCH_DEFAULTS = {
    'test': {
        'globally_active': True
    },
    'things': {
        'globally_active': False,
        'description': 'This does some things'
    }
}


class UtilsTestCase(TestCase):

    def test_is_active_without_existing_flag_creates_it(self):
        self.assertFalse(Switch.objects.filter(label='some_feature').exists())

        self.assertFalse(hashbrown.is_active('some_feature'))

        self.assertTrue(Switch.objects.filter(label='some_feature').exists())

    def test_is_active_with_existing_disabled_flag(self):
        Switch.objects.create(label='some_feature', globally_active=False)

        with self.assertNumQueries(1):  # get
            self.assertFalse(hashbrown.is_active('some_feature'))

        self.assertEqual(
            Switch.objects.filter(label='some_feature').count(), 1)

    def test_is_active_with_existing_enabled_flag(self):
        Switch.objects.create(label='some_feature', globally_active=True)

        with self.assertNumQueries(1):  # get
            self.assertTrue(hashbrown.is_active('some_feature'))

        self.assertEqual(
            Switch.objects.filter(label='some_feature').count(), 1)

    def test_is_active_disabled_globally_for_users(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')

        Switch.objects.create(label='some_feature', globally_active=False)

        with self.assertNumQueries(2):  # get, check users
            self.assertFalse(hashbrown.is_active('some_feature', user=user))

    def test_is_active_enabled_globally_for_users(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')

        Switch.objects.create(label='some_feature', globally_active=True)

        with self.assertNumQueries(1):  # get
            self.assertTrue(hashbrown.is_active('some_feature', user=user))

    def test_is_active_for_certain_user_with_flag_enabled(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')
        switch = Switch.objects.create(
            label='some_feature', globally_active=True)
        switch.users.add(user)

        with self.assertNumQueries(1):  # get
            self.assertTrue(hashbrown.is_active('some_feature', user=user))

    def test_is_active_for_different_user_with_flag_enabled(self):
        user_1 = get_user_model().objects.create(
            email='test@example.com', username='test')
        user_2 = get_user_model().objects.create(
            email='test@example.com', username='test2')
        switch = Switch.objects.create(
            label='some_feature', globally_active=False)
        switch.users.add(user_1)

        with self.assertNumQueries(2):  # get, check user
            self.assertFalse(hashbrown.is_active('some_feature', user=user_2))

    @override_settings(HASHBROWN_SWITCH_DEFAULTS=HASHBROWN_SWITCH_DEFAULTS)
    def test_default_switches_on_settings(self):
        self.assertTrue(hashbrown.is_active('test'))

        self.assertFalse(hashbrown.is_active('things'))

        self.assertEqual(
            Switch.objects.get(label='things').description,
            'This does some things'
        )


class TemplateTagsTestCase(TestCase):
    def test_simple(self):
        Switch.objects.create(label='test', globally_active=True)

        template = Template("""
            {% load hashbrown_tags %}
            {% ifswitch 'test' %}
            hello world!
            {% endifswitch %}
        """)
        rendered = template.render(Context())

        self.assertTrue('hello world!' in rendered)

    def test_simple_new_switch(self):
        template = Template("""
            {% load hashbrown_tags %}
            {% ifswitch 'test' %}
            hello world!
            {% endifswitch %}
        """)
        rendered = template.render(Context())

        self.assertFalse('hello world!' in rendered)
        self.assertTrue(Switch.objects.filter(label='test').exists())

    def test_not_closing_raises_error(self):
        self.assertRaises(TemplateSyntaxError, Template, """
            {% load hashbrown_tags %}
            {% ifswitch 'test' %}
            hello world!
        """)

    def test_no_attribute_raises_error(self):
        self.assertRaises(TemplateSyntaxError, Template, """
            {% load hashbrown_tags %}
            {% ifswitch %}
            hello world!
            {% endifswitch %}
        """)

    def test_else(self):
        template = Template("""
            {% load hashbrown_tags %}
            {% ifswitch 'test' %}
            hello world!
            {% else %}
            things!
            {% endifswitch %}
        """)
        rendered = template.render(Context())

        self.assertFalse('hello world!' in rendered)
        self.assertTrue('things!' in rendered)

    def test_with_user(self):
        user_1 = get_user_model().objects.create(
            email='test@example.com', username='test')
        user_2 = get_user_model().objects.create(
            email='test@example.com', username='test2')
        switch = Switch.objects.create(
            label='some_feature', globally_active=False)
        switch.users.add(user_1)

        template = Template("""
            {% load hashbrown_tags %}
            {% ifswitch 'some_feature' user %}
            hello world!
            {% else %}
            things!
            {% endifswitch %}
        """)

        rendered = template.render(Context({'user': user_1}))
        self.assertTrue('hello world!' in rendered)
        self.assertFalse('things!' in rendered)

        rendered = template.render(Context({'user': user_2}))
        self.assertFalse('hello world!' in rendered)
        self.assertTrue('things!' in rendered)


class TestUtilsTestCase(TestCase):

    def test_as_decorator_active(self):
        @switches(things=True)
        def test():
            return hashbrown.is_active('things')

        self.assertTrue(test())

    def test_as_decorator_inactive(self):
        @switches(things=False)
        def test():
            return hashbrown.is_active('things')

        self.assertFalse(test())


class SwitchModelTestCase(TestCase):
    def test_label_is_unique(self):
        foo_switch = Switch.objects.create(label='foo')

        with self.assertRaises(IntegrityError):
            Switch.objects.create(label='foo')


class ManagementCommandTestCase(TestCase):
    def test_switches_command_creates_missing_switches(self):
        self.assertEqual(Switch.objects.count(), 0)

        with self.settings(HASHBROWN_SWITCH_DEFAULTS=HASHBROWN_SWITCH_DEFAULTS):
            call_command('switches')

        self.assertEqual(
            list(Switch.objects.values_list('label', flat=True)),
            ['test', 'things'],
        )

    def test_switches_command_ignores_existing_switches(self):
        foo = Switch.objects.create(
            label='foo',
            globally_active=False,
            description='Before description',
        )

        defaults = {
            'foo': {
                'globally_active': True,
                'description': 'After description',
            },
        }

        with self.settings(HASHBROWN_SWITCH_DEFAULTS=defaults):
            call_command('switches')

        self.assertEqual(
            list(Switch.objects.values()),
            [
                {
                    'id': foo.pk,
                    'label': 'foo',
                    'globally_active': False,
                    'description': 'Before description',
                }
            ],
        )

    def test_force_flag_deletes_unknown_switches(self):
        Switch.objects.create(label='foo')

        with self.settings(HASHBROWN_SWITCH_DEFAULTS={}):
            call_command('switches', force=True)

        self.assertEqual(Switch.objects.count(), 0)
