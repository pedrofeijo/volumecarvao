#!/bin/bash
rm -fr CMakeCache.txt CMakeFiles/ cmake_install.cmake  LICENSE licenses/ Makefile pptk/ setup.py build/ dist/ pptk.egg-info/
cmake -G "Unix Makefiles" ..
make -j4
python3 setup.py bdist_wheel
echo "+95'12" | sudo -S pip3 uninstall pptk -y 2> /dev/null # remove pptk antigo
echo "+95'12" | sudo -S pip3 install dist/*.whl 2> /dev/null # instala novo pptk
#pip uninstall -y pptk
#pip install dist/*
