#!/usr/bin/env python3
"""Build the Beautiful Reaper theme.

    python3 src/build.py            -> dist/BeautifulReaper.ReaperThemeZip

Outputs:
  build/BeautifulReaper/            unpacked theme (images, rtconfig.txt)
  build/BeautifulReaper/200/        2x images for HiDPI / Retina
  build/BeautifulReaper.ReaperTheme color + font file
  dist/BeautifulReaper.ReaperThemeZip
"""
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import colors  # noqa: E402
import images  # noqa: E402
import palette as P  # noqa: E402

NAME = "BeautifulReaper"
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")
DIST = os.path.join(ROOT, "dist")

TOKENS = {
    "PANEL": P.PANEL,
    "BG_DEEP": P.BG_DEEP,
    "PANEL_SEL": P.PANEL_SEL,
    "PANEL_RAISED": P.PANEL_RAISED,
    "CONTROL": P.CONTROL,
    "DIVIDER": P.DIVIDER,
    "INDENT": P.mix(P.PANEL, P.BG_DEEP, 0.55),
    "ENV_BG": P.mix(P.PANEL, P.BG_DEEP, 0.35),
    "TEXT": P.TEXT,
    "TEXT_2": P.TEXT_2,
    "TEXT_3": P.TEXT_3,
    "METER_CLIP": P.METER_CLIP,
}


def render_rtconfig():
    with open(os.path.join(HERE, "rtconfig.txt")) as f:
        src = f.read()

    def sub(m):
        key = m.group(1)
        if key == "TOKENS":
            return "$TOKENS$"
        return " ".join(str(v) for v in P.rgb(TOKENS[key]))
    return re.sub(r"\$([A-Z_0-9]+)\$", sub, src)


def main():
    theme_dir = os.path.join(BUILD, NAME)
    shutil.rmtree(BUILD, ignore_errors=True)
    n = images.generate(theme_dir, 1)
    images.generate(os.path.join(theme_dir, "200"), 2)
    with open(os.path.join(theme_dir, "rtconfig.txt"), "w", newline="\r\n") as f:
        f.write(render_rtconfig())
    theme_file = os.path.join(BUILD, NAME + ".ReaperTheme")
    colors.write_theme_file(theme_file, NAME)

    os.makedirs(DIST, exist_ok=True)
    zpath = os.path.join(DIST, NAME + ".ReaperThemeZip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(theme_file, NAME + ".ReaperTheme")
        for base, _, files in os.walk(theme_dir):
            for fn in sorted(files):
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, BUILD))
    print("built %s (%d images x 2 scales)" % (os.path.relpath(zpath, ROOT), n))


if __name__ == "__main__":
    main()
