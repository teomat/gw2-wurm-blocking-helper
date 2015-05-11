
from distutils.core import setup
import py2exe

py2exe_options = dict(
	excludes=['doctest', 'pdb', 'unittest', 'difflib', 'inspect'],
	includes=['sip'],
	dll_excludes=['w9xpopen.exe'],
	compressed=True,
	dist_dir="wurm_blocking_helper",
	bundle_files=1
)

data_files= [
	'coordinates.json',
	'README.md',
	'COPYING.txt'
]

setup(windows=['wurm overlay.py'], options={"py2exe": py2exe_options}, zipfile=None, data_files=data_files)
