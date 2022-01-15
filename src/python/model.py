import time
import settings
import queues
import helpers as hlp
from instance import Instance, State
import pipe
import json
import sched
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
import hotkeys
import shutil
import atexit
import validate

def main_loop(sc):
    global need_to_reset_timer
    global last_log_time
    global last_crash_check_time
    global last_launch_time

    if settings.attempt_to_relaunch_crashed_instances() and time.time() - last_crash_check_time > settings.check_for_crashes_delay():
        last_crash_check_time = time.time()
        hlp.identify_crashed_instances()

    hotkeys.process_hotkey_events()

    queues.update_all()

    max_concurrent = settings.get_max_concurrent()
    unfrozen_queue_size = settings.get_unfrozen_queue_size()

    if settings.is_wall_enabled():
        if obs.get_stream_wall().is_active():
            unfrozen_queue_size = max(unfrozen_queue_size, settings.get_wall_unfrozen_queue_size())
            max_concurrent = max(max_concurrent, settings.get_max_concurrent_on_wall())

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
        if settings.is_wall_enabled():
            if False:
                if len(queues.get_approved_instances()) > 0:
                    new_primary_instance = queues.get_approved_instances()[0]
                try_set_primary(new_primary_instance)
                need_to_reset_timer = True
        else:
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

    if settings.is_wall_enabled():
        obs.get_stream_wall().update_shown()
        obs.get_screen_wall().update_shown()

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

    num_to_launch = min(1, max(0,1-len(queues.get_launching_instances())))

    num_working_instances = len(queues.get_launching_instances()) + len(queues.get_mainmenu_instances())
    num_working_instances += len(queues.get_pregen_instances()) + len(queues.get_gen_instances())
    num_working_instances += len(queues.get_paused_instances()) + len(queues.get_unpaused_instances())
    
    if obs.get_primary_instance() is not None:
        if obs.get_primary_instance().is_ready() or obs.get_primary_instance().is_approved():
            # if our primary instance is ready/approved, it is not counted towards num_working currently
            # but it will be marked active later in this loop, so we need to count it towards active
            # this is only true if it's not already being counted from unfrozen queue size though
            if unfrozen_queue_size == 0:
                num_working_instances += 1
        elif obs.get_primary_instance().is_active():
            # we don't want to launch with an active primary instance
            num_working_instances += 1
            num_to_launch = 0
    
    # instead of adding unfrozen queue size to num working, we should add min(unfrozen queue size, num_ready + num_approved)
    num_working_instances += min(unfrozen_queue_size, len(queues.get_ready_instances()) + len(queues.get_approved_instances()))
    
    num_booting_instances = len(queues.get_booting_instances())
    num_to_boot = min(1,max_concurrent - num_working_instances)

    num_working_instances += num_booting_instances
    
    if not settings.prioritize_booting_over_worldgen():
        num_to_boot -= len(queues.get_free_instances())

    num_to_boot = min(num_to_boot, len(queues.get_preboot_instances()))

    if not settings.should_auto_launch():
        num_to_boot = len(queues.get_dead_instances())
    
    if len(queues.get_booting_instances()) > 0:
        if not hlp.has_passed(queues.get_booting_instances()[-1].timestamp, settings.get_unfreeze_delay()):
            num_to_boot = 0
    
    num_to_launch = min(num_to_launch, len(queues.get_dead_instances()))

    if (settings.show_debug() or settings.is_test_mode()) and time.time() - last_log_time > settings.get_debug_interval():
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
    for i in range(num_to_launch):
        inst = queues.get_dead_instances()[i]
        if settings.should_auto_launch():
            if not hlp.has_passed(last_launch_time, settings.get_multimc_launch_delay()):
                continue
            inst.mark_launching()
            inst.launch()
            num_working_instances += 1
            break
        else:
            old_pid = inst.pid
            inst.assign_pid(queues.get_all_instances())
            if inst.pid != old_pid:
                inst.mark_launching()
            break
    
    # Handle launching instances
    for inst in queues.get_launching_instances():
        if settings.should_auto_launch():
            old_pid = inst.pid
            if old_pid == -1:
                inst.assign_pid(queues.get_all_instances())
            if old_pid != inst.pid:
                last_launch_time = time.time()
                inst.mark_preboot()
                inst.suspend()

    # Handle preboot instances (recently frozen instances that are candidates to be unfrozen and boot up)
    for inst in queues.get_preboot_instances():
        # check if it's not frozen
            # if so, throw error
        if not inst.is_ready_for_unfreeze():
            continue
        if settings.wait_for_all_to_launch_before_booting() and (len(queues.get_dead_instances()) > 0 or len(queues.get_launching_instances()) > 0):
            continue
        if num_booting_instances < num_to_boot:
            inst.mark_booting()
            inst.resume()
            num_booting_instances += 1
            num_working_instances += 1

    # Handle booting instances
    for inst in queues.get_booting_instances():
        # check if it's been at least X time since its timestamp
            # why do we need this again
            # if not, continue
        if not inst.is_done_booting():
            continue
        inst.mark_mainmenu()
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
        inst.reset_from_title()
        inst.mark_generating()

    # Handle pregen instances (recently unfrozen worlds that need to be generated)
    for inst in queues.get_pregen_instances():
        if not inst.is_done_unfreezing():
            continue
        # state = FREE
        if num_working_instances > max_concurrent:
            # strictly greater than because it means we've surpassed the cap
            # ideally we shouldn't enter this if. this is a safeguard.
            # it can maybe happen due to us using this fact about pregen being optimistic
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
        if len(queues.get_pregen_instances()) > 0:
            continue
        # state = PREGEN
        inst.mark_pregen()
        inst.resume()
        num_working_instances += 1
        break

    # Handle world gen instances
    for inst in queues.get_gen_instances():
        if not inst.is_in_world():
            continue
        inst.mark_worldgen_finished()

    obs.set_scene_item_visible('indicator',len(queues.get_unpaused_instances()) > 0)

    for inst in queues.get_unpaused_instances():
        if inst.check_should_auto_reset():
            continue
        if inst.is_primary() and not inst.is_active():
            inst.mark_active()
            continue
    
    total_to_unfreeze = unfrozen_queue_size - len(queues.get_approved_instances())

    # Handle paused instances
    # TODO - when resetting a paused instance, we should prioritize it since we can reduce suspend/unsuspends
    for inst in queues.get_paused_instances():
        # let chunks load some amount
        if inst.is_primary() and not inst.is_active():
            inst.mark_active()
            continue
        if not inst.is_ready_for_freeze():
            continue
            # state = READY
        print('inst {} ready now'.format(inst.num))
        inst.mark_ready()

    # Handle ready instances (paused instances on a world we haven't evaluated yet. may or may not be frozen)
    index = 0
    # make sure we prioritize having approved worlds unfrozen since they will become active before us

    for inst in queues.get_ready_instances():
        if inst.is_primary() and not inst.is_active():
            inst.mark_active()
            continue
        index += 1
        if inst.is_primary():
            inst.mark_active()
            continue
        if inst.check_should_auto_reset():
            continue
        if index <= total_to_unfreeze:
            inst.resume()
            continue
        # state = ?
        # print('inst {} is ready'.format(inst.num))
        inst.suspend()

    # Handle approved instances
    index = 0
    # this is fine because we will either loop up to this number, and all ready are frozen, or we will loop to less than this number anyways
    total_to_unfreeze = unfrozen_queue_size
    for inst in queues.get_approved_instances():
        if inst.is_primary() and not inst.is_active():
            inst.mark_active()
            continue
        index += 1
        if inst.check_should_auto_reset():
            continue
        if index <= total_to_unfreeze:
            inst.resume()
            continue
        inst.suspend()

    schedule_next(sc)