import settings
import queues
import helpers as hlp
from instance import Instance, State
import json
import sched
import time
import os
import keyboard as kb
from pathlib import Path
from datetime import datetime
import launch
import obs
import sys
import traceback
import requests
import subprocess as sp
import shlex

IS_BETA = True

# Load settings
SCHEDULER = sched.scheduler(time.time, time.sleep)

# did_error = False

max_concurrent = settings.get_max_concurrent()
max_concurrent_boot = settings.get_max_concurrent_boot()



unfreeze_delay = settings.get_unfreeze_delay()

last_log_time = time.time()


def try_launch_instance():
    # let's make sure to not try and set primary until after this is over
    # launch the instance that we have selected
    ahk.launchSelectedInstance(blocking=True)
    # select another instance for next time
    if not next_launch_instancae.exists():
        ahk.createInstanceFromTemplate(blocking=True)
    else:
        ahk.selectFirstMultiMCInstance(blocking=True)
        ahk.selectMultiMCInstance(instance, blocking=False)

# TODO @Sharpieman20 - fix this to be more like how queue states are handled
def try_set_primary(new_primary_instance):
    primary_instance = obs.get_primary_instance()
    if primary_instance is not None and new_primary_instance is not None:
        if new_primary_instance.num != primary_instance.num:
            obs.set_new_primary(new_primary_instance)

def try_set_focused(new_focused_instance):
    primary_instance = obs.get_primary_instance()
    focused_instance = obs.get_focused_instance()
    if primary_instance is not None and new_focused_instance is not None:
        if focused_instance is None or (not focused_instance.is_ready() and new_focused_instance.num != focused_instance.num and new_focused_instance.num != primary_instance.num):
            obs.set_new_focused(new_focused_instance)

def assure_globals():
    if 'did_init_globals' not in globals():
        global did_error
        did_error = False
        global listening
        listening = True
        global is_first_check_manual_launch
        is_first_check_manual_launch = True
        global first_check_after_all_processes_started
        first_check_after_all_processes_started = False
        global done_with_manual_launch_batch
        done_with_manual_launch_batch = False
        global done_with_all_manual_launch_batches
        done_with_all_manual_launch_batches = False
        global did_init_globals
        did_init_globals = True
        global manual_launch_index
        manual_launch_index = 0

def schedule_next(sc):
    if not did_error:
        SCHEDULER.enter(settings.get_loop_delay(), 1, main_loop_wrapper, (sc,))

def main_loop(sc):
    global need_to_reset_timer
    global last_log_time

    queues.update_all()

    # Pick primary instance
    primary_instance = obs.get_primary_instance()
    focused_instance = obs.get_focused_instance()
    if primary_instance is None:
        # only needed for initialization, so let's just show nothing until a world is ready
        if len(queues.get_gen_instances()) > 0:
            obs.set_new_primary(queues.get_gen_instances()[0])
            need_to_reset_timer = True
    elif not primary_instance.is_active():
        new_primary_instance = None
        if len(queues.get_approved_instances()) > 0:
            new_primary_instance = queues.get_approved_instances()[0]
        elif len(queues.get_ready_instances()) > 0:
            new_primary_instance = queues.get_ready_instances()[0]
        elif len(queues.get_paused_instances()) > 0:
            new_primary_instance = queues.get_paused_instances()[0]
        elif len(queues.get_gen_instances()) > 0:
            new_primary_instance = queues.get_gen_instances()[0]
        try_set_primary(new_primary_instance)
        need_to_reset_timer = True

    # Pick focused instance
    if focused_instance is None:
        new_focused_instance = None
        if len(queues.get_ready_instances()) > 0:
            new_focused_instance = queues.get_ready_instances()[0]
        elif not settings.only_focus_ready():
            if len(queues.get_paused_instances()) > 0:
                new_focused_instance = queues.get_paused_instances()[0]
            elif len(queues.get_gen_instances()) > 0:
                new_focused_instance = queues.get_gen_instances()[0]
        try_set_focused(new_focused_instance)

    unfrozen_queue_size = settings.get_unfrozen_queue_size()

    num_working_instances = len(queues.get_gen_instances()) + len(queues.get_launching_instances()) + len(queues.get_pregen_instances())
    num_working_instances += len(queues.get_paused_instances()) + len(queues.get_unpaused_instances()) + unfrozen_queue_size
    
    if obs.get_primary_instance() is not None and obs.get_primary_instance().is_active():
        num_working_instances += 1
    
    # instead of adding unfrozen queue size to num working, we should add min(unfrozen queue size, num_ready + num_approved)
    num_working_instances += min(unfrozen_queue_size, len(queues.get_ready_instances()) + len(queues.get_approved_instances()))
    
    num_booting_instances = len(queues.get_booting_instances())

    num_to_boot = max_concurrent - num_working_instances
    if not settings.prioritize_booting_over_worldgen():
        num_to_boot -= len(queues.get_free_instances())

    num_to_boot = min(num_to_boot, max_concurrent_boot-len(queues.get_booting_instances()))
    num_to_boot = min(num_to_boot, len(queues.get_dead_instances()))

    if not settings.should_auto_launch():
        num_to_boot = len(queues.get_dead_instances())

    if settings.is_test_mode() and time.time() - last_log_time > settings.get_debug_interval():
        last_log_time = time.time()
        tmp_all_queues = queues.get_all_queues()
        print('---------------')
        for key in tmp_all_queues.keys():
            print(key,end="|")
            for value in tmp_all_queues[key]:
                print(value,end=" ")
            print()
        print()
        print(f'DisplayState.FOCUSED {obs.get_focused_instance()}')
        print(f'DisplayState.PRIMARY {obs.get_primary_instance()}')
        print(num_to_boot)
        print('---------------')

    # Handle dead instances
    # num_to_launch should always be 0 if we're in a run
    # also we should never launch an instance when we already have one launching
    # TODO @Sharpieman20 - redo this code for auto launch
    for i in range(num_to_launch):
        inst = queues.get_dead_instances()[i]
        if settings.should_auto_launch():
            inst.mark_booting()
            inst.boot()
            num_booting_instances += 1
            num_working_instances += 1
            break
        else:
            old_pid = inst.pid
            inst.assign_pid(queues.get_all_instances())
            if inst.pid != old_pid:
                inst.mark_booting()
            break
    
    # Handle launching instances
    for inst in queues.get_launching_instances():
        if settings.should_auto_launch():
            old_pid = inst.pid
            if old_pid == -1:
                inst.assign_pid(queues.get_all_instances())
            if old_pid != inst.pid:
                inst.mark_preboot()
                inst.suspend()

    # Handle preboot instances (recently frozen instances that are candidates to be unfrozen and boot up)
    for inst in queues.get_preboot_instances():
        # check if it's not frozen
            # if so, throw error
        # check if it's been at least X time since it got frozen
            # if not, continue
        # check if less than num_to_boot
            # if so, unfreeze
            # set timestamp
            # mark booting

    # Handle booting instances
    for inst in queues.get_booting_instances():
        # check if it's been at least X time since its timestamp
            # if not, continue
        # check if latest.log file exists
            # if not, continue
        # check if latest.log mod time is > timestamp
            # if not, continue
        # check if latestl.log mod time is < cur_time - boot-delay
            # if not, continue
        # mark as main menu
        # don't update timestamp

    if not settings.should_auto_launch():
        if len(queues.get_dead_instances()) > 0 and len(queues.get_booting_instances()) < settings.get_manual_launch_batch_size():
            schedule_next(sc)
            return
        global done_with_manual_launch_batch
        if not done_with_manual_launch_batch:
            schedule_next(sc)
            return
        for inst in queues.get_booting_instances():
            inst.suspend()
            inst.free()
        if len(queues.get_dead_instances()) > 0:
            is_first_check_manual_launch = True
            schedule_next(sc)
            return

    # Handle main menu instances
    for inst in queues.get_mainmenu_instances():
        # exact same as pregen
        # except we call different reset function

    # Handle pregen instances (recently unfrozen worlds that need to be generated)
    for inst in queues.get_pregen_instances():
        if not inst.is_done_unfreezing():
            continue
        # state = FREE
        if num_working_instances > max_concurrent:
            # strictly greater than because it means we've surpassed the cap
            # ideally we shouldn't enter this if. this is a safeguard.
            inst.suspend()
            inst.release()
            continue
        # state = GENERATING
        inst.mark_generating()
        inst.reset()

    # Handle free instances (frozen instances that are on a world, and we've decided to reset this world)
    for inst in queues.get_free_instances():
        # >= because we don't want to unfreeze while at the cap
        if num_working_instances >= max_concurrent:
            continue
        if not inst.is_ready_for_unfreeze():
            inst.suspend()
            continue
        # state = PREGEN
        inst.mark_pregen()
        inst.resume()
        num_working_instances += 1

    # Handle world gen instances
    for inst in queues.get_gen_instances():
        if not inst.is_in_world():
            continue
        # state = PAUSED
        # TODO - why do we need to pause after creating a world? shouldnt it auto-pause?
        if not inst.is_primary():
            inst.mark_worldgen_finished()
            if settings.should_auto_pause():
                inst.pause()
        else:
            inst.mark_active()

    obs.set_scene_item_properties('indicator',len(queues.get_unpaused_instances()) > 0)

    for inst in queues.get_unpaused_instances():
        if inst.check_should_auto_reset():
            continue
    
    total_to_unfreeze = unfrozen_queue_size - len(queues.get_approved_instances())

    # Handle paused instances
    for inst in queues.get_paused_instances():
        # let chunks load some amount
        if inst.is_primary():
            inst.mark_active()
            continue
        if not inst.is_ready_for_freeze():
            continue
            # state = READY
        inst.mark_ready()

    # Handle ready instances (paused instances on a world we haven't evaluated yet. may or may not be frozen)
    index = 0
    # make sure we prioritize having approved worlds unfrozen since they will become active before us

    for inst in queues.get_ready_instances():
        index += 1
        if inst.check_should_auto_reset():
            continue
        if index <= total_to_unfreeze:
            inst.resume()
            continue
        # state = ?
        if inst.is_primary():
            inst.mark_active()
            continue
        inst.suspend()

    # Handle approved instances
    index = 0
    # this is fine because we will either loop up to this number, and all ready are frozen, or we will loop to less than this number anyways
    total_to_unfreeze = unfrozen_queue_size
    for inst in queues.get_approved_instances():
        index += 1
        if inst.check_should_auto_reset():
            continue
        if index <= total_to_unfreeze:
            inst.resume()
            continue
        if inst.is_primary():
            inst.mark_active()
            continue
        inst.suspend()


    schedule_next(sc)

def main_loop_wrapper(sc):
    try:
        main_loop(sc)
    except Exception:
        global did_error
        did_error = True
        traceback.print_exc(file=sys.stdout)
        time.sleep(5000)

# Callbacks
def reset_primary():
    # TODO - add safeguard after X time in run
    primary_instance = obs.get_primary_instance()
    if primary_instance is not None:
        primary_instance.reset_active()

def reset_focused():
    focused_instance = obs.get_focused_instance()
    if focused_instance is not None:
        if focused_instance.state == State.PAUSED or focused_instance.state == State.READY:
            focused_instance.release()

def approve_focused():
    focused_instance = obs.get_focused_instance()
    if focused_instance is not None:
        focused_instance.mark_approved()

def debug_background():
    if len(queues.get_unpaused_instances()) > 0:
        inst = queues.get_unpaused_instances()[0]
        hlp.run_ahk('debugGame',pid=inst.pid)

def pause_background():
    if len(queues.get_unpaused_instances()) > 0:
        inst = queues.get_unpaused_instances()[0]
        inst.mark_paused()
        inst.pause()

def mark_manual_launch_batch_done():
    global done_with_manual_launch_batch
    done_with_manual_launch_batch = True

def unfreeze_all():
    for inst in queues.get_all_instances():
        inst.resume(True)
        inst.mark_ready()

def toggle_hotkeys():
    global listening
    listening = not listening
    if listening:
        print('Hotkeys enabled')
    else:
        print('Hotkeys disabled')

def wrap(func, override=False):
    def inner(event):
        global listening
        if not override and not listening:
            return
        func()
    return inner

def handle_manual_launch_inner(sc):
    global done_with_manual_launch_batch
    if not done_with_manual_launch_batch:
        SCHEDULER.enter(settings.get_loop_delay(), 1, handle_manual_launch_inner, (sc,))
        return
    global done_with_all_manual_launch_batches
    global manual_launch_index
    start_ind = manual_launch_index*settings.get_manual_launch_batch_size()+1
    end_ind = min(settings.get_num_instances(),(manual_launch_index+1)*settings.get_manual_launch_batch_size())
    if start_ind >= end_ind:
        done_with_all_manual_launch_batches = True
        return
    done_with_manual_launch_batch = False
    print("Manually open instances {} through {}. Then press '{}' once they've finished launching.".format(start_ind, end_ind, settings.get_hotkeys()['manual-launch-completed']))
    SCHEDULER.enter(settings.get_loop_delay(), 1, handle_manual_launch_inner, (sc,))

def handle_manual_launch(sc):
    global done_with_manual_launch_batch
    done_with_manual_launch_batch = True
    handle_manual_launch_inner(sc)

def download_branch(branch):
    installer_file = Path.cwd() / "run_aim.py"
    if installer_file.exists():
        installer_file.unlink()
    installer_file_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/{}/run_aim.py'.format(branch)
    r = requests.get(installer_file_url, allow_redirects=True)
    installer_file.touch()
    open(installer_file.name, 'w').write(r.text)
    sp.call(shlex.split('py run_aim.py'))

def try_download_regular():
    global IS_BETA
    if not IS_BETA:
        return
    download_branch('main')

def try_download_beta():
    global IS_BETA
    if IS_BETA:
        return
    download_branch('beta')

assure_globals()

if __name__ == "__main__":
    # TODO @Sharpieman20 - add more good assertions
    # TODO @Sharpieman20 - add error messages explaining
    try:
        if settings.should_use_beta():
            try_download_beta()
        else:
            try_download_regular()
        assert settings.get_unfrozen_queue_size() < max_concurrent
        launch.launch_all_programs()
        input("Press any key to continue...")
        print("Macro started")
        print("Connecting to OBS")
        obs.connect_to_stream_obs()
        obs.hide_all()
        print(settings.get_hotkeys())
        kb.on_press_key(settings.get_hotkeys()['reset-active'], wrap(reset_primary))
        kb.on_press_key(settings.get_hotkeys()['reset-focused'], wrap(reset_focused))
        kb.on_press_key(settings.get_hotkeys()['approve-focused'], wrap(approve_focused))
        kb.on_press_key(settings.get_hotkeys()['toggle-hotkeys'], wrap(toggle_hotkeys, override=True))
        kb.on_press_key(settings.get_hotkeys()['background-debug'], wrap(debug_background))
        kb.on_press_key(settings.get_hotkeys()['background-pause'], wrap(pause_background))
        kb.on_press_key(settings.get_hotkeys()['unfreeze-all'], wrap(unfreeze_all))
        if not settings.should_auto_launch():
            kb.on_press_key(settings.get_hotkeys()['unfreeze-all'], wrap(mark_manual_launch_batch_done))
            
        if settings.should_use_tts():
            hlp.run_ahk("ttsInit")
        setup_file = Path.cwd() / 'setup.py'
        if setup_file.exists():
            setup_file.unlink()
        print("Starting launch procedure")
        SCHEDULER.enter(settings.get_loop_delay(), 1, main_loop_wrapper, (SCHEDULER,))
        if not settings.should_auto_launch():
            SCHEDULER.enter(0.01, 1, handle_manual_launch, (SCHEDULER,))
        # while 
        SCHEDULER.run()
    except Exception:
        global did_error
        did_error = True
        traceback.print_exc(file=sys.stdout)
        time.sleep(5000)
