import settings
import helpers as hlp
from enum import Enum
if not settings.is_test_mode():
    import win32process

def set_process_priority(process_handle, priority):
    if settings.is_test_mode():
        return
    win32process.SetPriorityClass(process_handle, priority)

def set_memory_priority(process_handle, priority):
    # SetProcessInformation
    # but i cna't find any examples of anyone using it?? does it even work???
    pass

class Process:
    def assign_pid(self, all_processes):
        # for now, require auto-launch mode enabled
        if settings.is_test_mode() and not settings.launch_java_test_processes():
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

class SuspendableProcess(Process):
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


class Priority(Enum):
    IDLE = 64

class MemoryPriority(Enum):
    IDLE = 0
    ACTIVE = 1

class PrioritizeableProcess(SuspendableProcess):

    def suspend(self):
        if not settings.use_prioritization():
            return super().suspend()
        if self.is_suspended():
            return
        self.suspended = True
        set_process_priority(self.pid, Priority.IDLE)
        set_memory_priority(self.pid, Priority.IDLE)
    
    def resume(self):
        if not settings.use_prioritization():
            return super().resume()
        if not self.is_suspended():
            return
        self.suspended = False
        set_process_priority(self.pid, Priority.ACTIVE)
        set_memory_priority(self.pid, Priority.ACTIVE)
        
