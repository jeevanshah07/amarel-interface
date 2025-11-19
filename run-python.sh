#!/bin/bash
chmod 777 install-pip.sh
./install-pip.sh

cd /scratch/$USER
pipenv shell

python3 /home/$USER/amarel-interface/build-pipfile.py "$1" --output Pipfile
pipenv install

python3 "$1"
