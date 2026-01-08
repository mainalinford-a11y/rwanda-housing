#!/bin/bash
set -e
echo "Building the project..."

# Create and activate a virtual environment for isolated builds
python -m venv .venv
source .venv/bin/activate

# Upgrade pip and install project dependencies into the venv
pip install --upgrade pip
pip install -r requirements.txt

# Ensure project root is on PYTHONPATH so Django settings are discoverable
export PYTHONPATH="$PWD:$PYTHONPATH"

# Collect static files to STATIC_ROOT (configured as 'staticfiles' in settings)
python manage.py collectstatic --noinput

echo "Build complete!"
