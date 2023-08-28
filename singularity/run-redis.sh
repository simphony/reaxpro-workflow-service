#!/bin/bash

source $1
singularity exec \
    --writable-tmpfs --no-mount hostfs \
    --env-file $1 \
    redis_latest.sif \
    redis-server --port $REAXPRO_REDIS_PORT
