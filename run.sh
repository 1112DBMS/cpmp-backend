#!/bin/bash
gunicorn3 --bind 0.0.0.0:56100 run:app
