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

# Make start script executable
chmod +x start.sh

echo "✅ Build complete! Database connection and migrations will run in start.sh"
