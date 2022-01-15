
from pathlib import Path
import subprocess as sp
import sys, os, shlex, urllib
import requests

os.chdir(Path(__file__).parent.resolve())

fullrepo_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/rewrite/build/fullrepo.zip'

r = requests.get(fullrepo_url, allow_redirects=True)
open('../fullrepo.zip', 'wb').write(r.content)
