#!/bin/bash

rm -rf tmp
mkdir tmp
rsync sharpie_settings.json tmp
rsync dist/setup.py tmp
cd tmp
python3 setup.py
cd ..
