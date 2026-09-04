#!/usr/bin/env python3
"""Crop out horizontal black letterbox bars from portfolio images.

See detect_black_bars.py for the detection logic (flat AND dark rows only,
bridging short embedded-overlay interruptions) — this only adds the actual
crop + backup step. Originals are backed up under
scripts/_backup-before-crop/<same relative path> before being overwritten
in place, so the crop is easy to inspect/undo.
"""
from pathlib import Path
import shutil
import numpy as np
from PIL import Image

SITE_ROOT = Path(__file__).resolve().parents[1]
ROOT = SITE_ROOT / "src/assets/images/portfolio"
BACKUP_ROOT = Path(__file__).resolve().parent / "_backup-before-crop"
FOLDERS = ["carnet", "bd-et-illustrations", "collaboration-creation-contenu", "dessin-live"]

DARK_THRESH = 10
FLAT_THRESH = 5
GAP_TOLERANCE = 20
MIN_BAR_PX = 6
MAX_BAR_FRACTION = 0.35


def band_height(is_bar, height, from_top):
    idxs = list(range(height)) if from_top else list(range(height - 1, -1, -1))
    n = len(idxs)
    pos = 0
    boundary = 0
    while pos < n:
        if is_bar[idxs[pos]]:
            pos += 1
            boundary = pos
            continue
        gap_start = pos
        while pos < n and not is_bar[idxs[pos]] and (pos - gap_start) < GAP_TOLERANCE:
            pos += 1
        if pos < n and is_bar[idxs[pos]]:
            continue
        break
    return boundary


def analyze(gray_arr):
    h, w = gray_arr.shape
    row_mean = gray_arr.mean(axis=1)
    row_std = gray_arr.std(axis=1)
    is_bar = (row_mean < DARK_THRESH) & (row_std < FLAT_THRESH)
    top = band_height(is_bar, h, True)
    bottom = band_height(is_bar, h, False)
    cap = int(h * MAX_BAR_FRACTION)
    top = min(top, cap)
    bottom = min(bottom, cap)
    if top < MIN_BAR_PX:
        top = 0
    if bottom < MIN_BAR_PX:
        bottom = 0
    return top, bottom


def main():
    processed = []
    for folder in FOLDERS:
        d = ROOT / folder
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue

            backup_path = BACKUP_ROOT / p.relative_to(ROOT)
            source = backup_path if backup_path.exists() else p

            im = Image.open(source)
            gray = np.array(im.convert("L"), dtype=np.float32)
            top, bottom = analyze(gray)
            if not top and not bottom:
                continue

            h = gray.shape[0]

            if not backup_path.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, backup_path)

            cropped = im.crop((0, top, im.width, h - bottom))
            if p.suffix.lower() == ".png":
                cropped.save(p)
            else:
                cropped.convert("RGB").save(p, quality=95)

            processed.append((p.relative_to(ROOT), im.width, h, top, bottom, cropped.height))

    if not processed:
        print("Aucune image a recadrer.")
        return

    print(f"{len(processed)} image(s) recadree(s) (original dans scripts/_backup-before-crop/):\n")
    for rel, w, h, top, bottom, newh in processed:
        print(f"  {rel}  {w}x{h} -> {w}x{newh}  (top-{top}px, bottom-{bottom}px)")


if __name__ == "__main__":
    main()
