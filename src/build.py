#!/usr/bin/env python3
"""Build the Beautiful Reaper theme.

    python3 src/build.py            -> dist/BeautifulReaper.ReaperThemeZip

Outputs:
  build/BeautifulReaper/            unpacked theme (images, rtconfig.txt)
  build/BeautifulReaper/<pct>/      images for each UI scale step (125..300%)
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
    "GUIDE": P.mix(P.BG_DEEP, P.TEXT_3, 0.4),
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


# UI scale steps (percent). REAPER picks the nearest step for the current UI
# scale; every step gets its own layout, image folder and pair of fonts.
SCALES = [100, 125, 150, 175, 200, 250, 300]


def layout_blocks(macro):
    out = ["%s 1 0" % macro]
    for k, pct in enumerate(SCALES):
        name = "A" if pct == 100 else "%d%%_A" % pct
        folder = "" if pct == 100 else ' "%d"' % pct
        out.append('Layout "%s"%s\n\t%s %g %d\nendLayout' % (name, folder, macro, pct / 100, 2 * k))
    return "\n".join(out)


def dpi_rules():
    lines = ["; Scale steps: from each threshold (midway between steps) up, use that step.",
             "; '' covers tracks with no layout chosen, which is almost all of them."]
    for lo, pct in zip(SCALES, SCALES[1:]):
        thr = (lo + pct) / 200
        lines.append("misc_dpi_translate %d %d" % (round(thr * 100), pct))
        for src in ("''", "'A'"):
            lines.append("layout_dpi_translate %s %.3f '%d%%_A'" % (src, thr, pct))
    return "\n".join(lines)


def render_rtconfig():
    with open(os.path.join(HERE, "rtconfig.txt")) as f:
        src = f.read()
    src = re.sub(r"\$LAYOUTS (\w+)\$", lambda m: layout_blocks(m.group(1)), src)
    src = src.replace("$DPI_RULES$", dpi_rules())

    def sub(m):
        key = m.group(1)
        if key == "TOKENS":
            return "$TOKENS$"
        return " ".join(str(v) for v in P.rgb(TOKENS[key]))
    return re.sub(r"\$([A-Z_0-9]+)\$", sub, src)


def main():
    theme_dir = os.path.join(BUILD, NAME)
    shutil.rmtree(BUILD, ignore_errors=True)
    for pct in SCALES:
        n = images.generate(theme_dir if pct == 100 else os.path.join(theme_dir, str(pct)), pct / 100)
    with open(os.path.join(theme_dir, "rtconfig.txt"), "w", newline="\r\n") as f:
        f.write(render_rtconfig())
    theme_file = os.path.join(BUILD, NAME + ".ReaperTheme")
    colors.write_theme_file(theme_file, NAME, SCALES)

    os.makedirs(DIST, exist_ok=True)
    zpath = os.path.join(DIST, NAME + ".ReaperThemeZip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(theme_file, NAME + ".ReaperTheme")
        for base, _, files in os.walk(theme_dir):
            for fn in sorted(files):
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, BUILD))
    print("built %s (%d images x %d scales)" % (os.path.relpath(zpath, ROOT), n, len(SCALES)))


if __name__ == "__main__":
    main()
