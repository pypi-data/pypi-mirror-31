# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from setuptools import find_packages, setup


def readme():
    with open('./README.rst') as f:
        readme = f.read()
    with open('./CHANGELOG.rst') as f:
        log = f.read()
    return readme + '\n\n' + log


setup(name='axe-selenium-python',
      version='2.0.3',
      description='Python library to integrate axe and selenium for web \
                accessibility testing.',
      long_description=readme(),
      url='http://github.com/mozilla-services/axe-selenium-python',
      author='Kimberly Sereduck',
      author_email='ksereduck@mozilla.com',
      packages=find_packages(),
      package_data={'axe_selenium_python': ['src/axe.min.js'], },
      install_requires=[
          'selenium>=3.0.2',
          'pytest>=3.0'
      ],
      license='Mozilla Public License 2.0 (MPL 2.0)',
      keywords='axe-core selenium pytest-selenium accessibility automation mozilla')
