#!/bin/sh

# Stop immediately if a command fails
set -e

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start server
echo "Starting Gunicorn server..."
exec gunicorn app.main:app \
    -w 1 \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:${PORT:-8080} \
    --timeout 120