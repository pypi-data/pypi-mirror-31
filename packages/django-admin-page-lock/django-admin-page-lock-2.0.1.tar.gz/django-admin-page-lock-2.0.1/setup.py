from __future__ import unicode_literals

import imp
import os

from setuptools import (
    find_packages,
    setup
)


ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
README_FILE = os.path.join(ROOT, 'README.md')
INIT = os.path.join(ROOT, 'admin_page_lock', '__init__.py')
APP = imp.load_source('page_lock', INIT)

# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def fread(fname):
    return open(fname).read()


setup(
    name=APP.NAME,
    version=APP.VERSION,
    packages=find_packages(),
    include_package_data=True,
    license='Apache License, Version 2.0',
    description='Page Lock application prevents users from editing '
                'a page while it is being edited by someone else. '
                'The application is tailored to django admin implementation.',
    long_description=fread(README_FILE),
    long_description_content_type='text/markdown',
    url='https://github.com/ShowMax/django-admin-page-lock',
    author='Vojtech Stefka',
    author_email='oss+djangopage@showmax.com',
    keywords=['django', 'admin', 'locking', 'concurrency'],
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
)
