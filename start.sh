#!/bin/bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
cp backend/config_template.py backend/config.py
python3 backend/api_server.py
