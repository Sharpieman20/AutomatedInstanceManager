
import subprocess as sp
import sys, os, shlex

def run_cmd(cmd):
    print(cmd)
    sp.call(shlex.split(cmd))

run_cmd('{}\python.exe -m pip install requests'.format(os.path.dirname(sys.executable)))

import requests

get_release_url = 'https://raw.githubusercontent.com/Sharpieman20/MultiResetTinder/main/dist/setup.txt'

release_url = requests.get(get_release_url).text.rstrip()

print(release_url)

r = requests.get(release_url, allow_redirects=True)
open('setup.py', 'w').write(r.text)

import setup
