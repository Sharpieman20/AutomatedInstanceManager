import json
from pathlib import Path
import sys

custom_settings_file = Path.cwd() / sys.argv[1]

print('Using custom settings file {}'.format(custom_settings_file))

settings = {}


if custom_settings_file.exists():
    with open(custom_settings_file, "r") as custom_settings_readable:
        settings = json.load(custom_settings_readable)

default_settings_file = Path.cwd() / "defaults" / "settings.json"
default_settings = {}

if default_settings_file.parent.exists() and default_settings_file.exists():
    with open(default_settings_file, "r") as default_settings_readable:
        default_settings = json.load(default_settings_readable)

for key in default_settings.keys():
    if key not in settings.keys():
        settings[key] = default_settings[key]
    elif key == 'hotkeys':
        for sub_key in default_settings[key].keys():
            if sub_key not in settings[key]:
                settings[key][sub_key] = default_settings[key][sub_key]

print('using settings {}'.format(settings))

def is_test_mode():
    return settings['test-mode']

def get_num_instances():
    return int(settings['num-instances'])

def get_max_concurrent():
    return int(settings['max-concurrent'])

def get_unfreeze_delay():
    return float(settings['unfreeze-delay']) / 1000.0

def get_freeze_delay():
    return float(settings['freeze-delay']) / 1000.0

def get_unfrozen_queue_size():
    return int(settings['unfrozen-queue-size'])

def get_hotkeys():
    return settings['hotkeys']

def should_use_tts():
    return not settings['disable-tts']

def get_loop_delay():
    return float(settings['loop-delay']) / 1000.0

def get_daemon_loop_delay():
    return int(settings['loop-delay'])

def get_lines_from_bottom():
    return int(settings['lines-from-bottom'])

def get_multimc_path():
    return Path(settings['multi-mc-path'])

def get_base_instance_name():
    return settings['template-instance']

def get_boot_delay():
    return float(settings['boot-delay'])

def get_switch_delay():
    return int(settings['switch-delay'])

def get_obs_delay():
    return float(settings['obs-delay'])

def is_fullscreen_enabled():
    return settings['fullscreen']

def get_fullscreen_delay():
    return int(settings['fullscreen-delay'])

def get_debug_interval():
    return 2.0

def get_test_worldgen_time():
    return 1.7

def should_auto_launch():
    return settings['auto-launch']

def get_stream_obs_web_host():
    return settings['stream-obs-settings']['web-host']

def get_stream_obs_port():
    return settings['stream-obs-settings']['port']

def get_stream_obs_password():
    return settings['stream-obs-settings']['password']

def get_recording_obs_web_host():
    return settings['recording-obs-settings']['web-host']

def get_recording_obs_port():
    return settings['recording-obs-settings']['port']

def get_recording_obs_password():
    return settings['recording-obs-settings']['password']

def get_obs_source_type():
    if settings['use-game-capture']:
        return 'game_capture'
    return 'window_capture'

def should_auto_pause():
    return settings['auto-pause']

def is_ahk_enabled():
    return settings['ahk-enabled']

def is_obs_enabled():
    return settings['obs-enabled']

def only_focus_ready():
    return True

def get_max_unpaused_time():
    return settings['max-unpaused-time']

def prioritize_booting_over_worldgen():
    return settings['prio-booting-over-worldgen']

def minimum_time_for_settings_reset():
    return settings['min-time-for-settings-reset']

def get_load_chunk_time():
    return settings['chunk-load-time']

def get_obs_path():
    return settings['obs-path']

def get_livesplit_path():
    return Path(settings['livesplit-path'])

def get_start_create_world_delay():
    return settings['min-time-from-reset-to-world-entry']

def should_parallelize_ahk():
    return settings['parallelize-ahk']

def get_key_delay():
    return int(settings['key-delay'])

def get_pause_delay():
    return int(settings['pause-delay'])


def get_is_borderless():
    return settings['borderless']

def get_manual_launch_batch_size():
    batch_size = settings['manual-launch-batch-size']
    if batch_size > 0:
        return batch_size
    return get_max_concurrent()

def should_maximize():
    return settings['should-maximize']

def get_max_time_before_auto_reset():
    return settings['max-time-before-auto-reset']

def should_auto_unpause():
    return settings['auto-unpause']

def get_maximize_delay():
    return settings['maximize-delay']

def use_switching_daemon():
    return settings['use-switching-daemon']

def should_use_beta():
    return settings['use-beta']

def get_unpause_delay():
    return settings['auto-unpause-delay']

def get_old_worlds_directory():
    return Path(settings['old-worlds-folder'])

def should_move_old_worlds():
    return settings['move-old-worlds']

def use_reset_counter():
    return settings['use-reset-counter']

def retry_freezes():
    return settings['randomly-retry-freezes']

def stay_always_on_top_when_still_launching():
    return settings['stay-on-top-while-launching']

def get_version():
    return settings['version']

def should_set_window_titles():
    return settings['set-window-titles']

def get_window_title_template():
    return settings['window-title-template']

def use_custom_background_ahk_process():
    return settings['run-custom-background-ahk-script']

def attempt_to_relaunch_crashed_instances():
    return settings['relaunch-crashed-instances']

def check_for_crashes_delay():
    return settings['check-for-crashes-delay']

def should_auto_launch_multimc():
    return False

def use_click_macro():
    return settings['use-click-macro']

def should_settings_reset_first_world():
    return settings['settings-reset-first-world']

def try_fast_launch():
    return False

def wait_for_all_to_launch_before_booting():
    return settings['frontload-launching']

def get_multimc_delay():
    return settings['multi-mc-delay']

def use_custom_ahk_scripts():
    return settings['use-custom-ahk-scripts']

def should_kill_all_on_exit():
    return settings['quit-instances-on-exit']

def should_reorder_scene_items():
    return settings['dynamically-reorder-scene-items']

def should_show_focused_as_active():
    return settings['show-focused-as-active']

def should_auto_launch_apps():
    return settings['auto-launch-apps']
def get_max_concurrent_in_run():
    max_concurrent_in_run = int(settings['max-concurrent-in-run'])
    if max_concurrent_in_run == -1:
        return get_max_concurrent()
    return max_concurrent_in_run

def get_recording_instance_height():
    return settings['recording-instance-height']

def get_recording_instance_width():
    return settings['recording-instance-width']

def use_prioritization():
    return False

def launch_java_test_processes():
    return True

def get_stream_canvas_width():
    return settings['stream-canvas-width']

def get_stream_canvas_height():
    return settings['stream-canvas-height']

def auto_configure_obs():
    return settings['auto-configure-obs']

def use_recording_obs():
    return settings['use-recording-obs']

def is_wall_enabled():
    return settings['use-wall']

def get_monitor_base_x():
    return int(settings['monitor-base-x'])

def get_monitor_base_y():
    return int(settings['monitor-base-y'])

def get_monitor_height():
    return int(settings['monitor-height'])

def get_monitor_width():
    return int(settings['monitor-width'])

def wall_single_select_mode():
    return settings['wall-single-select']

def reset_all_on_wall():
    return settings['wall-reset-all']

def stay_on_wall_if_none_good():
    return settings['stay-on-wall-if-none-good']

def show_only_ready_on_wall():
    return False

def dump_obs_config():
    return settings['dump-obs-config']

def show_debug():
    return True

# INTENTIONALLY HARDCODED SETTINGS

def get_multimc_launch_delay():
    return 4.0

def get_title_screen_obs_delay():
    return int(settings['title-delay'])

def max_worldgen_time():
    return 30.0
