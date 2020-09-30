from setuptools import setup

# Read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    README = f.read()

with open('vulcan/VERSION') as version_file:
    version = version_file.read().strip()
assert isinstance(version, str)


install_requirements = []

setup(name='vulcan',
      version=version,
      description='A collection of tools for managing and automating vulnerability management.',
      long_description=README,
      license='Apache License',
      author='Matt Ferreira',
      author_email='rackreaver@gmail.com',
      download_url='https://github.com/RackReaver/VulnDBs',
      install_requires=install_requirements
      )
