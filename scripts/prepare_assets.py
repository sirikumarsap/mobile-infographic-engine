#!/usr/bin/env python3
"""Crop, clean, and resize a screenshot or table image for the visual section.

Usage:
    python3 prepare_assets.py infographic/assets/grid.png infographic/assets/prepared/grid.png
    python3 prepare_assets.py in.png out.png --max-width 960

Requires Pillow:  pip install pillow
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageOps


def trim_border(img: Image.Image, tolerance: int = 16) -> Image.Image:
    """Remove uniform margins, using the top-left pixel as the background color."""
    background = Image.new("RGB", img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, background).convert("L")
    bbox = diff.point(lambda p: 255 if p > tolerance else 0).getbbox()
    return img.crop(bbox) if bbox else img


def prepare(src: Path, dst: Path, max_width: int) -> None:
    img = Image.open(src).convert("RGB")
    original = img.size
    img = trim_border(img)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Sharpness(img).enhance(1.3)
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, round(img.height * ratio)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, optimize=True)
    print(f"{src}: {original} -> {img.size}, saved to {dst}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare an image asset.")
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    parser.add_argument("--max-width", type=int, default=960,
                        help="Visual section width after 40px margins and card padding")
    args = parser.parse_args()
    prepare(args.src, args.dst, args.max_width)


if __name__ == "__main__":
    main()