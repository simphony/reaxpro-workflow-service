#!/bin/bash

if [ "$APP_MODE" == "worker" ]; then
  # Start the Celery worker
  $PYTHON_BIN -m celery -A osp.app.tasks:celery worker -Q $REAXPRO_WORKER_NAME -n $REAXPRO_WORKER_NAME --concurrency $REAXPRO_WORKER_CONCURRENCY
elif [ "$APP_MODE" == "server" ]; then
  # Start the uvicorn server
  $PYTHON_BIN -m osp.app.main
else
  # Invalid APP_MODE value
  echo "Invalid APP_MODE value: $APP_MODE"
fi
