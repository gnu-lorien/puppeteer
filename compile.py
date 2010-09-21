import sys
import shutil
import os.path
from distutils.core import setup
import py2exe

setup(console=['PuppetPrinceUploader.py'])
shutil.rmtree('build')
