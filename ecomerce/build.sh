#!/usr/bin/env bash
# Rodado pelo Render a cada build/deploy.
# O Render executa com o Root Directory em ecomerce/, entao o
# requirements.txt fica um nivel acima.
set -o errexit

pip install -r ../requirements.txt
python manage.py collectstatic --no-input