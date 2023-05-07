#!/usr/bin/env bash
cd "${0%/*}"
mkdir -p logs
eval "$(conda shell.bash hook)"
conda env create -f environment.yml
conda activate vafdb
cd vafdb
python manage.py makemigrations
python manage.py migrate
cd ..
pip install ./client/
echo "VAFDB setup complete."