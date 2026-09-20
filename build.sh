#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
chmod +x start.sh

echo "Build complete. Migrations run in start.sh."
