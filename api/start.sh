#!/bin/bash
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Checking gunicorn installation..."
which gunicorn
gunicorn --version

echo "Current directory structure:"
pwd
ls -la

echo "Starting server..."
cd backend
gunicorn --bind 0.0.0.0:$PORT api_server:app
