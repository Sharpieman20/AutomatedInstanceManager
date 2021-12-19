import settings

max_concurrent = settings.get_max_concurrent()

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
