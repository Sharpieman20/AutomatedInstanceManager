import time
import os
import shutil
import psutil
import uuid
import subprocess as sp
from datetime import datetime
import settings
from pathlib import Path
if settings.is_ahk_enabled() and not settings.is_test_mode():
    from ahk import AHK
    ahk = AHK()

def get_time():
    return time.time()

def has_passed(start_time, duration):
    return (get_time() - start_time) > duration

def get_pids():
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        return list(inst for inst in queues.get_all_instances() if inst.pid != -1)
    # TODO @Specnr - check that this actually works correctly
    my_pids = []
    for proc in psutil.process_iter():
        # Get process detail as dictionary
        process_info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent'])
        if "Minecraft" in process_info['name']:
            my_pids.append((process_info['name'],process_info['pid']))
    print(my_pids)
    return list(map(int, run_ahk_blocking("getPIDs", instances=int(settings.get_num_instances()), MultiMC=True).split("|")))

def is_livesplit_open():
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        return  
    return ahk.find_window(title=b"LiveSplit") is not None

def file_to_script(script_name, **kwargs):
    script_str = ""
    for key in kwargs:
        script_str += f'global {key} := "{kwargs[key]}"\n'
    path = Path.cwd() / "src" / "ahk" / "{}.ahk".format(script_name)
    with open(path, "r") as ahk_script:
        script_str += ahk_script.read()
    return script_str

def run_ahk(script_name, **kwargs):
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        print("Run AHK script {} {}".format(script_name, kwargs))
        return
    return ahk.run_script(file_to_script(script_name, **kwargs), blocking=False)

def run_ahk_blocking(script_name, **kwargs):
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        print("Run AHK script {} {}".format(script_name, kwargs))
        return
    return ahk.run_script(file_to_script(script_name, **kwargs), blocking=settings.get_ahk_default_background())

def add_attempt():
    curr_attempts = 0
    if os.path.exists("./attempts.txt"):
        with open("attempts.txt", "r") as f:
            curr_attempts = int(f.read().strip())
    with open("attempts.txt", "w") as f:
        f.write(str(curr_attempts + 1))
