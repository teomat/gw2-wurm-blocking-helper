
from distutils.core import setup
import py2exe

setup(windows=['wurm overlay.py'], options={"py2exe":{"includes":["sip"]}})
