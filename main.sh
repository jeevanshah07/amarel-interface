#!/bin/bash
module load python/3.8.2

cd "/scratch/$USER"

if ! python3 -m pip --version &>/dev/null; then
    python3 -m ensurepip --upgrade
fi

python3 -m pip install --quiet pipenv

python3 build_pipfile.py $1

python3 -m pipenv --python 3.8 > /dev/null

python3 -m pipenv install > /dev/null

python3 -m pipenv run python3 $1
