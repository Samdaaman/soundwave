#!/bin/bash

while :
do
    echo $$ > /opt/ping
    date >> /opt/ping
    echo hello world | nc -lvp 1337
    sleep 1
done
