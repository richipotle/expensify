#!/usr/bin/env bash
# Script de build para Render.com
#
# En instancias Free, Render no permite usar "Pre-Deploy Command" (solo
# disponible en planes de pago), así que las migraciones y la creación
# del admin por defecto se ejecutan aquí, como parte del build.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

python manage.py create_default_admin
