#!/bin/bash

./run-headworker.sh $1 &
./run-catalytic.sh $1 &
./run-ams.sh $1 &
./run-zacros.sh $1 &
./run-fastapi.sh $1 &
