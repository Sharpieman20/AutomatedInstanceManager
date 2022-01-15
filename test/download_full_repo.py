
from pathlib import Path
import subprocess as sp
import sys, os, shlex, urllib
import urllib.request

os.chdir(Path(__file__).parent.resolve())

fullrepo_file = Path.cwd().parent / 'fullrepo.zip'

if fullrepo_file.exists():
    fullrepo_file.unlink()

fullrepo_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/rewrite/build/fullrepo.zip'

fullrepo_resource = urllib.request.urlopen(fullrepo_url)

fullrepo_content = fullrepo_resource.read().decode(fullrepo_resource.headers.get_content_charset())

open('fullrepo.zip', 'w').write(fullrepo_content)
