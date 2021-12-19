import settings
import shutil
import time
from pathlib import Path

IS_BETA = True

max_concurrent = settings.get_max_concurrent()

def download_branch(branch):
    installer_file = Path.cwd() / "run_aim.py"
    if installer_file.exists():
        installer_file.unlink()
    installer_file_url = 'https://raw.githubusercontent.com/Sharpieman20/AutomatedInstanceManager/{}/run_aim.py'.format(branch)
    r = requests.get(installer_file_url, allow_redirects=True)
    installer_file.touch()
    open(installer_file.name, 'w').write(r.text)
    hlp.run_cmd('py run_aim.py', blocking=True)

def try_download_regular():
    global IS_BETA
    if not IS_BETA:
        return
    download_branch('main')

def try_download_beta():
    global IS_BETA
    if IS_BETA:
        return
    download_branch('beta')

def run_validation():
    if not settings.is_test_mode():
        if settings.should_use_beta():
            try_download_beta()
        else:
            try_download_regular()
    if settings.use_custom_ahk_scripts() and not settings.is_test_mode():
        src_ahk = Path.cwd() / "src" / "ahk"
        custom_directory = Path.cwd() / "custom"
        if custom_directory.exists():
            for custom_ahk in custom_directory.iterdir():
                shutil.copyfile(custom_ahk, src_ahk / custom_ahk.name)
        else:
            custom_directory.mkdir()
    assert settings.get_unfrozen_queue_size() < max_concurrent
    if max_concurrent - settings.get_unfrozen_queue_size() <= 1:
        print('ERROR: max-concurrent and unfrozen-queue-size are within 1. Increment max-concurrent or decrease unfrozen-queue-size.')
        time.sleep(5000)
    if not settings.is_test_mode() and not settings.get_multimc_path().exists():
        print('ERROR: Your MultiMC path is set incorrectly! Set your MultiMC path in my_settings.json.')
        time.sleep(5000)
