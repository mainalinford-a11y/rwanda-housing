#!/bin/bash
echo "Building the project..."

# Collect static files
python manage.py collectstatic --noinput

echo "Build complete!"
