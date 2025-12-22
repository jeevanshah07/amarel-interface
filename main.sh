#!/bin/bash
module load python/3.8.2

cd "/scratch/$USER"

# Check if pip for Python 3.8.2 is installed
if ! python3 -m pip --version &>/dev/null; then
    # Install ensurepip if needed
    python3 -m ensurepip --upgrade
fi

python3 -m pip install --quiet pipenv

python3 build_pipfile.py $1

python3 -m pipenv --python 3.8 > /dev/null

# Install packages from Pipfile using pipenv
python3 -m pipenv install > /dev/null

# Run the target Python file and only show its output
python3 -m pipenv run python3 $1
