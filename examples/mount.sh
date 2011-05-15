#!/bin/sh
mkdir -p mountdir

# Check if python2 exists else fallback to python
PYTHON=$(which python2)
if [ $? -ne 0 ]; then
    PYTHON=python
fi

$PYTHON main.py -f mountdir
