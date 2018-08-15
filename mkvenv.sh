#!/usr/bin/env bash
#
# Script to set up a virtual environment with the Python packages needed for
# the code here. Choose which interpreter to run it with as in
#
#   $ ./mkvenv.sh python3.6
#
# With no arguments it defaults to using "python3":
#
#   $ ./mkvenv.sh
#
# The script will:
#
#   1. Create a venv in venv
#   2. Upgrade it to latest pip
#   3. Install the needed packages
#   4. Output the used versions of packages to requirements.txt
#
# You can use git diff to see if the versions have changed.
#
# Afterwards you can activate the virtual environment with:
#
#   $ . venv/bin/activate
#

set -o errexit

if [ $# -eq 0 ]
then
  PY=python3
else
  PY=$1
fi

$PY -m venv venv
. venv/bin/activate
cd venv  # Leave build dir in here...
pip install --upgrade pip
pip install numpy scipy matplotlib jupyter ipython opencv-python
pip list | tee requirements.txt
