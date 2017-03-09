# Django Hashbrown

[![build-status-image]][travis]

Yet another dead simple feature switching library for Django.

Supports Django 1.8, 1.9 & 1.10.

## Installation

Django Hashbrown is [hosted on PyPI](https://pypi.python.org/pypi/django-hashbrown) so
you can just install it using either:


    $ pip install django-hashbrown

Or:


    $ easy_install django-hashbrown

If you prefer to use the development version of it, you can clone the repository
and build it manually:

    $ git clone https://github.com/potatolondon/django-hashbrown.git
    $ cd django-hashbrown
    $ python setup.py install


[build-status-image]: https://secure.travis-ci.org/potatolondon/django-hashbrown.png?branch=master
[travis]: http://travis-ci.org/potatolondon/django-hashbrown?branch=master


## Usage

The main object to store feature switches data is `hashbrown.models.Switch`. This model has 4
attributes:

* `label` - Short name to identify each Switch
* `description` - Longer description about what the switch is about
* `globally_active` - Marks the tag as active all the time
* `users` - M2M marking what users have the feature activated

### Python

The simplest way to work with Hashbrown is to use `is_active` method:

    import hashbrown

    if hashbrown.is_active('things'):
        do_something()
    else:
        do_something_else()

If the given switch doesn't exist it'll be created disabled by default. This
way `Switch` objects will never be on the database until code that checks it
gets executed.

Hashbrown switches can be linked to different users so only those people have
access to certain feature:

    import hashbrown

    if hashbrown.is_active('things', user_object):
        do_something()
    else:
        do_something_else()

### Django templates

Same way, you can use the templatetag `ifswitch`:

    {% load hashbrown_tags %}

    {% ifswitch 'test' %}
        hello world!
    {% else %}
        things!
    {% endifswitch %}

Even with the user:

    {% load hashbrown_tags %}

    {% ifswitch 'test' user %}
        hello world!
    {% else %}
        things!
    {% endifswitch %}

## Configuration

You can prepare your switches before they get created in your settings,
indicating that way either if it'll be enabled or disabled. You can add into
your `settings.py` something like:

    HASHBROWN_SWITCH_DEFAULTS = {
        'test': {
            'globally_active': True
        },
        'things': {
            'globally_active': False,
            'description': 'This does some things'
        }
    }

So, when the switch "test" gets checked the first time, the switch will get
created globally active, while "things" won't be active but it'll have a
description.

## Testing

Another useful feature is the ability to mock switches in your tests, so
you can write tests for any case you are covering. It'll look something like:

    from hashbrown.testutils import switches

    @switches(my_flag=True)
    def test_things(self):
        # whatever you wanna test

## Django management command

Django Hashbrown adds a 'switches' management command, which creates / deletes
switches defined in your HASHBROWN_SWITCH_DEFAULTS settings.

To create all switches listed in HASHBROWN_SWITCH_DEFAULTS:

    python manage.py switches

Any existing switches already in the database will not be updated.

To create all switches and delete any switches *not* listed in
HASHBROWN_SWITCH_DEFAULTS:

    python manage.py switches --delete

You will be prompted for confirmation before the switches are deleted. Use
`--force` to delete the switches without confirmation.


## Acknowledgements

Django Hashbrown is based and takes some pieces of code from Django Gargoyle
https://github.com/disqus/gargoyle
