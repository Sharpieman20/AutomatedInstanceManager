import settings
from obswebsocket import requests as obsrequests
from obswebsocket import obsws
import queues
import helpers as hlp
from wall import Wall
import helpers as hlp
import time

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
    global recording_obs
    recording_obs = obsws(settings.get_recording_obs_web_host(),
               settings.get_recording_obs_port(),
               settings.get_recording_obs_password())
    recording_obs.connect()

def call_recording_websocket(arg):
    # print(args)
    if not settings.is_obs_enabled():
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

def set_new_primary(inst):
    if inst is not None:
        global primary_instance
        if primary_instance is not None:
            primary_instance.mark_hidden()
        set_primary_instance(inst)
        primary_instance.mark_primary()
        if primary_instance.is_ready():
            primary_instance.mark_active()
        primary_instance.resume()
        # TODO @Specnr: Update ls user config (is this still needed?)
        # TODO @Specnr: Change sound source on stream maybe?
        if settings.is_fullscreen_enabled():
            hlp.run_ahk("toggleFullscreen", pid=primary_instance.pid)

def set_new_focused(inst):
    global focused_instance
    if inst is not None:
        if focused_instance is not None:
            focused_instance.mark_hidden()
        set_focused_instance(inst)
        focused_instance.mark_focused()



def hide_all():
    scene_items = get_scene_items()
    for s in scene_items:
        if 'active' in s['sourceName'] or 'focused' in s['sourceName']:
            set_scene_item_visible({'id': s['itemId']}, visible=False)

def hide_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=False))

def show_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=True))

def hide_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=False))

def show_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=True))



def setup_stream_obs():
    pass


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
        time.sleep(0.1)
    return True
    # return False
    # for item in scene_items:
    #     print(item)
    # return True

def is_stream_obs_configured():
    scene_items = get_scene_items(True)
    correct_scene_items = ['tile{}'.format(inst.num) for inst in queues.get_all_instances()]
    current_scene_items = [scene_item['sourceName'] for scene_item in scene_items if 'tile' in scene_item['sourceName']]
    for correct_scene_item in recording_current_scene_items:
        has_match = False
        for scene_item in current_scene_items:
            if scene_item == correct_scene_item:
                has_match = True
        if not has_match:
            return False
        set_scene_item_visible({'name': correct_scene_item}, visible=False, stream=False)
        time.sleep(0.1)
        correct_scene_items = ['tile{}'.format(inst.num) for inst in queues.get_all_instances()]
    correct_scene_items = ['active{}'.format(inst.num) for inst in queues.get_all_instances()]
    current_scene_items = [scene_item['sourceName'] for scene_item in scene_items if 'active' in scene_item['sourceName']]
    for correct_scene_item in recording_current_scene_items:
        has_match = False
        for scene_item in current_scene_items:
            if scene_item == correct_scene_item:
                has_match = True
        if not has_match:
            return False
        set_scene_item_visible({'name': correct_scene_item}, visible=False, stream=False)
        time.sleep(0.1)
    return True



def prompt_for_correct_dimensions():
    global recording_wall
    print('Detecting recording OBS is not configured.')
    recording_wall = Wall(settings.get_num_instances(), settings.get_recording_instance_width(), settings.get_recording_instance_height())
    x, y = recording_wall.get_pixel_dimensions()
    input('Please set your recording OBS to output resolution {}x{}, then press any key to continue.'.format(x,y))


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


def create_scene_item_for_instance(inst, stream=False):
    scene_item = {}
    sceneName = get_scene_name(stream)
    scene_item['sourceName'] = 'recording{}'.format(inst.num)
    scene_item['sourceKind'] = settings.get_obs_source_type()
    scene_item['sceneName'] = sceneName
    # scene_item['sourceSettings'] = 
    result = create_scene_item([item for item in scene_item.values()], stream)
    print(result)

def set_source_settings_for_instance(inst, stream=False):
    global recording_wall
    source_settings = {}
    source_settings['owner_name'] = 'java'
    source_settings['window'] = 99999+inst.num
    source_settings['window_name'] = 'Instance {}'.format(inst.num)
    source_settings['sourceType'] = settings.get_obs_source_type()
    result = set_source_settings('recording{}'.format(inst.num), source_settings)
    print(result)

def set_scene_item_properties_for_instance(inst, stream=False):
    global recording_wall
    scene_item = {}
    coords = recording_wall.get_coords_for_instance(inst)
    bounds = (settings.get_recording_instance_width(), settings.get_recording_instance_height())
    scene_item['position'] = {'x': coords[0], 'y': coords[1]}
    scene_item['bounds'] = {'x': bounds[0], 'y': bounds[1], 'type': 'OBS_BOUNDS_STRETCH'}
    result = set_scene_item_properties('recording{}'.format(inst.num), scene_item)
    print(result)



def clear_recording_scene_items():
    for scene_item in get_scene_items(False):
        print(scene_item)
        print(get_scene_item_properties(scene_item['sourceName']))
        print(get_source_settings(scene_item['sourceName']))
        print()
        my_scene_item = {'name': scene_item['sourceName']}
        if 'recording' in scene_item['sourceName']:
            delete_scene_item(my_scene_item)


def create_recording_scene_items():
    for inst in queues.get_all_instances():
        create_scene_item_for_instance(inst)
        set_source_settings_for_instance(inst)
        time.sleep(0.1)
        set_scene_item_properties_for_instance(inst)
        time.sleep(0.25)
    pass


def clear_stream_scene_items():
    for scene_item in get_scene_items(True):
        my_scene_item = {'name': scene_item['sourceName']}
        if 'tile' in scene_item['sourceName']:
            if 'tile1' not in scene_item['sourceName']:
                delete_scene_item(my_scene_item, True)
        if 'active' in scene_item['sourceName']:
            if 'active1' not in scene_item['sourceName']:
                delete_scene_item(my_scene_item, True)

def create_scene_item_for_instance_from_template(inst, template, stream=True):

def create_stream_scene_items():
    for inst in queues.get_all_instances():
        create_scene_item_for_instance_from_template(inst, 'tile')
        time.sleep(0.25)
        create_scene_item_for_instance_from_template(inst, 'tile')
        time.sleep(0.25)
        create_scene_item_for_instance_from_template(inst, 'tile')
        time.sleep(0.25)
        create_scene_item_for_instance_from_template(inst, 'active')
        time.sleep(0.25)
        create_scene_item_for_instance_from_template(inst, 'active')
        time.sleep(0.25)
        create_scene_item_for_instance_from_template(inst, 'active')
        time.sleep(0.25)


def setup_recording_obs():
    if not is_recording_obs_configured():
        prompt_for_correct_dimensions()
        clear_recording_scene_items()
        create_recording_scene_items()


def setup_stream_obs():
    if not is_stream_obs_configured():
        clear_stream_scene_items()
        create_stream_scene_items()
