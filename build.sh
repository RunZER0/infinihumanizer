#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data (required for text analysis)
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Collect static files
python manage.py collectstatic --no-input

# Wait for database to be available (with retry logic for SSL issues)
python manage.py wait_for_db

# Run database migrations
python manage.py migrate
