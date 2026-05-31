#!/usr/bin/env sh
if pgrep -x wofi > /dev/null 2>&1; then
    pkill -x wofi
    exit 0
fi

SELECTED=$(ls "$HOME/.config/xray/json/" | wofi --dmenu --prompt "Выбери конфиг:")

[ -z "$SELECTED" ] && exit 0

[ -L "$HOME/.config/xray/config.json" ] && rm "$HOME/.config/xray/config.json"
ln -s "$HOME/.config/xray/json/$SELECTED" "$HOME/.config/xray/config.json"
sleep 0.3

REAL_CONFIG=$(readlink -f ~/.config/xray/config.json)
CONFIG_NAME=$(basename "$REAL_CONFIG")

pkill xray
pkill xray

zenity --notification --text="$CONFIG_NAME" &

xray run -c "$HOME/.config/xray/json/$SELECTED"
