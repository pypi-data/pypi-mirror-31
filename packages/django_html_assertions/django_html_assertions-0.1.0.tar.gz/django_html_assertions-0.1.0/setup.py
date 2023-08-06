# -*- coding: utf-8 -*-
"""
Setup scripts for html_assertions
"""
from setuptools import find_packages, setup
import django_html_assertions
import os


# Read the contents of the README rst file for the long description
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_html_assertions',
    version=django_html_assertions.get_version(),
    packages=find_packages(exclude=['app']),
    include_package_data=True,
    license='MIT',
    description='A simple Django app to add html related assertions to djangos testing classes.',
    long_description=README,
    url='https://github.com/omni-digital/django_html_assertions/',
    download_url='https://github.com/omni-digital/django_html_assertions/tarball/{0}'.format(
        django_html_assertions.get_version()
    ),
    author='Omni Digital',
    author_email='dev@omni-digital.co.uk',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords=['django', 'test', 'tests', 'testing', 'html', 'assert', 'assertion', 'assertions'],
    install_requires=[]
)
