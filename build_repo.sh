#!/usr/bin/env bash

cd ..
zip -r fullrepo MultiResetTinder -x MultiResetTinder/.git/**\*
cd MultiResetTinder
rm -rf build
mkdir build
./build.sh
mv ../fullrepo.zip build
