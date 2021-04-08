"""Setup file.
"""
__copyright__ = "Copyright (C) 2021  Matt Ferreira"
__license__ = "Apache License"

from setuptools import setup

# Read contents of README.md file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    README = f.read()

with open('avmp/core/VERSION') as version_file:
    version = version_file.read().strip()
assert isinstance(version, str)

install_requirements = ['pyTenable', 'requests']

setup(name='avmp',
      version=version,
      description='Command line vulnerability program manager.',
      long_description=README,
      license='Apache License',
      author='Matt Ferreira',
      author_email='rackreaver@gmail.com',
      download_url='https://github.com/RackReaver/AVMP',
      install_requires=install_requirements,
      packages=['avmp']
      )
