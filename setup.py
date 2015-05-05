
from distutils.core import setup
import py2exe

py2exe_options = dict(
	excludes=['doctest', 'pdb', 'unittest', 'difflib', 'inspect'],
	includes=['sip'],
	dll_excludes=['w9xpopen.exe'],
	compressed=True,
	dist_dir="wurm_blocking_helper"
)

setup(windows=['wurm overlay.py'], options={"py2exe": py2exe_options})
