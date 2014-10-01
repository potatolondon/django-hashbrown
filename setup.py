import os
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name="django-hashbrown",
    version="0.5",
    author="Pablo Recio",
    author_email="pablo@potatolondon.com",
    description="Yet another dead simple feature switching library for Django.",
    long_description=(read('README.md')),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    license="BSD",
    keywords="django feature switching potato",
    url='https://github.com/potatolondon/django-hashbrown',
    packages=['hashbrown'],
    zip_safe=False,
)
