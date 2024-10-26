#!/bin/bash
echo "Current PORT setting: $PORT"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo "Starting gunicorn..."
gunicorn --bind 0.0.0.0:$PORT backend.api_server:app
