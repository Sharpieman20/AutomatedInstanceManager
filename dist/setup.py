
from pathlib import Path
import subprocess as sp
import shlex
import os
import sys
import shutil

def run_cmd(cmd):
    sp.call(shlex.split(cmd))

run_cmd('py -m ensurepip')
run_cmd('py -m pip install --upgrade setuptools')
run_cmd('py -m pip install wheel')
run_cmd('py -m pip install --only-binary wheel requests')

import requests

src_dir = Path.cwd() / 'src'
if src_dir.exists():
    shutil.rmtree(Path.cwd() / 'src')

get_release_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/profiling/dist/release.txt'

release_url = requests.get(get_release_url).text.rstrip()

r = requests.get(release_url, allow_redirects=True)
open('release.zip', 'wb').write(r.content)

directory_to_extract_to = ''

import zipfile
with zipfile.ZipFile('release.zip', 'r') as zip_ref:
    zip_ref.extractall()

os.remove('release.zip')

wheel_urls = []

wheel_urls.append('https://github.com/Sharpieman20/AutomatedInstanceManager/raw/profiling/res/six-1.16.0-py2.py3-none-any.whl')
wheel_urls.append('https://github.com/Sharpieman20/AutomatedInstanceManager/raw/profiling/res/websocket_client-1.2.1-py2.py3-none-any.whl')
wheel_urls.append('https://github.com/Sharpieman20/AutomatedInstanceManager/raw/profiling/res/obs_websocket_py-0.5.3-py3-none-any.whl')
# wheel_urls.append('https://github.com/Sharpieman20/MultiResetTinder/raw/main/res/psutil-5.8.0-cp39-cp39-win_amd64.whl')

for url in wheel_urls:
    run_cmd('py -m pip install {}'.format(url))
# run_cmd('py -m pip install res/')
run_cmd('py -m pip install --only-binary :all: -r src/requirements.txt'.format(os.path.dirname(sys.executable)))

defaults_dir = Path.cwd() / 'defaults'

if defaults_dir.exists():
    shutil.rmtree(Path.cwd() / 'defaults')

settings_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/profiling/settings.json'
r = requests.get(settings_url, allow_redirects=True)

defaults_dir.mkdir()
settings_json = defaults_dir / 'settings.json'
if settings_json.exists():
    settings_json.unlink()
settings_json.touch()

open('defaults/settings.json', 'w').write(r.text)

settings_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/profiling/dist/basic_settings.json'
r = requests.get(settings_url, allow_redirects=True)

my_settings_json = Path('my_settings.json')

if not my_settings_json.exists():
    my_settings_json.touch()
    open(my_settings_json.name, 'w').write(r.text)


mock_mc_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/profiling/LaunchMockMC.java'
r = requests.get(mock_mc_url, allow_redirects=True)

test_dir = Path('test')

if not test_dir.exists():
    test_dir.mkdir()

mock_mc_fil = test_dir / 'LaunchMockMC.java'

if mock_mc_fil.exists():
    mock_mc_fil.unlink()

mock_mc_fil.touch()
mock_mc_fil.open('w').write(r.text)

run_cmd('py src/python/main.py my_settings.json'.format(os.path.dirname(sys.executable)))
