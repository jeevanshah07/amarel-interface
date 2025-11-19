#!/bin/bash
set -e  # exit immediately if a command fails
module load python/3.8.2

cd "/scratch/$USER"

# Check if pip for Python 3.8.2 is installed
if ! python3 -m pip --version &>/dev/null; then
    # Install ensurepip if needed
    python3 -m ensurepip --upgrade
fi

# Install pipenv silently if not installed
if ! pip show pipenv &>/dev/null; then
    python3 -m pip install --quiet pipenv
fi

# Download the build script
wget -q https://raw.githubusercontent.com/jeevanshah07/amarel-interface/main/build-pipfile.py -O build-pipfile.py

# Run the script to generate the Pipfile (suppress its output)
python3 build-pipfile.py "$1" --output Pipfile > /dev/null

# Install packages from Pipfile using pipenv
pipenv install --deploy --ignore-pipfile > /dev/null

# Run the target Python file and only show its output
pipenv run python3 "$1"
