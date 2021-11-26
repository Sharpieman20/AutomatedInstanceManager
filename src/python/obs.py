import settings
from obswebsocket import requests as obsrequests
from obswebsocket import obsws
import queues
import helpers as hlp

'''
Manage global state
'''

primary_ids = {}
focused_ids = {}

focused_instance = None
primary_instance = None
stream_obs = None

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


'''
Low level utility OBS Functions
'''

def connect_to_stream_obs():
    if not settings.is_obs_enabled():
        return
    global stream_obs
    stream_obs = obsws(settings.get_obs_web_host(),
               settings.get_obs_port(),
               settings.get_obs_password())
    stream_obs.connect()

def call_stream_websocket(arg):
    # print(args)
    if not settings.is_obs_enabled():
        return
    global stream_obs
    return stream_obs.call(arg)

def get_scene_items():
    websocket_result = call_stream_websocket(obsrequests.GetSceneItemList())
    if websocket_result is None:
        return []
    return websocket_result.getSceneItems()

def set_scene_item_properties(name, visible):
    call_stream_websocket(obsrequests.SetSceneItemProperties(name, visible=visible))

'''
High level utility OBS functions
'''

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

def update_scene_item_order():
    if not settings.should_reorder_scene_items():
        return
    scene_items = get_scene_items()
    scene_item_names = []
    for scene_item in scene_items:
        scene_item_names.append(scene_item['sourceName'])
    new_order = []
    tried_set_primary = False
    indices_of_actives = []
    index = 0
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

    call_stream_websocket(obsrequests.ReorderSceneItems(new_order))

def set_new_primary(inst):
    # print(inst)
    if inst is not None:
        update_scene_item_order()
        global primary_instance
        primary_pid = -1
        if primary_instance is not None:
            primary_instance.mark_back()
            primary_pid = primary_instance.pid
        inst.mark_front(len(queues.get_dead_instances()) > 0)
        if settings.use_switching_daemon():
            with open(hlp.get_pipe_file_location(), 'w') as fil:
                fil.write('{}\n{}'.format(primary_pid, inst.pid))
        inst.mark_primary()
        if primary_instance is not None:
            primary_instance.mark_hidden()
        if inst.is_focused():
            global focused_instance
            focused_instance = None
        set_primary_instance(inst)
        if primary_instance.is_ready():
            primary_instance.mark_active()
        primary_instance.resume()

def set_new_focused(inst):
    global focused_instance
    if inst is not None:
        update_scene_item_order()
        if focused_instance is not None:
            focused_instance.mark_hidden()
        set_focused_instance(inst)
        if settings.should_show_focused_as_active():
            show_primary(inst)
        focused_instance.mark_focused()

def create_scene_item_for_instance(inst):
    pass

def hide_all():
    scene_items = get_scene_items()
    for s in scene_items:
        if 'active' in s['sourceName'] or 'focused' in s['sourceName']:
            set_scene_item_properties({'id': s['itemId']}, visible=False)

def hide_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=False))

def show_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=True))

def hide_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=False))

def show_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=True))
