"""Writes the [color theme] + [REAPER] sections of the .ReaperTheme file."""
import palette as P
from palette import mix

# REAPER encodes draw modes as 0x20000 + opacity * 0x10000 + mode
# (mode: 0 normal, 1 add, 2 overlay, 3 multiply, ...).
def blend(opacity, mode=0):
    return 0x20000 + (int(round(opacity * 256)) << 8) + mode


def col(hexstr):
    r, g, b = P.rgb(hexstr)
    return r | (g << 8) | (b << 16)


def theme_colors():
    t = {}

    def s(k, v):
        t[k] = col(v) if isinstance(v, str) else v

    # --- main window / dialogs (Windows + macOS use these) ---
    s("col_main_bg2", P.PANEL)
    s("col_main_text2", P.TEXT_2)
    s("col_main_textshadow", P.PANEL)
    s("col_main_3dhl", P.BG_DEEP)
    s("col_main_3dsh", P.BG_DEEP)
    s("col_main_resize2", P.DIVIDER)
    s("col_main_text", P.TEXT)
    s("col_main_bg", P.PANEL)
    t["col_main_bg"] = col(P.BG_DEEP) - 0x100000000 + 0x80000000  # high bit: theme overrides OS
    s("col_main_editbk", P.WELL)
    s("col_nodarkmodemiscwnd", 1)
    s("col_transport_editbk", P.WELL)
    s("col_toolbar_text", P.TEXT_2)
    s("col_toolbar_text_on", P.ACCENT)
    s("col_toolbar_frame", P.PANEL)
    s("toolbararmed_color", P.REC)
    s("toolbararmed_drawmode", blend(0.75))
    s("io_text", P.TEXT)
    s("io_3dhl", P.PANEL_RAISED)
    s("io_3dsh", P.DIVIDER)
    # generic lists (track manager, FX browser, region manager...)
    s("genlist_bg", P.BG_LANE)
    s("genlist_fg", P.TEXT)
    s("genlist_grid", P.PANEL)
    s("genlist_selbg", mix(P.ACCENT, P.BG_LANE, 0.35))
    s("genlist_selfg", "#FFFFFF")
    s("genlist_seliabg", P.CONTROL)
    s("genlist_seliafg", P.TEXT)
    s("genlist_hilite", P.ACCENT)
    s("genlist_hilite_sel", "#FFFFFF")
    s("col_buttonbg", P.CONTROL)

    # --- track panels ---
    s("col_tcp_text", P.TEXT)
    s("col_tcp_textsel", "#FFFFFF")
    s("col_seltrack", P.PANEL_SEL)
    s("col_seltrack2", P.PANEL_SEL)
    s("tcplocked_color", P.BG_DEEP)
    s("tcplocked_drawmode", blend(0.5))
    s("col_tracklistbg", P.BG_DEEP)
    s("col_mixerbg", P.BG_DEEP)
    s("col_arrangebg", P.BG_DEEP)
    s("arrange_vgrid", P.BG_LANE)
    s("col_fadearm", P.REC)
    s("col_fadearm2", P.REC)
    s("col_fadearm3", P.REC)

    # --- timeline / ruler ---
    s("col_tl_fg", P.TEXT_2)
    s("col_tl_fg2", P.TEXT_3)
    s("col_tl_bg", P.PANEL)
    s("col_tl_bgsel", P.TIME_SEL)
    s("timesel_drawmode", blend(0.10))
    s("col_tl_bgsel2", P.TIME_SEL)
    s("col_trans_bg", P.PANEL)
    s("col_trans_fg", P.TEXT)
    s("playrate_edited", P.FX_BYPASS)
    s("selitem_dot", "#FFFFFF")

    # --- media items ---
    s("col_mi_label", P.TEXT_ON_COLOR)
    s("col_mi_label_sel", "#000000")
    s("col_mi_label_float", P.TEXT)
    s("col_mi_label_float_sel", "#FFFFFF")
    s("col_mi_bg", "#4A4C52")
    s("col_mi_bg2", "#4A4C52")
    s("col_tr1_itembgsel", "#6A6D75")
    s("col_tr2_itembgsel", "#6A6D75")
    s("itembg_drawmode", blend(1.0))
    s("col_tr1_peaks", P.ITEM_WAVE)
    s("col_tr2_peaks", P.ITEM_WAVE)
    s("col_tr1_ps2", P.ITEM_WAVE)
    s("col_tr2_ps2", P.ITEM_WAVE)
    s("col_peaksedge", P.ITEM_WAVE)
    s("col_peaksedge2", P.ITEM_WAVE)
    s("col_peaksedgesel", "#000000")
    s("col_peaksedgesel2", "#000000")
    s("cc_chase_drawmode", blend(0.25))
    s("col_peaksfade", "#FFFFFF")
    s("col_peaksfade2", "#FFFFFF")
    s("col_mi_fades", "#000000")
    s("fadezone_color", "#000000")
    s("fadezone_drawmode", blend(0.22))
    s("fadearea_color", "#000000")
    s("fadearea_drawmode", blend(0.0))
    s("col_mi_fade2", "#FFFFFF")
    s("col_mi_fade2_drawmode", blend(0.35))
    s("item_grouphl", P.ACCENT)
    s("col_offlinetext", P.REC)
    s("col_stretchmarker", P.TEXT_2)
    s("col_stretchmarker_h0", P.TEXT_2)
    s("col_stretchmarker_h1", P.FX_BYPASS)
    s("col_stretchmarker_h2", P.REC)
    s("col_stretchmarker_b", "#FFFFFF")
    s("col_stretchmarkerm", P.FX_ON)
    s("col_stretchmarker_text", P.TEXT)
    s("col_stretchmarker_tm", P.FX_ON)
    s("take_marker", P.SOLO)
    s("take_marker_sel", "#FFFFFF")
    s("selitem_tag", "#FFFFFF")
    s("activetake_tag", P.ACCENT)

    # --- arrange lanes ---
    s("col_tr1_bg", P.BG_LANE)
    s("col_tr2_bg", P.BG_LANE_ALT)
    s("selcol_tr1_bg", P.BG_LANE_SEL)
    s("selcol_tr2_bg", P.BG_LANE_SEL)
    s("track_lane_tabcol", P.CONTROL)
    s("track_lanesolo_tabcol", P.SOLO)
    s("track_lanesolo_text", P.TEXT_ON_COLOR)
    s("track_lane_gutter", P.PANEL)
    s("track_lane_gutter_drawmode", blend(0.5))
    s("col_tr1_divline", P.BG_DEEP)
    s("col_tr2_divline", P.BG_DEEP)
    s("col_envlane1_divline", P.DIVIDER)
    s("col_envlane2_divline", P.DIVIDER)
    s("mute_overlay_col", P.BG_DEEP)
    s("mute_overlay_mode", blend(0.55))
    s("inactive_take_overlay_col", P.BG_DEEP)
    s("inactive_take_overlay_mode", blend(0.6))
    s("locked_overlay_col", "#000000")
    s("locked_overlay_mode", blend(0.25))
    s("marquee_fill", P.ACCENT)
    s("marquee_drawmode", blend(0.15))
    s("marquee_outline", P.ACCENT)
    s("marqueezoom_fill", "#FFFFFF")
    s("marqueezoom_drawmode", blend(0.12))
    s("marqueezoom_outline", "#FFFFFF")
    s("areasel_fill", P.ACCENT)
    s("areasel_drawmode", blend(0.12))
    s("areasel_outline", P.ACCENT)
    s("areasel_outlinemode", blend(0.9))
    s("linkedlane_fill", P.ACCENT)
    s("linkedlane_fillmode", blend(0.1))
    s("linkedlane_outline", P.ACCENT)
    s("linkedlane_outlinemode", blend(0.7))
    s("linkedlane_unsynced", P.FX_BYPASS)
    s("linkedlane_unsynced_mode", blend(0.7))
    s("col_cursor", P.EDIT_CURSOR)
    s("col_cursor2", P.EDIT_CURSOR)
    s("playcursor_color", P.PLAYHEAD)
    s("playcursor_drawmode", blend(0.9))
    s("col_gridlines", P.GRID_BAR)
    s("col_gridlines1dm", blend(1.0))
    s("col_gridlines2", P.GRID_BEAT)
    s("col_gridlines2dm", blend(1.0))
    s("col_gridlines3", P.GRID_BEAT)
    s("col_gridlines3dm", blend(0.6))
    s("guideline_color", P.ACCENT)
    s("guideline_drawmode", blend(0.8))
    s("mouseitem_color", "#FFFFFF")
    s("mouseitem_mode", blend(0.06))

    # --- markers / regions / tempo ---
    s("region", P.REGION)
    s("region_lane_bg", P.PANEL)
    s("region_lane_text", P.TEXT)
    s("region_edge", P.REGION)
    s("region_edge_sel", "#FFFFFF")
    s("marker", P.MARKER)
    s("marker_lane_bg", P.PANEL)
    s("marker_lane_text", P.TEXT)
    s("marker_edge", P.MARKER)
    s("marker_edge_sel", "#FFFFFF")
    s("col_tsigmark", P.TEXT_2)
    s("ts_lane_bg", P.PANEL)
    s("ts_lane_text", P.TEXT_2)
    s("timesig_sel_bg", P.ACCENT)

    # --- routing, meters ---
    s("col_routinghl1", P.ACCENT)
    s("col_routinghl2", P.FX_ON)
    s("col_routingact", P.FX_ON)
    s("col_vudoint", 0)
    s("col_vuclip", P.METER_CLIP)
    s("col_vutop", P.METER_HIGH)
    s("col_vumid", P.METER_MID)
    s("col_vubot", P.METER_LOW)
    s("col_vuintcol", P.WELL)
    s("col_vumidi", P.AUTO_PREVIEW)
    s("col_vuind1", P.WELL)
    s("col_vuind2", mix(P.METER_LOW, P.WELL, 0.5))
    s("col_vuind3", P.METER_LOW)
    s("col_vuind4", P.METER_MID)
    s("vu_gr_bgcol", P.WELL)
    s("vu_gr_fgcol", P.FX_BYPASS)

    # --- mixer lists ---
    s("mcp_sends_normal", P.TEXT)
    s("mcp_sends_muted", P.TEXT_3)
    s("mcp_send_midihw", P.AUTO_PREVIEW)
    s("mcp_sends_levels", P.ACCENT)
    s("mcp_fx_normal", P.TEXT)
    s("mcp_fx_bypassed", P.FX_BYPASS)
    s("mcp_fx_offlined", P.REC)
    s("mcp_fxparm_normal", P.TEXT_2)
    s("mcp_fxparm_bypassed", P.FX_BYPASS)
    s("mcp_fxparm_offlined", P.REC)
    s("tcp_list_scrollbar", P.TEXT_3)
    s("tcp_list_scrollbar_mode", blend(0.5))
    s("tcp_list_scrollbar_mouseover", P.TEXT_2)
    s("tcp_list_scrollbar_mouseover_mode", blend(0.8))
    s("mcp_list_scrollbar", P.TEXT_3)
    s("mcp_list_scrollbar_mode", blend(0.5))
    s("mcp_list_scrollbar_mouseover", P.TEXT_2)
    s("mcp_list_scrollbar_mouseover_mode", blend(0.8))

    # --- MIDI editor ---
    s("midi_rulerbg", P.PANEL)
    s("midi_rulerfg", P.TEXT_2)
    s("midi_grid2", "#FFFFFF")
    s("midi_griddm2", blend(0.10))
    s("midi_grid3", "#FFFFFF")
    s("midi_griddm3", blend(0.05))
    s("midi_grid1", "#FFFFFF")
    s("midi_griddm1", blend(0.16))
    s("midi_trackbg1", P.BG_LANE_ALT)
    s("midi_trackbg2", P.BG_LANE)
    s("midi_trackbg_outer1", P.BG_DEEP)
    s("midi_trackbg_outer2", P.BG_DEEP)
    s("midi_selpitch1", mix(P.ACCENT, P.BG_LANE, 0.75))
    s("midi_selpitch2", mix(P.ACCENT, P.BG_LANE, 0.8))
    s("midi_selbg", "#FFFFFF")
    s("midi_selbg_drawmode", blend(0.06))
    s("midi_gridhc", "#000000")
    s("midi_gridhcdm", blend(0.35))
    s("midi_gridh", "#000000")
    s("midi_gridhdm", blend(0.25))
    s("midi_ccbut", P.TEXT_2)
    s("midi_ccbut_text", P.TEXT)
    s("midi_ccbut_arrow", P.TEXT_2)
    s("midioct", P.DIVIDER)
    s("midi_inline_trackbg1", P.BG_LANE_ALT)
    s("midi_inline_trackbg2", P.BG_LANE)
    s("midioct_inline", P.DIVIDER)
    s("midi_endpt", P.TEXT_2)
    s("midi_notebg", P.BG_DEEP)
    s("midi_notefg", "#FFFFFF")
    s("midi_notemute", P.TEXT_3)
    s("midi_notemute_sel", P.TEXT_2)
    s("midi_itemctl", P.TEXT_2)
    s("midi_ofsn", P.TEXT_3)
    s("midi_ofsnsel", P.TEXT)
    s("midi_editcurs", P.EDIT_CURSOR)
    s("midi_pkey1", "#F2F2F5")
    s("midi_pkey2", "#1C1D20")
    s("midi_pkey3", P.ACCENT)
    s("midi_noteon_flash", P.ACCENT)
    s("midi_leftbg", P.PANEL)
    s("midifont_col_light_unsel", "#FFFFFF")
    s("midifont_col_dark_unsel", "#000000")
    s("midifont_mode_unsel", blend(0.6))
    s("midifont_col_light", "#FFFFFF")
    s("midifont_col_dark", "#000000")
    s("midifont_mode", blend(0.9))
    s("score_bg", "#F2F2F5")
    s("score_fg", "#1C1D20")
    s("score_sel", P.ACCENT)
    s("score_timesel", mix(P.ACCENT, "#FFFFFF", 0.85))
    s("score_loop", P.SOLO)
    s("midieditorlist_bg", P.BG_LANE)
    s("midieditorlist_fg", P.TEXT)
    s("midieditorlist_grid", P.PANEL)
    s("midieditorlist_selbg", mix(P.ACCENT, P.BG_LANE, 0.35))
    s("midieditorlist_selfg", "#FFFFFF")
    s("midieditorlist_seliabg", P.CONTROL)
    s("midieditorlist_seliafg", P.TEXT)
    s("midieditorlist_bg2", P.PANEL)
    s("midieditorlist_fg2", P.TEXT_2)
    s("midieditorlist_selbg2", P.CONTROL)
    s("midieditorlist_selfg2", P.TEXT)

    # --- media explorer ---
    s("col_explorer_sel", P.ACCENT)
    s("col_explorer_seldm", blend(0.3))
    s("col_explorer_seledge", P.ACCENT)
    s("explorer_grid", P.PANEL)
    s("explorer_pitchtext", P.TEXT)

    # --- docker / tabs ---
    s("docker_shadow", P.DIVIDER)
    s("docker_selface", P.PANEL_SEL)
    s("docker_unselface", P.PANEL)
    s("docker_text", P.TEXT_2)
    s("docker_text_sel", P.TEXT)
    s("docker_bg", P.BG_DEEP)
    s("windowtab_bg", P.BG_DEEP)

    # --- envelopes ---
    s("auto_item_unsel", P.TEXT_3)
    s("col_env1", P.AUTO_READ)       # volume (pre-FX)
    s("col_env2", P.AUTO_READ)       # volume
    s("env_trim_vol", P.TEXT_2)
    s("col_env3", P.AUTO_PREVIEW)    # pan (pre-FX)
    s("col_env4", P.AUTO_PREVIEW)    # pan
    s("env_track_mute", P.MUTE)
    s("col_env5", P.FX_BYPASS)
    s("col_env6", P.FX_BYPASS)
    s("col_env7", P.AUTO_LATCH)
    s("col_env8", P.AUTO_LATCH)
    s("col_env9", P.AUTO_READ)
    s("col_env10", P.AUTO_PREVIEW)
    s("env_sends_mute", P.MUTE)
    s("col_env11", P.TEXT_2)
    s("col_env12", P.SOLO)
    s("col_env13", P.AUTO_TOUCH)
    s("col_env14", P.AUTO_LATCH)
    s("col_env15", P.AUTO_PREVIEW)
    s("col_env16", P.FX_BYPASS)
    s("env_item_vol", P.AUTO_READ)
    s("env_item_pan", P.AUTO_PREVIEW)
    s("env_item_mute", P.MUTE)
    s("env_item_pitch", P.AUTO_LATCH)

    # --- routing matrix / wiring ---
    s("wiring_grid2", P.PANEL)
    s("wiring_grid", P.BG_LANE)
    s("wiring_border", P.TEXT_3)
    s("wiring_tbg", P.PANEL)
    s("wiring_ticon", P.TEXT)
    s("wiring_recbg", mix(P.REC, P.PANEL, 0.7))
    s("wiring_recitem", P.REC)
    s("wiring_media", P.ACCENT)
    s("wiring_recv", P.TEXT_2)
    s("wiring_send", P.TEXT_2)
    s("wiring_fader", P.ACCENT)
    s("wiring_parent", P.TEXT_2)
    s("wiring_parentwire_border", P.TEXT_3)
    s("wiring_parentwire_master", P.TEXT)
    s("wiring_parentwire_folder", P.TEXT_2)
    s("wiring_pin_normal", P.TEXT_2)
    s("wiring_pin_connected", P.FX_ON)
    s("wiring_pin_disconnected", P.TEXT_3)
    s("wiring_horz_col", P.CONTROL)
    s("wiring_sendwire", P.ACCENT)
    s("wiring_hwoutwire", P.TEXT_2)
    s("wiring_recinputwire", P.REC)
    s("wiring_hwout", P.CONTROL)
    s("wiring_recinput", P.CONTROL)
    s("wiring_activity", P.FX_ON)

    # --- groups: Apple system colors, cycled ---
    s("autogroup", "#FFFFFF")
    group_cols = ["#FF453A", "#FF9F0A", "#FFD60A", "#30D158", "#64D2FF", "#0A84FF", "#5E5CE6", "#BF5AF2",
                  "#FF375F", "#AC8E68", "#66D4CF", "#98989D"]
    for i in range(64):
        s("group_%d" % i, group_cols[i % len(group_cols)])

    s("pinned_track_gap", P.BG_DEEP)
    s("pinned_track_gap_unreachable", mix(P.REC, P.BG_DEEP, 0.5))
    s("pinned_track_gap_mode", blend(1.0))
    return t


def logfont(size_px, weight=500, face="Inter"):
    """Hex-encoded Win32 LOGFONT, as REAPER stores fonts in .ReaperTheme."""
    import struct
    b = struct.pack("<iiiii", -size_px, 0, 0, 0, weight)
    b += bytes([0, 0, 0, 0, 3, 2, 1, 2])  # italic, underline, strike, charset, out/clip precision, quality, pitch
    name = face.encode("ascii")[:31]
    b += name + bytes(32 - len(name))
    b += bytes([sum(b) & 0xFF])
    return b.hex().upper()


# Font slots referenced from rtconfig.txt (".font" values 1..5; 6..10 / 11..15 are
# the 1.5x / 2x versions). Inter ships with REAPER 7.
FONT_SIZES = [
    (1, 10, 500),   # tiny: meter scale, send levels
    (2, 11, 500),   # small: values, dB readouts
    (3, 12, 500),   # body: fx list, input names
    (4, 13, 500),   # track names
    (5, 13, 600),   # emphasis: master strip name
]


def fonts():
    out = {"lb_font": logfont(12, 500), "lb_font2": logfont(11, 500),
           "tl_font": logfont(11, 500), "mi_font": logfont(11, 500),
           "trans_font": logfont(22, 500), "user_font0": logfont(13, 500)}
    for idx, size, weight in FONT_SIZES:
        out["user_font%d" % idx] = logfont(size, weight)
        out["user_font%d" % (idx + 5)] = logfont(round(size * 1.5), weight)
        out["user_font%d" % (idx + 10)] = logfont(size * 2, weight)
    return out


def write_theme_file(path, img_dir_name):
    lines = ["[color theme]"]
    for k, v in theme_colors().items():
        lines.append("%s=%d" % (k, v))
    lines.append("[REAPER]")
    lines.append("ui_img=%s" % img_dir_name)
    for k, v in fonts().items():
        lines.append("%s=%s" % (k, v))
    with open(path, "w", newline="\r\n") as f:
        f.write("\n".join(lines) + "\n")
