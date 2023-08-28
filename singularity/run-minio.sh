#!/bin/bash

source $1
mkdir data
singularity exec \
        --writable-tmpfs \
        --no-mount hostfs \
        --env MINIO_ROOT_USER=$REAXPRO_MINIO_USER \
        --env MINIO_ROOT_PASSWORD=$REAXPRO_MINIO_PASSWORD \
        --mount 'type=bind,source=./data,destination=/data' \
        minio_latest.sif minio server --address $REAXPRO_MINIO_ENDPOINT /data
