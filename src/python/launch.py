import settings
import psutil
from copy import copy
import subprocess as sp
import shlex
import os

def launch_instance(inst):
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        return
    # os.popen(f'{settings.get_multimc_path()} -l "{inst.name}"')
    instance_process = sp.Popen(f'{settings.get_multimc_path()} -l "{inst.name}"')

    # NOTE - for multimc this is the multimc process, NOT the underlying java process. we need to freeze underlying java process.
    return instance_process.pid
    # return None

def launch_obs():
    # TODO @Sharpieman20 - replace with something better
    os.system(f'start /d "{settings.get_obs_path()}" "" obs64.exe')

def launch_livesplit():
    os.startfile(settings.get_livesplit_path())

def launch_multimc():
    pass

def launch_all_programs():
    if settings.is_test_mode() or not settings.should_auto_launch():
        return
    # TODO: add stat tracker?
    all_programs = ["OBS", "LiveSplit", "MultiMC"]
    are_launched = {program: False for program in all_programs}
    launch_funcs = {all_programs[0]: launch_obs, all_programs[1]: launch_livesplit, all_programs[2]: launch_multimc}
    # TODO @Sharpieman20 - change from psutil to ctypes 
    # https://stackoverflow.com/questions/12554176/how-to-get-all-running-python-processes-under-windows-in-an-acceptable-time
    for process in psutil.process_iter():
        for program in all_programs:
            if program.lower() in process.name().lower():
                are_launched[program] = True
    for program in all_programs:
        if not are_launched[program]:
            launch_funcs[program]()
