#!/bin/bash

./run-redis.sh $1 &
./run-minio.sh $1 &
