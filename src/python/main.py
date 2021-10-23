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

# Load settings
SCHEDULER = sched.scheduler(time.time, time.sleep)

# did_error = False

max_concurrent = settings.get_max_concurrent()
max_concurrent_boot = settings.get_max_concurrent_boot()

unfrozen_queue_size = settings.get_unfrozen_queue_size()

unfreeze_delay = settings.get_unfreeze_delay()

last_log_time = time.time()

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
        if not focused_instance.is_ready() and new_focused_instance.num != focused_instance.num and new_focused_instance.num != primary_instance.num:
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

def schedule_next(sc):
    if not did_error:
        SCHEDULER.enter(settings.get_loop_delay(), 1, main_loop_wrapper, (sc,))

def main_loop(sc):
    global need_to_reset_timer
    global last_log_time

    queues.update_all()

    num_working_instances = len(queues.get_gen_instances()) + len(queues.get_booting_instances()) + len(queues.get_pregen_instances()) + len(queues.get_paused_instances()) + len(queues.get_unpaused_instances()) + unfrozen_queue_size
    
    if obs.get_primary_instance() is not None and obs.get_primary_instance().is_active():
        num_working_instances += 1
    
    num_booting_instances = len(queues.get_booting_instances())

    num_to_boot = max_concurrent - num_working_instances
    if not settings.prioritize_booting_over_worldgen():
        num_to_boot -= len(queues.get_free_instances())
    num_to_boot = max(0,min(1, num_to_boot))

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
    for i in range(num_to_boot):
        inst = queues.get_dead_instances()[i]
        if settings.should_auto_launch():
            inst.mark_booting()
            inst.boot()
            num_booting_instances += 1
            num_working_instances += 1
        else:
            old_pid = inst.pid
            inst.assign_pid(queues.get_all_instances())
            if inst.pid != old_pid:
                inst.mark_booting()
            break
    
    # Handle booting instances
    for inst in queues.get_booting_instances():
        if settings.should_auto_launch():
            old_pid = inst.pid
            if old_pid == -1:
                inst.assign_pid(queues.get_all_instances())
            if inst.is_done_booting():
                inst.initialize_after_boot()

    if not settings.should_auto_launch():
        if len(queues.get_dead_instances()) > 0 and len(queues.get_booting_instances()) < settings.get_manual_launch_batch_size():
            schedule_next(sc)
            return
        global is_first_check_manual_launch
        global done_with_manual_launch_batch
        if is_first_check_manual_launch:
            done_with_manual_launch_batch = False
            is_first_check_manual_launch = False
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

    # Handle pregen instances (recently unfrozen worlds that need to be generated)
    for inst in queues.get_pregen_instances():
        if not inst.is_done_unfreezing():
            continue
        # state = FREE
        if num_working_instances > max_concurrent:
            inst.suspend()
            inst.release()
            continue
        # state = GENERATING
        inst.mark_generating()
        inst.reset()

    # Handle free instances (frozen instances that are on a world, and we've decided to reset this world)
    for inst in queues.get_free_instances():
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
        inst.suspend()

    # Handle ready instances (paused instances on a world we haven't evaluated yet. may or may not be frozen)
    index = 0
    # make sure we prioritize having approved worlds unfrozen since they will become active before us
    total_to_unfreeze = unfrozen_queue_size - len(queues.get_approved_instances())
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
    
    # Pick primary instance
    primary_instance = obs.get_primary_instance()
    focused_instance = obs.get_focused_instance()
    if primary_instance is None:
        # only needed for initialization, so let's just show nothing until a world is ready
        if len(queues.get_booting_instances()) > 0:
            obs.set_new_primary(queues.get_booting_instances()[0])
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
        # only needed for initialization, so let's just show nothing until a world is ready
        if len(queues.get_booting_instances()) > 0 and primary_instance is not None:
            # we don't want an instance to be both focused and primary
            focused_instance = queues.get_booting_instances()[0]
            if not focused_instance.is_primary():
                obs.set_new_focused(focused_instance)
    else:
        new_focused_instance = None
        if len(queues.get_ready_instances()) > 0:
            new_focused_instance = queues.get_ready_instances()[0]
        elif not settings.only_focus_ready():
            if len(queues.get_paused_instances()) > 0:
                new_focused_instance = queues.get_paused_instances()[0]
            elif len(queues.get_gen_instances()) > 0:
                new_focused_instance = queues.get_gen_instances()[0]
        try_set_focused(new_focused_instance)

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

def wrap(func):
    def inner(event):
        global listening
        if not listening:
            return
        func()
    return inner

assure_globals()

if __name__ == "__main__":
    # TODO @Sharpieman20 - add more good assertions
    # TODO @Sharpieman20 - add error messages explaining
    try:
        assert unfrozen_queue_size < max_concurrent
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
        kb.on_press_key(settings.get_hotkeys()['toggle-hotkeys'], wrap(toggle_hotkeys))
        kb.on_press_key(settings.get_hotkeys()['background-debug'], wrap(debug_background))
        kb.on_press_key(settings.get_hotkeys()['background-pause'], wrap(pause_background))
        kb.on_press_key(settings.get_hotkeys()['unfreeze-all'], wrap(unfreeze_all))
        if settings.should_use_tts():
            hlp.run_ahk("ttsInit")
        setup_file = Path.cwd() / 'setup.py'
        if setup_file.exists():
            setup_file.unlink()
        print("Starting launch procedure")
        SCHEDULER.enter(settings.get_loop_delay(), 1, main_loop_wrapper, (SCHEDULER,))
        SCHEDULER.run()
        if not settings.should_auto_launch():
            index = 0
            global done_with_all_manual_launch_batches
            while not done_with_all_manual_launch_batches:
                start_ind = index*settings.get_manual_launch_batch_size()+1
                end_ind = min(settings.get_num_instances(),(index+1)*settings.get_manual_launch_batch_size())
                input("Manually open instances {} through {}. Then press any key once they've finished launching.".format(start_ind, end_ind))
                mark_manual_launch_batch_done()
                time.sleep(1)
    except Exception:
        global did_error
        did_error = True
        traceback.print_exc(file=sys.stdout)
        time.sleep(5000)
