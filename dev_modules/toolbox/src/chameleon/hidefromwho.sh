#!/bin/bash

addr=::1; xxd -p < /var/run/utmp | tr -d '\n' | sed -e 'H;${x;s/0a/\n/g;s/^\n//;p;};d' | grep -v `echo -n $addr | xxd -p | tr -d '\n'` | sed -e 'H;${x;s/\n/0a/g;s/^0a//;p;};d' | xxd -r -p > /tmp/utmp.new; sudo mv -f /tmp/utmp.new /var/run/utmp
