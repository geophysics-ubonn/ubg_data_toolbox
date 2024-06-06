#!/bin/bash
# delete and recreate the virtualenv "crtomo"
source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

rmvirtualenv data
mkvirtualenv --python /usr/bin/python3 data
pip install -r requirements.txt
pip install .
