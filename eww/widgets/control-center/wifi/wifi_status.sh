#!/bin/bash

if [ "$(nmcli radio wifi)" = "disabled" ]; then
  echo "Off"
  exit
fi

ssid=$(nmcli -t -f active,ssid dev wifi | grep "^yes" | cut -d: -f2)

if [ -z "$ssid" ]; then
  echo "No net"
elif [ ${#ssid} -gt 8 ]; then
  echo "${ssid:0:8}…"
else
  echo "$ssid"
fi
