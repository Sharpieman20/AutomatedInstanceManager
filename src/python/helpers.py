import time
import os
import shutil
import uuid
import subprocess as sp
from datetime import datetime
import settings
import queues
from pathlib import Path
import queues
import shlex
from pipe import IoLockablePipe

if settings.is_ahk_enabled() and not settings.is_local_test_mode():
    from ahk.script import _resolve_executable_path

if settings.is_local_test_mode():
    import shlex
    import time
    from AppKit import NSRunningApplication
    import psutil
else:
    import wmi

def run_cmd(cmd, split=True, blocking=False):
    if split:
        cmd = shlex.split(cmd,posix=False)
    if blocking:
        return sp.call(cmd)
    else:
        return sp.Popen(cmd, stdout=sp.DEVNULL, stderr=sp.STDOUT, creationflags=sp.CREATE_NO_WINDOW)

def get_time():
    return time.time()

def has_passed(start_time, duration):
    return (get_time() - start_time) > duration

def get_pids():
    all_pids = []
    if settings.is_local_test_mode():
        for process in psutil.process_iter():
            if 'java' in process.name().lower():
                all_pids.append(process.pid)
    else:
        print('get all pids')
        my_wmi = wmi.WMI()
        query_results = my_wmi.query('Select ProcessId,Commandline from Win32_Process where Name like "java%"')
        print('{} {}'.format(time.time(), query_results))
        for process in wmi.WMI().Win32_Process():
            # print('name {} pid {} caption {} commandline {}'.format(process.Name, process.ProcessId, process.Caption, process.Commandline))
            if 'java' in process.Name.lower():
                print('{} {}'.format(process.ProcessId,process.Commandline))
                if process.Commandline is None:
                    continue
                if 'jdk' in process.Commandline and 'Mojang' in process.Commandline:
                    all_pids.append(process.ProcessId)
        print('-------')
    return all_pids

def get_multimc_pid():
    if settings.is_test_mode():
        return 0
    global multimcpid
    if 'multimcpid' not in globals():
        multimcpid = -1
        print('get multimc pid')
        for process in wmi.WMI().Win32_Process():
            if 'multimc' in process.Name.lower():
                print('{} {}'.format(process.ProcessId,process.Commandline))
                multimcpid = process.ProcessId
    return multimcpid

def identify_crashed_instances():
    all_pids = []
    for process in wmi.WMI().Win32_Process():
        all_pids.append(process.ProcessId)
    for inst in queues.get_all_instances():
        if inst.pid != -1 and inst.pid not in all_pids:
            print('instance {} pid {} has crashed'.format(inst.num, inst.pid))
            inst.mark_dead()

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
    if settings.is_local_test_mode() or not settings.is_ahk_enabled():
        print("Run AHK script {} {}".format(script_name, kwargs))
        return
    # return ahk.run_script(file_to_script(script_name, **kwargs), blocking=not settings.should_parallelize_ahk())
    ahk_path = _resolve_executable_path()
    script_path = Path.cwd() / "src" / "ahk" / "{}.ahk".format(script_name)
    if settings.show_debug():
        print('{} running {} args {}'.format(time.time(), script_name, kwargs))
    elif 'pid' in kwargs:
        print('{} running {} pid {} with ahk path {}'.format(time.time(), script_name, kwargs['pid'], ahk_path))
    else:
        print('{} running {} with ahk path {}'.format(time.time(), script_name, ahk_path))
    should_block = False
    if 'blocking' in kwargs:
        should_block = kwargs['blocking']
    args = [ahk_path, "/force", "/ErrorStdOut", script_path.resolve().as_posix()]
    for key in kwargs:
        if isinstance(kwargs[key], bool):
            args.append('{}'.format(kwargs[key]).lower())
        elif isinstance(kwargs[key], str):
            args.append('{}'.format(kwargs[key]))
        else:
            args.append(str(kwargs[key]))
    if settings.should_parallelize_ahk() and not should_block:
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

def get_switching_daemon_pipe():
    return IoLockablePipe('switching')

def get_pipe_file_location():
    return get_switching_daemon_pipe().outfile

def increment_reset_counter():

    if not settings.use_reset_counter():
        return
    if settings.is_test_mode():
        return

    attempts_fil = Path.cwd() / "attempts.txt"

    if not attempts_fil.exists():
        attempts_fil.touch()
        attempts_fil.write_text('0')

    num_attempts = -1
    
    with attempts_fil.open('r') as attempts_fil_opened:
        num_attempts = int(str(attempts_fil_opened.read()).rstrip())

    attempts_fil.unlink()
    attempts_fil.touch()

    with attempts_fil.open('w') as attempts_fil_opened:
        attempts_fil_opened.write(str(num_attempts+1))



def hide_mac_window(inst):
    process = NSRunningApplication.runningApplicationWithProcessIdentifier_(inst.pid)
    process.hide()

def show_mac_window(inst):
    process = NSRunningApplication.runningApplicationWithProcessIdentifier_(inst.pid)
    process.unhide()
