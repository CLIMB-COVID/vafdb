#!/usr/bin/bash
python transform.py $1 | parallel -j ${2:-10} "python vafdb.py create {}"
