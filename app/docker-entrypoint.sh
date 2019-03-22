#!/bin/sh
cd /app
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
gunicorn --bind 0.0.0.0:80 --timeout=260 app:app
