#!/bin/bash
set -e  # Exit on error

# Create logs directory
mkdir -p /tmp/vercel/logs

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a /tmp/vercel/logs/build.log
}

log "Starting build process..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:/var/task"

# Install Python dependencies
log "Installing dependencies..."
pip install -r requirements.txt

# Create static files directory if it doesn't exist
mkdir -p staticfiles

# Set DJANGO_SETTINGS_MODULE if not set
if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    export DJANGO_SETTINGS_MODULE="app.settings"
fi

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 | tee -a /tmp/vercel/logs/collectstatic.log

# Run migrations
log "Running migrations..."
python manage.py migrate --no-input 2>&1 | tee -a /tmp/vercel/logs/migrate.log

# Create cache directory for whitenoise
mkdir -p .cache

# Create vercel.json if it doesn't exist
if [ ! -f vercel.json ]; then
    echo '{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "vercel_build.sh",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "staticfiles"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}' > vercel.json
fi

log "Build completed successfully!"

# Print environment info for debugging
echo "----- Environment Info -----"
python -c "import sys; print('Python version:', sys.version)"
python -c "import django; print('Django version:', django.get_version())"
pwd
ls -la
