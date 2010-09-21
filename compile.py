import sys
import shutil
import os.path
from distutils.core import setup
import py2exe

setup(console=['PuppetPrinceUploader.py'])

#if os.path.exists('dist'):
#    shutil.rmtree('dist')
#if os.path.exists('build'):
#    shutil.rmtree('build')
"""
try:
    # if this doesn't work, try import modulefinder
    import py2exe.mf as modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]:
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

from distutils.core import setup
import sys, subprocess

def run(cmd):
    p = subprocess.Popen(cmd)
    p.wait()
    if p.poll():
        raise RuntimeError('failed running command: %r'%cmd)

#sys.path.append('..\\..\\..\\..\\core\\tools\\builds')
sys.argv.append('py2exe')
setup(
    options = {
        'py2exe'        : {
            'bundle_files': 1,
            #'includes'  : ['WoD_Update', 'dbhash',],
            #'packages'  : ['zsync',],
            'includes'  : ['PuppetPrinceUploader', '_scproxy'],

            # These DLLs are OS sensitive so we can not package them with the .exe file
            'dll_excludes': [ "mswsock.dll", "powrprof.dll" ]
            },
        },
    console=['PuppetPrinceUploader.py'],
    zipfile = None,
    )

"""
shutil.rmtree('build')
