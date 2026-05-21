#!/usr/bin/env python3
import os
import re


def read_accent_color(path: str) -> str:
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return "#00F9FF"
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("accent ="):
                if (m := re.search(r'["\']([^"\']+)["\']', line)):
                    if (col := m.group(1)).startswith("#"):
                        return col.upper()
    return "#00F9FF"


def generate_dark_alacritty_toml(accent: str) -> str:
    acc = accent.upper()
    return f'''[colors.primary]

[colors.normal]
green = '{acc}'

[colors.bright]
green = '{acc}'
'''


def main():
    accent = read_accent_color("~/.config/hypr/colors/term_acent_alacritty_temp.toml")
    out = os.path.expanduser("~/.config/hypr/colors/term_alacritty.toml")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write(generate_dark_alacritty_toml(accent))

    print(f"Alacritty theme regenerated using accent: {accent} → {out}")


if __name__ == "__main__":
    main()
