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

def is_test_mode():
    return settings['test-mode']

def get_num_instances():
    return int(settings['num-instances'])

def get_max_concurrent():
    return int(settings['max-concurrent'])

def get_max_concurrent_boot():
    return int(settings['max-concurrent-boot'])

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

def get_debug_interval():
    return 2.0

def get_test_worldgen_time():
    return 5.0

def should_auto_launch():
    return settings['auto-launch']

def get_obs_web_host():
    return settings['obs-settings']['web-host']

def get_obs_port():
    return settings['obs-settings']['port']

def get_obs_password():
    return settings['obs-settings']['password']

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
    return settings['livesplit-path']

def get_start_create_world_delay():
    return settings['min-time-from-reset-to-world-entry']

def should_parallelize_ahk():
    return settings['parallelize-ahk']

def get_key_delay():
    return int(settings['key-delay'])

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

