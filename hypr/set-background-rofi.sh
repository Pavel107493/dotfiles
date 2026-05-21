#!/usr/bin/env sh

WALLPAPERS_DIR="$HOME/.Wallpapers"
TARGET_DIR="$HOME/.config"
SYMLINK_NAME="background"

# Проверка папки с обоями
[ ! -d "$WALLPAPERS_DIR" ] && {
    echo "Error $WALLPAPERS_DIR not found"
    exit 1
}

# Выбор обоев через rofi с превьюшками
IMAGE=$(
    find "$WALLPAPERS_DIR" -type f \( \
        -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.gif' -o -iname '*.webp' \
    \) | while IFS= read -r file; do
        printf '%s\0icon\x1fthumbnail://%s\n' "$file" "$file"
    done | rofi -dmenu \
        -i \
        -show-icons \
        -p "Wallpaper" \
        -theme-str '
            window {
                height: 60%;
            }

            listview {
                columns: 4;
                lines: 3;
            }
            entry {
                enabled: false;
            }
            element {
                orientation: vertical;
                padding: 0px;
            }

            element-icon {
                size: 110px;
            }

            element-text {
                enabled: false;
            }
        '
)

# Если отменено — выход
[ -z "$IMAGE" ] && {
    echo "Error"
    exit 0
}

# Проверка папки
case "$IMAGE" in
    "$WALLPAPERS_DIR"/*) ;;
    *)
        echo "Error $WALLPAPERS_DIR!"
        exit 1
        ;;
esac

# Симлинк
SYMLINK_PATH="$TARGET_DIR/$SYMLINK_NAME"
[ -L "$SYMLINK_PATH" ] && rm "$SYMLINK_PATH"
ln -s "$IMAGE" "$SYMLINK_PATH"

ICON=/home/pavel/.config/hypr/logo.png
TITLE="The wallpaper has been changed"
MESSAGE="The wallpaper has been changed"

zenity --notification \
    --window-icon="$ICON" \
    --text="$MESSAGE"

# sleep 0.5

# Смена обоев в swww
awww img "$IMAGE" \
    --transition-type wipe \
    --transition-duration 1.7

sleep 0.5

echo "Готово: $SYMLINK_PATH → $(basename "$IMAGE")"

# Обновление темы
sleep 0.5
python ~/.config/hypr/color_script/theme_icon_text_color_swicher.py

sleep 0.5
python ~/.config/hypr/color_script/alacritty_theme_generator.py
pkill -SIGUSR2 waybar
eww reload
