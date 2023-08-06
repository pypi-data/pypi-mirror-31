import os
from setuptools import setup, find_packages
#from distutils.core import setup

#with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
#    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'radiant',
    version = '1.0',
    packages = find_packages(),
    #package_dir = {'djangoforandroid': 'djangoforandroid'},


    author = 'Yeison Cardona',
    author_email = 'yeisoneng@gmail.com',
    maintainer = 'Yeison Cardona',
    maintainer_email = 'yeisoneng@gmail.com',

    #url = 'http://www.pinguino.cc/',
    url = 'http://yeisoncardona.com/',
    download_url = 'https://bitbucket.org/djangoforandroid/django-for-android/downloads',

    install_requires = ['django',
                        'python-for-android', #install from git
                        'appdirs',
                        'colorama>=0.3.3',
                        'sh>=1.10,<1.12.5',
                        'jinja2',
                        'six',
                        'django-static-precompiler',
                        ],

    include_package_data = True,
    license = 'BSD License',
    description = "Deploy Django web application on Android as APK.",
#    long_description = README,

    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
    ],



    scripts = [
          "cmd/radiant",
    ]
)
