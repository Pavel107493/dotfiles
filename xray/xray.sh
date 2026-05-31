#!/bin/bash

pkill xray
sleep 0.5

REAL_CONFIG=$(readlink -f ~/.config/xray/config.json)
CONFIG_NAME=$(basename "$REAL_CONFIG")

zenity --notification --text="$CONFIG_NAME" &

/usr/bin/xray run -c ~/.config/xray/config.json
