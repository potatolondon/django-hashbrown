#!/usr/bin/env python
import os, sys

import django
from django.conf import settings

DIRNAME = os.path.dirname(__file__)
settings.configure(
      DEBUG = True,
      DATABASES = {
            'default': {'ENGINE': 'django.db.backends.sqlite3'},
      },
      INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'hashbrown',
      ),
      # Django 1.7 raises a warning if this isn't set. Pollutes test output.
      MIDDLEWARE_CLASSES = (),
)

try:
      django.setup()
except AttributeError:
      # Running Django<1.7
      pass

try:
      from django.test.runner import DiscoverRunner as TestSuiteRunner
except ImportError:
      # Running Django<1.6
      from django.test.simple import DjangoTestSuiteRunner as TestSuiteRunner

test_runner = TestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(['hashbrown', ])
if failures:
    sys.exit(failures)
