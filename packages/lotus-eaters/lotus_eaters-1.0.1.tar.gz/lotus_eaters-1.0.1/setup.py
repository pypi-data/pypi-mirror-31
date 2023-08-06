#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code is distributed under the two-clause MIT license.
# Copyright (c) 2018 Michael Petychakis


__author__ = 'mpetyx (Michael Petychakis)'
__version__ = "1.0.1"
__maintainer__ = "Michael Petychakis"
__email__ = "hello@apilama.com"
__status__ = "Production"

from distutils.core import setup
from distutils import cmd
import os
import re
import sys

root_dir = os.path.abspath(os.path.dirname(__file__))


def get_version(package_name):
    version_re = re.compile(r"^__version__ = [\"']([\w_.-]+)[\"']$")
    package_components = package_name.split('.')
    path_components = package_components + ['version.py']
    with open(os.path.join(root_dir, *path_components)) as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '1.0.1'


class test(cmd.Command):
    """Run the tests for this package."""
    command_name = 'test'
    description = 'run the tests associated with the package'

    user_options = [
        ('test-suite=', None, "A test suite to run (defaults to 'tests')"),
    ]

    DEFAULT_TEST_SUITE = 'tests'

    def initialize_options(self):
        self.test_runner = None
        self.test_suite = None

    def finalize_options(self):
        self.ensure_string('test_suite', self.DEFAULT_TEST_SUITE)

    def run(self):
        """Run the test suite."""
        try:
            import unittest2 as unittest
        except ImportError:
            import unittest

        if self.verbose:
            verbosity=1
        else:
            verbosity=0

        loader = unittest.defaultTestLoader
        suite = unittest.TestSuite()

        if self.test_suite == self.DEFAULT_TEST_SUITE:
            for test_module in loader.discover('.'):
                suite.addTest(test_module)
        else:
            suite.addTest(loader.loadTestsFromName(self.test_suite))

        result = unittest.TextTestRunner(verbosity=verbosity).run(suite)

        if not result.wasSuccessful():
            sys.exit(1)


PACKAGE = 'lotus_eaters'


setup(
    name="lotus_eaters",
    version=get_version(PACKAGE),
    author="Michael Petychakis",
    author_email="hello@apilama.com",
    description="A simple Python throttling library relying on the token bucket algorithm with Redis Backend.",
    license="MIT",
    keywords=['throttle', 'rate limit', 'token bucket', 'leaky bucket'],
    url="http://github.com/mpetyx/lotus_eaters",
    download_url="http://pypi.python.org/pypi/lotus_eaters/",
    packages=['lotus_eaters'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    cmdclass={'test': test},
)
