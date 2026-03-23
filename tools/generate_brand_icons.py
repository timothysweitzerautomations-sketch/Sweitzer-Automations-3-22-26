#!/usr/bin/env python3
"""
Regenerate Sweitzer Automations 3-22-26 launcher artwork for Windows, Android, and Apple targets.
Requires Pillow: pip install pillow
Run from repo root: python3 tools/generate_brand_icons.py
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print("Install Pillow: python3 -m pip install pillow", file=sys.stderr)
    raise SystemExit(1) from e


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def make_brand_image(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (12, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    margin = max(4, size // 9)
    radius = max(4, size // 12)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        outline=(52, 58, 75, 255),
        width=max(1, size // 64),
        fill=(21, 28, 36, 255),
    )
    stripe_h = max(3, size // 16)
    draw.rectangle(
        [
            margin + size // 16,
            margin + size // 14,
            size - margin - size // 16,
            margin + size // 14 + stripe_h,
        ],
        fill=(34, 197, 94, 255),
    )
    font_size = int(size * 0.42)
    font = None
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ):
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
    text = "S"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) // 2
    ty = (size - th) // 2 - size // 32
    draw.text((tx, ty), text, fill=(232, 237, 245, 255), font=font)
    return img


def write_windows_ico(root: Path) -> None:
    out = root / "windows" / "icon.ico"
    out.parent.mkdir(parents=True, exist_ok=True)
    base = make_brand_image(256)
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = [base.resize(s, Image.Resampling.LANCZOS) for s in sizes]
    images[0].save(out, format="ICO", sizes=[(s[0], s[1]) for s in sizes])
    print("Wrote", out)


def write_android_mipmaps(root: Path) -> None:
    sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }
    base = root / "android" / "app" / "src" / "main" / "res"
    for folder, px in sizes.items():
        d = base / folder
        d.mkdir(parents=True, exist_ok=True)
        im = make_brand_image(px)
        im.save(d / "ic_launcher.png", format="PNG")
        im.save(d / "ic_launcher_round.png", format="PNG")
        print("Wrote", d / "ic_launcher.png")


def write_apple_appicon(root: Path) -> None:
    appicon = (
        root
        / "apple"
        / "SweitzerAutomations"
        / "SweitzerAutomations"
        / "Assets.xcassets"
        / "AppIcon.appiconset"
    )
    appicon.mkdir(parents=True, exist_ok=True)
    (appicon.parent / "Contents.json").write_text(
        '{"info":{"author":"xcode","version":1}}',
        encoding="utf-8",
    )
    make_brand_image(1024).save(appicon / "AppIcon-1024.png", format="PNG")
    make_brand_image(512).save(appicon / "AppIcon-mac-512.png", format="PNG")
    make_brand_image(1024).save(appicon / "AppIcon-mac-1024.png", format="PNG")
    contents = """{
  "images" : [
    {
      "filename" : "AppIcon-1024.png",
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024"
    },
    {
      "filename" : "AppIcon-mac-512.png",
      "idiom" : "mac",
      "scale" : "1x",
      "size" : "512x512"
    },
    {
      "filename" : "AppIcon-mac-1024.png",
      "idiom" : "mac",
      "scale" : "2x",
      "size" : "512x512"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
"""
    (appicon / "Contents.json").write_text(contents, encoding="utf-8")
    print("Wrote", appicon)


def main() -> None:
    root = repo_root()
    write_windows_ico(root)
    write_android_mipmaps(root)
    write_apple_appicon(root)
    print("Brand icons regenerated under windows/, android/, and apple/.")


if __name__ == "__main__":
    main()
