import obs
import settings
import helpers as hlp
from helpers import get_time
import os
import shutil
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from launch import launch_instance

num_per_state = {}

def assign_to_state(instance, state):
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
    BOOTING = 1
    FREE = 2
    PREGEN = 3
    GEN = 4
    UNPAUSED = 5
    PAUSED = 6
    READY = 7
    APPROVED = 8
    ACTIVE = 9

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
                self.pid = pid

class Suspendable(Process):
    def suspend(self):
        if self.is_suspended():
            return
        self.suspended = True
        hlp.run_ahk("suspendInstance", pid=self.pid)

    def resume(self):
        if not self.is_suspended():
            return
        self.suspended = False
        hlp.run_ahk("resumeInstance", pid=self.pid)

    def is_suspended(self):
        return self.suspended



class Stateful(Suspendable):

    def mark_booting(self):
        assign_to_state(self, State.BOOTING)
        self.timestamp = get_time()
    
    def mark_pregen(self):
        assign_to_state(self, State.PREGEN)
    
    def mark_generating(self):
        assign_to_state(self, State.GEN)
        self.timestamp = get_time()
    
    def mark_worldgen_finished(self):
        if settings.should_auto_pause():
            assign_to_state(self, State.PAUSED)
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

    def mark_approved(self):
        assign_to_state(self, State.APPROVED)

    def is_ready(self):
        return self.state == State.READY

    def mark_active(self):
        assign_to_state(self, State.ACTIVE)
        self.was_active = True
        self.timestamp = get_time()

    def mark_inactive(self):
        # add to free
        self.mark_free()
        self.timestamp = get_time()

class DisplayStateful(Stateful):

    def mark_hidden(self):
        if self.displayState == DisplayState.FOCUSED:
            obs.hide_focused(self)
        elif self.displayState == DisplayState.PRIMARY:
            obs.hide_primary(self)
        self.displayState = DisplayState.HIDDEN
    
    def mark_focused(self):
        obs.show_focused(self)
        self.displayState = DisplayState.FOCUSED

    def mark_primary(self):
        obs.show_primary(self)
        hlp.run_ahk("activateWindow", pid=self.pid)
        self.displayState = DisplayState.PRIMARY

    def is_primary(self):
        return self.displayState == DisplayState.PRIMARY

# TODO @Sharpieman20 - get these durations from settings
class ConditionalTransitionable(DisplayStateful):

    def is_ready_for_freeze(self):
        duration = settings.get_load_chunk_time()
        return hlp.has_passed(self.timestamp, duration)

    def is_done_unfreezing(self):
        duration = settings.get_freeze_delay()
        return hlp.has_passed(self.timestamp, duration)

    def is_ready_for_unfreeze(self):
        duration = settings.get_unfreeze_delay()
        return hlp.has_passed(self.timestamp, duration)
    
    def is_done_booting(self):
        # TODO @Sharpieman20 - dynamically check if booted
        duration = settings.get_boot_delay()
        return hlp.has_passed(self.timestamp, duration)

    def check_should_auto_reset(self):
        if self.state == State.UNPAUSED:
            duration = settings.get_max_unpaused_time()
        else:
            duration = 300.0
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
    
    def boot(self):
        self.pid = launch_instance(self)
        
    # not yet implemented (not needed in v1)
    def create_multimc_instance(self):
        # import from zip in launch command or something
        pass

    # not yet implemented (not needed in v1)
    def create_obs_instance(self):
        obs.create_scene_item_for_instance(self)

    def initialize_after_boot(self, all_instances):
        # assign our pid somehow
        self.assign_pid(all_instances)
        # start generating world w/ duncan mod
        hlp.run_ahk("resetFromTitle", pid=self.pid, keydelay=settings.get_key_delay())
        # set state to generating
        self.mark_generating()

    def reset_active(self):
        if self.is_active():
            self.pause()
            self.mark_inactive()

    def reset(self):
        if self.was_active and hlp.has_passed(self.timestamp, settings.minimum_time_for_settings_reset()):
            hlp.run_ahk("resetSettings", pid=self.pid, keydelay=settings.get_key_delay())
        else:
            hlp.run_ahk("reset", pid=self.pid, keydelay=settings.get_key_delay())
        self.was_active = False
        self.current_world = None

    def pause(self):
        hlp.run_ahk("pauseGame", pid=self.pid, keydelay=settings.get_key_delay())

    # TODO - call this method somewhere
    def move_worlds(self, old_worlds):
        if settings.is_test_mode():
            print("Moving worlds for instance {}".format(self.name))
            return
        for dir_name in os.listdir(self.mcdir + "/saves"):
            # TODO - i think this should be like "Attempt #X" or something cuz of duncan mod
            if dir_name.startswith("New World"):
                try:
                    shutil.move(self.mcdir + "/saves/" + dir_name,
                                old_worlds + f"/{uuid.uuid1()}")
                except:
                    continue

    # TODO - call this method somewhere
    def copy_logs(self):
        # we should copy all relevant logs out of the instance probably since we want to dynamically create instances
        pass

    def get_current_world(self):
        if self.current_world is not None:
            return self.current_world
        max_time = 0.0
        for world in (self.mcdir / "saves").iterdir():
            world_time = world.stat().st_mtime
            if world_time > max_time:
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

        return (cur_world / "icon.png").exists()

    def __str__(self):
        return "({},{})".format(self.name, self.pid)
