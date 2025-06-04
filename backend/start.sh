#!/bin/sh
# This script can be used to run database migrations before starting the app, if any.
# For now, it just starts gunicorn.
# Example for migrations (if using Flask-Migrate):
# flask db upgrade

echo "Starting Gunicorn..."
gunicorn backend.app.main:application --bind 0.0.0.0:$PORT --timeout 120 -w 4
