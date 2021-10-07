
import subprocess as sp
import sys, os

def run_cmd(cmd):
    sp.call(shlex.split(cmd))

run_cmd('{}/pip3 install requests'.format(os.path.dirname(sys.executable)))

import requests

get_release_url = 'https://raw.githubusercontent.com/Sharpieman20/MultiResetTinder/main/dist/setup.txt'

release_url = requests.get(get_release_url).text.rstrip()

print(release_url)

r = requests.get(release_url, allow_redirects=True)
open('setup.py', 'w').write(r.text)

import setup
