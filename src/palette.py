"""The Beautiful Reaper palette.

One source of truth for every color in the theme: the PNG generator, the
.ReaperTheme color file and the WALTER layout (rtconfig.txt) all read from here.

Dark graphite surfaces, one accent, and semantic colors borrowed from Apple's
system palette (and Logic Pro's conventions): mute is blue, solo is yellow,
record is red, automation read is green.
"""

# Surfaces, darkest to lightest.
BG_DEEP = "#141517"      # empty arrange / behind everything
BG_LANE = "#1B1C1F"      # arrange track lanes
BG_LANE_ALT = "#1E1F22"  # alternate lane
BG_LANE_SEL = "#24262A"  # lane of a selected track
PANEL = "#232427"        # track panels, mixer strips, transport
PANEL_SEL = "#2F3136"    # selected track panel
PANEL_RAISED = "#2B2C30" # grouped surfaces (master, headers)
CONTROL = "#36383D"      # button face
CONTROL_HOVER = "#42444A"
CONTROL_PRESS = "#2C2E32"
KNOB = "#56585F"         # knob caps
SLOT_EMPTY = "#1F2023"   # empty insert/send slot: present, but quiet
WELL = "#141517"         # inset wells: fader tracks, meters, inputs
DIVIDER = "#0E0F10"      # 1px separators

# Text.
TEXT = "#ECECEF"
TEXT_2 = "#A0A1A7"
TEXT_3 = "#6A6B71"
TEXT_ON_COLOR = "#141517"

# Accent + semantic colors.
ACCENT = "#0A84FF"
MUTE = "#409CFF"
SOLO = "#FFD60A"
REC = "#FF453A"
FX_ON = "#30D158"
FX_BYPASS = "#FF9F0A"
MONITOR = "#FF9F0A"

AUTO_READ = "#30D158"
AUTO_WRITE = "#FF453A"
AUTO_TOUCH = "#FF9F0A"
AUTO_LATCH = "#BF5AF2"
AUTO_PREVIEW = "#64D2FF"

# Meters (bottom -> top).
METER_OFF = "#303237"    # unlit meter segments (doubles as the fader track)
METER_LOW = "#30D158"
METER_MID = "#FFD60A"
METER_HIGH = "#FF9F0A"
METER_CLIP = "#FF453A"

# Arrange view.
ITEM_WAVE = "#17181A"     # waveforms: dark ink on the track-colored region
PLAYHEAD = "#F2F2F7"
EDIT_CURSOR = "#0A84FF"
GRID_BAR = "#2C2D31"
GRID_BEAT = "#222326"
TIME_SEL = "#0A84FF"
LOOP = "#0A84FF"
MARKER = "#FF9F0A"
REGION = "#5E5CE6"


def rgb(hexstr):
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(hexstr, a=255):
    return rgb(hexstr) + (a,)


def mix(a, b, t):
    """Blend two hex colors; t=0 -> a, t=1 -> b."""
    ra, rb = rgb(a), rgb(b)
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))
