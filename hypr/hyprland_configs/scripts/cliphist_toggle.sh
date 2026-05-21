#!/bin/bash
if pgrep -x wofi > /dev/null; then
    pkill -x wofi
else
    cliphist list | wofi --dmenu | cliphist decode | wl-copy
fi
