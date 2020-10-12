from setuptools import setup

# Read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    README = f.read()

with open(path.join(this_directory, 'vulcan', 'VERSION')) as version_file:
    version = version_file.read().strip()
assert isinstance(version, str)


install_requirements = [
    # Pre-built object for accessing the Tenable.io API
    'pyTenable',

    # Pre-built object for accessing the Jira API
    'jira'
]

setup(name='vulcan',
      version=version,
      description='A collection of tools for managing and automating vulnerability management.',
      long_description=README,
      long_description_content_type='text/markdown',
      license='Apache License',
      author='Matt Ferreira',
      author_email='rackreaver@gmail.com',
      url='https://github.com/RackReaver/Vulcan',
      install_requires=install_requirements
      )
