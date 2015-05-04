
from distutils.core import setup
import py2exe

py2exe_options = dict(
	excludes=['doctest', 'pdb', 'unittest', 'difflib', 'inspect'],
	includes=['sip'],
	compressed=True
)

setup(windows=['wurm overlay.py'], options={"py2exe": py2exe_options})
