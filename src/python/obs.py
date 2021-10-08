import settings
from obswebsocket import requests as obsrequests
from obswebsocket import obsws
import queues

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




def set_new_primary(inst):
    print(inst)
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
            run_ahk("toggleFullscreen")

def set_new_focused(inst):
    global focused_instance
    if inst is not None:
        if focused_instance is not None:
            focused_instance.mark_hidden()
        set_focused_instance(inst)
        focused_instance.mark_focused()

def create_scene_item_for_instance(inst):
    # TODO @Specnr
    # get_primary_scene_item_for_instance(inst)

    # scenes = call_stream_websocket(obsrequests.GetSceneList())
    # all_sources = call_stream_websocket(obsrequests.GetSourcesList())
    # scene_items = call_stream_websocket(obsrequests.GetSceneItemList())
    # # settings_active = call_stream_websocket(obsrequests.GetSourceSettings('active'))
    # # base_props = call_stream_websocket(obsrequests.GetSceneItemProperties(item='active'))
    # # for s in scenes.getScenes():
    # #     # print(s['name'])
    # #     print(len(s['sources']))
    # #     print(s['sources'][0])

    # # active_group = None

    # for scene_item in scene_items.getSceneItems():
    #     # if scene_item['sourceName'] == 'instance2':
    #     #     props = call_stream_websocket(obsrequests.GetSceneItemProperties('instance2'))
    #     #     print(props)
    #     print(scene_item)

    scene_item_id = get_primary_scene_item_id_for_instance(inst)

    call_stream_websocket(obsrequests.SetSceneItemProperties({'id':scene_item_id},visible=True))

    # print(scene_items.datain)
    raise

    # temp_item = get_base_primary_item()
    # temp_item['name'] = 'newitem'

    # print(temp_item)
    # temp_item = {'itemId': 59, 'name': 'active'}

    # result = call_stream_websocket(obsrequests.DuplicateSceneItem(item=temp_item))

    # print(result.datain)

    # result2 = call_stream_websocket(obsrequests.GetSceneItemProperties(item='active'))

    # create a source with this:
    # https://github.com/Elektordi/obs-websocket-py/blob/master/obswebsocket/requests.py#L551
    # we can create a source that is a copy of a different source returned from
    # https://github.com/Elektordi/obs-websocket-py/blob/master/obswebsocket/requests.py#L524

    # obs1
    #      create a source for when this instance is active
    #   create a source for when this instance is focused
    # obs2
    #   create a source for this instance
    #       tile based on total number of instances
    pass

# def get_primary_scene_item_id_for_instance(inst):
#     global primary_ids
#     if inst.num in primary_ids.keys():
#         return primary_ids[inst.num]
    
#     scene_items = get_scene_items()
#     for scene_item in scene_items:
#         # sub_props = call_stream_websocket(obsrequests.GetSceneItemProperties(sub['itemId']))
#         # print(sub)
#         # print()
#         if str(inst.num) in scene_item['sourceName']:
#             primary_ids[inst.num] = scene_item['itemId']
#             return scene_item['itemId']
#     return -1

# def get_focused_scene_item_id_for_instance(inst):
#     global focused_ids
#     if inst.num in focused_ids.keys():
#         return focused_ids[inst.num]
    
#     scene_items = get_scene_items()
#     found_yet = False
#     for scene_item in scene_items:
#         # sub_props = call_stream_websocket(obsrequests.GetSceneItemProperties(sub['itemId']))
#         # print(sub)
#         # print()
#         print(scene_item['sourceName'])
#         if str(inst.num) in scene_item['sourceName']:
#             if not found_yet:
#                 found_yet = True
#             else:
#                 focused_ids[inst.num] = scene_item['itemId']
#                 return scene_item['itemId']
#     return -1

def hide_all():
    scene_items = get_scene_items()
    for s in scene_items:
        set_scene_item_properties({'id': s['itemId']}, visible=False)

def hide_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=False))

def show_primary(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'active{}'.format(inst.num)},visible=True))

def hide_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=False))

def show_focused(inst):
    call_stream_websocket(obsrequests.SetSceneItemProperties({'name':'focused{}'.format(inst.num)},visible=True))
