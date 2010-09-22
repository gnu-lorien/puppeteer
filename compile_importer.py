import shutil
from distutils.core import setup
import py2exe

setup(console=['import.py'])
shutil.rmtree('build')
