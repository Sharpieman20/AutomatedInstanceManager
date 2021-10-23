import settings
from obswebsocket import requests as obsrequests
from obswebsocket import obsws
import queues
import helpers as hlp
from wall import Wall

'''
Manage global state
'''

primary_ids = {}
focused_ids = {}

focused_instance = None
primary_instance = None
stream_obs = None
recording_obs = None
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

def connect_to_recording_obs():
    if not settings.is_obs_enabled():
        return
    global stream_obs
    recording_obs = obsws(settings.get_obs_web_host(),
               settings.get_obs_port(),
               settings.get_obs_password())
    stream_obs.connect()

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

def set_new_primary(inst):
    if inst is not None:
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
        if focused_instance is not None:
            focused_instance.mark_hidden()
        set_focused_instance(inst)
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



def setup_stream_obs():
    pass


def is_recording_obs_configured():
    scene_items = get_scene_items(False)
    if len(scene_items) != settings.get_num_instances():
        return False
    for item in scene_items:
        print(item)
    return True


def prompt_for_correct_dimensions():
    global recording_wall
    print('Detecting recording OBS is not configured.')
    recording_wall = Wall(settings.get_num_instances(), settings.get_recording_instance_width(), settings.get_recording_instance_height())
    x, y = recording_wall.get_pixel_dimensions()
    input('Please set your recording OBS to output resolution {}x{}, then press any key to continue.'.format(x,y))

def clear_recording_scene_items():
    for scene_item in get_scene_items(False):
        delete_scene_item(scene_item)


def create_recording_scene_items():



def setup_recording_obs():

    if not is_recording_obs_configured():
        prompt_for_correct_dimensions()
        clear_recording_scene_items()
        create_recording_scene_items()


    # check if sources exist
        # if not, prompt user to set canvas siz
        # initialize sources
    # start recording

    print(scene_items)
    raise
