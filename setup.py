from setuptools import setup, find_packages
import os

version = '1.0b2'

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
      description="Facebook messenger bot framework",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='morepath facebook bot messenger chatbot',
      author='Izhar Firdaus',
      author_email='kagesenshi.87@gmail.com',
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
