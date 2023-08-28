#!/bin/bash

source $1
singularity run \
        --no-mount hostfs --no-home \
        --writable-tmpfs \
        --env-file $1 \
        --env APP_MODE=server \
        --pwd $TMPDIR \
        "fastapi-celery_${APP_VERSION}-singularity-production.sif"
