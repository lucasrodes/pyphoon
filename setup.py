from setuptools import setup, find_packages
setup(
    name="pyphoon",
    version="0.1",
    packages=find_packages(),
)

from distutils.core import setup

setup(
  name='pyphoon',
  packages=['pyphoon'], # this must be the same as the name above
  version='0.1',
  description='Python interface with Digital Typhoon dataset',
  author='Kitamoto Lab interns',
  author_email='hi@lcsrg.me',
  url='https://github.com/lucasrodes/pyphoon',
  download_url='https://github.com/lucasrodes/pyphoon/archive/0.1.tar.gz', # I'll explain this in a second
  keywords=['testing', 'logging', 'example'], # arbitrary keywords
  classifiers=[],
)