#!/bin/bash

# Проверяем статус Wi-Fi через nmcli
# Команда возвращает 'enabled' или 'disabled'
wifi_status=$(nmcli radio wifi)

if [ "$wifi_status" = "disabled" ]; then
    echo "Wi-Fi выключен. Включаю..."
    nmcli radio wifi on
else
    echo "Wi-Fi уже включен."
fi

