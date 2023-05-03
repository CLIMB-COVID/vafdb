#!/usr/bin/env bash
cd "${0%/*}"
VAFDB_PIDS=`cat logs/vafdb.pids`
echo "Stopping PIDs: ${VAFDB_PIDS}"
kill $VAFDB_PIDS
echo "VAFDB stopped."
