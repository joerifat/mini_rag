#!/bin/bash
set -e 

echo "Running database migrations..."

cd /app/models/schemas/minirag
alembic upgrade head

cd /app