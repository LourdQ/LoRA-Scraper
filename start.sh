#!/bin/bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python backend/api_server.py
