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

Download installer.py\
Right click it, run/open with python

Create X instances named 1.16INST1, 1.16INST2, 1.16INST3, etc. in multi MC

You can configure options by making a new file "settings.json" in the same directory as installer.py\
Check "defaults/settings.json" for the default settings which you might want to override\
DO NOT edit defaults/settings.json, you must edit the other settings.json file

Custom AHK scripts can be placed in directory "custom"

Each time you want to run the macro, right click installer.py and run it\