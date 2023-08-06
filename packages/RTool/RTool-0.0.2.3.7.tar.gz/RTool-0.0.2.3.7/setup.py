tag = '0.0.2.3.7'
from setuptools import setup, find_packages
#from distutils.core import setup
setup(
  name = 'RTool',
  packages = find_packages(),#['RTool'], # this must be the same as the name above
  version = '%s'%tag,
  description = 'A collection of personal tools, mostly Windows dependant',
  author = 'Ron Nofar',
  author_email = 'ronnofar2@gmail.com',
  url = 'https://github.com/RonNofar/RToolPackage', # use the URL to the github repo
  download_url = 'https://github.com/RonNofar/RToolPackage/archive/%s.tar.gz'%tag, # I'll explain this in a second
  keywords = ['RTool', 'win32', 'Maya'], # arbitrary keywords
  classifiers = []
  #package_data={'RTool' : ['ffmpeg/bin/ffmpeg.exe']}#,include_package_data=True
)

#http://wiki.python.org/moin/Distutils/Cookbook/AutoPackageDiscovery
