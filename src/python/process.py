import settings
import helpers as hlp
from enum import Enum
if not settings.is_test_mode():
    import win32process
else:
    import threading
    import time

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
                if pid > self.pid:
                    self.pid = pid

class Suspendable(Process):
    def suspend(self):
        if self.is_suspended() or self.forceResumed:
            if not settings.retry_freezes() or random.randint(0, 50) != 0:
                return
        self.suspended = True
        hlp.run_ahk("suspendInstance", pid=self.pid)

    # TODO @Sharpieman20 use SetProcessInformation to increase memory priority for active instances
    def resume(self, force=False):
        if not force and not self.is_suspended():
            return
        self.suspended = False
        if force and not self.forceResumed:
            self.forceResumed = True
        modified_page_writer_delay = 0
        if settings.ram_buffer_size() > 0:
            ram_buffer_size_formatted = '{}g'.format(str(int(settings.ram_buffer_size())))
            modified_page_writer_delay = 1000
            hlp.run_cmd('java -XX:+AlwaysPreTouch -Xms{} -Xmx{} src/java/RamBuffer.java {}'.format(ram_buffer_size_formatted, ram_buffer_size_formatted, modified_page_writer_delay))
        hlp.run_ahk("resumeInstance", pid=self.pid, resumedelay=modified_page_writer_delay)

    def is_suspended(self):
        return self.suspended

# CURRENTLY UNUSED
class SuspendableProcess(Process):
    def suspend(self):
        if self.is_suspended():
            return
        self.suspended = True
        if settings.is_local_test_mode():
            def sleep_and_stop():
                time.sleep(1)
                hlp.run_cmd('kill -STOP {}'.format(self.pid))
            hlp.hide_mac_window(self)
            th = threading.Thread(target=sleep_and_stop)
            th.start()
            return
        hlp.run_ahk("suspendInstance", pid=self.pid)

    def resume(self, override=False):
        if not self.is_suspended():
            return
        self.suspended = False
        if settings.is_local_test_mode():
            def show_mac_window_inner():
                time.sleep(1)
                hlp.show_mac_window(self)
            hlp.run_cmd('kill -CONT {}'.format(self.pid))
            th = threading.Thread(target=show_mac_window_inner)
            th.start()
            return
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
    
    def resume(self, override=False):
        if not settings.use_prioritization():
            return super().resume(override)
        if not self.is_suspended():
            return
        self.suspended = False
        set_process_priority(self.pid, Priority.ACTIVE)
        set_memory_priority(self.pid, Priority.ACTIVE)
        
