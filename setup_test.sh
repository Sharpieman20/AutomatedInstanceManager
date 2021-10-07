#!/bin/bash

rm -rf test
mkdir test
rsync dist/setup.py test
cd test
python3 setup.py
cd ..
