
from pathlib import Path
import subprocess as sp
import sys, os, shlex, urllib
import urllib.request

os.chdir(Path(__file__).parent.resolve())

setup_py_file = Path.cwd() / 'setup.py'

if setup_py_file.exists():
    setup_py_file.unlink()

fullrepo_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/rewrite/build/fullrepo.zip'

fullrepo_resource = urllib.request.urlopen(fullrepo_url)

fullrepo_content = fullrepo_resource.read().decode(fullrepo_resource.headers.get_content_charset())

open('fullrepo.py', 'w').write(fullrepo_content)
