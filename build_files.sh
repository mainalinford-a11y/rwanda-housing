#!/bin/bash
set -e
echo "Building the project..."

# Ensure pip is available and install Python dependencies into a local folder
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --target ./.vercel_python

# Add the installed packages to PYTHONPATH so Django can be imported
export PYTHONPATH="$PWD/.vercel_python:$PYTHONPATH"

# Collect static files to STATIC_ROOT (configured as 'staticfiles' in settings)
python manage.py collectstatic --noinput

echo "Build complete!"
