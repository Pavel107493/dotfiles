#!/usr/bin/env bash
BAT_DIR="/sys/class/power_supply/BAT0"
ICONS_DIR="/home/pavel/.dotfiles/eww/widgets/top-panel/power_modul"
if [ ! -d "$BAT_DIR" ]; then
