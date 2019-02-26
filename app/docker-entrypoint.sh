#!/bin/sh
cd /app
uname
uname -r
uname --m
ls -l
./signpass -p PhippsSampleGeneric.pass -o Pass Files/test.pkpass
# python3 manage.py seed
# gunicorn --bind 0.0.0.0:80 --timeout=260 app:app
