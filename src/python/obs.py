import settings
from obswebsocket import requests as obsrequests
from obswebsocket import obsws
import queues
import helpers as hlp
from wall import Wall, SquareWall, ScreenWall
import helpers as hlp
import time
from pynput import mouse

'''
Manage global state
'''

primary_ids = {}
focused_ids = {}

focused_instance = None
primary_instance = None
stream_obs = None
recording_obs = None
stream_wall = None
recording_wall = None

obs_delay = 0.1


class OBS:
    def connect():
        pass
    
    def start_recording():
        pass

    def clear_scene_items():
        pass

    def get_scene_items():
        pass

def get_primary_instance():
    global primary_instance
    return primary_instance

def get_focused_instance():
    global focused_instance
    return focused_instance

def set_primary_instance(inst):
    global primary_instance
    primary_instance = inst

def set_focused_instance(inst):
    global focused_instance
    focused_instance = inst

def try_hide_primary():
    if get_primary_instance() is not None:
        get_primary_instance().mark_hidden()

def try_hide_focused():
    if get_focused_instance() is not None:
        get_focused_instance().mark_hidden()

'''
Low level utility OBS Functions
'''

def connect_to_stream_obs():
    if not settings.is_obs_enabled():
        return
    global stream_obs
    stream_obs = obsws(settings.get_stream_obs_web_host(),
               settings.get_stream_obs_port(),
               settings.get_stream_obs_password())
    stream_obs.connect()

def call_stream_websocket(arg):
    # print(args)
    if not settings.is_obs_enabled():
        return
    global stream_obs
    return stream_obs.call(arg)

def connect_to_recording_obs():
    if not settings.is_obs_enabled():
        return
    if not settings.use_recording_obs():
        return
    global recording_obs
    recording_obs = obsws(settings.get_recording_obs_web_host(),
               settings.get_recording_obs_port(),
               settings.get_recording_obs_password())
    recording_obs.connect()

def call_recording_websocket(arg):
    # print(args)
    if not settings.is_obs_enabled():
        return
    if not settings.use_recording_obs():
        return
    global recording_obs
    return recording_obs.call(arg)

def get_scene_items(stream=True):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.GetSceneItemList())
    else:
        websocket_result = call_recording_websocket(obsrequests.GetSceneItemList())
    if websocket_result is None:
        return []
    return websocket_result.getSceneItems()

def set_scene_item_visible(name, visible, stream=True):
    if stream:
        call_stream_websocket(obsrequests.SetSceneItemProperties(name, visible=visible))
    else:
        call_recording_websocket(obsrequests.SetSceneItemProperties(name, visible=visible))

'''
High level utility OBS functions
'''

def is_wall_active():
    if not settings.is_wall_enabled():
        return False
    if get_stream_wall() is None:
        return False
    return get_screen_wall().is_active()

def get_item_with_name(name):
    scene_items = get_scene_items()

    for item in scene_items:
        # print(item['name'])
        # print(item.keys())
        # item_name = None
        item_name = item['sourceName']
        if item_name == name:
            return item
    
    return None

def get_base_focused_item():
    return get_item_with_name('focused')

def get_base_primary_item():
    return get_item_with_name('active')

def get_indicator_item():
    return get_item_with_name('indicator')

def update_scene_item_order(force=False):
    if not force and not settings.should_reorder_scene_items():
        return
    scene_items = get_scene_items()
    time.sleep(obs_delay)
    scene_item_names = []
    for scene_item in scene_items:
        scene_item_names.append(scene_item['sourceName'])
    print('names are {}'.format(scene_item_names))
    new_order = []
    tried_set_primary = False
    indices_of_actives = []
    index = 0
    for name in scene_item_names:
        if 'tile' in name:
            continue
        new_order.append(name)
    scene_item_names = new_order
    new_order = []
    for name in scene_item_names:
        if 'active' in name:
            indices_of_actives.append(index)
        new_order.append(name)
        index += 1
    index = 0
    used_instances = []
    if get_primary_instance() is not None:
        inst = get_primary_instance()
        new_order[indices_of_actives[index]] = 'active{}'.format(inst.num)
        used_instances.append(inst.num)
        index += 1
    if get_focused_instance() is not None:
        if get_primary_instance() is not None:
            if get_focused_instance().num == get_primary_instance().num:
                pass
            else:
                inst = get_focused_instance()
                new_order[indices_of_actives[index]] = 'active{}'.format(inst.num)
                used_instances.append(inst.num)
                index += 1
    for i in range(settings.get_num_instances()+1):
        if i == 0:
            continue
        if i not in used_instances:
            new_order[indices_of_actives[index]] = 'active{}'.format(i)
            index += 1
    if settings.is_wall_enabled():
        for i in range(settings.get_num_instances()+1):
            if i == 0:
                continue
            new_order.append('tile{}'.format(i))
    
    print('new order {}'.format(new_order))

    new_order_fmt = []

    for name in new_order:
        new_order_fmt.append({'name':name})

    call_stream_websocket(obsrequests.ReorderSceneItems(new_order_fmt))

def _switch_to_primary(inst):
    global primary_instance
    primary_pid = -1
    if primary_instance is not None:
        if inst is None or primary_instance.num != inst.num:
            primary_instance.mark_back()
            primary_pid = primary_instance.pid
    if inst is not None:
        inst.mark_front(len(queues.get_dead_instances()) > 0)
        if settings.use_switching_daemon():
            with open(hlp.get_pipe_file_location(), 'w') as fil:
                fil.write('{}\n{}'.format(primary_pid, inst.pid))
        inst.mark_primary()
    if primary_instance is not None:
        primary_instance.mark_hidden()
    if inst is not None:
        if inst.is_focused():
            global focused_instance
            focused_instance = None
    set_primary_instance(inst)
    if primary_instance is not None:
        if primary_instance.is_ready() or primary_instance.is_approved():
            primary_instance.mark_active()
        primary_instance.resume()

def set_new_primary(inst):
    global primary_instance
    if is_wall_active():
        set_primary_instance(inst)
        primary_instance.resume()
        return
    _switch_to_primary(inst)

def _switch_focused(inst):
    global focused_instance
    update_scene_item_order()
    if focused_instance is not None:
        focused_instance.mark_hidden()
    set_focused_instance(inst)
    if focused_instance is not None:
        if settings.should_show_focused_as_active():
            show_primary(inst)
        focused_instance.mark_focused()

def set_new_focused(inst):
    global focused_instance
    if is_wall_active():
        set_focused_instance(inst)
        return
    _switch_focused(inst)

def hide_all():
    scene_items = get_scene_items()
    for s in scene_items:
        if 'active' in s['sourceName'] or 'focused' in s['sourceName'] or 'tile' in s['sourceName']:
            set_scene_item_visible({'id': s['itemId']}, visible=False)

def hide_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=False))

def show_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=True))

def hide_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=False))

def show_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=True))

def is_recording_obs_configured():
    scene_items = get_scene_items(False)
    correct_scene_items = ['recording{}'.format(inst.num) for inst in queues.get_all_instances()]
    recording_current_scene_items = [scene_item['sourceName'] for scene_item in scene_items if 'recording' in scene_item['sourceName']]
    if len(correct_scene_items) != len(recording_current_scene_items):
        return False
    for correct_scene_item in recording_current_scene_items:
        has_match = False
        for recording_scene_item in recording_current_scene_items:
            if recording_scene_item == correct_scene_item:
                has_match = True
        if not has_match:
            return False
        set_scene_item_visible({'name': correct_scene_item}, visible=False, stream=False)
        time.sleep(obs_delay)
    return True
    # return False
    # for item in scene_items:
    #     print(item)
    # return True

def is_stream_obs_configured():
    scene_items = get_scene_items(True)
    if settings.is_wall_enabled():
        correct_scene_items = ['tile{}'.format(inst.num) for inst in queues.get_all_instances()]
        current_scene_items = [scene_item['sourceName'] for scene_item in scene_items if 'tile' in scene_item['sourceName']]
        if len(correct_scene_items) != len(current_scene_items):
            return False
        for correct_scene_item in correct_scene_items:
            has_match = False
            for scene_item in current_scene_items:
                if scene_item == correct_scene_item:
                    has_match = True
            if not has_match:
                return False
            set_scene_item_visible({'name': correct_scene_item}, visible=False, stream=False)
            time.sleep(obs_delay)
            correct_scene_items = ['tile{}'.format(inst.num) for inst in queues.get_all_instances()]
    correct_scene_items = ['active{}'.format(inst.num) for inst in queues.get_all_instances()]
    current_scene_items = [scene_item['sourceName'] for scene_item in scene_items if 'active' in scene_item['sourceName']]
    if len(correct_scene_items) != len(current_scene_items):
        return False
    for correct_scene_item in correct_scene_items:
        has_match = False
        for scene_item in current_scene_items:
            if scene_item == correct_scene_item:
                has_match = True
        if not has_match:
            return False
        set_scene_item_visible({'name': correct_scene_item}, visible=False, stream=False)
        time.sleep(obs_delay)
    return False
    # return True



def prompt_for_correct_dimensions():
    global recording_wall
    print('Detecting recording OBS is not configured.')
    recording_wall = Wall(settings.get_num_instances(), settings.get_recording_instance_width(), settings.get_recording_instance_height())
    x, y = recording_wall.get_pixel_dimensions()
    input('Please set your recording OBS to Canvas size {}x{}, then press any key to continue.'.format(x,y))


def delete_scene_item(scene_item, stream=False):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.DeleteSceneItem(scene_item))
    else:
        websocket_result = call_recording_websocket(obsrequests.DeleteSceneItem(scene_item))

def create_scene_item(scene_item_args, stream=False):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.CreateSource(*scene_item_args))
    else:
        websocket_result = call_recording_websocket(obsrequests.CreateSource(*scene_item_args))
    return websocket_result
    
def get_source_settings(source, stream=False):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.GetSourceSettings(source))
    else:
        websocket_result = call_recording_websocket(obsrequests.GetSourceSettings(source))
    return websocket_result

def get_scene_item_properties(name, stream=False):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.GetSceneItemProperties(name))
    else:
        websocket_result = call_recording_websocket(obsrequests.GetSceneItemProperties(name))
    return websocket_result

def set_scene_item_properties(name, props, stream=False):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.SetSceneItemProperties(name, **props))
    else:
        websocket_result = call_recording_websocket(obsrequests.SetSceneItemProperties(name, **props))
    return websocket_result

def set_source_settings(name, source_settings, stream=False):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.SetSourceSettings(name, source_settings))
    else:
        websocket_result = call_recording_websocket(obsrequests.SetSourceSettings(name, source_settings))
    return websocket_result

def get_scene_name(stream=False):
    if stream:
        websocket_result = call_stream_websocket(obsrequests.GetCurrentScene())
    else:
        websocket_result = call_recording_websocket(obsrequests.GetCurrentScene())
    return websocket_result.getName()


def create_scene_item_for_instance(inst, template='recording', stream=False):
    scene_item = {}
    sceneName = get_scene_name(stream)
    scene_item['sourceName'] = '{}{}'.format(template, inst.num)
    scene_item['sourceKind'] = settings.get_obs_source_type()
    scene_item['sceneName'] = sceneName
    # scene_item['sourceSettings'] = 
    result = create_scene_item([item for item in scene_item.values()], stream)
    # print(result)

def reset_source_settings_for_instance(inst, template='recording', stream=False):
    global recording_wall
    source_settings = {}
    source_settings['owner_name'] = None
    source_settings['window'] = 99999+inst.num
    source_settings['window_name'] = None
    source_settings['sourceType'] = settings.get_obs_source_type()
    result = set_source_settings('{}{}'.format(template, inst.num), source_settings, stream)

def set_source_settings_for_instance(inst, template='recording', stream=False):
    global recording_wall
    source_settings = {}
    source_settings['owner_name'] = 'java'
    source_settings['window'] = 99999+inst.num
    source_settings['window_name'] = settings.get_window_title_template().replace("#",str(inst.num))
    source_settings['sourceType'] = settings.get_obs_source_type()
    result = set_source_settings('{}{}'.format(template, inst.num), source_settings, stream)
    # print(result)

def set_scene_item_properties_for_instance(inst, stream=False):
    global recording_wall
    scene_item = {}
    coords = recording_wall.get_coords_for_instance(inst)
    bounds = (settings.get_recording_instance_width(), settings.get_recording_instance_height())
    scene_item['position'] = {'x': coords[0], 'y': coords[1]}
    scene_item['bounds'] = {'x': bounds[0], 'y': bounds[1], 'type': 'OBS_BOUNDS_STRETCH'}
    result = set_scene_item_properties('recording{}'.format(inst.num), scene_item)
    # print(result)



def clear_recording_scene_items():
    for scene_item in get_scene_items(False):
        # print(scene_item)
        # print(get_scene_item_properties(scene_item['sourceName']))
        # print(get_source_settings(scene_item['sourceName']))
        # print()
        my_scene_item = {'name': scene_item['sourceName']}
        if 'recording' in scene_item['sourceName']:
            delete_scene_item(my_scene_item)


def create_recording_scene_items():
    for inst in queues.get_all_instances():
        create_scene_item_for_instance(inst)
        set_source_settings_for_instance(inst)
        time.sleep(obs_delay)
        set_scene_item_properties_for_instance(inst)
        time.sleep(obs_delay)
    pass


def clear_stream_scene_items():
    for scene_item in get_scene_items(True):
        my_scene_item = {'name': scene_item['sourceName']}
        print(my_scene_item['name'])
        if 'wall' == scene_item['sourceName']:
            delete_scene_item(my_scene_item, True)
        if 'tile' in scene_item['sourceName']:
            if not 'tile1' == scene_item['sourceName']:
                delete_scene_item(my_scene_item, True)
        if 'active' in scene_item['sourceName']:
            if not 'active1' == scene_item['sourceName']:
                delete_scene_item(my_scene_item, True)

def set_scene_item_properties_for_instance_from_template(inst, template, stream=True):
    name = '{}1'.format(template)
    result = get_scene_item_properties(name, stream)
    time.sleep(1.0)
    template_item = result.datain
    # print(template_item)
    scene_item = {}
    if template == 'tile':
        coords = get_stream_wall().get_coords_for_instance(inst)
        bounds = (get_stream_wall().instance_pixel_width, get_stream_wall().instance_pixel_height)
        scene_item['position'] = {'x': coords[0], 'y': coords[1]}
        scene_item['bounds'] = {'x': bounds[0], 'y': bounds[1], 'type': 'OBS_BOUNDS_STRETCH'}
    else:
        scene_item['bounds'] = template_item['bounds']
    scene_item['crop'] = template_item['crop']
    scene_item['scale'] = template_item['scale']
    return set_scene_item_properties('{}{}'.format(template, inst.num), scene_item, stream)

def create_stream_scene_items():
    if settings.is_wall_enabled():
        for inst in queues.get_all_instances():
            if inst.num != 1:
                create_scene_item_for_instance(inst, 'tile', True)
                time.sleep(obs_delay)
            reset_source_settings_for_instance(inst, 'tile', True)
            time.sleep(obs_delay)
            set_source_settings_for_instance(inst, 'tile', True)
            time.sleep(obs_delay)
            set_scene_item_properties_for_instance_from_template(inst, 'tile')
            time.sleep(obs_delay)
    for inst in queues.get_all_instances():
        if inst.num != 1:
            create_scene_item_for_instance(inst, 'active', True)
            time.sleep(obs_delay)
        reset_source_settings_for_instance(inst, 'active', True)
        time.sleep(obs_delay)
        set_source_settings_for_instance(inst, 'active', True)
        time.sleep(obs_delay)
        set_scene_item_properties_for_instance_from_template(inst, 'active')
        time.sleep(obs_delay)

def reorder_stream_scene_items():
    update_scene_item_order(True)

def setup_recording_obs():
    if not settings.is_obs_enabled():
        return
    if not settings.auto_configure_obs():
        return
    if not settings.use_recording_obs():
        return
    if not is_recording_obs_configured():
        prompt_for_correct_dimensions()
        clear_recording_scene_items()
        create_recording_scene_items()

def get_stream_wall():
    global stream_wall
    return stream_wall

def get_screen_wall():
    global screen_wall
    return screen_wall

def setup_stream_obs():
    if settings.is_wall_enabled():
        global stream_wall
        stream_wall = SquareWall(settings.get_num_instances(), settings.get_stream_canvas_width(), settings.get_stream_canvas_height())
        global screen_wall
        screen_wall = ScreenWall(stream_wall, settings.get_num_instances(), settings.get_monitor_base_x(), settings.get_monitor_width(), settings.get_monitor_base_y(), settings.get_monitor_height())
    if not settings.is_obs_enabled():
        return
    if not settings.auto_configure_obs():
        return
    if not is_stream_obs_configured():
        clear_stream_scene_items()
        create_stream_scene_items()
        reorder_stream_scene_items()


def register_mouse_listener(cur_wall):
    def on_click(x, y, button, pressed):
        if pressed:
            if pressed and button == mouse.Button.left:
                print('press at coords {} {}'.format(x, y))
                cur_wall.press_instance_at_coords(x, y)

    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()


def stop_mouse_listener():
    global mouse_listener
    mouse.Listener.stop(mouse_listener)

def enter_wall():
    # hide active/focused/etc.
    # switch to the windowed projector
    # enable the wall
    print('enter wall')
    set_new_focused(None)
    set_new_primary(None)
    time.sleep(settings.get_switch_delay()/1000.0)
    hlp.run_ahk("activateWall")
    get_stream_wall().enable()
    get_screen_wall().enable()
    print('done entering')

def exit_wall():
    # show active/focused/etc.
    # switch off the windowed projector
    # disable the wall
    print('exit wall')
    get_screen_wall().disable()
    hlp.run_ahk("deactivateWall")
    time.sleep(settings.get_switch_delay()/1000.0)
    temp_primary = get_primary_instance()
    set_primary_instance(None)
    print('set as primary {}'.format(temp_primary))
    set_new_primary(temp_primary)
    temp_focused = get_focused_instance()
    set_focused_instance(None)
    set_new_focused(temp_focused)
    stream_wall = get_stream_wall()
    for inst in queues.get_all_instances():
        if inst.isShownOnWall:
            inst.release()
    stream_wall.disable()
    print('done exiting')

