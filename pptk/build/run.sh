#!/bin/bash
cmake -G "Unix Makefiles" ..
make -j4
python3 setup.py bdist_wheel
pip uninstall pptk -y # remove pptk antigo
pip install dist/*.whl # instala novo pptk
