Install AHK\
Install python

Set up your OBS like this:\
indicator\
group (focused)\
    focused1\
    focused2\
    focused3\
    ...\
    focusedX\
group (active)\
    active1\
    active2\
    active3\
    ...\
    activeX

Install this extension https://obsproject.com/forum/resources/obs-websocket-remote-control-obs-studio-from-websockets.466/

To view BG resets, right click on focused group, windowed projector.\
This will make a preview window. If you right click on this preview window and select "Always On Top" then you will have a preview you can place anywhere

Download installer.py\
Right click it, run/open with python

Create X instances named 1.16INST1, 1.16INST2, 1.16INST3, etc. in multi MC

You can configure options by editing "my_settings.json"\
Check "defaults/settings.json" for the default settings which you might want to override

Custom AHK scripts can be placed in directory "custom"

Each time you want to run the macro, right click installer.py and run it\