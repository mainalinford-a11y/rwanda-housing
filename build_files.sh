#!/bin/bash
set -e
echo "Building the project..."

# Create and activate a virtual environment for isolated builds
# Create a virtual environment and activate it (POSIX-compatible)
python -m venv .venv
# Use POSIX-compatible activation so `/bin/sh` can run it on Vercel
. .venv/bin/activate

# Upgrade pip and install only minimal dependencies required for collectstatic
pip install --upgrade pip
# Install lightweight runtime packages needed to run Django's collectstatic
# Avoid installing the entire requirements list to keep build fast and reliable on Vercel
pip install --no-cache-dir Django==5.2.8 whitenoise==6.5.0 pillow

# Ensure project root is on PYTHONPATH so Django settings are discoverable
export PYTHONPATH="$PWD:$PYTHONPATH"

# Collect static files to STATIC_ROOT (configured as 'staticfiles' in settings)
python manage.py collectstatic --noinput

echo "Build complete!"
