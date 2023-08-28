#!/bin/bash

# Find and kill minio
for pid in $(pgrep -f '/bin/minio'); do
    echo "Killing minio with PID: $pid"
    kill "$pid"
done

# Find and kill redis
for pid in $(pgrep -f 'redis'); do
    echo "Killing redis with PID: $pid"
    kill -9 "$pid"
done
