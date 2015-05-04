
from distutils.core import setup
import py2exe

setup(windows=['wurm overlay.pyw'], options={"py2exe":{"includes":["sip"]}})
