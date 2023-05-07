#!/usr/bin/env bash
cd "${0%/*}"
./stop.sh > /dev/null 2>&1
eval "$(conda shell.bash hook)"
conda activate vafdb
cd vafdb/
gunicorn vafdb.wsgi -c gunicorn.conf.py > ../logs/server.log 2>&1 &
celery -A vafdb worker -Q generate_queue --concurrency=5 -l INFO -n GENERATE_NODE@%%h > ../logs/generate.log 2>&1 &
celery -A vafdb worker -Q store_queue --concurrency=1 -l INFO -n STORE_NODE@%%ha3 > ../logs/store.log 2>&1 &
echo "VAFDB started."
