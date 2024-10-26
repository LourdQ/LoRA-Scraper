#!/bin/bash
echo "Current directory:"
pwd
echo "Listing backend directory:"
ls -la backend/
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
echo "Copying config template..."
cp backend/config_template.py backend/config.py
echo "Verifying config file:"
ls -la backend/
echo "Starting server..."
python3 backend/api_server.py
