import settings
from copy import copy
import subprocess as sp
import shlex
import os
import helpers as hlp
import queues
if not settings.is_test_mode():
    import wmi

def try_launch_instance(inst):
    # let's make sure to not try and set primary until after this is over
    # launch the instance that we have selected
    if len(queues.get_dead_instances()) == len(queues.get_all_instances()):
        hlp.run_ahk('selectFirstMultiMCInstance', blocking=True)
    hlp.run_ahk('launchSelectedInstance', keydelay=settings.get_key_delay(),blocking=True)
    # select another instance for next time
    if not inst.has_directory():
        # ahk.createInstanceFromTemplate(blocking=True)
        run_ahk('createInstanceFromTemplate', keydelay=settings.get_key_delay(), instname=inst.name, blocking=True,)
    else:
        run_ahk('selectFirstMultiMCInstance',keydelay=settings.get_key_delay(), blocking=True)
        run_ahk('selectMultiMCInstance',rightarrows=(inst.num%4),downarrows=int(inst.num/4),blocking=False)

def launch_instance(inst):
    if settings.is_test_mode() or not settings.is_ahk_enabled():
        return
    if settings.get_num_instances() > 5:
        try_launch_instance(inst)
        return
    # os.popen(f'{settings.get_multimc_path()} -l "{inst.name}"')
    instance_process = sp.Popen(f'{settings.get_multimc_path()} -l "{inst.name}"')

    # NOTE - for multimc this is the multimc process, NOT the underlying java process. we need to freeze underlying java process.
    return instance_process.pid

def launch_obs():
    # TODO @Sharpieman20 - replace with something better
    os.system(f'start /d "{settings.get_obs_path()}" "" obs64.exe')

def launch_livesplit():
    if not settings.get_livesplit_path().exists():
        return
    os.startfile(settings.get_livesplit_path())

def launch_multimc():
    os.startfile(settings.get_multimc_path())

def launch_all_programs():
    if settings.use_custom_background_ahk_process():
        hlp.run_ahk('customBackground')
    if settings.is_test_mode() or not settings.should_auto_launch():
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

