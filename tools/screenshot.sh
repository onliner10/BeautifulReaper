#!/usr/bin/env bash
# Render REAPER with a theme under Xvfb and capture a screenshot.
# Usage: screenshot.sh REAPER_DIR THEME_FILE PROJECT.rpp OUT.png [WxH] [extra reaper.ini lines file]
set -euo pipefail
REAPER_DIR=$1; THEME=$2; RPP=$3; OUT=$4; GEOM=${5:-1920x1080}; EXTRA=${6:-}
W=${GEOM%x*}; H=${GEOM#*x}
WORK=$(mktemp -d)
export HOME=$WORK/home
CFG=$HOME/.config/REAPER
mkdir -p "$CFG/ColorThemes"
cp "$THEME" "$CFG/ColorThemes/"
# Optional license (base64 of the .rk key text) so the evaluation nag stays away.
if [ -n "${FME_REAPER_LICENSE_B64:-}" ]; then
  (umask 077; echo "$FME_REAPER_LICENSE_B64" | base64 -d > "$CFG/reaper-license.rk")
fi
cat > "$CFG/reaper.ini" <<INI
[REAPER]
lastthemefn5=$CFG/ColorThemes/$(basename "$THEME")
wnd_x=0
wnd_y=0
wnd_w=$W
wnd_h=$H
wnd_state=0
mixwnd_vis=${MIXER:-0}
mixwnd_dock=1
leftpanewid=${TCPW:-470}
splash=0
verchk=0
newprojtmpl=
errnowarn=5
linux_audio_mode=2
linux_audio_srate=44100
linux_audio_bsize=512
INI
[ -n "$EXTRA" ] && cat "$EXTRA" >> "$CFG/reaper.ini"
DISP=:$((RANDOM % 400 + 100))
Xvfb $DISP -screen 0 ${W}x${H}x24 >/dev/null 2>&1 &
XPID=$!
sleep 1
export DISPLAY=$DISP
"$REAPER_DIR/reaper" -newinst -nosplash "$RPP" >"$WORK/reaper.log" 2>&1 &
RPID=$!
sleep 9
# Dismiss the evaluation nag (its "Still Evaluating" button unlocks after a countdown).
for _ in $(seq 1 30); do
  A=$(xdotool search --onlyvisible --name "^About REAPER" 2>/dev/null | head -1 || true)
  [ -z "$A" ] && break
  eval "$(xdotool getwindowgeometry --shell "$A")"
  xdotool mousemove $((X + 488)) $((Y + 395)) click 1
  sleep 1
done
sleep 0.5
M=$(xdotool search --onlyvisible --name " - REAPER v" | head -1)
xdotool windowmove "$M" 0 0 windowsize "$M" "$W" "$H"
xdotool mousemove $((W - 1)) $((H - 1))
# PLAY=1: start playback and let meters settle before capturing.
if [ "${PLAY:-0}" = 1 ]; then
  xdotool mousemove $((W / 2)) $((H / 2)) click 1
  sleep 0.3; xdotool key space; sleep "${PLAY_SECS:-3}"
fi
[ -n "${PRE_SHOT:-}" ] && eval "$PRE_SHOT"
sleep 3
import -window root "$OUT"
kill $RPID 2>/dev/null || true
sleep 0.5; kill -9 $RPID 2>/dev/null || true
kill $XPID 2>/dev/null || true
rm -rf "$WORK"
