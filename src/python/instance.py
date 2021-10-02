import helpers as hlp
import os
import shutil
import uuid
from datetime import datetime

num_per_state = {}

def assign_to_state(instance, state):
    global num_per_state
    if state not in num_per_state:
        num_per_state[state] = 0
    num_per_state[state] = num_per_state[state] + 1
    instance.priority = num_per_state[state]

class State(Enum):
    DEAD = 0
    BOOTING = 1
    FREE = 2
    PREGEN = 3
    GEN = 4
    PAUSED = 5
    READY = 6
    APPROVED = 7
    ACTIVE = 8

class Process:
    def assign_pid(self, all_processes):
        if settings.is_test_mode():
            self.pid = settings.get_global_test_pid()
            return
        all_pids = hlp.get_pids()
        for pid in all_pids:
            pid_maps_to_instance = False
            for instance in all_instances:
                if instance.pid == pid:
                    pid_maps_to_instance = True
            if not pid_maps_to_instance:
                self.pid = pid


class Suspendable(Process):
    def suspend(self):
        if self.is_suspended():
            return
        self.suspended = True
        run_ahk("suspendInstance", pid=self.pid)

    def resume(self):
        if not self.is_suspended():
            return
        self.is_suspended = False
        run_ahk("resumeInstance", pid=self.pid)

    def is_suspended(self):
        return self.suspended


class Stateful(Suspendable):

    def mark_booting(self):
        assign_to_state(self, State.BOOTING)
        self.timestamp = get_time()
    
    def mark_pregen(self):
        self.was_active = False
        assign_to_state(self, State.PREGEN)
    
    def mark_generating(self):
        assign_to_state(self, State.GEN)
    
    def mark_worldgen_finished(self):
        assign_to_state(self, State.PAUSED)
        self.timestamp = get_time()
    
    def mark_free(self):
        assign_to_state(self, State.FREE)
    
    def release(self):
        if self.is_suspended():
            assign_to_state(self, State.FREE)
        else:
            assign_to_state(self, State.PREGEN)
        self.timestamp = get_time()

    def mark_ready(self):
        pass

    def mark_active(self):
        assign_to_state(self, State.ACTIVE)
        self.was_active = True

    def mark_inactive(self):
        # add to pregen
        self.mark_pregen()


class ConditionalTransitionable(Stateful):

    def is_ready_for_freeze(self):
        if self.state == State.PAUSED:
            duration = 2.0
        return has_passed(self.timestamp, duration)

    def is_done_unfreezing(self):
        duration = 0.5
        return has_passed(self.timestamp, duration)

    def is_ready_for_unfreeze(self):
        duration = 0.5
        return has_passed(self.timestamp, duration)

    def check_should_auto_reset(self):
        duration = 300.0
        if has_passed(self.timestamp, duration):
            self.release()
            return True

class Instance(ConditionalTransitionable):

    def __init__(self, num):
        self.num = num
        self.priority = assign_to_state(self, 0)
        self.pid = -1
        self.first_reset = True
        self.suspended = False
        self.state = -1
        self.timestamp = 0
        self.was_active = False
    
    def boot(self):
        hlp.run_cmd('{} --launch "{}"'.format(executable, inst_name))

    # not yet implemented
    def create_multimc_instance(self):
        pass

    # not yet implemented
    def create_obs_instance(self):
        pass

    def initialize_after_boot(self, all_instances):
        # assign our pid somehow
        self.assign_pid(all_instances)
        # set our title
        hlp.run_ahk("updateTitle", pid=self.pid,
            title=f"Minecraft* - Instance {i+1}")
        # start generating world w/ duncan mod
        hlp.run_ahk("startDuncanModSession", pid=self.pid)
        # set state to generating
        self.mark_generating()

    def reset_active(self):
        self.pause()
        self.mark_inactive()

    def reset(self):
        hlp.run_ahk("reset", pid=self.pid)

    def pause(self):
        hlp.run_ahk("pauseGame", pid=self.pid)

    def move_worlds(self, old_worlds):
        for dir_name in os.listdir(self.mcdir + "/saves"):
            if dir_name.startswith("New World"):
                try:
                    shutil.move(self.mcdir + "/saves/" + dir_name,
                                old_worlds + f"/{uuid.uuid1()}")
                except:
                    continue

    def read_logs(self, func_check, lines_from_bottom=2):
        log_file = self.mcdir + "/logs/latest.log"
        with open(log_file, "r") as logs:
            lines = logs.readlines()
            for i in range(len(lines)):
                if (len(lines) - i <= lines_from_bottom):
                    if (func_check(lines[i])):
                        return True
        return False

    def is_in_world(self, lines_from_bottom=2):
        if self.first_reset:
            return False
        # Read logs and see if is done world gen
        return self.read_logs(lambda x: "Saving chunks for level 'ServerLevel" in x and "minecraft:the_end" in x, lines_from_bottom)