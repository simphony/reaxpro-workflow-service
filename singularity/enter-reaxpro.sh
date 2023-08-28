#!/bin/bash

source $1
singularity exec \
        --no-mount hostfs \
        --fakeroot \
        --writable-tmpfs \
        --env-file $1 \
        -B ${AMSHOME} \
        "fastapi-celery_${APP_VERSION}-singularity-production.sif" bash
