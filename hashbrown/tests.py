from django.contrib.auth import get_user_model
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

from .models import Switch
from .utils import is_active


class UtilsTestCase(TestCase):

    def test_is_active_without_existing_flag_creates_it(self):
        self.assertFalse(Switch.objects.filter(label='some_feature').exists())

        with self.assertNumQueries(4):  # get, start transaction, creation, end transaction
            self.assertFalse(is_active('some_feature'))

        self.assertTrue(Switch.objects.filter(label='some_feature').exists())

    def test_is_active_with_existing_disabled_flag(self):
        Switch.objects.create(label='some_feature', globally_active=False)

        with self.assertNumQueries(1):  # get
            self.assertFalse(is_active('some_feature'))

        self.assertEqual(
            Switch.objects.filter(label='some_feature').count(), 1)

    def test_is_active_with_existing_enabled_flag(self):
        Switch.objects.create(label='some_feature', globally_active=True)

        with self.assertNumQueries(1):  # get
            self.assertTrue(is_active('some_feature'))

        self.assertEqual(
            Switch.objects.filter(label='some_feature').count(), 1)

    def test_is_active_disabled_globally_for_users(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')

        Switch.objects.create(label='some_feature', globally_active=False)

        with self.assertNumQueries(2):  # get, check users
            self.assertFalse(is_active('some_feature', user=user))

    def test_is_active_enabled_globally_for_users(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')

        Switch.objects.create(label='some_feature', globally_active=True)

        with self.assertNumQueries(1):  # get
            self.assertTrue(is_active('some_feature', user=user))

    def test_is_active_for_certain_user_with_flag_enabled(self):
        user = get_user_model().objects.create(
            email='test@example.com', username='test')
        switch = Switch.objects.create(
            label='some_feature', globally_active=True)
        switch.users.add(user)

        with self.assertNumQueries(1):  # get
            self.assertTrue(is_active('some_feature', user=user))

    def test_is_active_for_different_user_with_flag_enabled(self):
        user_1 = get_user_model().objects.create(
            email='test@example.com', username='test')
        user_2 = get_user_model().objects.create(
            email='test@example.com', username='test2')
        switch = Switch.objects.create(
            label='some_feature', globally_active=False)
        switch.users.add(user_1)

        with self.assertNumQueries(2):  # get, check user
            self.assertFalse(is_active('some_feature', user=user_2))


class TemplateTagsTestCase(TestCase):
    def test_simple(self):
        Switch.objects.create(label='test', globally_active=True)

        template = Template("""
            {% load hashbrown_tags %}
            {% ifswitch test %}
            hello world!
            {% endifswitch %}
        """)
        rendered = template.render(Context())

        self.assertTrue('hello world!' in rendered)

    def test_simple_new_switch(self):
        template = Template("""
            {% load hashbrown_tags %}
            {% ifswitch test %}
            hello world!
            {% endifswitch %}
        """)
        rendered = template.render(Context())

        self.assertFalse('hello world!' in rendered)

    def test_not_closing_raises_error(self):
        self.assertRaises(TemplateSyntaxError, Template, """
            {% load hashbrown_tags %}
            {% ifswitch test %}
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
            {% ifswitch test %}
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
            {% ifswitch some_feature user %}
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
