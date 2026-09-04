#!/usr/bin/env python3
"""Sync Anne's 4 reorganized portfolio folders into the site's asset pipeline.

Source (real folders on her machine, outside the site repo):
  portfolio/DESSIN-LIVE        -> site slug "dessin-live"       (new)
  portfolio/COLLAB-CONTENU     -> site slug "collaboration-creation-contenu"
  portfolio/BD-ILLUSTRATIONS   -> site slug "bd-et-illustrations"
  portfolio/CARNET             -> site slug "carnet"

For each destination slug folder under site/src/assets/images/portfolio/:
  - wipe it and repopulate from the matching source folder (old "portraits" and
    "personnes-dessinees" content is retired separately, not handled here)
  - convert HEIC/HEIC-cased files to JPG via `sips` (Astro's image pipeline can't
    read HEIC)
  - normalize filenames to lowercase-with-dashes, preserving the timestamp/"page no
    X" ordering the BD reading-order sort already relies on
  - skip non-image files (.mov, .DS_Store, etc.)
"""
import re
import shutil
import subprocess
from pathlib import Path

REAL_ROOT = Path("/Users/anneleblanc/Desktop/Claude code/portfolio")
SITE_ROOT = Path(__file__).resolve().parents[1] / "src/assets/images/portfolio"

SLUG_MAP = {
    "DESSIN-LIVE": "dessin-live",
    "COLLAB-CONTENU": "collaboration-creation-contenu",
    "BD-ILLUSTRATIONS": "bd-et-illustrations",
    "CARNET": "carnet",
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic"}


def slugify_stem(stem: str) -> str:
    s = stem.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def main():
    for src_name, slug in SLUG_MAP.items():
        src_dir = REAL_ROOT / src_name
        dest_dir = SITE_ROOT / slug
        if not src_dir.exists():
            print(f"! source manquante: {src_dir}")
            continue

        if dest_dir.exists():
            shutil.rmtree(dest_dir)
        dest_dir.mkdir(parents=True)

        used_names = set()
        count = 0
        skipped = []
        for f in sorted(src_dir.iterdir()):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext not in IMAGE_EXTS:
                skipped.append(f.name)
                continue

            base = slugify_stem(f.stem)
            out_ext = ".jpg" if ext == ".heic" else ext
            name = f"{base}{out_ext}"
            n = 2
            while name in used_names:
                name = f"{base}-{n}{out_ext}"
                n += 1
            used_names.add(name)
            dest_path = dest_dir / name

            if ext == ".heic":
                res = subprocess.run(
                    ["sips", "-s", "format", "jpeg", str(f), "--out", str(dest_path)],
                    capture_output=True, text=True,
                )
                if res.returncode != 0:
                    print(f"  ERREUR conversion {f.name}: {res.stderr.strip()}")
                    continue
            else:
                shutil.copy2(f, dest_path)
            count += 1

        print(f"{src_name} -> {slug}: {count} image(s) copiee(s)/convertie(s)")
        if skipped:
            print(f"  ignore(s) (non-image): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
