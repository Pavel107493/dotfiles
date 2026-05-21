#!/usr/bin/env sh

WALLPAPERS_DIR="$HOME/.Wallpapers"
TARGET_DIR="$HOME/.config"
SYMLINK_NAME="background"

# Проверка папки с обоями
[ ! -d "$WALLPAPERS_DIR" ] && {
    echo "Error $WALLPAPERS_DIR not found"
    exit 1
}

# Стандартный диалог выбора файла
IMAGE=$(zenity --file-selection \
    --title="$WALLPAPERS_DIR" \
    --filename="$WALLPAPERS_DIR/") #\
#    --file-filter="pic | *.jpg *.jpeg *.png *.webp")

# Если отменено — выход
[ $? -ne 0 ] || [ -z "$IMAGE" ] && {
    echo "Error"
    exit 0
}

# Проверка папки
case "$IMAGE" in
    "$WALLPAPERS_DIR"/*) ;;  # OK
    *) 
        echo "Error $WALLPAPERS_DIR!"
        exit 1
        ;;
esac

# Симлинк
SYMLINK_PATH="$TARGET_DIR/$SYMLINK_NAME"
[ -L "$SYMLINK_PATH" ] && rm "$SYMLINK_PATH"
ln -s "$IMAGE" "$SYMLINK_PATH"

# ICON=/home/pavel/$IMAGE
ICON=/home/pavel/.config/hypr/logo.png
TITLE="The wallpaper has been changed"
MESSAGE="The wallpaper has been changed"

zenity --notification \
    --window-icon="/home/pavel/.config/hypr/logo.png" \
    --text="$MESSAGE"

sleep 0.5
# Смена обоев в swww
awww img "$IMAGE" --transition-type wipe --transition-duration 1.7 

# Перезапуск hyprpaper
#pkill hyprpaper 2>/dev/null
sleep 0.5
#hyprpaper &

echo "Готово: $SYMLINK_PATH → $(basename "$IMAGE") | Hyprpaper restarted"

#Запуск theme_icon_text_color_swicher.py
sleep 0.5
python ~/.config/hypr/color_script/theme_icon_text_color_swicher.py
sleep 0.5
python ~/.config/hypr/color_script/alacritty_theme_generator.py & pkill -SIGUSR2 waybar
# sleep 0.2



