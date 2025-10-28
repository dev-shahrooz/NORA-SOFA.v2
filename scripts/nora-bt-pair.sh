#!/usr/bin/env bash
set -e
bluetoothctl <<EOF
power on
system-alias "Nora Sofa"
disconnect
discoverable on
pairable on
EOF
