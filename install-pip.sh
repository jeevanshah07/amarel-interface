#!/bin/bash
# Exit on error
set -e

module load python/3.8.2
PYTHON="python3"

echo "Checking for Python 3.8.2..."

# Check Python version
if ! command -v $PYTHON >/dev/null 2>&1; then
    echo "❌ Python 3.8 is not installed."
    exit 1
fi

VERSION=$($PYTHON -V 2>&1)

if [[ "$VERSION" != "Python 3.8.2" ]]; then
    echo "⚠️ Python installed, but version is not 3.8.2:"
    echo "Found: $VERSION"
else
    echo "✔ Python 3.8.2 found."
fi

echo
echo "Checking for pip for Python 3.8..."

# Check if pip is installed for this python version
if $PYTHON -m pip --version >/dev/null 2>&1; then
    echo "✔ pip is already installed."
    exit 0
fi

echo "❌ pip not found. Installing pip..."

# Try ensurepip first (works on most systems)
if $PYTHON -m ensurepip --default-pip >/dev/null 2>&1; then
    echo "✔ pip installed using ensurepip."
    exit 0
fi

# Fall back to get-pip.py
echo "Using get-pip.py fallback..."
curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py -o get-pip.py
$PYTHON get-pip.py
rm -f get-pip.py

echo "✔ pip successfully installed."

