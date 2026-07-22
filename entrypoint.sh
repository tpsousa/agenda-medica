#!/bin/sh
set -e

python seed.py
exec python run.py
