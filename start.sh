#!/bin/bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
gunicorn --bind 0.0.0.0:$PORT backend.api_server:app
