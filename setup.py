from setuptools import setup, find_packages
import os

version = '1.0b1'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='koslab.messengerbot',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://github.com/koslab/koslab.messengerbot/',
      license='MIT',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['koslab'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'kombu',
          'requests',
          'beaker',
          'morepath',
          'PyYAML'
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts':
              'messengerbot_hub=koslab.messengerbot.scripts:start_hub'
      })
