import settings
from copy import copy
import subprocess as sp
import shlex
import os
import helpers as hlp
import queues
import time
if not settings.is_local_test_mode():
    import wmi

def get_index_of_inst(inst):
    all_inst_nums = []

    for i in range(inst.num+1):
        if i > 0:
            all_inst_nums.append(str(i))
    
    all_inst_nums.sort()

    for i in range(len(all_inst_nums)):
        if str(inst.num) == all_inst_nums[i]:
            return i+1
    return -1

def try_launch_instance(inst):
    # let's make sure to not try and set primary until after this is over
    # launch the instance that we have selected
    inst_index = get_index_of_inst(inst)
    instance_columns = 6
    print('try launching instance {} {}'.format(inst.num, inst_index))
    if not settings.try_fast_launch() or len(queues.get_dead_instances()) == len(queues.get_all_instances()):
        hlp.run_ahk('selectFirstMultiMCInstance', multimcpid=hlp.get_multimc_pid(), multimcdelay=settings.get_multimc_delay(), blocking=True)
        if not inst.has_directory():
            hlp.run_ahk('createInstanceFromTemplate', multimcpid=hlp.get_multimc_pid(), multimcdelay=settings.get_multimc_delay(), instname=inst.name, blocking=True)
        else:
            hlp.run_ahk('selectMultiMCInstance',multimcpid=hlp.get_multimc_pid(),multimcdelay=settings.get_multimc_delay(), downarrows=int(inst_index/instance_columns),rightarrows=(inst_index%instance_columns),blocking=True)
    hlp.run_ahk('launchSelectedInstance',multimcpid=hlp.get_multimc_pid(),multimcdelay=settings.get_multimc_delay(),blocking=True)
    # select another instance for next time

    if settings.try_fast_launch():
        if not inst.has_directory():
            hlp.run_ahk('createInstanceFromTemplate', multimcpid=hlp.get_multimc_pid(), multimcdelay=settings.get_multimc_delay(), instname=inst.name, blocking=True)
        else:
            hlp.run_ahk('selectFirstMultiMCInstance',multimcpid=hlp.get_multimc_pid(), multimcdelay=settings.get_multimc_delay(), blocking=True)
            hlp.run_ahk('selectMultiMCInstance',multimcpid=hlp.get_multimc_pid(),multimcdelay=settings.get_multimc_delay(),downarrows=int(inst_index/instance_columns),rightarrows=(inst_index%instance_columns),blocking=True)
def run_cmd(cmd):
    sp.Popen(shlex.split(cmd))

def launch_test_instance(inst):
    run_cmd('java -Xdock:name=java -Xms64m -Xmx64m test/LaunchMockMC.java {}'.format(inst.num))

def launch_instance(inst):
    if settings.is_test_mode():
        launch_test_instance(inst)
        return
    if settings.get_num_instances() > 5 and settings.use_click_macro():
        try_launch_instance(inst)
        return

    instance_process = hlp.run_cmd(f'{settings.get_multimc_path()} -l "{inst.name}"', split=False)

def launch_obs():
    if not settings.is_obs_enabled():
        return
    hlp.run_cmd('start /d "{}" "" obs64.exe'.format(settings.get_obs_path()))
    time.sleep(3)

def launch_livesplit():
    if not settings.get_livesplit_path().exists():
        return
    hlp.run_cmd('start "{}"'.format(settings.get_livesplit_path()))
    time.sleep(3)

def launch_multimc():
    hlp.run_cmd('{}'.format(settings.get_multimc_path()))
    time.sleep(3)

def launch_all_programs():
    if settings.use_custom_background_ahk_process():
        hlp.run_ahk('customBackground')
    if settings.is_test_mode() or not settings.should_auto_launch_apps():
        return
    # TODO: add stat tracker?
    all_programs = ["OBS", "LiveSplit", "MultiMC"]
    are_launched = {program: False for program in all_programs}
    launch_funcs = {all_programs[0]: launch_obs, all_programs[1]: launch_livesplit, all_programs[2]: launch_multimc}
    for process in wmi.WMI().Win32_Process():
        for program in all_programs:
            if program.lower() in process.Name.lower():
                are_launched[program] = True
    for program in all_programs:
        if not are_launched[program]:
            launch_funcs[program]()
    if settings.use_switching_daemon():
        hlp.run_ahk('windowSwitchingDaemon', switchDelay=settings.get_switch_delay(), borderless=settings.get_is_borderless(), maximize=settings.should_maximize(), autoUnpause=settings.should_auto_unpause(), playDelay=settings.get_unpause_delay(), pipeFileLocation=hlp.get_pipe_file_location(), loopDelay=settings.get_daemon_loop_delay(), blocking=False)

