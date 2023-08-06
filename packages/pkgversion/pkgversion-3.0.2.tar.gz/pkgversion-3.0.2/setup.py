
from setuptools import setup
setup(**{'author': 'Niels Lensink',
 'author_email': 'niels@elements.nl',
 'classifiers': ['Development Status :: 5 - Production/Stable',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.5',
                 'Topic :: Internet :: WWW/HTTP'],
 'description': 'Versioning utils for python projects',
 'include_package_data': True,
 'install_requires': [],
 'long_description': 'Python pkgversion\n'
                     '=================\n'
                     '\n'
                     '.. image:: '
                     'https://secure.travis-ci.org/kpn-digital/py-pkgversion.svg?branch=master\n'
                     '    :target:  '
                     'http://travis-ci.org/kpn-digital/py-pkgversion?branch=master\n'
                     '\n'
                     '.. image:: '
                     'https://img.shields.io/codecov/c/github/kpn-digital/py-pkgversion/master.svg\n'
                     '    :target: '
                     'http://codecov.io/github/kpn-digital/py-pkgversion?branch=master\n'
                     '\n'
                     '.. image:: https://img.shields.io/pypi/v/pkgversion.svg\n'
                     '    :target: https://pypi.python.org/pypi/pkgversion\n'
                     '\n'
                     '.. image:: '
                     'https://readthedocs.org/projects/py-pkgversion/badge/?version=latest\n'
                     '    :target: '
                     'http://py-pkgversion.readthedocs.org/en/latest/?badge=latest\n'
                     '\n'
                     '\n'
                     'Versioning utils for python projects\n',
 'name': 'pkgversion',
 'packages': ['pkgversion'],
 'tests_require': ['tox'],
 'url': 'https://github.com/kpn-digital/py-pkgversion',
 'version': '3.0.2',
 'zip_safe': False})
