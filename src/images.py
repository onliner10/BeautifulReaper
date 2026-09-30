"""Vector-drawn theme images.

Every image is drawn in 1x "points" on a 4x-supersampled canvas and then
downsampled, so the same code produces crisp 1x and 2x (HiDPI) PNGs.

Conventions REAPER expects:
  * buttons are 3 frames laid out horizontally: normal, hover, pressed
  * knob stacks are square frames stacked vertically (min -> max)
  * stretchable images carry a 1px pink (255,0,255) border marking the
    non-stretching margins
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

import palette as P

SS = 4  # supersampling factor
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_MEDIUM = os.path.join(HERE, "fonts", "Inter-Medium.ttf")
FONT_SEMIBOLD = os.path.join(HERE, "fonts", "Inter-SemiBold.ttf")

REGISTRY = {}


def px(v, s):
    """v points at scale s, as whole pixels (scales may be fractional)."""
    return max(1, int(round(v * s)))


def image(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


def c(hexstr, a=255):
    return P.rgba(hexstr, a)


class Canvas:
    def __init__(self, w, h, s):
        self.w, self.h, self.s = w, h, s
        self.k = s * SS
        self.im = Image.new("RGBA", (round(w * self.k), round(h * self.k)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _p(self, v):
        return round(v * self.k)

    def rrect(self, x, y, w, h, r, fill=None, outline=None, width=1.0):
        box = [self._p(x), self._p(y), self._p(x + w) - 1, self._p(y + h) - 1]
        self.d.rounded_rectangle(box, radius=self._p(r), fill=fill, outline=outline,
                                 width=max(1, self._p(width)) if outline else 0)

    def rect(self, x, y, w, h, fill):
        self.d.rectangle([self._p(x), self._p(y), self._p(x + w) - 1, self._p(y + h) - 1], fill=fill)

    def circle(self, cx, cy, r, fill=None, outline=None, width=1.0):
        box = [self._p(cx - r), self._p(cy - r), self._p(cx + r), self._p(cy + r)]
        self.d.ellipse(box, fill=fill, outline=outline, width=max(1, self._p(width)) if outline else 0)

    def poly(self, pts, fill):
        self.d.polygon([(self._p(x), self._p(y)) for x, y in pts], fill=fill)

    def line(self, pts, fill, width=1.0, round_caps=True):
        pp = [(self._p(x), self._p(y)) for x, y in pts]
        wpx = max(1, self._p(width))
        self.d.line(pp, fill=fill, width=wpx, joint="curve")
        if round_caps:
            for x, y in (pp[0], pp[-1]):
                r = wpx / 2
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def arc(self, cx, cy, r, a0, a1, fill, width=1.0):
        """Arc in degrees, 0 = up, clockwise."""
        if abs(a1 - a0) < 0.5:
            return
        lo, hi = min(a0, a1), max(a0, a1)
        steps = max(2, int((hi - lo) / 3))
        pts = [(cx + r * math.sin(math.radians(lo + (hi - lo) * i / steps)),
                cy - r * math.cos(math.radians(lo + (hi - lo) * i / steps))) for i in range(steps + 1)]
        self.line(pts, fill, width)

    def text(self, cx, cy, s, size, fill, font=FONT_SEMIBOLD):
        f = ImageFont.truetype(font, self._p(size))
        self.d.text((self._p(cx), self._p(cy)), s, font=f, fill=fill, anchor="mm")

    def result(self):
        return self.im.resize((round(self.w * self.s), round(self.h * self.s)), Image.LANCZOS)


def hstack(ims):
    out = Image.new("RGBA", (sum(i.width for i in ims), max(i.height for i in ims)), (0, 0, 0, 0))
    x = 0
    for i in ims:
        out.paste(i, (x, 0))
        x += i.width
    return out


def vstack(ims):
    out = Image.new("RGBA", (max(i.width for i in ims), sum(i.height for i in ims)), (0, 0, 0, 0))
    y = 0
    for i in ims:
        out.paste(i, (0, y))
        y += i.height
    return out


def pink_border(im, left, top, right, bottom):
    """Wrap im in a 1px border; pink runs mark fixed (non-stretched) margins."""
    w, h = im.size
    out = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    out.paste(im, (1, 1))
    px = out.load()
    pink = (255, 0, 255, 255)
    for x in range(0, left + 1):
        px[x, 0] = pink
    for y in range(0, top + 1):
        px[0, y] = pink
    for x in range(w + 1 - right, w + 2):
        px[x, h + 1] = pink
    for y in range(h + 1 - bottom, h + 2):
        px[w + 1, y] = pink
    return out


STATES = ("normal", "hover", "pressed")


def frames3(w, h, s, draw):
    ims = []
    for st in STATES:
        cv = Canvas(w, h, s)
        draw(cv, st)
        ims.append(cv.result())
    return hstack(ims)


def face(state, base=P.CONTROL):
    if state == "hover":
        return P.mix(base, "#FFFFFF", 0.10)
    if state == "pressed":
        return P.mix(base, "#000000", 0.18)
    return base


# ---------------------------------------------------------------- buttons ----

BTN_W, BTN_H = 20, 20


def pill_button(s, glyph, on_color=None, w=BTN_W, h=BTN_H, glyph_fn=None, text_size=9.5,
                off_glyph=P.TEXT_2, bg=P.CONTROL):
    """Rounded square button. When on_color is set the button is 'lit'."""
    def draw(cv, st):
        if on_color:
            cv.rrect(1, 2, w - 2, h - 4, 4, fill=c(face(st, on_color)))
            gcol = c(P.TEXT_ON_COLOR)
        else:
            cv.rrect(1, 2, w - 2, h - 4, 4, fill=c(face(st, bg)))
            gcol = c(P.mix(off_glyph, "#FFFFFF", 0.25) if st == "hover" else off_glyph)
        if glyph_fn:
            glyph_fn(cv, gcol, st)
        elif glyph:
            cv.text(w / 2, h / 2 + 0.2, glyph, text_size, gcol)
    return frames3(w, h, s, draw)


for _name, _g, _col in (("track_mute_off", "M", None), ("track_mute_on", "M", P.MUTE),
                        ("track_solo_off", "S", None), ("track_solo_on", "S", P.SOLO)):
    image(_name)(lambda s, g=_g, col=_col: pill_button(s, g, col))

image("track_solodefeat_on")(lambda s: pill_button(s, "S", P.mix(P.SOLO, P.PANEL, 0.45)))
image("tcp_solodefeat_on")(lambda s: pill_button(s, "S", P.mix(P.SOLO, P.PANEL, 0.45)))


def rec_glyph(color_fill, ring=False, auto=False):
    def g(cv, gcol, st):
        cx, cy = BTN_W / 2, BTN_H / 2
        cv.circle(cx, cy, 4.2, fill=c(color_fill) if color_fill else gcol)
        if auto:
            cv.circle(cx, cy, 1.6, fill=gcol if not color_fill else c(P.TEXT_ON_COLOR))
    return g


def recarm(s, armed, norec=False, auto=False):
    if armed:
        fill = P.mix(P.REC, P.PANEL, 0.35) if norec else P.REC

        def draw(cv, st):
            cv.rrect(1, 2, BTN_W - 2, BTN_H - 4, 4, fill=c(face(st, P.mix(P.REC, P.PANEL, 0.72))))
            cv.circle(BTN_W / 2, BTN_H / 2, 4.3, fill=c(face(st, fill)))
            if auto:
                cv.circle(BTN_W / 2, BTN_H / 2, 1.5, fill=c(P.TEXT_ON_COLOR))
        return frames3(BTN_W, BTN_H, s, draw)
    return pill_button(s, None, None, glyph_fn=rec_glyph(None, auto=auto), off_glyph=P.TEXT_3)


image("track_recarm_off")(lambda s: recarm(s, False))
image("track_recarm_on")(lambda s: recarm(s, True))
image("track_recarm_norec")(lambda s: recarm(s, True, norec=True))
image("track_recarm_auto")(lambda s: recarm(s, False, auto=True))
image("track_recarm_auto_on")(lambda s: recarm(s, True, auto=True))
image("track_recarm_auto_norec")(lambda s: recarm(s, True, norec=True, auto=True))


def monitor_glyph(cv, gcol, st):
    # headphones
    cx, cy = BTN_W / 2, BTN_H / 2 + 0.5
    cv.arc(cx, cy, 4.6, -90, 90, gcol, 1.3)
    cv.rrect(cx - 5.9, cy - 0.6, 2.6, 4.2, 1, fill=gcol)
    cv.rrect(cx + 3.3, cy - 0.6, 2.6, 4.2, 1, fill=gcol)


def monitor_auto_glyph(cv, gcol, st):
    monitor_glyph(cv, gcol, st)
    cv.text(BTN_W / 2, BTN_H / 2 + 2.6, "A", 5, gcol)


image("track_monitor_off")(lambda s: pill_button(s, None, None, glyph_fn=monitor_glyph, off_glyph=P.TEXT_3))
image("track_monitor_on")(lambda s: pill_button(s, None, P.MONITOR, glyph_fn=monitor_glyph))
image("track_monitor_auto")(lambda s: pill_button(s, None, P.mix(P.MONITOR, P.PANEL, 0.3), glyph_fn=monitor_glyph))


def fx_button(s, state_kind, w=24):
    def draw(cv, st):
        if state_kind == "norm":
            cv.rrect(1, 2, w - 2, BTN_H - 4, 4, fill=c(face(st, P.mix(P.FX_ON, P.PANEL, 0.78))))
            col = c(P.FX_ON)
        elif state_kind == "dis":
            cv.rrect(1, 2, w - 2, BTN_H - 4, 4, fill=c(face(st, P.mix(P.FX_BYPASS, P.PANEL, 0.78))))
            col = c(P.FX_BYPASS)
        else:
            cv.rrect(1, 2, w - 2, BTN_H - 4, 4, fill=c(face(st, P.CONTROL)))
            col = c(P.TEXT_2 if st == "hover" else P.TEXT_3)
        cv.text(w / 2, BTN_H / 2 + 0.2, "FX", 8.5, col)
    return frames3(w, BTN_H, s, draw)


for _k in ("empty", "norm", "dis"):
    image("track_fx_" + _k)(lambda s, k=_k: fx_button(s, k))
    image("mcp_fx_" + _k)(lambda s, k=_k: fx_button(s, k, 26))
    image("track_fx_in_" + _k)(lambda s, k=_k: fx_button(s, k))


def env_glyph(cv, gcol, st):
    cx, cy = BTN_W / 2, BTN_H / 2
    pts = [(cx - 5.5, cy + 3), (cx - 2, cy - 3), (cx + 1.5, cy + 1.5), (cx + 5.5, cy - 3.5)]
    cv.line(pts, gcol, 1.4)
    for x, y in pts[1:3]:
        cv.circle(x, y, 1.4, fill=gcol)


ENV_MODES = {"": None, "_read": P.AUTO_READ, "_write": P.AUTO_WRITE, "_touch": P.AUTO_TOUCH,
             "_latch": P.AUTO_LATCH, "_preview": P.AUTO_PREVIEW}
for _suffix, _col in ENV_MODES.items():
    def _env(s, col=_col, w=BTN_W):
        def draw(cv, st):
            cv.rrect(1, 2, w - 2, BTN_H - 4, 4, fill=c(face(st, P.CONTROL if not col else P.mix(col, P.PANEL, 0.75))))
            env_glyph(cv, c(col) if col else c(P.TEXT_2 if st == "hover" else P.TEXT_3), st)
        return frames3(w, BTN_H, s, draw)
    image("track_env" + _suffix)(_env)
    image("mcp_env" + _suffix)(lambda s, f=_env: f(s))


# track_io[_r][_s][_dis]: _s/_r = has sends/receives (marked with an accent dot),
# _dis = master/parent send disabled (dimmed glyph).
for _suffix in ("", "_r", "_s", "_s_r"):
    for _dis in ("", "_dis"):
        def _io(s, dis=_dis, has=bool(_suffix), w=24):
            def draw(cv, st):
                cv.rrect(1, 2, w - 2, BTN_H - 4, 4, fill=c(face(st, P.CONTROL)))
                cv.text(w / 2, BTN_H / 2 + 0.3, "I/O", 8, c(P.TEXT_3 if dis else (P.TEXT if st == "hover" else P.TEXT_2)))
                if has:
                    cv.circle(w - 3.5, 3.5, 2.2, fill=c(P.ACCENT))
            return frames3(w, BTN_H, s, draw)
        image("track_io" + _suffix + _dis)(_io)
        image("mcp_io" + _suffix + _dis)(lambda s, f=_io: f(s))


def phase_glyph(cv, gcol, st):
    cx, cy = BTN_W / 2, BTN_H / 2
    cv.circle(cx, cy, 3.8, outline=gcol, width=1.2)
    cv.line([(cx - 4.5, cy + 4.5), (cx + 4.5, cy - 4.5)], gcol, 1.2)


image("track_phase_norm")(lambda s: pill_button(s, None, None, glyph_fn=phase_glyph, off_glyph=P.TEXT_3))
image("track_phase_inv")(lambda s: pill_button(s, None, P.FX_BYPASS, glyph_fn=phase_glyph))
image("mcp_phase_norm")(lambda s: pill_button(s, None, None, glyph_fn=phase_glyph, off_glyph=P.TEXT_3))
image("mcp_phase_inv")(lambda s: pill_button(s, None, P.FX_BYPASS, glyph_fn=phase_glyph))


# Folder collapse: a big, obvious disclosure chevron.
FOLD = 20


def chevron(cv, cx, cy, direction, col, size=3.6, width=1.7):
    if direction == "down":
        pts = [(cx - size, cy - size / 2), (cx, cy + size / 2), (cx + size, cy - size / 2)]
    else:
        pts = [(cx - size / 2, cy - size), (cx + size / 2, cy), (cx - size / 2, cy + size)]
    cv.line(pts, col, width)


def fold_button(s, direction, small=False, w=FOLD, h=FOLD):
    def draw(cv, st):
        if st != "normal":
            cv.rrect(1, 1, w - 2, h - 2, 5, fill=c(face(st, P.CONTROL)))
        col = c(P.TEXT if st != "normal" else P.TEXT_2)
        chevron(cv, w / 2, h / 2, direction, col)
        if small:
            cv.line([(w / 2 - 3.6, h / 2 + 4.2), (w / 2 + 3.6, h / 2 + 4.2)], col, 1.2)
    return frames3(w, h, s, draw)


image("track_fcomp_off")(lambda s: fold_button(s, "down"))
image("track_fcomp_small")(lambda s: fold_button(s, "down", small=True))
image("track_fcomp_tiny")(lambda s: fold_button(s, "right"))
image("mcp_fcomp_off")(lambda s: fold_button(s, "down"))
image("mcp_fcomp_tiny")(lambda s: fold_button(s, "right"))


def blank3(s, w=BTN_W, h=BTN_H):
    return frames3(w, h, s, lambda cv, st: None)


for _n in ("track_folder_off", "track_folder_on", "track_folder_last", "mcp_folder_on", "mcp_folder_off",
           "mcp_folder_last", "tcp_pinned"):
    image(_n)(lambda s: blank3(s))


# ------------------------------------------------------ faders & knobs -------

@image("tcp_volbg")
def tcp_volbg(s):
    # Transparent: in the track panel the level meter is drawn as the fader track.
    cv = Canvas(22, 20, s)
    return pink_border(cv.result(), px(10, s), px(1, s), px(10, s), px(1, s))


@image("envcp_faderbg")
def envcp_faderbg(s):
    cv = Canvas(22, 20, s)
    cv.rrect(0, 8.5, 22, 3, 1.5, fill=c(P.WELL))
    return pink_border(cv.result(), px(10, s), px(1, s), px(10, s), px(1, s))


@image("tcp_volthumb")
def tcp_volthumb(s):
    # Fader position marker for a fader whose track is the level meter.
    # REAPER paints meters above everything, so the marker is a pair of tabs
    # that stick out above and below the meter: a white wedge on each side.
    cv = Canvas(10, 20, s)
    cv.poly([(0.6, 0), (9.4, 0), (5, 4.6)], fill=c("#F4F4F7"))
    cv.poly([(0.6, 20), (9.4, 20), (5, 15.4)], fill=c("#F4F4F7"))
    cv.rect(4.25, 3, 1.5, 14, fill=c("#F4F4F7"))
    return cv.result()


@image("envcp_fader")
def envcp_fader(s):
    cv = Canvas(8, 16, s)
    cv.rrect(0.5, 1, 7, 15, 2.5, fill=c("#000000", 110))
    cv.rrect(0.5, 0.5, 7, 14.5, 2.5, fill=c("#E4E5EA"))
    return cv.result()


@image("tcp_panbg")
def tcp_panbg(s):
    cv = Canvas(56, 10, s)
    cv.rrect(0, 3.5, 56, 3, 1.5, fill=c(P.WELL))
    cv.rect(27.5, 2, 1, 6, fill=c(P.TEXT_3))
    return pink_border(cv.result(), px(6, s), px(1, s), px(6, s), px(1, s))


image("tcp_widthbg")(tcp_panbg)
image("mcp_panbg")(tcp_panbg)
image("mcp_widthbg")(tcp_panbg)


@image("tcp_panthumb")
def tcp_panthumb(s):
    cv = Canvas(9, 13, s)
    cv.rrect(0.5, 0.5, 8, 12, 3, fill=c("#D9DADF"))
    return cv.result()


image("tcp_widththumb")(tcp_panthumb)
image("mcp_panthumb")(tcp_panthumb)
image("mcp_widththumb")(tcp_panthumb)


@image("mcp_volbg")
def mcp_volbg(s):
    # vertical fader track
    cv = Canvas(24, 20, s)
    cv.rrect(10.5, 0, 3, 20, 1.5, fill=c(P.WELL))
    return pink_border(cv.result(), px(1, s), px(9, s), px(1, s), px(9, s))


@image("mcp_volthumb")
def mcp_volthumb(s):
    cv = Canvas(26, 14, s)
    cv.rrect(1, 1.5, 24, 12, 3.5, fill=c("#000000", 110))
    cv.rrect(1, 0.5, 24, 12, 3.5, fill=c("#D9DADF"))
    cv.line([(5, 6.5), (21, 6.5)], c("#6E6F75"), 1.2)
    return cv.result()


def knob_stack(s, size, bipolar, frames=41, ring=P.ACCENT, face_col=P.KNOB):
    ims = []
    for i in range(frames):
        v = i / (frames - 1)
        cv = Canvas(size, size, s)
        cx = cy = size / 2
        r_ring = size / 2 - 1.6
        cv.arc(cx, cy, r_ring, -135, 135, c(P.CONTROL), 2.2)
        ang = -135 + 270 * v
        if bipolar:
            cv.arc(cx, cy, r_ring, 0, ang, c(ring), 2.2)
        else:
            cv.arc(cx, cy, r_ring, -135, ang, c(ring), 2.2)
        r_face = size / 2 - 3.9
        cv.circle(cx, cy, r_face, fill=c(face_col))
        px = cx + (r_face - 1.2) * math.sin(math.radians(ang))
        py = cy - (r_face - 1.2) * math.cos(math.radians(ang))
        px0 = cx + 1.0 * math.sin(math.radians(ang))
        py0 = cy - 1.0 * math.cos(math.radians(ang))
        cv.line([(px0, py0), (px, py)], c(P.TEXT), 1.4)
        ims.append(cv.result())
    return vstack(ims)


image("tcp_pan_knob_stack")(lambda s: knob_stack(s, 20, True, ring=P.TEXT_2))
image("tcp_wid_knob_stack")(lambda s: knob_stack(s, 20, False, ring=P.TEXT_2))
image("tcp_vol_knob_stack")(lambda s: knob_stack(s, 20, False, ring=P.TEXT_2))
image("mcp_pan_knob_stack")(lambda s: knob_stack(s, 26, True, ring=P.TEXT_2))
image("mcp_wid_knob_stack")(lambda s: knob_stack(s, 26, False, ring=P.TEXT_2))
image("mcp_vol_knob_stack")(lambda s: knob_stack(s, 26, False, ring=P.TEXT_2))
image("tcp_send_knob_stack")(lambda s: knob_stack(s, 16, True, ring=P.TEXT_2, face_col=P.CONTROL))
image("mcp_send_knob_stack")(lambda s: knob_stack(s, 18, False, ring=P.ACCENT))
image("mcp_fxparm_knob_stack")(lambda s: knob_stack(s, 18, False, ring=P.FX_ON))
image("tcp_fxparm_knob_stack")(lambda s: knob_stack(s, 18, False, ring=P.FX_ON))
image("envcp_knob_stack")(lambda s: knob_stack(s, 20, False, ring=P.AUTO_READ))


# ------------------------------------------------------------- meters --------

def solid(hexstr, w=6, h=6):
    def f(s):
        return Image.new("RGBA", (px(w, s), px(h, s)), c(hexstr))
    return f


image("meter_bg_v")(solid(P.WELL))
image("meter_bg_h")(solid(P.WELL))
image("meter_bg_mcp")(solid(P.WELL))


def meter_strip(vertical, rms=False):
    """REAPER meter strip: 4 segments (low, mid, high, clip), each 4px of
    unlit color followed by 4px of lit color."""
    unlit = [P.METER_OFF, P.METER_OFF, P.METER_OFF, P.mix(P.METER_CLIP, P.METER_OFF, 0.75)]
    lit = [P.METER_LOW, P.METER_BODY, P.METER_MID, P.METER_CLIP]
    if rms:
        lit = [P.mix(x, "#000000", 0.35) for x in lit]
    seq = []
    for u, l in zip(unlit, lit):
        seq += [u] * 4 + [l] * 4

    def f(s):
        n = len(seq)
        if vertical:
            im = Image.new("RGBA", (n, 2))
            for x, col_ in enumerate(seq):
                for y in range(2):
                    im.putpixel((x, y), c(col_))
        else:
            im = Image.new("RGBA", (2, n))
            for y, col_ in enumerate(seq):
                for x in range(2):
                    im.putpixel((x, y), c(col_))
        return im
    return f


image("meter_strip_v")(meter_strip(True))
image("meter_strip_h")(meter_strip(False))
image("meter_strip_v_rms")(meter_strip(True, True))
image("meter_strip_h_rms")(meter_strip(False, True))


def meter_overlay(vertical, length=240, thick=12, pitch=3):
    """Drawn over the meter: thin dark gaps every `pitch` px turn the bar into
    LED segments."""
    def f(s):
        n, t = px(length, s), px(thick, s)
        p, g = px(pitch, s), px(1, s)
        im = Image.new("RGBA", (t, n) if vertical else (n, t), (0, 0, 0, 0))
        gap = c(P.METER_GAP)
        for start in range(p - g, n, p):
            for i in range(start, min(start + g, n)):
                for j in range(t):
                    im.putpixel((j, i) if vertical else (i, j), gap)
        return im
    return f


# Exactly the track meter's size (110x12pt), so REAPER never rescales the
# segment pattern. The mixer's meters vary in height, so they stay unsegmented.
image("meter_ol_tcp")(meter_overlay(False, 110, 12))
image("meter_ol_h")(meter_overlay(False, 110, 12))


def meter_clip(vertical, size=14):
    """Clip indicator: [unlit, lit] halves. Lit is a loud red block that
    latches until clicked."""
    def f(s):
        n, t = px(size, s), px(4, s)
        im = Image.new("RGBA", (t, 2 * n) if vertical else (2 * n, t))
        for i in range(2 * n):
            col_ = c(P.mix(P.METER_CLIP, P.METER_OFF, 0.82) if i < n else "#FF3B30")
            for j in range(t):
                im.putpixel((j, i) if vertical else (i, j), col_)
        return im
    return f


image("meter_clip_v")(meter_clip(True))
image("meter_clip_h")(meter_clip(False))


def meter_badge(glyph, col):
    def f(s):
        cv = Canvas(16, 16, s)
        cv.rrect(1, 1, 14, 14, 4, fill=c(col))
        cv.text(8, 8.2, glyph, 8.5, c(P.TEXT_ON_COLOR))
        return cv.result()
    return f


# Mute/solo state is already shown by the lit M/S buttons - no badge on the meter.
for _n in ("meter_mute", "meter_foldermute", "meter_automute", "meter_unsolo", "meter_solodim"):
    image(_n)(solid("#000000", 16, 16) if False else (lambda s: Image.new("RGBA", (px(16, s), px(16, s)), (0, 0, 0, 0))))


# ---------------------------------------------------------- transport --------

TW, TH = 30, 30


def transport_btn(glyph_fn, lit=None, w=TW, h=TH):
    def f(s):
        def draw(cv, st):
            if lit:
                cv.rrect(2, 3, w - 4, h - 6, 7, fill=c(face(st, P.mix(lit, P.PANEL, 0.78))))
                col = c(lit)
            else:
                if st != "normal":
                    cv.rrect(2, 3, w - 4, h - 6, 7, fill=c(face(st, P.CONTROL)))
                col = c(P.TEXT if st != "normal" else P.TEXT_2)
            glyph_fn(cv, col, w, h)
        return frames3(w, h, s, draw)
    return f


def g_play(cv, col, w, h):
    cx, cy = w / 2 + 1, h / 2
    cv.poly([(cx - 4.5, cy - 6), (cx + 6, cy), (cx - 4.5, cy + 6)], fill=col)


def g_stop(cv, col, w, h):
    cv.rrect(w / 2 - 5, h / 2 - 5, 10, 10, 2, fill=col)


def g_pause(cv, col, w, h):
    cv.rrect(w / 2 - 5, h / 2 - 5.5, 3.6, 11, 1.2, fill=col)
    cv.rrect(w / 2 + 1.4, h / 2 - 5.5, 3.6, 11, 1.2, fill=col)


def g_rec(cv, col, w, h):
    cv.circle(w / 2, h / 2, 5.5, fill=c(P.REC) if col[:3] != P.rgb(P.REC) else col)


def g_rec_on(cv, col, w, h):
    cv.circle(w / 2, h / 2, 5.5, fill=c(P.REC))


def g_repeat(cv, col, w, h):
    cx, cy = w / 2, h / 2
    cv.rrect(cx - 7, cy - 4.5, 14, 9, 4.5, outline=col, width=1.6)
    cv.rect(cx - 1.5, cy - 6, 3, 3, fill=(0, 0, 0, 0))
    cv.poly([(cx - 1, cy - 7.2), (cx + 2.8, cy - 4.5), (cx - 1, cy - 1.8)], fill=col)


def g_prev(cv, col, w, h):
    cx, cy = w / 2, h / 2
    cv.rrect(cx - 6, cy - 5, 2, 10, 0.8, fill=col)
    cv.poly([(cx + 5, cy - 5), (cx - 3, cy), (cx + 5, cy + 5)], fill=col)


def g_next(cv, col, w, h):
    cx, cy = w / 2, h / 2
    cv.rrect(cx + 4, cy - 5, 2, 10, 0.8, fill=col)
    cv.poly([(cx - 5, cy - 5), (cx + 3, cy), (cx - 5, cy + 5)], fill=col)


image("transport_play")(transport_btn(g_play))
image("transport_play_on")(transport_btn(g_play, lit=P.FX_ON))
image("transport_play_sync")(transport_btn(g_play))
image("transport_play_sync_on")(transport_btn(g_play, lit=P.FX_ON))
image("transport_stop")(transport_btn(g_stop))
image("transport_pause")(transport_btn(g_pause))
image("transport_pause_on")(transport_btn(g_pause, lit=P.FX_BYPASS))
image("transport_record")(transport_btn(g_rec))
image("transport_record_on")(transport_btn(g_rec_on, lit=P.REC))
image("transport_record_item")(transport_btn(g_rec))
image("transport_record_item_on")(transport_btn(g_rec_on, lit=P.REC))
image("transport_record_loop")(transport_btn(g_rec))
image("transport_record_loop_on")(transport_btn(g_rec_on, lit=P.REC))
image("transport_repeat_off")(transport_btn(g_repeat))
image("transport_repeat_on")(transport_btn(g_repeat, lit=P.ACCENT))
image("transport_home")(transport_btn(g_prev))
image("transport_previous")(transport_btn(g_prev))
image("transport_end")(transport_btn(g_next))
image("transport_next")(transport_btn(g_next))


@image("transport_bpm_bg")
def transport_bpm_bg(s):
    return Image.new("RGBA", (px(4, s), px(4, s)), (0, 0, 0, 0))


image("transport_group_bg")(transport_bpm_bg)


@image("transport_tap")
def transport_tap(s):
    return frames3(60, 20, s, lambda cv, st: cv.rrect(1, 1, 58, 18, 4, fill=c(face(st, P.PANEL))) if st != "normal" else None)


@image("transSectionBg")
def trans_section_bg(s):
    cv = Canvas(16, 16, s)
    cv.rrect(0, 0, 16, 16, 6, fill=c(P.WELL))
    return pink_border(cv.result(), px(7, s), px(7, s), px(7, s), px(7, s))


# ------------------------------------------------------------- envcp ---------

def small_toggle(label, on_col=None, w=36, h=18):
    def f(s):
        def draw(cv, st):
            if on_col:
                cv.rrect(1, 2, w - 2, h - 4, 4, fill=c(face(st, P.mix(on_col, P.PANEL, 0.75))))
                col = c(on_col)
            else:
                cv.rrect(1, 2, w - 2, h - 4, 4, fill=c(face(st, P.CONTROL)))
                col = c(P.TEXT_2 if st == "hover" else P.TEXT_3)
            cv.text(w / 2, h / 2 + 0.2, label, 7.5, col)
        return frames3(w, h, s, draw)
    return f


image("envcp_arm_off")(lambda s: recarm(s, False))
image("envcp_arm_on")(lambda s: recarm(s, True))
image("envcp_bypass_off")(small_toggle("ON"))
image("envcp_bypass_on")(small_toggle("OFF", P.FX_BYPASS))
image("envcp_learn")(small_toggle("LRN"))
image("envcp_learn_on")(small_toggle("LRN", P.ACCENT))
image("envcp_parammod")(small_toggle("MOD"))
image("envcp_parammod_on")(small_toggle("MOD", P.ACCENT))


@image("envcp_hide")
def envcp_hide(s):
    def draw(cv, st):
        if st != "normal":
            cv.rrect(1, 1, 18, 18, 5, fill=c(face(st, P.CONTROL)))
        col = c(P.TEXT if st != "normal" else P.TEXT_3)
        cv.line([(6.5, 6.5), (13.5, 13.5)], col, 1.5)
        cv.line([(13.5, 6.5), (6.5, 13.5)], col, 1.5)
    return frames3(20, 20, s, draw)




# --------------------------------------------------------- misc / lists ------

@image("tcp_recinput")
def tcp_recinput(s):
    cv = Canvas(26, 20, s)
    cv.rrect(0, 2, 26, 16, 4, fill=c(P.WELL))
    chevron(cv, 20, 10, "down", c(P.TEXT_3), 2.2, 1.2)
    return pink_border(cv.result(), px(6, s), px(5, s), px(10, s), px(5, s))


image("mcp_recinput")(tcp_recinput)


@image("tcp_namebg")
def tcp_namebg(s):
    return Image.new("RGBA", (px(6, s), px(6, s)), (0, 0, 0, 0))


image("mcp_namebg")(tcp_namebg)


def list_slot(fill_col, w=20, h=20):
    """Background for an FX / send list slot: 3 states stacked vertically,
    wrapped in a single pink stretch border."""
    def f(s):
        ims = []
        for st in STATES:
            cv = Canvas(w, h, s)
            cv.rrect(0, 1, w, h - 2, 3.5, fill=c(face(st, fill_col)))
            ims.append(cv.result())
        return pink_border(vstack(ims), px(5, s), px(5, s), px(5, s), px(5, s))
    return f


image("mcp_fxlist_norm")(list_slot(P.CONTROL))
image("mcp_fxlist_byp")(list_slot(P.mix(P.FX_BYPASS, P.PANEL, 0.8)))
image("mcp_fxlist_off")(list_slot(P.mix(P.REC, P.PANEL, 0.8)))
image("mcp_fxlist_empty")(list_slot(P.SLOT_EMPTY))
image("tcp_fxlist_norm")(list_slot(P.CONTROL))
image("tcp_fxlist_byp")(list_slot(P.mix(P.FX_BYPASS, P.PANEL, 0.8)))
image("tcp_fxlist_off")(list_slot(P.mix(P.REC, P.PANEL, 0.8)))
image("tcp_fxlist_empty")(list_slot(P.SLOT_EMPTY))
image("mcp_sendlist_norm")(list_slot(P.mix(P.ACCENT, P.PANEL, 0.82)))
image("mcp_sendlist_mute")(list_slot(P.PANEL_RAISED))
image("mcp_sendlist_empty")(list_slot(P.SLOT_EMPTY))
def send_slot(field, w=56, h=20, knob_w=22):
    """Track-panel send slot. Frame 0 is the field; REAPER paints the send
    level over it, tinted with the destination track's color. Frames 1-2
    are hover / pressed.
    The right `knob_w` points hold the send knob and never stretch."""
    def f(s):
        ims = []
        for st in STATES:
            cv = Canvas(w, h, s)
            base = face(st, field)
            # flat and nearly square: REAPER paints the level (in the destination
            # track's color) as a square-cornered fill over this field
            cv.rrect(0, 2, w, h - 4, 2, fill=c(base))
            ims.append(cv.result())
        return pink_border(vstack(ims), px(6, s), px(4, s), px(knob_w, s), px(4, s))
    return f


image("tcp_sendlist_norm")(send_slot(P.SEND_FIELD))
image("tcp_sendlist_mute")(send_slot(P.mix(P.SEND_FIELD, P.PANEL, 0.6)))
image("tcp_sendlist_empty")(lambda s: pink_border(Image.new("RGBA", (px(56, s), px(60, s)), (0, 0, 0, 0)), px(6, s), px(4, s), px(22, s), px(4, s)))


@image("mcp_fxlist_bg")
def mcp_fxlist_bg(s):
    return Image.new("RGBA", (px(4, s), px(4, s)), c(P.PANEL))


image("mcp_sendlist_bg")(mcp_fxlist_bg)
image("tcp_fxlist_bg")(mcp_fxlist_bg)
image("tcp_sendlist_bg")(mcp_fxlist_bg)


# ------------------------------------------------------ media item icons ----
# 3 frames of 14x14. "Off" states are near-invisible until hovered, so items
# stay clean; "on" states are clear colored badges.

IW = 14


def item_icon(glyph_fn, on_col=None):
    def f(s):
        def draw(cv, st):
            if on_col:
                cv.rrect(1, 1, IW - 2, IW - 2, 3, fill=c(face(st, on_col)))
                glyph_fn(cv, c(P.TEXT_ON_COLOR))
            else:
                if st == "normal":
                    cv.rrect(1, 1, IW - 2, IW - 2, 3, fill=c("#000000", 40))
                    glyph_fn(cv, c("#FFFFFF", 70))
                else:
                    cv.rrect(1, 1, IW - 2, IW - 2, 3, fill=c("#000000", 150 if st == "hover" else 190))
                    glyph_fn(cv, c("#FFFFFF", 230))
        return frames3(IW, IW, s, draw)
    return f


def gi_text(t, size=6.5):
    return lambda cv, col: cv.text(IW / 2, IW / 2 + 0.2, t, size, col)


def gi_lock(cv, col):
    cv.rrect(4, 6.5, 6, 4.5, 1, fill=col)
    cv.arc(7, 6.5, 2, -90, 90, col, 1.1)


def gi_env(cv, col):
    cv.line([(3.5, 9.5), (6, 5), (8.5, 8.5), (10.5, 4.5)], col, 1.1)


def gi_props(cv, col):
    for y in (5, 7, 9):
        cv.line([(4.5, y), (9.5, y)], col, 1)


def gi_note(cv, col):
    cv.rrect(4, 3.5, 6, 7, 1, outline=col, width=1)
    cv.line([(5.5, 6), (8.5, 6)], col, 0.8)


def gi_group(cv, col):
    cv.rrect(3.5, 3.5, 4.5, 4.5, 1, outline=col, width=1)
    cv.rrect(6, 6, 4.5, 4.5, 1, fill=col)


def gi_pool(cv, col):
    cv.circle(5.5, 7, 2.3, outline=col, width=1)
    cv.circle(8.5, 7, 2.3, outline=col, width=1)


def gi_beat(cv, col):
    cv.circle(5.5, 9, 1.8, fill=col)
    cv.line([(7, 9), (7, 3.5), (9.5, 4.5)], col, 1)


def gi_time(cv, col):
    cv.circle(7, 7, 3.4, outline=col, width=1)
    cv.line([(7, 5), (7, 7), (8.5, 8)], col, 0.9)


def gi_rank(cv, col):
    cv.poly([(4, 8.5), (7, 4.5), (10, 8.5)], fill=col)


for _n, _g, _on in (("item_mute", gi_text("M"), P.MUTE), ("item_fx", gi_text("FX", 5.5), P.FX_ON),
                    ("item_lock", gi_lock, P.FX_BYPASS), ("item_env", gi_env, P.AUTO_READ),
                    ("item_note", gi_note, P.SOLO)):
    image(_n + "_off")(item_icon(_g))
    image(_n + "_on")(item_icon(_g, _on))
image("item_props")(item_icon(gi_props))
image("item_props_on")(item_icon(gi_props, P.ACCENT))
image("item_group")(item_icon(gi_group))
image("item_group_sel")(item_icon(gi_group, P.ACCENT))
image("item_pooled")(item_icon(gi_pool))
image("item_pooled_on")(item_icon(gi_pool, P.ACCENT))
image("item_timebase_beat")(item_icon(gi_beat))
image("item_timebase_beat_on")(item_icon(gi_beat, P.ACCENT))
image("item_timebase_time")(item_icon(gi_time))
image("item_timebase_time_on")(item_icon(gi_time, P.ACCENT))
image("item_rank")(item_icon(gi_rank))
image("item_rank_up")(item_icon(gi_rank, P.FX_ON))
image("item_rank_down")(item_icon(lambda cv, col: cv.poly([(4, 5.5), (7, 9.5), (10, 5.5)], fill=col), P.FX_BYPASS))


# ----------------------------------------------------------- toolbar ---------
# 3 frames of 30x30, SF Symbols-style line icons.

TB = 30


def toolbar_icon(glyph_fn, on=False, on_col=P.ACCENT):
    def f(s):
        def draw(cv, st):
            if on:
                cv.rrect(3, 3, TB - 6, TB - 6, 6, fill=c(face(st, P.mix(on_col, P.PANEL, 0.78))))
                col = c(on_col)
            else:
                if st != "normal":
                    cv.rrect(3, 3, TB - 6, TB - 6, 6, fill=c(face(st, P.CONTROL)))
                col = c(P.TEXT if st != "normal" else P.TEXT_2)
            glyph_fn(cv, col)
        return frames3(TB, TB, s, draw)
    return f


W_ = 1.4  # stroke


def t_new(cv, col):
    cv.line([(11, 8), (17, 8), (20, 11), (20, 22), (11, 22), (11, 8)], col, W_)
    cv.line([(17, 8), (17, 11), (20, 11)], col, W_)


def t_load(cv, col):
    cv.line([(8, 20.5), (8, 10), (12.5, 10), (14, 12), (22, 12), (22, 20.5), (8, 20.5)], col, W_)


def t_save(cv, col):
    cv.line([(15, 8), (15, 17)], col, W_)
    cv.line([(11.5, 13.5), (15, 17), (18.5, 13.5)], col, W_)
    cv.line([(9, 18), (9, 21.5), (21, 21.5), (21, 18)], col, W_)


def t_projprop(cv, col):
    for y, x in ((10.5, 18), (15, 12), (19.5, 16.5)):
        cv.line([(8.5, y), (21.5, y)], col, W_)
        cv.circle(x, y, 2.1, fill=c(P.PANEL) if False else None, outline=col, width=W_)


def t_undo(cv, col):
    cv.line([(10, 12.5), (18, 12.5)], col, W_, round_caps=True)
    cv.arc(18, 16, 3.5, 0, 180, col, W_)
    cv.line([(18, 19.5), (12, 19.5)], col, W_)
    cv.line([(13, 9.5), (10, 12.5), (13, 15.5)], col, W_)


def t_redo(cv, col):
    cv.line([(20, 12.5), (12, 12.5)], col, W_)
    cv.arc(12, 16, 3.5, 180, 360, col, W_)
    cv.line([(12, 19.5), (18, 19.5)], col, W_)
    cv.line([(17, 9.5), (20, 12.5), (17, 15.5)], col, W_)


def t_metro(cv, col):
    cv.line([(12, 21.5), (13.5, 8.5), (16.5, 8.5), (18, 21.5), (12, 21.5)], col, W_)
    cv.line([(15, 18), (19.5, 10)], col, W_)


def t_xfade(cv, col):
    cv.line([(8, 20), (22, 10)], col, W_)
    cv.line([(8, 10), (22, 20)], col, W_)


def t_group(cv, col):
    cv.rrect(8, 9, 8, 8, 2, outline=col, width=W_)
    cv.rrect(14, 13, 8, 8, 2, outline=col, width=W_)


def t_ripple_off(cv, col):
    cv.rrect(7.5, 11, 6, 8, 1.5, outline=col, width=W_)
    cv.rrect(16.5, 11, 6, 8, 1.5, outline=col, width=W_)


def t_ripple_one(cv, col):
    t_ripple_off(cv, col)
    cv.line([(14.2, 8), (15.8, 8)], col, W_)
    cv.poly([(20, 6.5), (23, 8), (20, 9.5)], fill=col)
    cv.line([(15, 8), (20, 8)], col, W_)


def t_ripple_all(cv, col):
    t_ripple_one(cv, col)
    cv.line([(8, 22.5), (22, 22.5)], col, W_)


def t_envitem(cv, col):
    cv.rrect(7, 10, 16, 11, 2, outline=col, width=W_)
    cv.line([(9.5, 18), (13, 13), (16.5, 16), (20.5, 12.5)], col, W_)


def t_grid(cv, col):
    for v in (11, 15, 19):
        cv.line([(v, 8), (v, 22)], col, 1.1)
        cv.line([(8, v), (22, v)], col, 1.1)


def t_snap(cv, col):
    cv.arc(15, 15, 5.5, 90, 270, col, 2.2)
    cv.line([(9.5, 15), (9.5, 9)], col, 2.2, round_caps=False)
    cv.line([(20.5, 15), (20.5, 9)], col, 2.2, round_caps=False)
    cv.line([(8, 11), (11, 11)], col, 1)
    cv.line([(19, 11), (22, 11)], col, 1)


def t_lock(cv, col):
    cv.rrect(10, 14, 10, 8, 2, outline=col, width=W_)
    cv.arc(15, 14, 3.5, -90, 90, col, W_)


def t_relsnap(cv, col):
    t_snap(cv, col)


def t_filter(cv, col):
    cv.line([(8.5, 9.5), (21.5, 9.5), (16.5, 15.5), (16.5, 21), (13.5, 19.5), (13.5, 15.5), (8.5, 9.5)], col, W_)


def t_dock(cv, col):
    cv.rrect(8, 9, 14, 12, 2, outline=col, width=W_)
    cv.line([(8.5, 17), (21.5, 17)], col, W_)


def t_quant(cv, col):
    for x, y in ((10, 18), (14, 12), (18, 16), (22, 11)):
        cv.rrect(x - 1.5, y, 3, 22 - y, 1, fill=col)


def t_blank(cv, col):
    pass


def t_revert(cv, col):
    cv.arc(15, 15, 6, -60, 240, col, W_)
    cv.poly([(8.5, 9), (12, 12.5), (8, 13.5)], fill=col)


def t_replace(cv, col):
    cv.rrect(8, 11, 14, 8, 2, outline=col, width=W_)
    cv.line([(12, 15), (18, 15)], col, W_)


for _n, _g in (("new", t_new), ("load", t_load), ("save", t_save), ("projprop", t_projprop),
               ("undo", t_undo), ("redo", t_redo), ("revert", t_revert), ("blank", t_blank),
               ("replacemode", t_replace), ("midi_step", t_quant)):
    image("toolbar_" + _n)(toolbar_icon(_g))
for _n, _g in (("metro", t_metro), ("xfade", t_xfade), ("group", t_group), ("envitem", t_envitem),
               ("grid", t_grid), ("snap", t_snap), ("lock", t_lock), ("relsnap", t_relsnap),
               ("filter", t_filter), ("dock", t_dock), ("quant", t_quant),
               ("midi_itemsel", t_group), ("midi_tracksel", t_ripple_off)):
    image("toolbar_%s_off" % _n)(toolbar_icon(_g))
    image("toolbar_%s_on" % _n)(toolbar_icon(_g, on=True))
def t_razor(cv, col):
    cv.line([(9, 21), (21, 9)], col, W_)
    cv.poly([(17, 9), (21, 9), (21, 13)], fill=col)
    cv.rrect(8, 18, 4, 4, 1, fill=col)


def t_marquee(cv, col):
    for x0, y0, x1, y1 in ((8, 9, 12, 9), (14, 9, 18, 9), (20, 9, 22, 9), (8, 21, 12, 21), (14, 21, 18, 21), (20, 21, 22, 21),
                           (8, 11, 8, 14), (8, 16, 8, 19), (22, 11, 22, 14), (22, 16, 22, 19)):
        cv.line([(x0, y0), (x1, y1)], col, 1.2)


for _n, _g in (("razor", t_razor), ("marquee_cursor_selection", t_marquee)):
    image("toolbar_%s_off" % _n)(toolbar_icon(_g))
    image("toolbar_%s_on" % _n)(toolbar_icon(_g, on=True))
image("toolbar_filter_solo")(toolbar_icon(t_filter, on=True, on_col=P.SOLO))
image("toolbar_ripple_off")(toolbar_icon(t_ripple_off))
image("toolbar_ripple_one")(toolbar_icon(t_ripple_one, on=True, on_col=P.FX_BYPASS))
image("toolbar_ripple_all")(toolbar_icon(t_ripple_all, on=True, on_col=P.REC))


# Master mono check: labelled, lit (orange = "you are not hearing stereo") when on.
image("track_stereo")(lambda s: pill_button(s, "Mono", None, w=42, text_size=9))
image("track_mono")(lambda s: pill_button(s, "Mono", P.FX_BYPASS, w=42, text_size=9))
image("mcp_stereo")(lambda s: pill_button(s, "Mono", None, w=42, text_size=9))
image("mcp_mono")(lambda s: pill_button(s, "Mono", P.FX_BYPASS, w=42, text_size=9))


def generate(outdir, scale):
    os.makedirs(outdir, exist_ok=True)
    for name, fn in sorted(REGISTRY.items()):
        fn(scale).save(os.path.join(outdir, name + ".png"), optimize=True)
    return len(REGISTRY)
