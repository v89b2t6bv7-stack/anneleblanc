#!/usr/bin/env python3
"""Dry-run detector for horizontal black letterbox bars on portfolio images.

A row counts as "bar" only if it is BOTH very dark (mean < DARK_THRESH) AND
essentially flat (std < FLAT_THRESH) — true digital letterboxing reads as
literal (0, 0, 0) with zero variance across the whole row width. Real dark
photography or dark artwork (charcoal on black paper, low-light event
photos, etc.) still has texture/contrast within a "dark" row (std stays
high, ~20-40+), so it is never mistaken for a bar, no matter how dark it
looks overall — this is the check that matters, not raw brightness.

From each edge we scan inward and accumulate a run of bar-rows, BRIDGING
over short interruptions (<= GAP_TOLERANCE rows) — e.g. a paused video's
grey scrubber pill embedded in an otherwise flat black bar — as long as
flat-black resumes right after. A long or unresolved interruption (i.e.
real content) stops the scan for good.
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1] / "src/assets/images/portfolio"
FOLDERS = ["carnet", "bd-et-illustrations", "collaboration-creation-contenu", "dessin-live"]

DARK_THRESH = 10       # row mean brightness (0-255) below this = "dark enough"
FLAT_THRESH = 5         # row std-dev below this = "flat" (uniform bar, not real texture)
GAP_TOLERANCE = 20      # bridge over short embedded-overlay interruptions (px)
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
            continue  # bridged: keep scanning, boundary will extend again
        break
    return boundary


def analyze(path):
    try:
        im = Image.open(path).convert("L")
    except Exception:
        return None
    arr = np.array(im, dtype=np.float32)
    h, w = arr.shape
    row_mean = arr.mean(axis=1)
    row_std = arr.std(axis=1)
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
    return {"path": path, "w": w, "h": h, "top": top, "bottom": bottom}


def main():
    results = []
    for folder in FOLDERS:
        d = ROOT / folder
        if not d.exists():
            continue
        for p in sorted(d.iterdir()):
            if p.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            r = analyze(p)
            if r and (r["top"] or r["bottom"]):
                results.append(r)

    if not results:
        print("Aucune bande noire detectee.")
        return

    print(f"{len(results)} image(s) avec bande(s) detectee(s):\n")
    for r in results:
        rel = r["path"].relative_to(ROOT)
        print(f"  {rel}  ({r['w']}x{r['h']})  top={r['top']}px  bottom={r['bottom']}px  -> nouvelle hauteur={r['h']-r['top']-r['bottom']}px")


if __name__ == "__main__":
    main()
