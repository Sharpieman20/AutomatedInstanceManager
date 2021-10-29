
from pathlib import Path
import subprocess as sp
import sys, os, shlex

os.chdir(Path(__file__).parent.resolve())

setup_py_file = Path.cwd() / 'setup.py'

if setup_py_file.exists():
    setup_py_file.unlink()

get_release_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/main/dist/setup.txt'

resource = urllib.request.urlopen(get_release_url)

release_url = resource.read().decode(resource.headers.get_content_charset())

r = requests.get(release_url, allow_redirects=True)
open('setup.py', 'w').write(r.text)

import setup
