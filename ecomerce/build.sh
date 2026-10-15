#!/usr/bin/env bash
# Executado pelo Render durante o build/deploy.
set -o errexit

pip install -r requirements.txt
python manage.py migrate --no-input
python manage.py collectstatic --no-input
