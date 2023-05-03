#!/usr/bin/env bash
cd "${0%/*}"
mkdir -p logs
eval "$(conda shell.bash hook)"
conda activate vafdb
pip install ./client/
python vafdb/manage.py makemigrations
python vafdb/manage.py migrate
echo "VAFDB setup complete."