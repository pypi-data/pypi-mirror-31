#!/usr/bin/env python

# Python
import os
import sys

# Setuptools
from setuptools import setup, find_packages

# Django-Admin-Object-Actions
from admin_object_actions import __version__

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='django-admin-object-actions',
    version=__version__,
    author='Nine More Minutes, Inc.',
    author_email='support@ninemoreminutes.com',
    description='Django middleware to capture current request and user.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'),
                          'rb').read().decode('utf-8'),
    license='BSD',
    keywords='django admin object actions',
    url='https://github.com/ninemoreminutes/django-admin-object-actions/',
    packages=find_packages(exclude=['test_project']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.11',
        'django-crum',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'django>=1.11',
        'pytest',
        'pytest-cov',
        'pytest-django',
        'pytest-flake8',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    options={
        'egg_info': {
            'tag_build': '.dev',
        },
        'build_sphinx': {
            'source_dir': 'docs',
            'build_dir': 'docs/_build',
            'all_files': True,
            'version': __version__,
            'release': __version__,
        },
        'upload_sphinx': {
            'upload_dir': 'docs/_build/html',
        },
        'upload_docs': {
            'upload_dir': 'docs/_build/html',
        },
        'aliases': {
            'dev_build': 'egg_info sdist build_sphinx',
            'release_build': 'egg_info -b "" sdist build_sphinx',
            'test': 'pytest',
        },
    },
    **extra
)
