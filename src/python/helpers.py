import time
import os
import shutil
import uuid
import subprocess as sp
from datetime import datetime
import settings
import queues
from pathlib import Path

if settings.is_ahk_enabled() and not settings.is_test_mode():
    from ahk import AHK
    ahk = AHK()
    import wmi
if settings.is_test_mode():
    import shlex
    import time
    from AppKit import NSRunningApplication
    import psutil

def run_cmd(cmd):
    sp.call(shlex.split(cmd))

def get_time():
    return time.time()

def has_passed(start_time, duration):
    return (get_time() - start_time) > duration

def get_pids():
    all_pids = []
    if settings.is_test_mode():
        for process in psutil.process_iter():
            if 'java' in process.name().lower():
                all_pids.append(process.pid)
    else:
        for process in wmi.WMI().Win32_Process():
            if 'java' in process.Name.lower():
                all_pids.append(process.ProcessId)
    return all_pids

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
    return ahk.run_script(file_to_script(script_name, **kwargs), blocking=not settings.should_parallelize_ahk())

def run_ahk_blocking(script_name, **kwargs):
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        print("Run AHK script {} {}".format(script_name, kwargs))
        return
    return ahk.run_script(file_to_script(script_name, **kwargs), blocking=True)

def add_attempt():
    curr_attempts = 0
    if os.path.exists("./attempts.txt"):
        with open("attempts.txt", "r") as f:
            curr_attempts = int(f.read().strip())
    with open("attempts.txt", "w") as f:
        f.write(str(curr_attempts + 1))


def hide_mac_window(inst):
    process = NSRunningApplication.runningApplicationWithProcessIdentifier_(inst.pid)
    process.hide()

def show_mac_window(inst):
    process = NSRunningApplication.runningApplicationWithProcessIdentifier_(inst.pid)
    process.unhide()
