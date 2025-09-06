#!/usr/bin/env bash
set -e
TIMEOUT=${1:-120}
bluetoothctl <<EOF
power on
agent NoInputNoOutput
default-agent
system-alias "Nora Sofa"
disconnect
discoverable on
pairable on
EOF
sleep "$TIMEOUT"
bluetoothctl <<EOF
discoverable off
pairable off
scan off
EOF