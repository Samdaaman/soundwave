#!/bin/bash

docker build -t test_box .
exec docker run -it --network host test_box