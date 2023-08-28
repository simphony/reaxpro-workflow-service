#!/bin/bash

./run-databases.sh $1 &
./run-reaxpro.sh $1 &
