import time
import os
import shutil
import uuid
import subprocess as sp
from datetime import datetime
import settings
from pathlib import Path

if settings.is_ahk_enabled() and not settings.is_test_mode():
    from ahk.script import _resolve_executable_path
    import wmi

def get_time():
    return time.time()

def has_passed(start_time, duration):
    return (get_time() - start_time) > duration

def get_pids():
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        return list(inst for inst in queues.get_all_instances() if inst.pid != -1)
    all_pids = []
    print('get all pids')
    for process in wmi.WMI().Win32_Process():
        # print('name {} pid {} caption {} commandline {}'.format(process.Name, process.ProcessId, process.Caption, process.Commandline))
        if 'java' in process.Name.lower():
            if 'jdk' in process.Commandline:
                all_pids.append(process.ProcessId)
    print('-------')
    return all_pids

def is_livesplit_open():
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        return  
    return ahk.find_window(title=b"LiveSplit") is not None

def file_to_script(script_name, **kwargs):
    script_str = ""
    for key in kwargs:
        script_str += f'global {key} := "{kwargs[key]}"\n'

    with open(path, "r") as ahk_script:
        script_str += ahk_script.read()
    return script_str

def run_ahk(script_name, **kwargs):
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        print("Run AHK script {} {}".format(script_name, kwargs))
        return
    # return ahk.run_script(file_to_script(script_name, **kwargs), blocking=not settings.should_parallelize_ahk())
    ahk_path = _resolve_executable_path()
    script_path = Path.cwd() / "src" / "ahk" / "{}.ahk".format(script_name)
    if 'pid' in kwargs:
        print('running {} pid {} with ahk path {}'.format(script_name, kwargs['pid'], ahk_path))
    else:
        print('running {} with ahk path {}'.format(script_name, ahk_path))
    args = [ahk_path, "/force", "/ErrorStdOut", script_path.resolve().as_posix()]
    for key in kwargs:
        if isinstance(kwargs[key], bool):
            args.append('{}'.format(kwargs[key]).lower())
        else:
            args.append(str(kwargs[key]))
    if settings.should_parallelize_ahk():
        sp.Popen(args)
    else:
        sp.call(args)

def add_attempt():
    curr_attempts = 0
    if os.path.exists("./attempts.txt"):
        with open("attempts.txt", "r") as f:
            curr_attempts = int(f.read().strip())
    with open("attempts.txt", "w") as f:
        f.write(str(curr_attempts + 1))

def get_pipe_file_location():
    global didInitializePipe

    if 'didInitializePipe' not in globals():
        didInitializePipe = True
        if pipe_file.exists():
            pipe_file.unlink()

    pipe_file = Path.cwd() / ".aim.daemonpipe"

    return pipe_file

def increment_reset_counter():

    if not settings.use_reset_counter():
        return
    if settings.is_test_mode():
        return

    attempts_fil = Path.cwd() / "attempts.txt"

    if not attempts_fil.exists():
        attempts_fil.touch()
        attempts_fil.write_text('1')

    num_attempts = -1
    
    with attempts_fil.open('r') as attempts_fil_opened:
        num_attempts = int(str(attempts_fil_opened.read()).rstrip())

    attempts_fil.unlink()
    attempts_fil.touch()

    with attempts_fil.open('w') as attempts_fil_opened:
        attempts_fil_opened.write(str(num_attempts))


