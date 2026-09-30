#!/usr/bin/env python3
"""Write index.xml, the ReaPack repository index for the theme.

    python3 tools/make_index.py

Bump VERSION and rebuild (src/build.py) before releasing: ReaPack only
offers an update when the version in index.xml changes.
"""
import datetime
import os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/onliner10/BeautifulReaper"
BRANCH = "main"
PKG = "BeautifulReaper.ReaperThemeZip"

version = open(os.path.join(ROOT, "VERSION")).read().strip()
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
desc = ("A calm, modern REAPER 7 theme: the track panel is the whole channel "
        "(LED meter + fader, sends, routing, automation), tree-style folders, "
        "HiDPI from 100% to 300%.")

xml = f"""<?xml version="1.0" encoding="utf-8"?>
<index version="1" name="Beautiful Reaper">
  <category name="Themes">
    <reapack name="{PKG}" type="theme" desc="Beautiful Reaper">
      <metadata>
        <description><![CDATA[{desc}]]></description>
        <link rel="website">{REPO}</link>
        <link rel="screenshot">{REPO}/raw/{BRANCH}/docs/arrange.png</link>
      </metadata>
      <version name="{escape(version)}" author="Mateusz Urban" time="{now}">
        <source>{REPO}/raw/{BRANCH}/dist/{PKG}</source>
      </version>
    </reapack>
  </category>
  <metadata>
    <description><![CDATA[Beautiful Reaper theme]]></description>
    <link rel="website">{REPO}</link>
  </metadata>
</index>
"""
with open(os.path.join(ROOT, "index.xml"), "w") as f:
    f.write(xml)
print("index.xml -> version", version)
