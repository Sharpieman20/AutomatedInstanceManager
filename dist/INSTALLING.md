Install AHK
Install python

Set up your OBS like this:
indicator
group (focused)
    focused1
    focused2
    focused3
    ...
    focusedX
group (active)
    active1
    active2
    active3
    ...
    activeX

Download installer.py
Right click it, run/open with python

You can configure options by making a new file "settings.json" in the same directory as installer.py
Check "defaults/settings.json" for the default settings which you might want to override

Custom AHK scripts can be placed in directory "custom"

Each time you want to run the macro, right click installer.py and run it