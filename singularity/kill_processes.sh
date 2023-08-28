#!/bin/bash

# Find and kill all Celery worker processes
for pid in $(pgrep -f 'osp.app.tasks:celery worker'); do
    echo "Killing worker with PID: $pid"
    kill "$pid"
done

# Find and kill fastapi
for pid in $(pgrep -f 'osp.app.main'); do
    echo "Killing fastapi process with PID: $pid"
    kill "$pid"
done
