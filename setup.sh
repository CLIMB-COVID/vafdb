#!/usr/bin/env bash
cd "${0%/*}"
mkdir -p logs
eval "$(conda shell.bash hook)"
conda activate vafdb
pip install ./client/
cd vafdb
python manage.py makemigrations
python manage.py migrate
echo "VAFDB setup complete."