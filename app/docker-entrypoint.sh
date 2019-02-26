#!/bin/sh
cd /app
python3 manage.py seed
# gunicorn --bind 0.0.0.0:80 --timeout=260 app:app
