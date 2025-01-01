#!/bin/bash
source venv/bin/activate
sudo env PATH=$PATH VIRTUAL_ENV=$VIRTUAL_ENV python src/app.py
