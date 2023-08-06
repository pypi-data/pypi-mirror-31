#!/usr/bin/env python
#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).


from distutils.core import setup
import os.path

with open(os.path.join(os.path.dirname(__file__), 'README')) as f:
    description = f.read()

setup(name="oops_amqp",
      version="0.1.0",
      description=\
              "OOPS AMQP transport.",
      long_description=description,
      maintainer="Launchpad Developers",
      maintainer_email="launchpad-dev@lists.launchpad.net",
      url="https://launchpad.net/python-oops-amqp",
      packages=['oops_amqp'],
      package_dir = {'':'.'},
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          ],
      install_requires = [
          'bson',
          'oops>=0.0.11',
          'amqp>=2.0.0',
          ],
      extras_require = dict(
          test=[
              'rabbitfixture',
              'six',
              'testresources',
              'testtools',
              ]
          ),
        entry_points=dict(
            console_scripts=[ # `console_scripts` is a magic name to setuptools
                'oops-amqp-trace = oops_amqp.trace:main',
                ]),
      )
