#!/bin/bash

source $1
singularity run \
        --no-mount hostfs --no-home \
        --writable-tmpfs \
        --env-file $1 \
        --env REAXPRO_WORKER_NAME=simphony-workflows \
        --env APP_MODE=worker \
        --pwd $TMPDIR \
        "fastapi-celery_${APP_VERSION}-singularity-production.sif"
