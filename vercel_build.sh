#!/bin/bash
set -e  # Exit on error

# Create logs directory
mkdir -p /tmp/vercel/logs

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a /tmp/vercel/logs/build.log
}

log "Starting build process..."

# Install Python dependencies
log "Installing dependencies..."
pip install -r requirements.txt --no-cache-dir 2>&1 | tee -a /tmp/vercel/logs/deps.log

# Verify Django is installed
if ! python -c "import django" 2>/dev/null; then
    log "ERROR: Django is not installed!"
    exit 1
fi

# Set environment variables
export PYTHONPATH=$PWD

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | tee -a /tmp/vercel/logs/collectstatic.log

# Run migrations
log "Running migrations..."
python manage.py migrate --no-input 2>&1 | tee -a /tmp/vercel/logs/migrate.log

# Verify Django can find the settings module
if ! python -c "from django.conf import settings; print(settings.BASE_DIR)" 2>/dev/null; then
    log "ERROR: Django cannot find the settings module!"
    exit 1
fi

log "Build completed successfully!"
