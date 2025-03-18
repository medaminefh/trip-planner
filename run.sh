#!/bin/bash
cd trip-planner-frontend && npm install && npm run build && cd ..
cp -r trip-planner-frontend/dist/* .
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn --bind 0.0.0.0:8000 trip_planner.wsgi:application