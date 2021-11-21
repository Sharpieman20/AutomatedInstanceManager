import obs
import settings
import helpers as hlp
from helpers import get_time
import os
import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path
from launch import launch_instance
import random

num_per_state = {}

def assign_to_state(instance, state):
    print('assign instance {} to state {}'.format(instance.num, state))
    global num_per_state
    if state not in num_per_state:
        num_per_state[state] = 0
    num_per_state[state] = num_per_state[state] + 1
    instance.state = state
    instance.priority = num_per_state[state]



global_pid = 81461

def get_global_test_pid():
    global global_pid
    global_pid += 1
    return global_pid

class State(Enum):
    DEAD = 0
    LAUNCHING = 1
    PREBOOT = 2
    BOOTING = 3
    MAINMENU = 4
    FREE = 5
    PREGEN = 6
    GEN = 7
    UNPAUSED = 8
    PAUSED = 9
    READY = 10
    APPROVED = 11
    ACTIVE = 12

class DisplayState(Enum):
    HIDDEN = 0
    FOCUSED = 1
    PRIMARY = 2

class Process:
    def assign_pid(self, all_processes):
        # for now, require auto-launch mode enabled
        if settings.is_test_mode():
            self.pid = get_global_test_pid()
            return
        all_pids = hlp.get_pids()
        for pid in all_pids:
            pid_maps_to_instance = False
            for instance in all_processes:
                if instance.pid == pid:
                    pid_maps_to_instance = True
            if not pid_maps_to_instance:
                if pid > self.pid:
                    self.pid = pid

class Suspendable(Process):
    def suspend(self):
        if self.is_suspended() or self.forceResumed:
            if not settings.retry_freezes() or random.randint(0, 50) != 0:
                return
        self.suspended = True
        hlp.run_ahk("suspendInstance", pid=self.pid)

    def resume(self, force=False):
        if not force and not self.is_suspended():
            return
        self.suspended = False
        if not self.forceResumed:
            self.forceResumed = True
        
        hlp.run_ahk("resumeInstance", pid=self.pid)

    def is_suspended(self):
        return self.suspended



class Stateful(Suspendable):

    def mark_dead(self):
        assign_to_state(self, State.DEAD)
        self.pid = -1
        self.first_reset = True
        self.current_world = None

    def mark_launching(self):
        assign_to_state(self, State.LAUNCHING)

    def mark_preboot(self):
        assign_to_state(self, State.PREBOOT)
        self.timestamp = get_time()

    def mark_mainmenu(self):
        assign_to_state(self, State.MAINMENU)

    def mark_booting(self):
        assign_to_state(self, State.BOOTING)
        self.timestamp = get_time()

    def mark_pregen(self):
        assign_to_state(self, State.PREGEN)
        self.timestamp = get_time()
    
    def mark_generating(self):
        assign_to_state(self, State.GEN)
        self.timestamp = get_time()
    
    def mark_worldgen_finished(self):
        if self.first_reset and settings.should_settings_reset_first_world():
            self.first_reset = False
            self.settings_reset()
            self.mark_generating()
            self.timestamp += settings.get_settings_reset_delay()
        elif settings.should_auto_pause():
            assign_to_state(self, State.PAUSED)
            self.pause()
        else:
            assign_to_state(self, State.UNPAUSED)
        self.timestamp = get_time()
    
    def mark_paused(self):
        assign_to_state(self, State.PAUSED)
        self.timestamp = get_time()
    
    def mark_free(self):
        assign_to_state(self, State.FREE)
    
    def release(self):
        if self.is_suspended():
            self.mark_free()
        else:
            self.mark_pregen()
        self.timestamp = get_time()

    def mark_ready(self):
        assign_to_state(self, State.READY)
        self.timestamp = get_time()

    def mark_approved(self):
        assign_to_state(self, State.APPROVED)

    def is_ready(self):
        return self.state == State.READY

    def mark_active(self):
        assign_to_state(self, State.ACTIVE)
        self.was_active = True
        self.timestamp = get_time()

    def mark_inactive(self):
        # add to pregen w/o setting timestamp
        assign_to_state(self, State.PREGEN)

class InstanceStateful(Stateful):

    def mark_front(self, stayOnTop=False):
        shouldAutoUnpause = settings.should_auto_unpause() and self.is_active()
        if stayOnTop and not settings.stay_always_on_top_when_still_launching():
            stayOnTop = False
        if not settings.use_switching_daemon():
            hlp.run_ahk("activateWindow", pid=self.pid, switchdelay=settings.get_switch_delay(), borderless=settings.get_is_borderless(), maximize=settings.should_maximize(), stayOnTop=stayOnTop, shouldAutoUnpause=shouldAutoUnpause, fullscreen=settings.is_fullscreen_enabled())
        self.is_always_on_top = stayOnTop
    
    def mark_back(self):
        if not settings.use_switching_daemon():
            hlp.run_ahk("deactivateWindow", pid=self.pid, isMaximized=settings.should_maximize(), fullscreen=settings.is_fullscreen_enabled())


class DisplayStateful(InstanceStateful):

    def mark_hidden(self):
        if self.displayState == DisplayState.FOCUSED:
            obs.hide_focused(self)
        elif self.displayState == DisplayState.PRIMARY:
            obs.hide_primary(self)
            self.is_always_on_top = False
        self.displayState = DisplayState.HIDDEN
    
    def mark_focused(self):
        obs.show_focused(self)
        self.displayState = DisplayState.FOCUSED

    def mark_primary(self):
        obs.show_primary(self)
        self.displayState = DisplayState.PRIMARY

    def is_primary(self):
        return self.displayState == DisplayState.PRIMARY

    def is_focused(self):
        return self.displayState == DisplayState.FOCUSED

# TODO @Sharpieman20 - get these durations from settings
class ConditionalTransitionable(DisplayStateful):

    def is_done_unfreezing(self):
        duration = settings.get_freeze_delay()
        return hlp.has_passed(self.timestamp, duration)

    def is_done_freezing(self):
        duration = settings.get_freeze_delay()
        return hlp.has_passed(self.timestamp, duration)

    def is_ready_for_unfreeze(self):
        return self.is_done_freezing()
    
    def is_ready_for_freeze(self):
        if self.state == State.PAUSED:
            duration = settings.get_load_chunk_time()
            return hlp.has_passed(self.timestamp, duration)
        return self.is_done_unfreezing()
    
    def is_done_booting(self):
        if hlp.has_passed(self.timestamp, 15.0):
            return True
        log_file = self.mcdir / 'logs' / 'latest.log'
        if not log_file.exists():
            return False
        mod_time = log_file.stat().st_mtime
        if mod_time < self.timestamp:
            return False
        if not hlp.has_passed(mod_time, settings.get_boot_delay()):
            return False
        return True

    def check_should_auto_reset(self):
        if self.state == State.UNPAUSED:
            duration = settings.get_max_unpaused_time()
        else:
            duration = settings.get_max_time_before_auto_reset()
        if hlp.has_passed(self.timestamp, duration):
            self.suspend()
            self.release()
            return True
    
    def should_auto_pause(self):
        if settings.should_auto_pause():
            return True
        if hlp.has_passed(self.timestamp, duration):
            return True
        return False

    def is_active(self):
        return self.state == State.ACTIVE

class Instance(ConditionalTransitionable):

    def __init__(self, num):
        self.num = num
        self.pid = -1
        self.window_pid = -1
        self.first_reset = True
        self.suspended = False
        self.state = State.DEAD
        self.displayState = DisplayState.HIDDEN
        assign_to_state(self, self.state)
        self.timestamp = 0
        self.was_active = False
        self.name = '{}{}'.format(settings.get_base_instance_name(), self.num)
        self.mcdir = settings.get_multimc_path().parent / "instances" / self.name / ".minecraft"
        self.current_world = None
        self.is_always_on_top = False
        self.forceResumed = False
    
    def launch(self):
        # TODO @Sharpieman20 - fix this to give pid from launch
        launch_instance(self)
        
    # not yet implemented (not needed in v1)
    def create_multimc_instance(self):
        # import from zip in launch command or something
        pass

    # not yet implemented (not needed in v1)
    def create_obs_instance(self):
        obs.create_scene_item_for_instance(self)

    def reset_from_title(self):
        # assign our pid somehow
        # start generating world w/ duncan mod
        if settings.should_set_window_titles():
            title_str = settings.get_window_title_template()
            title_str = title_str.replace('#',str(self.num))
            hlp.run_ahk("setInstanceTitle", pid=self.pid, title=title_str)
        hlp.run_ahk("resetFromTitle", pid=self.pid, keydelay=settings.get_key_delay())
        # set state to generating
        self.mark_generating()
        self.first_reset = True

    def reset_active(self):
        if self.is_active():
            self.pause()
            self.mark_inactive()
    
    def settings_reset(self):
        hlp.run_ahk("resetSettings", pid=self.pid, keydelay=settings.get_key_delay())
        self.first_reset = False

    def reset(self):
        if False and settings.should_set_window_titles():
            title_str = settings.get_window_title_template()
            title_str = title_str.replace('#',str(self.num))
            hlp.run_ahk("setInstanceTitle", pid=self.pid, title=title_str)
        if self.was_active and hlp.has_passed(self.timestamp, settings.minimum_time_for_settings_reset()):
            self.settings_reset()
        elif self.first_reset and not settings.should_auto_launch():
            self.reset_from_title()
            self.first_reset = False
        elif self.first_reset and settings.should_settings_reset_first_world():
            self.settings_reset()
        else:
            hlp.run_ahk("reset", pid=self.pid, keydelay=settings.get_key_delay())
        hlp.increment_reset_counter()
        self.was_active = False
        self.current_world = None

    def pause(self):
        hlp.run_ahk("pauseGame", pid=self.pid, keydelay=settings.get_key_delay())

    # TODO - call this method somewhere
    def move_worlds(self):
        if settings.is_test_mode():
            print("Moving worlds for instance {}".format(self.name))
            return
        if not settings.should_move_old_worlds():
            return
        old_worlds = settings.get_old_worlds_directory()
        for world_dir in (self.mcdir / "saves").iterdir():
            # TODO - i think this should be like "Attempt #X" or something cuz of duncan mod
            if world_dir.name.startswith("Attempt"):
                if world_dir.name == self.current_world.name:
                    continue
                global worldid
                if 'worldid' not in globals():
                    worldid = 1
                while (old_worlds / "Attempt {}".format(worldid)).exists():
                    worldid += 1
                try:
                    shutil.move(world_dir, (old_worlds / "Attempt {}".format(worldid)))
                except:
                    continue

    # TODO - call this method somewhere
    def copy_logs(self):
        # we should copy all relevant logs out of the instance probably since we want to dynamically create instances
        pass
    
    def has_directory(self):
        return self.mcdir.exists()

    def get_current_world(self):
        if self.current_world is not None:
            return self.current_world
        max_time = 0.0
        for world in (self.mcdir / "saves").iterdir():
            world_time = world.stat().st_mtime
            if world_time > max_time:
                if settings.get_version() == '1.8':
                    if world.is_dir() and not (world / 'stats').exists():
                        max_time = world_time
                        self.current_world = world
                else:
                    if world.is_dir() and not (world / 'advancements').exists():
                        max_time = world_time
                        self.current_world = world
        return self.current_world

    def is_in_world(self):
        if settings.is_test_mode():
            if hlp.has_passed(self.timestamp, settings.get_test_worldgen_time()):
                return True
            return False
        
        if not hlp.has_passed(self.timestamp, settings.get_start_create_world_delay()):
            return False

        cur_world = self.get_current_world()

        if cur_world is None:
            return False
        
        self.move_worlds()

        return (cur_world / "advancements").exists()

    def __str__(self):
        return "({},{})".format(self.name, self.pid)
