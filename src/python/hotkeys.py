import keyboard as kb
import threading
import settings
import obs
import queues
from instance import State
from global_hotkeys import register_hotkeys

hotkey_lock = threading.Lock()

# Callbacks
def reset_primary():
    print('start reset primary')
    primary_instance = obs.get_primary_instance()
    if primary_instance is not None:
        primary_instance.reset_active()
    if settings.is_wall_enabled():
        obs.enter_wall()

def exit_wall():
    obs.exit_wall()

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
    if not settings.should_use_beta():
        return
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
        hotkey_lock.acquire()
        global hotkeys
        hotkeys.append(func)
        hotkey_lock.release()
    return inner

def process_hotkey_events():
    if not hotkey_lock.acquire(False):
        return
    global hotkeys
    for hotkey_action in hotkeys:
        hotkey_action()
    hotkeys = []
    hotkey_lock.release()

def setup_hotkeys():
    global hotkeys
    hotkeys = []
    global listening
    listening = True
    my_bindings = []
    def add_hotkey(key_name, func, override=False):
        my_bindings.append([[settings.get_hotkeys()[key_name]], wrap(func, override), None])
    add_hotkey('reset-active', reset_primary)
    add_hotkey('toggle-hotkeys', toggle_hotkeys, True)
    if 'reset-focused' in settings.get_hotkeys():
        add_hotkey('reset-focused', reset_focused)
    if 'approve-focused' in settings.get_hotkeys():
        add_hotkey('approve-focused', approve_focused)
    if 'background-debug' in settings.get_hotkeys():
        add_hotkey('background-debug', debug_background)
    if 'background-pause' in settings.get_hotkeys():
        add_hotkey('background-pause', pause_background)
    if 'unfreeze-all' in settings.get_hotkeys():
        add_hotkey('unfreeze-all', unfreeze_all)
    if 'exit-wall' in settings.get_hotkeys():
        add_hotkey('exit-wall', exit_wall)
    register_hotkeys(my_bindings)

