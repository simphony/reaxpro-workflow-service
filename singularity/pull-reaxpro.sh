#!/bin/bash

source $1
singularity pull \
    "docker://registry.gitlab.cc-asp.fraunhofer.de/reaxpro/fastapi-celery:${APP_VERSION}-singularity-production"
