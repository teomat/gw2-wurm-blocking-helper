
from distutils.core import setup
import py2exe

py2exe_options = dict(
	excludes=['doctest', 'pdb', 'unittest', 'difflib', 'inspect'],
	includes=['sip'],
	dll_excludes=['w9xpopen.exe'],
	compressed=True,
	dist_dir="wurm_blocking_helper"
)

data_files= [
	'coordinates.json'
]

setup(windows=['wurm overlay.py'], options={"py2exe": py2exe_options}, data_files=data_files)
