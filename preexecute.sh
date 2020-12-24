#!/usr/bin/env bash
virtualenv venv -p python3.8
. ./venv/bin/activate
pip install -r requirements.txt
