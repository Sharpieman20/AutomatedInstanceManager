from pathlib import Path
import shutil
import shlex
import subprocess as sp
import os
import time

def run_cmd(cmd, split=True, blocking=False):
    if split:
        cmd = shlex.split(cmd,posix=False)
    if blocking:
        return sp.call(cmd)
    else:
        return sp.Popen(cmd, stdout=sp.DEVNULL, stderr=sp.STDOUT, creationflags=sp.CREATE_NO_WINDOW)

def init_test_env():
    aim_test_dir = Path.home() / 'aimtest'
    if aim_test_dir.exists():
        shutil.rmtree(aim_test_dir)
    shutil.copyfile(Path.cwd().parent / 'run_aim.py', aim_test_dir / 'run_aim.py')
    shutil.copyfile(Path.cwd().parent / 'test_settings.json', aim_test_dir / 'my_settings.json')
    
def start_test():
    base_dir = Path.cwd()
    os.chdir(Path.home() / 'aimtest')
    run_cmd('py run_aim.py')
    time.sleep(60)
    os.chdir(base_dir)
    return

def inject_test_settings(to_inject):
    all_lines = []
    aim_test_dir = Path.home() / 'aimtest'
    settings_fil = aim_test_dir / 'my_settings.json'
    for ln in settings_fil:
        cur_ln = ln
        for entry in to_inject.keys():
            if entry in ln:
                cur_ln = re.sub(r',.*', ', {}'.format(to_inject[key]), cur_ln, count=1)
        all_lines.append(cur_ln)
    settings_fil.unlink()
    settings_fil.write_text(all_lines.join('\n'))

