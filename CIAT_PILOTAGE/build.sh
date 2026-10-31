#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_demo
python manage.py create_jury_user
