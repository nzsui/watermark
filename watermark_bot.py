#!/usr/bin/env python3
"""Auto watermark bot — tempel logo di bagian bawah foto."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp"}

# Lebar logo (setelah crop padding) relatif terhadap foto
DEFAULT_SCALE = 0.22
DEFAULT_MARGIN = 0.03  # jarak dari tepi bawah (~3%)
DEFAULT_OPACITY = 1.0


def load_image(path: Path) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGBA")


def crop_watermark(wm: Image.Image) -> Image.Image:
    """Buang area transparan kosong di sekitar logo."""
    bbox = wm.getbbox()
    if not bbox:
        raise ValueError("Watermark kosong / fully transparent")
    cropped = wm.crop(bbox)
    # padding kecil biar tidak terpotong di tepi
    pad = 8
    canvas = Image.new("RGBA", (cropped.width + pad * 2, cropped.height + pad * 2), (0, 0, 0, 0))
    canvas.paste(cropped, (pad, pad), cropped)
    return canvas


def resize_watermark(wm: Image.Image, base_w: int, scale: float) -> Image.Image:
    target_w = max(40, int(base_w * scale))
    ratio = target_w / wm.width
    target_h = max(20, int(wm.height * ratio))
    return wm.resize((target_w, target_h), Image.Resampling.LANCZOS)


def apply_opacity(wm: Image.Image, opacity: float) -> Image.Image:
    if opacity >= 0.999:
        return wm
    r, g, b, a = wm.split()
    a = a.point(lambda p: int(p * opacity))
    return Image.merge("RGBA", (r, g, b, a))


def place_watermark(
    photo: Image.Image,
    wm: Image.Image,
    *,
    position: str = "bottom-center",
    margin_ratio: float = DEFAULT_MARGIN,
) -> Image.Image:
    pw, ph = photo.size
    ww, wh = wm.size
    margin_x = int(pw * margin_ratio)
    margin_y = int(ph * margin_ratio)

    if position == "bottom-left":
        x = margin_x
    elif position == "bottom-right":
        x = pw - ww - margin_x
    else:  # bottom-center
        x = (pw - ww) // 2

    y = ph - wh - margin_y
    y = max(0, y)
    x = max(0, min(x, pw - ww))

    out = photo.copy()
    out.alpha_composite(wm, (x, y))
    return out


def save_image(img: Image.Image, dst: Path, quality: int) -> None:
    """Simpan dengan format yang sama seperti ekstensi tujuan (HEIC tetap HEIC)."""
    ext = dst.suffix.lower()
    dst.parent.mkdir(parents=True, exist_ok=True)

    if ext in {".heic", ".heif"}:
        rgb = img.convert("RGB")
        rgb.save(dst, format="HEIF", quality=quality)
    elif ext == ".png":
        img.save(dst, format="PNG", optimize=True)
    elif ext == ".webp":
        img.convert("RGB").save(dst, format="WEBP", quality=quality)
    elif ext in {".tif", ".tiff"}:
        img.save(dst, format="TIFF")
    else:
        # jpg / jpeg / bmp / lainnya
        img.convert("RGB").save(dst, quality=quality, optimize=True, progressive=True)


def process_one(
    src: Path,
    dst: Path,
    wm_src: Image.Image,
    *,
    scale: float,
    opacity: float,
    position: str,
    margin: float,
    quality: int,
) -> None:
    photo = load_image(src)
    wm = resize_watermark(wm_src, photo.width, scale)
    wm = apply_opacity(wm, opacity)
    result = place_watermark(photo, wm, position=position, margin_ratio=margin)

    save_image(result, dst, quality)
    print(f"✓ {src.name} → {dst.name}  (wm {wm.size[0]}x{wm.size[1]})")


def collect_images(folder: Path) -> list[Path]:
    files = []
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in SUPPORTED and not p.name.startswith("."):
            files.append(p)
    return files


def main() -> int:
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Auto watermark foto di folder foto/")
    parser.add_argument("--input", "-i", type=Path, default=base / "foto")
    parser.add_argument("--output", "-o", type=Path, default=base / "output")
    parser.add_argument("--watermark", "-w", type=Path, default=base / "watermark.png")
    parser.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="Rasio lebar logo vs foto (default 0.22)")
    parser.add_argument("--opacity", type=float, default=DEFAULT_OPACITY)
    parser.add_argument(
        "--position",
        choices=["bottom-center", "bottom-left", "bottom-right"],
        default="bottom-center",
    )
    parser.add_argument("--margin", type=float, default=DEFAULT_MARGIN)
    parser.add_argument("--quality", type=int, default=92)
    args = parser.parse_args()

    if not args.watermark.exists():
        print(f"Watermark tidak ditemukan: {args.watermark}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"Folder input tidak ditemukan: {args.input}", file=sys.stderr)
        return 1

    images = collect_images(args.input)
    if not images:
        print(f"Tidak ada foto di {args.input}")
        return 1

    wm_src = crop_watermark(load_image(args.watermark))
    print(f"Watermark: {args.watermark.name} → cropped {wm_src.size[0]}x{wm_src.size[1]}")
    print(f"Scale: {args.scale:.0%} lebar foto | posisi: {args.position} | opacity: {args.opacity}")
    print(f"Memproses {len(images)} foto...\n")

    for src in images:
        # Pertahankan ekstensi asli (HEIC tetap .HEIC / .heic)
        out_name = f"{src.stem}_wm{src.suffix}"
        process_one(
            src,
            args.output / out_name,
            wm_src,
            scale=args.scale,
            opacity=args.opacity,
            position=args.position,
            margin=args.margin,
            quality=args.quality,
        )

    print(f"\nSelesai. Hasil di: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
