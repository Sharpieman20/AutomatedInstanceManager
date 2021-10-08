
import requests
import subprocess as sp
import shlex
import os
import sys
import shutil

def run_cmd(cmd):
    sp.call(shlex.split(cmd))

get_release_url = 'https://raw.githubusercontent.com/Sharpieman20/MultiResetTinder/main/dist/release.txt'

release_url = requests.get(get_release_url).text.rstrip()
 
r = requests.get(release_url, allow_redirects=True)
open('release.zip', 'wb').write(r.content)

directory_to_extract_to = ''

import zipfile
with zipfile.ZipFile('release.zip', 'r') as zip_ref:
    zip_ref.extractall()

os.remove('release.zip')

settings_url = 'https://raw.githubusercontent.com/Sharpieman20/MultiResetTinder/main/settings.json'
r = requests.get(settings_url, allow_redirects=True)
open('defaults/settings.json', 'w').write(r.content)

src_ahk = Path.cwd() / "src" / "ahk"
custom_directory = Path.cwd() / "custom"
if custom_directory.exists():
    for custom_ahk in custom_directory.iterdir():
        shutil.copyfile(custom_ahk, src_ahk / custom_ahk.name)

run_cmd('py -m pip install -r src/requirements.txt'.format(os.path.dirname(sys.executable)))
run_cmd('py src/python/main.py settings.json'.format(os.path.dirname(sys.executable)))

