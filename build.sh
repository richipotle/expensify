#!/usr/bin/env bash
# Script de build para Render.com
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
