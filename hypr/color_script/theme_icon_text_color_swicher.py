#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import numpy as np
from pathlib import Path
from PIL import Image


def get_wallpaper_path():
    """hyprpaper > swww > ~/.config/background."""
    try:
        r = subprocess.run(['hyprctl', 'hyprpaper', 'listloaded'], capture_output=True, text=True)
        if r.returncode == 0:
            for line in r.stdout.strip().split('\n'):
                if ',' in line and any(ext in line.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    path = line.split(',')[-1].strip().strip('"')
                    path = os.path.expanduser(path)
                    if os.path.exists(path):
                        return path
    except Exception:
        pass

    try:
        r = subprocess.run(['swww', 'query'], capture_output=True, text=True)
        if r.returncode == 0:
            data = json.loads(r.stdout)
            if data:
                return data[0]['path']
    except Exception:
        pass

    bg_link = Path.home() / '.config' / 'background'
    if bg_link.exists():
        try:
            return str(bg_link.resolve())
        except Exception:
            pass
    return None


def simple_kmeans(data, k=8, max_iter=20):
    """KMeans без sklearn (numpy-only)."""
    data = data.astype(np.float32)
    centroids = data[np.random.choice(len(data), k, replace=False)]
    for _ in range(max_iter):
        labels = np.argmin(np.linalg.norm(data[:, None] - centroids[None], axis=2), axis=1)
        new_centroids = np.array([
            data[labels == i].mean(axis=0) if np.any(labels == i) else centroids[i]
            for i in range(k)
        ])
        if np.allclose(centroids, new_centroids):
            break
        centroids = new_centroids
    return np.clip(centroids, 0, 255).astype(int)


def extract_accent_color(image_path, lighten_factor=1.2):
    """KMeans → акцентный цвет (насыщенный/яркий)."""
    try:
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((150, 150))
        data = np.array(img).reshape((-1, 3))

        colors = simple_kmeans(data, k=8)

        brightness = np.sum(colors, axis=1)
        saturation = np.ptp(colors, axis=1)
        gray_mask = saturation > 30
        bright_mask = (brightness > 400) & gray_mask

        if np.any(bright_mask):
            candidates_idx = np.where(bright_mask)[0]
            best_idx = candidates_idx[np.argmax(saturation[candidates_idx] * brightness[candidates_idx] / 765)]
        else:
            best_idx = np.argmax(saturation * brightness / 765)

        r, g, b = colors[best_idx]
        accent = (
            min(255, int(r * lighten_factor)),
            min(255, int(g * lighten_factor)),
            min(255, int(b * lighten_factor)),
        )

        hex_str = f'{accent[0]:02X}{accent[1]:02X}{accent[2]:02X}'
        return hex_str, colors
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return None, None


def make_itc2(accent_hex, darken_factor=0.75):
    """Чуть затемнённый акцент для itc2."""
    r = int(accent_hex[0:2], 16)
    g = int(accent_hex[2:4], 16)
    b = int(accent_hex[4:6], 16)
    rr = int(r * darken_factor)
    gg = int(g * darken_factor)
    bb = int(b * darken_factor)
    return f'{rr:02x}{gg:02x}{bb:02x}'


def make_bg_steps(accent_hex, steps=3):
    """
    Генерирует N промежуточных фоновых цветов от очень тёмного к немного светлее,
    сохраняя оттенок акцента. Возвращает список hex-строк от bg1 (темнее) к bgN (светлее).
    """
    r = int(accent_hex[0:2], 16)
    g = int(accent_hex[2:4], 16)
    b = int(accent_hex[4:6], 16)

    # Диапазон множителей яркости: bg1 совсем тёмный, bgN чуть посветлее
    # Пример для 3 шагов: 0.07, 0.12, 0.18
    min_factor = 0.07
    max_factor = 0.20
    factors = [min_factor + (max_factor - min_factor) * i / (steps - 1) for i in range(steps)]

    result = []
    for factor in factors:
        # Немного разный множитель по каналам для тёплого/холодного оттенка
        rr = min(255, int(r * factor * 1.05))
        gg = min(255, int(g * factor * 0.95))
        bb = min(255, int(b * factor * 1.00))
        result.append(f'{rr:02x}{gg:02x}{bb:02x}')

    return result  # [bg1_hex, bg2_hex, bg3_hex, ...]


def write_colors(cfg_dir, accent_hex, itc2_hex, bg_hexes):
    """Записывает все файлы с цветами."""
    n = len(bg_hexes)
    bg_vars = {f'bg{i+1}': bg_hexes[i] for i in range(n)}

    # --- color.conf (Hyprland) ---
    with open(cfg_dir / 'color.conf', 'w') as f:
        f.write(f'$itc = rgb({accent_hex})\n')
        f.write(f'$itc2 = rgb({itc2_hex})\n')
        for name, hex_val in bg_vars.items():
            f.write(f'${name} = rgb({hex_val})\n')

    # --- color.scss (eww) ---
    with open(cfg_dir / 'color.scss', 'w') as f:
        f.write(f'$itc: #{accent_hex};\n')
        f.write(f'$itc2: #{itc2_hex};\n')
        for name, hex_val in bg_vars.items():
            f.write(f'${name}: #{hex_val};\n')

    # --- color.css (waybar/wofi) ---
    with open(cfg_dir / 'color.css', 'w') as f:
        f.write(f'@define-color itc #{accent_hex};\n')
        f.write(f'@define-color itc2 #{itc2_hex};\n')
        for name, hex_val in bg_vars.items():
            f.write(f'@define-color {name} #{hex_val};\n')

    # --- kitty (term_acent.conf) --- без изменений
    with open(cfg_dir / 'term_acent.conf', 'w') as f:
        f.write(f'color2 #{accent_hex}\n')

    # --- Alacritty (term_acent_alacritty_temp.toml) --- без изменений
    with open(cfg_dir / 'term_acent_alacritty_temp.toml', 'w') as f:
        f.write(f'accent = "#{accent_hex}"\n')


def main():
    wallpaper = get_wallpaper_path()
    if not wallpaper:
        print("Обои не найдены!", file=sys.stderr)
        sys.exit(1)

    print(f"Обои: {wallpaper}")
    accent_hex, all_colors = extract_accent_color(wallpaper, lighten_factor=1.2)
    if not accent_hex:
        sys.exit(1)

    bg_hexes = make_bg_steps(accent_hex, steps=4)  # bg1, bg2, bg3
    itc2_hex = make_itc2(accent_hex, darken_factor=0.75)

    cfg_dir = Path.home() / '.config' / 'hypr' / 'colors'
    cfg_dir.mkdir(parents=True, exist_ok=True)

    write_colors(cfg_dir, accent_hex, itc2_hex, bg_hexes)

    print(f"🎨 Акцентный цвет: #{accent_hex}")
    print(f"🎨 itc2:           #{itc2_hex}")
    for i, hex_val in enumerate(bg_hexes, 1):
        print(f"🌑 bg{i}:            #{hex_val}")

    print("✅ Записано:")
    for fname in [
        'color.conf',
        'color.scss',
        'color.css',
        'term_acent.conf',
        'term_acent_alacritty_temp.toml',
    ]:
        print(f"   {cfg_dir / fname}")

    print("\n8 доминантных цветов:")
    for i, (r, g, b) in enumerate(all_colors):
        hex_c = f"{r:02X}{g:02X}{b:02X}"
        print(f"  {i}: #{hex_c}")

    try:
        subprocess.run(['hyprctl', 'reload'], check=False)
        print("🔄 Hyprland перезагружен!")
    except Exception:
        pass


if __name__ == "__main__":
    main()
