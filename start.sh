#!/bin/bash


set -e 

cd /app/cctv-app/

uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4