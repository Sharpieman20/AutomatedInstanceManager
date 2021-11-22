
from pathlib import Path
import subprocess as sp
import sys, os, shlex, urllib
import urllib.request

os.chdir(Path(__file__).parent.resolve())

setup_py_file = Path.cwd() / 'setup.py'

if setup_py_file.exists():
    setup_py_file.unlink()

get_release_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/main/dist/setup.txt'

resource = urllib.request.urlopen(get_release_url)

release_url = resource.read().decode(resource.headers.get_content_charset())

setup_fil_resource = urllib.request.urlopen(release_url)

setup_content = setup_fil_resource.read().decode(setup_fil_resource.headers.get_content_charset())

open('setup.py', 'w').write(setup_content)

import setup
