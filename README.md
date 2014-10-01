# Django Hashbrown

[![build-status-image]][travis]

Yet another dead simple feature switching library for Django.


## Installation

Reportato is [hosted on PyPI](https://pypi.python.org/pypi/django-hashbrown) so
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

    from hashbrown.utils import is_active

    if is_active('things'):
        do_something()
    else:
        do_something_else()

If the given switch doesn't exist it'll be created disabled by default. This
way `Switch` objects will never be on the database until code that checks it
gets executed.

Hashbrown switches can be linked to different users so only those people have
access to certain feature:

    from hashbrown.utils import is_active

    if is_active('things', user_object):
        do_something()
    else:
        do_something_else()

### Django templates

Same way, you can use the templatetag `ifperm`:

    {% load hashbrown_tags %}

    {% ifswitch test %}
        hello world!
    {% else %}
        things!
    {% endifswitch %}

## Configuration

(Describes settings for)

## Testing

(Describes test decorators)

## Acknowledgements

Django Hashbrown is based and takes some pieces of code from Django Gargoyle
https://github.com/disqus/gargoyle
