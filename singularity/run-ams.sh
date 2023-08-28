#!/bin/bash

source $1
singularity run \
        --no-mount hostfs --no-home \
        --writable-tmpfs \
        --env-file $1 \
        --env REAXPRO_WORKER_NAME=simphony-ams \
        --env REAXPRO_WRAPPER_NAME=osp.wrappers.simams.simams_session:SimamsSession \
        --env APP_MODE=worker \
        --pwd $TMPDIR \
        -B ${AMSHOME} \
        "fastapi-celery_${APP_VERSION}-singularity-production.sif"
