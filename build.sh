#!/usr/bin/env bash
# Exécute les migrations à chaque déploiement Render

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting server..."
