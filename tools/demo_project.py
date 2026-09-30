#!/usr/bin/env python3
"""Generate a demo REAPER project (with synthetic audio) used for theme screenshots.

Usage: demo_project.py OUTDIR
"""
import math
import os
import random
import struct
import sys
import wave

SR = 44100
BPM = 124
BEAT = 60.0 / BPM
BARS = 16
LEN = BARS * 4 * BEAT


def write_wav(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 32000)) for s in samples))


def render(n, fn):
    return [fn(i / SR) for i in range(n)]


def kick(bars=8):
    n = int(bars * 4 * BEAT * SR)
    out = [0.0] * n
    for b in range(bars * 4):
        s = int(b * BEAT * SR)
        for i in range(int(0.35 * SR)):
            t = i / SR
            if s + i < n:
                out[s + i] += math.sin(2 * math.pi * (50 + 120 * math.exp(-t * 30)) * t) * math.exp(-t * 9) * 0.95
    return out


def hats(bars=8):
    rnd = random.Random(3)
    n = int(bars * 4 * BEAT * SR)
    out = [0.0] * n
    for b in range(bars * 8):
        s = int((b * BEAT / 2) * SR)
        amp = 0.5 if b % 2 else 0.25
        for i in range(int(0.06 * SR)):
            if s + i < n:
                out[s + i] += (rnd.random() * 2 - 1) * math.exp(-i / SR * 70) * amp
    return out


def snare(bars=8):
    rnd = random.Random(5)
    n = int(bars * 4 * BEAT * SR)
    out = [0.0] * n
    for b in range(bars * 2):
        s = int((b * 2 + 1) * BEAT * SR)
        for i in range(int(0.25 * SR)):
            t = i / SR
            if s + i < n:
                out[s + i] += ((rnd.random() * 2 - 1) * 0.6 + math.sin(2 * math.pi * 190 * t) * 0.4) * math.exp(-t * 16) * 0.8
    return out


def bass(bars=8):
    notes = [41.2, 41.2, 49.0, 36.7]
    n = int(bars * 4 * BEAT * SR)
    out = []
    for i in range(n):
        t = i / SR
        bar = int(t / (4 * BEAT)) % 4
        f = notes[bar]
        ph = (t % (BEAT / 2)) / (BEAT / 2)
        env = math.exp(-ph * 3)
        out.append((math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t)) * env * 0.7)
    return out


def pad(bars=8, seed=1):
    rnd = random.Random(seed)
    n = int(bars * 4 * BEAT * SR)
    freqs = [220, 277.2, 329.6, 415.3]
    out = []
    for i in range(n):
        t = i / SR
        swell = 0.5 + 0.5 * math.sin(2 * math.pi * t / (4 * BEAT) - math.pi / 2)
        v = sum(math.sin(2 * math.pi * f * t + k) for k, f in enumerate(freqs)) / 4
        out.append(v * (0.25 + 0.55 * swell))
    return out


def vox(bars=8):
    n = int(bars * 4 * BEAT * SR)
    out = []
    for i in range(n):
        t = i / SR
        phrase = (t % (2 * BEAT * 4)) / (2 * BEAT * 4)
        gate = 1.0 if phrase < 0.7 else 0.0
        env = math.sin(math.pi * min(1, phrase / 0.7)) * gate
        f = 330 + 40 * math.sin(2 * math.pi * 0.5 * t)
        out.append((math.sin(2 * math.pi * f * t) * 0.6 + math.sin(4 * math.pi * f * t) * 0.2) * env * (0.6 + 0.4 * math.sin(2 * math.pi * 5 * t)))
    return out


def col(hexstr):
    r, g, b = int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16)
    return 0x1000000 | r | (g << 8) | (b << 16)


def js(name):
    return f"""    <JS {name} ""
      0 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    >
    FLOATPOS 0 0 0 0
    WAK 0 0
"""


def fxchain(names, bypass_last=False):
    if not names:
        return ""
    s = "  <FXCHAIN\n    SHOW 0\n    LASTSEL 0\n    DOCKED 0\n"
    for k, n in enumerate(names):
        byp = 1 if (bypass_last and k == len(names) - 1) else 0
        s += f"    BYPASS {byp} 0 0\n" + js(n)
    return s + "  >\n"


def item(pos, length, name, wav, color=None):
    c = f"      COLOR {color} B\n" if color else ""
    return f"""  <ITEM
    POSITION {pos}
    LENGTH {length}
    LOOP 1
    NAME "{name}"
{c}    <SOURCE WAVE
      FILE "{wav}"
    >
  >
"""


def track(name, color, isbus="0 0", items="", fx=(), vol=1.0, pan=0.0, mute=0, solo=0, rec="0 0 0 0 0 0 0",
          height=32, sel=0, fcomp=0, recv="", env="", bypass_last=False):
    return f"""<TRACK
  NAME "{name}"
  PEAKCOL {color}
  VOLPAN {vol} {pan} -1 -1 1
  MUTESOLO {mute} {solo} 0
  SEL {sel}
  REC {rec}
  TRACKHEIGHT {height} 0 0 0 0 0
  ISBUS {isbus}
  BUSCOMP {fcomp} 0 0 0 0
  NCHAN 2
{recv}{env}{fxchain(list(fx), bypass_last)}{items}>
"""


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    stems = {"kick": kick, "snare": snare, "hats": hats, "bass": bass, "pad": pad, "vox": vox}
    for k, fn in stems.items():
        p = os.path.join(out, k + ".wav")
        if not os.path.exists(p):
            write_wav(p, fn(4))
    L = 4 * 4 * BEAT
    def loop(wav, name, start=0, count=4, gap=0):
        return "".join(item(start + i * (L + gap), L, name, wav) for i in range(count))

    C = {"drums": col("FF6B5A"), "bass": col("FFB23F"), "keys": col("7BD88F"), "pad": col("4FC3F7"),
         "vox": col("B39DFF"), "fx": col("FF7AC6"), "bus": col("8E8E93")}
    vol_env = """  <VOLENV2
    EGUID {00000000-0000-0000-0000-000000000001}
    ACT 1 -1
    VIS 1 1 1
    LANEHEIGHT 30 0
    ARM 1
    DEFSHAPE 0 -1 -1
    PT 0 0.5 0
    PT 4 1 0
    PT 8 0.7 0
    PT 12 1 0
    PT 20 0.4 0
    PT 30 1 0
  >
"""
    tracks = [
        track("Drums", C["drums"], "1 1", fx=["utility/volume", "utility/volume"], sel=0),
        track("Kick", C["drums"], items=loop("kick.wav", "Kick"), fx=["utility/volume"]),
        track("Snare", C["drums"], items=loop("snare.wav", "Snare", 0, 4), vol=0.8),
        track("Hats", C["drums"], "2 -1", items=loop("hats.wav", "Hats", L, 3), vol=0.6, pan=0.25),
        track("Bass", C["bass"], items=loop("bass.wav", "Bass", 0, 4), fx=["utility/volume", "utility/volume"], sel=1, env=vol_env),
        track("Synths", C["keys"], "1 1", fcomp=2),
        track("Lead", C["keys"], items=loop("pad.wav", "Lead", L, 2)),
        track("Arp", C["keys"], "2 -1", items=loop("pad.wav", "Arp", 0, 4)),
        track("Pad", C["pad"], items=loop("pad.wav", "Pad", 0, 4), vol=0.5, pan=-0.3, mute=1),
        track("Lead Vocal", C["vox"], items=loop("vox.wav", "Vox take 3", L, 2), rec="1 0 1 0 0 0 0", height=56,
              fx=["utility/volume", "utility/volume", "utility/volume"], solo=0, bypass_last=True),
        track("Reverb", C["fx"], fx=["utility/volume"], vol=0.7,
              recv="  AUXRECV 9 0 0.5 0 0 0 0 0 0 -1:U 0 -1 ''\n  AUXRECV 4 0 0.3 0 0 0 0 0 0 -1:U 0 -1 ''\n"),
    ]
    rpp = f"""<REAPER_PROJECT 0.1 "7.0" 1700000000
  TEMPO {BPM} 4 4
  PLAYRATE 1 0 0.25 4
  SELECTION 16 32
  LOOP 1
  CURSOR 7.74
  ZOOM 34 0 0
  <MARKER 0 "Intro" 0 0 1 B>
  MARKER 1 {L} "Drop" 0 0 1 B
  MARKER 2 {2*L} "Break" 0 0 1 B
  <MASTERFXLIST
  >
  MASTER_VOLUME 1 0 -1 -1 1
  MASTER_NCH 2 2
""" + "".join(tracks) + ">\n"
    rpp = rpp.replace('  <MARKER 0 "Intro" 0 0 1 B>\n', '  MARKER 0 0 "Intro" 0 0 1 B\n')
    with open(os.path.join(out, "demo.rpp"), "w") as f:
        f.write(rpp)


if __name__ == "__main__":
    main()
