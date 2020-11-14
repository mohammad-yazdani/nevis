#!/bin/bash

PID=$(ps -A | grep kaldi | awk '{print $1}')
if [[ -z ${PID} ]]; then
    exit
fi

echo "Killing $PID"
sudo kill -9 ${PID}

TARGET_PORT="8000"
PORT_TO_PID=$(sudo netstat -ntlp | grep LISTEN | grep ${TARGET_PORT} | awk '{print $7}' | awk -F/ '{print $1}')
if [[ -z ${PORT_TO_PID} ]]; then
    exit
fi

echo "PID taking PORT $TARGET_PORT"
ps -A | grep ${PORT_TO_PID}
sudo kill -9 ${PORT_TO_PID}


