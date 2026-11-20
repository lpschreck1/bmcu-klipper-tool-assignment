# /// script
# requires-python = ">=3.12"
#
# [tool.orcaslicer.plugin]
# name = "BMCU-Klipper Tool Assignment"
# description = "For the Snapmaker U1 with BMCU-Klipper. On every export it reads the printer's live tool setup, puts the print's colors on the tools that need the fewest filament swaps, and lets you adjust it in a window. Includes printer checks, backup spools, unload buttons, several printers, and bed leveling / flow calibration / timelapse for Orca's Print button. Adds itself to Snapmaker U1 process profiles and includes a BMCU panel beside the 3D view."
# author = "Lawrence Schreck and Claude (Anthropic)"
# version = "1.1.0"
# type = "slicing-pipeline"
# ///
#
# BMCU-Klipper Tool Assignment
# Copyright (C) 2026 Lawrence Schreck
# Written with the help of Claude (Anthropic).
#
# This program is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details: <https://www.gnu.org/licenses/>.
r"""
BMCU-Klipper Tool Assignment - OrcaSlicer 2.5+ plugin for the Snapmaker U1 with BMCU-Klipper.
The plugin version of bmcu_klipper_remap.py: the same layout search and file changes, with
the windows drawn by OrcaSlicer. Nothing else to install.

SETUP
  1. Plugins > Install from file > this file.
  2. Approve the permission prompt OrcaSlicer shows when the plugin loads. It asks once for
     everything: running threads, and network access to your saved printers plus the
     print host of each Snapmaker U1 printer profile in OrcaSlicer. Each person who
     installs it is asked about their own printers; no address is built into the file.
  3. Pick a Snapmaker U1 printer profile. The plugin adds itself to the process profile's
     "Slicing Pipeline Plugin" setting (on a profile switch, a new or opened project, added
     objects or a plate change), and a notification says so: save the profile to keep it.
     To turn that off: Plugins > this plugin > Config > add_to_process_profiles = false.
  4. If bmcu_klipper_remap.py is still under Process > Post-processing scripts, remove it.
     (If both are set, the plugin sees the file was already done and leaves it alone.)

  First run: with no saved printer, a setup window offers the address from your printer
  profile, or searches the network (mDNS, plus a quick scan of every local /24 for the
  BMCU panel port 8291; "Also search subnet" adds others, e.g. 192.168.10.0/24, up to a
  /20 each). The search needs Full access for this plugin in the Plugins window, because
  it has to reach every address on the network; without it, type the address. It reads
  BMCU-Klipper's setup from the printer, saves it, and opens Printer tools to check.
  After adding a printer that wasn't in the first prompt, restart OrcaSlicer once so it
  can approve that printer as a whole (until then it may ask again for some requests).

  Settings (bmcu_klipper_remap.settings.json) and the log (bmcu_klipper_remap.log) are in
  the plugin's folder. "Cancel export" in the window stops the export.

  Export G-code: the window has Save file and Save & print (this plugin uploads and starts
  the print). Orca's Print / Send button: the window has Save & send; it checks the printer,
  sets the ticked bed leveling, flow calibration and timelapse on the U1, then OrcaSlicer
  uploads and starts the file.

  The BMCU panel (routing, loaded filament, unloads) beside the 3D view: Plugins > this
  plugin > "Show the BMCU panel" > Run.

  Safety guard (recommended): FIRST line of Printer settings -> Machine G-code ->
  Machine start G-code:
      SET_GCODE_VARIABLE MACRO=BMCU_REMAP_NOT_RUN VARIABLE=x VALUE=0
  If a file reaches the printer without passing through this plugin, Klipper errors on
  that line and the print stops before heating. The plugin deletes it.

WHAT IT DOES ON EVERY EXPORT
  1. Re-reads the tool setup from the printer (a few seconds at most), and again each
     time the window is rebuilt: which head each BMCU channel is routed to, the filament
     type and color in every tool, what's loaded in each head, and whether a stock
     feeder's filament is sitting in a head the BMCU also feeds. Tools you turned off and
     your slot layout are kept. If the printer can't be reached, the saved setup is used
     (with a notice). If it answers but BMCU-Klipper isn't running, the file is left
     exactly as OrcaSlicer wrote it (with a warning).
  2. Reads which filament slots the print uses, how much of each, and the order of
     every tool change.
  3. Works out which tool each color should go on. Tools on different heads switch for
     free; two colors on the SAME head need an unload/load every time the print
     alternates between them. The fastest layout wins; ties go to tools whose current
     filament is closest in color (and same type), then your slot layout, then fewest
     head changes. The search places the colors that alternate most first, improves
     that layout, then proves it's the best possible with branch-and-bound. It stops
     after 30 s (with a notice) and keeps the best layout found.
  4. More colors than tools: the closest colors (same filament type first) are combined
     onto shared tools - only as many as needed, preferring pairs that alternate most.
  5. Different filament types are kept on separate heads by default (Printer tools).
  6. Shows the assignment window, then rewrites the file to your choice.

THE ASSIGNMENT WINDOW
  One row per tool showing where its filament is and the color(s) assigned to it. Each
  color has its own menu: swap it with another tool's color(s), move it to an unused
  tool, or share a tool (warned). Tools that can't be used are listed with the reason.
  Buttons: Recommended, Reset to default, Printer tools..., Save file, Save & print,
  Cancel export. Tool heads: Unload buttons for filament loaded in a head (queued, they
  wait while the printer is busy and are refused while it prints) and Refresh from
  printer, "route is UNCERTAIN" buttons (Loaded in the head / Parked in the BMCU / Empty)
  that confirm where that filament really is, and what happens to the BMCU filament
  after the print (BMCU decides by default, or Unload, Keep loaded, As sliced). Under
  each BMCU tool used, "If it runs out" picks the unused spool the print continues
  from. Save & print re-checks the printer first (filament and type loaded where
  needed, routing, uncertain routes).

SEVERAL PRINTERS
  Every printer you add keeps its own tools, slot layout and Printer tools options. The
  window opens on the printer you used last; the Printer list at the top switches to
  another (it re-reads that printer and redoes the layout), "Add printer..." finds and
  adds one, "Remove" forgets the one shown. "Also print on" sends the same file to other
  saved printers with Save & print: the tool layout only fits printers whose tools sit
  on the same heads with the right filament loaded, so all of them are checked first.

PRINTER TOOLS
  BMCU-Klipper's live setup: which T number each channel is, which head it's routed to,
  and what's loaded. Untick tools the optimizer must not use and set your slot layout.
  BMCU-Klipper owns any head with BMCU channels routed to it, so that head's stock
  feeder is locked (detach the channels in the BMCU panel to use it). Stock filament
  sitting in a head blocks that head's BMCU channels until it's unloaded and pulled out.
  Options: prefer tools already holding the print's colors; keep filament types on
  separate heads; have the printer refuse to start if a channel is labeled with another
  filament type; continue from a same-type, close-color spool when one runs out; keep
  duplicate spools free as backups when there are enough other tools; turn the part
  cooling fan off before each tool change.
  Heads with a different nozzle size than the print was sliced for are never used.

PRINT TIME
  A head change costs Orca's machine_tool_change_time; a background swap adds
  BACKGROUND_SWAP_EXTRA; a back-to-back swap costs SWAP_SECONDS in total. Bed leveling
  and flow calibration add their time when ticked. The estimated printing time and M73
  progress lines are rewritten to match.

FILE CHANGES
  Tool numbers (T, M104/M109 T, TOOL=, INITIAL_TOOL=), the BMCU print plan (rebuilt for
  every tool used), the "; filament:" header and the per-filament metadata are
  re-indexed to the new tools; merged colors' usage is added together. The un-retract
  Orca adds right after a change to a BMCU tool (which would push a blob out at the
  prime tower) is removed. Before each tool change the part cooling fan is turned off
  (option, on by default) as soon as the old filament stops printing: the U1 hands the
  fan's speed on to the next head, and a fan blowing on the purge turns it into strings
  instead of a blob. Orca turns it back on after the change. Each BMCU line of the print plan gets EXPECT_ENDPOINT (the
  printer refuses to start if that channel was routed to another head since slicing)
  and EXPECT_MATERIAL (option). MATERIAL / COLOR, which relabel the channel for good,
  are only written where they describe what's in it, so merged or moved colors don't
  relabel a spool. Backups go in as BMCU_PRINT_REFILL, and the end-of-print choice
  into BMCU_PRINT_END.
"""

import base64
import concurrent.futures
import datetime
import ipaddress
import json
import math
import os
import random
import re
import selectors
import socket
import struct
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

# ============================ CONFIG ========================================
# False: show the window only when the recommendation beats your slot layout.
ALWAYS_SHOW_GUI = True
# Tool-change timing (seconds), used to pick the fastest layout and to correct the print
# time estimate (OrcaSlicer counts every tool change the same).
SWAP_SECONDS = 90             # filament swap on the head that's printing (no background swap)
BACKGROUND_SWAP_EXTRA = 15    # extra over a normal head change when BMCU swapped in the background
HEAD_CHANGE_SECONDS = None    # change to another head; None = Orca's machine_tool_change_time
# Added before the print when Save & print runs them. Snapmaker's figures: bed leveling
# about 5-7 minutes; dynamic flow calibration about 3m30s per head the print uses.
BED_LEVEL_SECONDS = 360
FLOW_CAL_SECONDS_PER_HEAD = 210
# Drop Orca's un-retract right after a change to a BMCU tool (it pushes a blob out at
# the prime tower; BMCU-Klipper issue #41).
DROP_TOOLCHANGE_UNRETRACT = True
FIRST_BMCU_TOOL = 4           # T0-T3 are the U1's stock heads, BMCU channels start at T4
SEARCH_TIME_MS = 30000        # layout search time limit
# ============================================================================

NAME = 'bmcu_klipper_remap'
TITLE = 'BMCU-Klipper Tool Assignment'   # name shown in messages and window titles
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(SCRIPT_DIR, NAME + '.log')
SETTINGS_PATH = os.path.join(SCRIPT_DIR, NAME + '.settings.json')
U1_FEEDER_MAP = {1: ('left', 1), 2: ('left', 0), 3: ('right', 0), 4: ('right', 1)}


STATE = {'printer_without_bmcu': False, 'last_out': '', 'last_error': '', 'path': ''}


# --- logging, errors ------------------------------------------------------------
def out(msg):
    STATE['last_out'] = msg
    try:
        print(msg, flush=True)
    except Exception:
        pass


def write_log(msg):
    try:
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > 1024 * 1024:
            os.replace(LOG_PATH, LOG_PATH + '.old')   # keep the previous 1 MB
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write('%s  %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))
    except Exception:
        pass


def fail(msg):
    STATE['last_error'] = msg
    sys.stderr.write('%s: ERROR: %s\n' % (TITLE, msg))
    sys.stderr.flush()
    write_log('ERROR %s | file: %s' % (msg, STATE['path']))
    if not msg.startswith('export cancelled'):
        show_box(msg + '\n\n(also saved in %s)' % LOG_PATH)
    sys.exit(1)


# --- small helpers ----------------------------------------------------------------
def to_hex6(c):
    c = str(c or '').strip().lstrip('#')
    if re.match(r'^[0-9A-Fa-f]{6}', c):
        return '#' + c[:6]
    return '#FFFFFF'


def color_dist(a, b):
    x = to_hex6(a)[1:]; y = to_hex6(b)[1:]
    d = 0
    for i in (0, 2, 4):
        v = int(x[i:i + 2], 16) - int(y[i:i + 2], 16)
        d += v * v
    return d


def color_close(a, b):
    return color_dist(a, b) <= 48 * 48


def tr_color(r):
    return r.get('color') or '#FFFFFF'


def same_spool(a, b):
    """Two tools hold the same kind of filament: same type and a close color."""
    ma = str(a.get('material') or '').strip().upper(); mb = str(b.get('material') or '').strip().upper()
    return bool(ma) and ma == mb and bool(a.get('color')) and bool(b.get('color')) and color_close(a['color'], b['color'])


def parse_float(s):
    try:
        v = float(str(s).strip())
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def from_duration(t):
    sec = 0.0
    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*([dhms])', t):
        v = float(m.group(1))
        sec += v * {'d': 86400, 'h': 3600, 'm': 60, 's': 1}[m.group(2)]
    return sec


def fmt_duration(sec):
    sec = max(0, int(round(sec)))
    d = sec // 86400; h = (sec % 86400) // 3600; m = (sec % 3600) // 60; x = sec % 60
    o = ''
    if d > 0:
        o += '%dd ' % d
    if d > 0 or h > 0:
        o += '%dh ' % h
    if d > 0 or h > 0 or m > 0:
        o += '%dm ' % m
    return o + '%ds' % x


def now_stamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')


# --- settings -----------------------------------------------------------------------
def tool_record(r):
    def b(key, default=False):
        v = r.get(key)
        return default if v is None else bool(v)
    try:
        slot = int(r.get('slot') or 0)
    except Exception:
        slot = 0
    return {
        'tool': int(r.get('tool', 0)), 'head': int(r.get('head', 0) or 0),
        'source': str(r.get('source') or ''), 'label': str(r.get('label') or ''),
        'material': str(r.get('material') or ''), 'color': str(r.get('color') or ''),
        'routed': b('routed', True),
        'present': b('present', True),          # has filament (last refresh)
        'stockLoaded': b('stockLoaded'),        # stock tool: its filament is in the head's shared path
        'stockPull': b('stockPull'),            # stock tool: unloaded from the head but still in the feeder
        'loaded': b('loaded'),                  # BMCU channel: loaded through to the head
        'enabled': b('enabled'),
        'slot': slot,
        'nozzle': parse_float(r.get('nozzle')) or 0.0,  # nozzle size of the head it feeds (0 = unknown)
        'uncertain': b('uncertain'),            # BMCU channel: route state needs confirming
        'device': str(r.get('device') or ''), 'channel': int(r.get('channel') or 0),
    }


# SETTINGS holds the shared options plus the ACTIVE printer's own fields (PRINTER_KEYS), so
# the rest of the script only ever deals with one printer. The other saved printers wait
# in PRINTERS; switch_printer() swaps them in. The file also keeps the active printer's
# fields at the top level, so older versions of the script can still read it.
# Per-printer options (Printer tools) and their defaults:
#   matchLoaded       ties go to tools already holding the print's color
#   separateMaterials different filament types on separate heads
#   expectMaterial    the printer refuses to start if a BMCU channel holds another filament type
#   closeBackups      a spool that runs out continues from an unused one of the same type and a close color
#   keepSpares        keep duplicate spools (same type and color) free as backups when there are enough tools
PRINTER_OPTIONS = {'matchLoaded': True, 'separateMaterials': True, 'expectMaterial': True,
                   'closeBackups': True, 'keepSpares': False, 'purgeFansOff': True}
PRINTER_KEYS = ('name', 'host', 'tools', 'toolsFrom') + tuple(PRINTER_OPTIONS)
SETTINGS = dict(PRINTER_OPTIONS, name='', host='', tools=[], toolsFrom='', bedLevel=True, flowCalibrate=False,
                timelapse=False, alsoPrint=[], endMode='AUTO')   # endMode: AUTO / UNLOAD / KEEP, or SLICED = leave it
PRINTERS = []          # every saved printer (dicts with PRINTER_KEYS)
ACTIVE = {'i': -1}     # index of the active printer in PRINTERS (-1: none yet)


def _printer_from(j):
    p = {'name': str(j.get('name') or ''), 'host': str(j.get('host') or ''), 'toolsFrom': str(j.get('toolsFrom') or ''),
         }
    for k, d in PRINTER_OPTIONS.items():
        p[k] = bool(j.get(k, d))
    tools = j.get('tools') or []
    if isinstance(tools, dict):
        tools = [tools]
    p['tools'] = [tool_record(t) for t in tools]
    complete_slots(p['tools'])     # also tidies settings saved by older versions
    return p


def printer_name(p):
    """How a printer is shown: its name, with the address too if another saved printer has
    the same name (two U1s can both be called the default hostname)."""
    n = p.get('name') or ''
    if not n:
        return p.get('host') or '(no address)'
    if sum(1 for x in PRINTERS if x.get('name') == n) > 1 and p.get('host'):
        return '%s (%s)' % (n, p['host'])
    return n


SETTINGS_LOCK = threading.RLock()   # the plugin's panel, windows and export share these settings


def locked(fn):
    """Run fn holding SETTINGS_LOCK, so two threads never change or save the settings at once."""
    def wrapper(*a, **kw):
        with SETTINGS_LOCK:
            return fn(*a, **kw)
    wrapper.__name__ = fn.__name__; wrapper.__doc__ = fn.__doc__
    return wrapper


@locked
def load_settings():
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, encoding='utf-8-sig') as f:
                j = json.load(f)
            for k in ('bedLevel', 'flowCalibrate', 'timelapse'):
                if j.get(k) is not None:
                    SETTINGS[k] = bool(j[k])
            SETTINGS['alsoPrint'] = [str(h) for h in (j.get('alsoPrint') or [])]
            em = str(j.get('endMode') or '').upper()
            SETTINGS['endMode'] = em if em in ('SLICED', 'UNLOAD', 'KEEP') else 'AUTO'
            if isinstance(j.get('printers'), list):
                PRINTERS[:] = [_printer_from(x) for x in j['printers'] if isinstance(x, dict)]
            elif j.get('tools') or j.get('host'):
                PRINTERS[:] = [_printer_from(j)]          # settings from before multi-printer support
            cur = str(j.get('current') or '')
            idx = next((i for i, p in enumerate(PRINTERS) if p['host'] == cur), 0)
            if PRINTERS:
                _activate(idx)
    except Exception:
        pass


def _activate(i):
    ACTIVE['i'] = i
    for k in PRINTER_KEYS:
        SETTINGS[k] = PRINTERS[i][k]


def _sync_active():
    if 0 <= ACTIVE['i'] < len(PRINTERS):
        for k in PRINTER_KEYS:
            PRINTERS[ACTIVE['i']][k] = SETTINGS[k]


@locked
def switch_printer(i):
    """Make saved printer i the active one (and the one used next time)."""
    _sync_active()
    _activate(i)
    save_settings()


@locked
def add_printer(host, tools, name=''):
    """Save a new printer (or replace the one with the same address) and make it active."""
    _sync_active()
    p = dict(PRINTER_OPTIONS, name=name, host=host, tools=tools, toolsFrom=now_stamp())
    same = [i for i, x in enumerate(PRINTERS) if x['host'] == host]
    if same:
        old = PRINTERS[same[0]]
        p.update({k: old[k] for k in PRINTER_OPTIONS}, name=name or old['name'])
        PRINTERS[same[0]] = p; i = same[0]
    else:
        PRINTERS.append(p); i = len(PRINTERS) - 1
    _activate(i)
    save_settings()


@locked
def remove_printer(i):
    _sync_active()
    gone = PRINTERS.pop(i)
    SETTINGS['alsoPrint'] = [h for h in SETTINGS['alsoPrint'] if h != gone['host']]
    if PRINTERS:
        _activate(min(i, len(PRINTERS) - 1) if i == ACTIVE['i'] else (ACTIVE['i'] - (1 if i < ACTIVE['i'] else 0)))
    else:
        ACTIVE['i'] = -1
        SETTINGS.update(PRINTER_OPTIONS, name='', host='', tools=[], toolsFrom='')
    save_settings()


@locked
def save_settings():
    _sync_active()
    data = {k: SETTINGS[k] for k in PRINTER_KEYS + ('bedLevel', 'flowCalibrate', 'timelapse', 'alsoPrint', 'endMode')}
    data['current'] = SETTINGS['host']
    data['printers'] = PRINTERS
    tmp = SETTINGS_PATH + '.tmp'
    try:   # write a temp file, then swap it in: a crash mid-write never leaves half a file
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, SETTINGS_PATH)
    except Exception:
        pass


def base_url(host):
    h = str(host or '').strip().rstrip('/')
    if not h:
        return ''
    if not re.match(r'^https?://', h, re.I):
        h = 'http://' + h
    return h


def err_text(e):
    if isinstance(e, urllib.error.URLError) and getattr(e, 'reason', None) is not None and not isinstance(e, urllib.error.HTTPError):
        return str(e.reason)
    return str(e) or e.__class__.__name__


def http_json(url, timeout, data=None, method=None):
    """GET (or POST JSON) and return the decoded JSON. Raises on HTTP errors, with the
    printer's own error message where it gives one."""
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        txt = ''
        try:
            txt = e.read().decode('utf-8', 'replace')
            j = json.loads(txt)
            if isinstance(j, dict) and isinstance(j.get('error'), dict) and j['error'].get('message'):
                txt = str(j['error']['message'])
        except Exception:
            pass
        raise RuntimeError(txt or ('HTTP %d %s' % (e.code, e.reason)))
    return json.loads(raw.decode('utf-8', 'replace') or 'null')


# --- tool locking / slots -------------------------------------------------------------
def tool_locked(r, alltools):
    """Unusable no matter what's ticked: unrouted, a stock feeder on a head with BMCU
    channels routed to it, or a BMCU channel on a head with stock filament in it."""
    if not r['routed'] or r['head'] <= 0:
        return True
    for o in alltools:
        if o['head'] != r['head']:
            continue
        if r['source'] == 'stock' and o['source'] == 'bmcu' and o['routed']:
            return True
        if r['source'] == 'bmcu' and o['source'] == 'stock' and o['stockLoaded']:
            return True
    return False


def compress_slots(alltools):
    """Slots keep their order, renumbered 1, 2, 3 ... A tool that's locked for now (not
    routed, or its head is blocked) keeps its slot for when it can be used again; the
    window only lays out slots for tools it can use."""
    n = 1
    for r in sorted([r for r in alltools if r['slot'] > 0], key=lambda r: (r['slot'], r['tool'])):
        r['slot'] = n; n += 1


def complete_slots(alltools):
    """Enabled, usable tools without a slot get the next free numbers."""
    compress_slots(alltools)
    taken = {r['slot'] for r in alltools if r['slot'] > 0}
    nxt = 1
    for r in sorted(alltools, key=lambda r: r['tool']):
        if r['enabled'] and r['slot'] <= 0 and not tool_locked(r, alltools):
            while nxt in taken:
                nxt += 1
            r['slot'] = nxt; taken.add(nxt)


def filament_where(r):
    m = (r['material'] + ' ') if r.get('material') else ''
    if not r['present']:
        return 'no filament'
    if r['source'] == 'stock' and r['stockLoaded'] and r['stockPull']:
        return m + 'in the feeder'
    if (r['source'] == 'stock' and r['stockLoaded']) or (r['source'] == 'bmcu' and r.get('loaded')):
        return m + 'in the tool head'
    if r['source'] == 'bmcu':
        return m + 'in the BMCU'
    return m + 'in the feeder'


def tool_label(r):
    s = 'T%d  - %s' % (r['tool'], r['label'])
    if r['source'] == 'bmcu':
        s += (' -> Head %d' % r['head']) if r['head'] > 0 else ' (not routed)'
    return s + '  [' + filament_where(r) + ']'


# --- printer: BMCU-Klipper status -------------------------------------------------------


def get_printer_tools(host, old_tools, timeout=15):
    """Read BMCU-Klipper's live configuration and merge it with the saved tool list.
    Returns (tools, None) or (None, error)."""
    base = base_url(host)
    if not base:
        return None, 'set the printer address first'
    try:
        resp = http_json(base + '/printer/objects/query?bmcu&print_task_config&configfile=settings', timeout)
    except Exception as e:
        return None, "couldn't read BMCU-Klipper from %s: %s" % (base, err_text(e))
    status = ((resp or {}).get('result') or {}).get('status') or {}
    b = status.get('bmcu')
    ptc = status.get('print_task_config')
    if not isinstance(b, dict) or b.get('devices') is None:
        STATE['printer_without_bmcu'] = True
        return None, "the printer at %s didn't return a BMCU-Klipper status" % base
    STATE['printer_without_bmcu'] = False

    old = {int(r['tool']): r for r in (old_tools or [])}
    bmcu = []
    devices = b.get('devices') or []
    if isinstance(devices, dict):
        devices = [devices]
    for di, d in enumerate(devices):
        letter = chr(65 + di)
        chans = d.get('channels') or []
        if isinstance(chans, dict):
            chans = [chans]
        for c in chans:
            try:
                t = int(c.get('virtual_tool'))
            except Exception:
                continue
            if t < FIRST_BMCU_TOOL:
                continue
            ep = str(c.get('endpoint') or '')
            m = re.match(r'^u1_head(\d+)$', ep)
            head = int(m.group(1)) + 1 if m else 0
            slot = c.get('slot') or {}
            ch = int(c.get('channel') or 0)
            bmcu.append({'tool': t, 'head': head, 'source': 'bmcu',
                         'label': 'BMCU-%s ch %d' % (letter, ch + 1),
                         'material': str(slot.get('material') or ''), 'color': str(slot.get('color') or ''),
                         'routed': head > 0, 'present': bool(c.get('present')),
                         'loaded': bool(c.get('loaded')), 'uncertain': bool(c.get('uncertain')),
                         'channel': ch, 'device': str(d.get('name') or ('bmcu%d' % di)),
                         'stockLoaded': False, 'stockPull': False})
    routed_heads = {r['head'] for r in bmcu if r['head'] > 0}

    tools = []
    endpoints = b.get('endpoints') or {}
    for t in range(FIRST_BMCU_TOOL):
        in_head = False; has = True; pull = False
        ep = endpoints.get('u1_head%d' % t)
        if ep:
            owner = ep.get('owner') or {}
            own = str(owner.get('owner') or '')
            pth = owner.get('path')
            if pth is None:
                pth = (ep.get('capabilities') or {}).get('u1_native_path')
            if pth and pth.get('known') is True:
                in_head = own in ('native', 'native_busy') and pth.get('busy') is True
                has = in_head or pth.get('feeder_input_detected') is True
                cs = str(pth.get('channel_state') or '').lower()
                pull = in_head and cs in ('unload_finish', 'preload_finish')
        s_mat = ''; s_col = ''
        if has and ptc:
            types = ptc.get('filament_type') or []
            if t < len(types):
                ty = str(types[t] or '')
                if ty and ty != 'NONE':
                    s_mat = ty
            rgba = ptc.get('filament_color_rgba') or []
            if t < len(rgba):
                v = str(rgba[t] or '')
                if re.match(r'^[0-9A-Fa-f]{6}', v):
                    s_col = '#' + v[:6]
        tools.append({'tool': t, 'head': t + 1, 'source': 'stock', 'label': 'Head %d stock feeder' % (t + 1),
                      'material': s_mat, 'color': s_col, 'routed': True, 'present': has,
                      'stockLoaded': in_head, 'stockPull': pull, 'loaded': False})
    tools += bmcu
    # nozzle size of each head, from the printer's config (extruder, extruder1 ...)
    cfg = ((status.get('configfile') or {}).get('settings') or {})
    for r in tools:
        ex = cfg.get('extruder' if r['head'] == 1 else 'extruder%d' % (r['head'] - 1)) or {}
        r['nozzle'] = parse_float(ex.get('nozzle_diameter')) or 0.0
    for r in tools:
        o = old.get(r['tool'])
        if o is not None and o['source'] == r['source']:
            r['enabled'] = bool(o['enabled']); r['slot'] = int(o['slot'])
        elif r['source'] == 'stock':
            r['enabled'] = r['head'] not in routed_heads; r['slot'] = 0
        else:
            r['enabled'] = True; r['slot'] = 0
    complete_slots(tools)
    return sorted(tools, key=lambda r: r['tool']), None


def set_print_preferences(host, opt):
    """Bed leveling / flow calibration / timelapse for the next print the U1 starts (it
    clears them when a print ends). '' or an error message."""
    cmd = 'SET_PRINT_PREFERENCES BED_LEVEL=%d FLOW_CALIBRATE=%d TIME_LAPSE_CAMERA=%d' % (
        int(bool(opt['bed'])), int(bool(opt['flow'])), int(bool(opt['tl'])))
    try:
        http_json(base_url(host) + '/printer/gcode/script', 20, {'script': cmd}, 'POST')
        return ''
    except Exception as e:
        return '%s failed on %s: %s' % (cmd, host, err_text(e))


def printer_hostname(host):
    """The printer's own name (Klipper hostname), or '' if it doesn't say."""
    try:
        info = http_json(base_url(host) + '/printer/info', 3)
        return str(((info or {}).get('result') or {}).get('hostname') or '')
    except Exception:
        return ''


def printer_activity(host):
    """('printing'|'busy'|'ready'|'unknown', detail)"""
    base = base_url(host)
    if not base:
        return 'unknown', 'no printer address'
    try:
        r = http_json(base + '/printer/objects/query?print_stats&idle_timeout&bmcu', 5)
    except Exception as e:
        return 'unknown', err_text(e)
    st = ((r or {}).get('result') or {}).get('status') or {}
    ps = str((st.get('print_stats') or {}).get('state') or '')
    if ps in ('printing', 'paused'):
        return 'printing', 'the printer is ' + ps
    op = (st.get('bmcu') or {}).get('active_operation')
    if op:
        if isinstance(op, dict):
            name = str(op.get('name') or op.get('operation') or 'a BMCU operation')
        else:
            name = str(op)
        return 'busy', name
    if str((st.get('idle_timeout') or {}).get('state') or '') == 'Printing':
        return 'busy', 'running G-code'
    return 'ready', ''


def invoke_unload(host, rec):
    """Unload one tool's filament from its head. '' or an error message."""
    base = base_url(host)
    if not base:
        return 'set the printer address first'
    if rec['source'] == 'bmcu':
        cmd = 'BMCU_UNLOAD TOOL=%d' % int(rec['tool'])
    else:
        fm = U1_FEEDER_MAP.get(int(rec['head']))
        if not fm:
            return 'no feeder known for head %s' % rec['head']
        cmd = 'FEED_AUTO MODULE=%s CHANNEL=%d UNLOAD=1' % fm
    try:
        http_json(base + '/printer/gcode/script', 600, {'script': cmd}, 'POST')
        return ''
    except Exception as e:
        return '%s failed: %s' % (cmd, err_text(e))


# --- printer: upload and start ----------------------------------------------------------
def _ws_connect(url, timeout):
    u = urllib.parse.urlparse(url)
    port = u.port or (443 if u.scheme == 'wss' else 80)
    sock = socket.create_connection((u.hostname, port), timeout=timeout)
    if u.scheme == 'wss':
        import ssl
        sock = ssl.create_default_context().wrap_socket(sock, server_hostname=u.hostname)
    key = base64.b64encode(os.urandom(16)).decode()
    path = u.path or '/'
    hosthdr = u.hostname + ('' if u.port is None else ':%d' % u.port)
    req = ('GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
           'Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n') % (path, hosthdr, key)
    sock.sendall(req.encode())
    buf = b''
    while b'\r\n\r\n' not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError('websocket handshake failed')
        buf += chunk
    head, rest = buf.split(b'\r\n\r\n', 1)
    if b' 101 ' not in head.split(b'\r\n')[0]:
        raise RuntimeError('websocket handshake refused')
    return sock, rest


def _ws_send_text(sock, text):
    data = text.encode('utf-8')
    hdr = bytearray([0x81])
    n = len(data)
    if n < 126:
        hdr.append(0x80 | n)
    elif n < 65536:
        hdr.append(0x80 | 126); hdr += struct.pack('>H', n)
    else:
        hdr.append(0x80 | 127); hdr += struct.pack('>Q', n)
    mask = os.urandom(4)
    hdr += mask
    sock.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


class _WsReader:
    def __init__(self, sock, pending):
        self.sock = sock; self.buf = pending

    def _need(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError('connection closed')
            self.buf += chunk
        d = self.buf[:n]; self.buf = self.buf[n:]
        return d

    def message(self):
        """Next complete text message, or None when the server closes."""
        parts = []
        while True:
            b1, b2 = self._need(2)
            fin = b1 & 0x80; op = b1 & 0x0F
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack('>H', self._need(2))[0]
            elif n == 127:
                n = struct.unpack('>Q', self._need(8))[0]
            mask = self._need(4) if b2 & 0x80 else None
            payload = self._need(n)
            if mask:
                payload = bytes(x ^ mask[i % 4] for i, x in enumerate(payload))
            if op == 8:
                return None
            if op == 9:   # ping -> pong (a control frame carries at most 125 bytes)
                m = os.urandom(4)
                try:
                    if len(payload) > 125:
                        raise ValueError('oversized ping')
                    self.sock.sendall(bytes([0x8A, 0x80 | len(payload)]) + m +
                                      bytes(x ^ m[i % 4] for i, x in enumerate(payload)))
                except Exception:
                    pass
                continue
            if op not in (0, 1, 2):   # pong or an unknown opcode: not part of a message
                continue
            parts.append(payload)
            if fin:
                return b''.join(parts).decode('utf-8', 'replace')


def send_to_printer(host, file_path, name, bed, flow, tl):
    """Upload the finished file to Moonraker and start it the way Snapmaker Orca does.
    None on success, or an error message."""
    h = base_url(host)
    if not h:
        return 'no printer address set'
    try:
        boundary = '----bmcu%s' % os.urandom(8).hex()
        safe = name.replace('"', "'")
        with open(file_path, 'rb') as f:
            content = f.read()
        body = (('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\n'
                 'Content-Type: application/octet-stream\r\n\r\n') % (boundary, safe)).encode('utf-8') + content + \
            ('\r\n--%s--\r\n' % boundary).encode()
        req = urllib.request.Request(h + '/server/files/upload', data=body,
                                     headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                up = r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            return 'upload failed: HTTP %d %s %s' % (e.code, e.reason, e.read().decode('utf-8', 'replace'))
        remote = name
        try:
            u = json.loads(up)
            p = (u.get('item') or {}).get('path') or ((u.get('result') or {}).get('item') or {}).get('path')
            if p:
                remote = p
        except Exception:
            pass
    except Exception as e:
        return "couldn't reach the printer at %s: %s" % (h, err_text(e))

    # start it through the printer's own "start_local_print" call (WebSocket)
    req = json.dumps({'jsonrpc': '2.0', 'method': 'server.files.start_local_print', 'id': 4242,
                      'params': {'type': 'gcode', 'path': remote, 'print_plate': 1,
                                 'options': {'bed_level': int(bed), 'flow_calibrate': int(flow), 'time_lapse_camera': int(tl)}}})
    sock = None
    try:
        sock, pending = _ws_connect(re.sub(r'^http', 'ws', h) + '/websocket', 10)
    except Exception:
        sock = None
    if sock is not None:
        try:
            sock.settimeout(90)
            _ws_send_text(sock, req)
            rd = _WsReader(sock, pending)
            deadline = time.time() + 90
            while time.time() < deadline:
                txt = rd.message()
                if txt is None:
                    return "uploaded as '%s', but the printer closed the connection before confirming the start - check the printer before trying again" % remote
                try:
                    msg = json.loads(txt)
                except Exception:
                    continue
                if not isinstance(msg, dict) or msg.get('id') != 4242:
                    continue
                if msg.get('error'):
                    return "uploaded as '%s', but the print didn't start: %s" % (remote, (msg['error'] or {}).get('message'))
                res = msg.get('result') or {}
                if isinstance(res, dict) and res.get('state') and res.get('state') != 'success':
                    return "uploaded as '%s', but the print didn't start: %s" % (remote, res.get('message'))
                return None
            raise TimeoutError('timed out')
        except Exception as e:
            return "uploaded as '%s' and asked the printer to start, but got no answer (%s) - check the printer before trying again" % (remote, err_text(e))
        finally:
            try:
                sock.close()
            except Exception:
                pass

    # fallback: start with the same Klipper command directly
    fn = remote.replace('"', '\\"')
    cmd = 'SDCARD_PRINT_FILE_WITH_PARAMETERS FILENAME="%s" BED_LEVEL="%d" FLOW_CALIBRATE="%d" TIME_LAPSE_CAMERA="%d"' % (fn, int(bed), int(flow), int(tl))
    try:
        http_json(h + '/printer/gcode/script', 120, {'script': cmd}, 'POST')
        return None
    except Exception as e:
        return "uploaded as '%s', but the print didn't start: %s" % (remote, err_text(e))


# --- printer discovery: mDNS + a quick scan of the BMCU panel port -------------------------
MAX_HOSTS = 4094   # largest extra subnet: a /20


def parse_subnets(text):
    """Parse '192.168.10.0/24, 10.0.0.0 255.255.255.0' -> ([(ip, prefix)], error or None)."""
    nets = []
    if not text:
        return nets, None
    for raw in re.split(r'[,;]', text):
        e = raw.strip()
        if not e:
            continue
        addr, mask = e, None
        cut = e.find('/')
        if cut < 0:
            cut = e.find(' ')
        if cut >= 0:
            addr = e[:cut].strip(); mask = e[cut + 1:].strip()
        try:
            ip = ipaddress.IPv4Address(addr)
            if len(addr.split('.')) != 4:
                raise ValueError
        except Exception:
            return nets, "'%s' isn't an IPv4 address" % e
        if mask is None:
            prefix = 24
        elif '.' not in mask:
            try:
                prefix = int(mask)
                if not 0 <= prefix <= 32:
                    raise ValueError
            except Exception:
                return nets, "'%s': the prefix after / must be 0-32" % e
        else:
            try:
                mv = int(ipaddress.IPv4Address(mask))
                if len(mask.split('.')) != 4:
                    raise ValueError
            except Exception:
                return nets, "'%s': '%s' isn't a subnet mask" % (e, mask)
            prefix = 0
            while prefix < 32 and (mv >> (31 - prefix)) & 1:
                prefix += 1
            expect = 0 if prefix == 0 else (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
            if mv != expect:
                return nets, "'%s': '%s' isn't a valid subnet mask" % (e, mask)
        hosts = (1 << (32 - prefix)) if prefix >= 31 else (1 << (32 - prefix)) - 2
        if hosts > MAX_HOSTS:
            return nets, "'%s' is %d addresses; the largest allowed is a /20 (%d)" % (e, hosts, MAX_HOSTS)
        nets.append((ip, prefix))
    return nets, None


def check_subnets(text):
    return parse_subnets(text)[1]


def local_ipv4():
    """This computer's IPv4 addresses (no loopback / link-local)."""
    ips = set()
    try:   # the address used for the default route (no packet is sent)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ips.add(s.getsockname()[0])
        finally:
            s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except Exception:
        pass
    good = []
    for ip in ips:
        try:
            a = ipaddress.IPv4Address(ip)
            if not (a.is_loopback or a.is_link_local or a.is_unspecified):
                good.append(ip)
        except Exception:
            pass
    return sorted(good)


MDNS_SERVICES = ['_services._dns-sd._udp.local', '_moonraker._tcp.local', '_http._tcp.local',
                 '_snapmaker._tcp.local', '_workstation._tcp.local']


def _mdns_query():
    q = bytearray([0, 0, 0, 0, 0, len(MDNS_SERVICES), 0, 0, 0, 0, 0, 0])
    for s in MDNS_SERVICES:
        for label in s.split('.'):
            lb = label.encode('ascii')
            q.append(len(lb)); q += lb
        q.append(0)
        q += bytes([0, 12, 0x80, 1])   # PTR, class IN with unicast-response bit
    return bytes(q)


def _mdns(cands, locals_, ms):
    q = _mdns_query()

    def one(local):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind((local, 0))
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local))
            dst = ('224.0.0.251', 5353)
            s.sendto(q, dst)
            end = time.time() + ms / 1000.0
            resent = False
            while True:
                left = end - time.time()
                if left <= 0:
                    break
                if not resent and left < ms / 2000.0:
                    s.sendto(q, dst); resent = True
                s.settimeout(max(0.05, min(left, ms / 2000.0)))
                try:
                    data, frm = s.recvfrom(9000)
                    if len(data) >= 12 and data[2] & 0x80 and frm[0] != local:
                        cands.add(frm[0])
                except socket.timeout:
                    pass
                except OSError:
                    pass
        except Exception:
            pass
        finally:
            if s:
                s.close()
    ths = [threading.Thread(target=one, args=(l,), daemon=True) for l in locals_]
    for t in ths:
        t.start()
    for t in ths:
        t.join()


def _scan(cands, locals_, extra, port, ms):
    targets = set()
    for ip in locals_:
        net = ipaddress.IPv4Network(ip + '/24', strict=False)
        targets.update(str(h) for h in net.hosts())
    for ip, prefix in extra:
        net = ipaddress.IPv4Network('%s/%d' % (ip, prefix), strict=False)
        if prefix >= 31:
            targets.update(str(h) for h in net)
        else:
            targets.update(str(h) for h in net.hosts())
    allt = sorted(targets)
    batch = 250   # stays under select()'s socket limit on Windows
    for s0 in range(0, len(allt), batch):
        sel = selectors.DefaultSelector()
        socks = []
        for ip in allt[s0:s0 + batch]:
            so = None
            try:
                so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                so.setblocking(False)
                so.connect_ex((ip, port))
                sel.register(so, selectors.EVENT_WRITE, ip)
                socks.append(so)
            except Exception:
                if so is not None:
                    try:
                        so.close()
                    except Exception:
                        pass
        end = time.time() + ms / 1000.0
        pending = len(socks)
        while pending > 0:
            left = end - time.time()
            if left <= 0:
                break
            for key, _ in sel.select(timeout=left):
                so = key.fileobj
                try:
                    if so.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0:
                        cands.add(key.data)
                except Exception:
                    pass
                sel.unregister(so); pending -= 1
        for so in socks:
            try:
                so.close()
            except Exception:
                pass
        sel.close()


def _probe(ip, timeout):
    try:
        q = http_json('http://%s/printer/objects/query?bmcu' % ip, timeout)
    except Exception:
        return None
    if not isinstance(q, dict) or 'result' not in q:
        return None
    st = ((q.get('result') or {}).get('status') or {})
    bm = isinstance(st.get('bmcu'), dict) and st['bmcu'].get('devices') is not None
    name = ip
    try:
        info = http_json('http://%s/printer/info' % ip, timeout)
        hn = ((info or {}).get('result') or {}).get('hostname')
        if hn:
            name = str(hn)
    except Exception:
        pass
    return {'ip': ip, 'name': name, 'bmcu': bm}


def find_printers(subnets='', timeout_ms=2000):
    """Printers on the local network: [{'ip', 'name', 'bmcu'}]. Raises PermissionError when
    the host (OrcaSlicer's plugin permissions) doesn't allow reaching arbitrary addresses."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.0.2.1', 9))       # documentation address: nothing is sent
    except PermissionError:
        raise
    except OSError:
        pass
    finally:
        s.close()
    cands = set()
    locals_ = local_ipv4()
    extra, perr = parse_subnets(subnets)
    if perr:
        extra = []
    t1 = threading.Thread(target=_mdns, args=(cands, locals_, timeout_ms), daemon=True)
    t2 = threading.Thread(target=_scan, args=(cands, locals_, extra, 8291, min(timeout_ms, 900)), daemon=True)
    t1.start(); t2.start(); t1.join(); t2.join()
    results = []
    if cands:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, len(cands))) as ex:
            for r in ex.map(lambda ip: _probe(ip, 2.5), sorted(cands)):
                if r:
                    results.append(r)
    return sorted(results, key=lambda r: r['ip'])
# --- layout search (port of the C# BmcuSolver) -----------------------------------
# Assigns print colors to tools so that colors sharing a print head need as few
# filament swaps as possible. Swaps depend only on WHICH colors share a head, so the
# search runs over head groupings, not individual tools; inside each head the colors
# go to channels by an optimal assignment that keeps spools where they already are.
# Score (lexicographic): time cost of swaps, tie-break 1, tie-break 2, head changes.
# Swap time per head = w_bg * swaps + w_fg * back-to-back swaps.
# Tools that can't retract (U1 stock feeders): on a shared head a stock-fed color must
# be the LAST color that head prints.
#  1. pair conflicts: how often each pair of colors alternates in the print
#  2. start: place the most-conflicting colors first, then improve by moving/swapping
#  3. prove: branch-and-bound over head groupings with monotone lower bounds and a
#     pigeonhole bound, within the time limit.



W = 1000                  # weight of tie-break 1 over tie-break 2 inside a head
BLOCK = W * 1000000
MEMO_CAP = 1500000
INF = float('inf')


class Solver:
    def __init__(self):
        self.cancel = False          # "use best so far"
        self.last_proven = False
        self.last_nodes = 0
        self._thread = None
        self.result = None
        self.score = None
        self.error = None

    # ---- background run, so the caller can show progress and offer a stop button ----
    def start(self, *args, **kw):
        self.cancel = False
        self.result = None; self.score = None; self.error = None

        def run():
            try:
                self.result, self.score = self.solve(*args, **kw)
            except Exception as e:   # reported to the caller
                self.error = e
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def wait(self, seconds):
        self._thread.join(seconds)
        return not self._thread.is_alive()

    # colors: number of colors; seq: color per tool change (no repeats);
    # tool_head: head per tool index; no_retract: per tool; move/src: [color][tool] costs
    # (move >= 1000 = forbidden pairing); materials: per color group or None.
    def solve(self, colors, seq, tool_head, no_retract, move, src, time_limit_ms,
              weight_swap=1, weight_b2b=0, materials=None):
        self.w_bg = max(1, int(weight_swap)); self.w_fg = max(0, int(weight_b2b))
        self.mat = materials
        self.no_retract = list(no_retract)
        self.t0 = time.monotonic(); self.time_limit = time_limit_ms / 1000.0
        self.k = colors; self.seq = list(seq)
        self.n_tools = len(tool_head)
        self.move = move; self.src = src
        ids = {}
        self.tool_head = []
        for h in tool_head:
            if h not in ids:
                ids[h] = len(ids)
            self.tool_head.append(ids[h])
        self.n_heads = len(ids)
        self.head_tools = [[] for _ in range(self.n_heads)]
        for t in range(self.n_tools):
            self.head_tools[self.tool_head[t]].append(t)
        self.swap_memo = {}
        self.assign_memo = [dict() for _ in range(self.n_heads)]
        self.assign_pick = [dict() for _ in range(self.n_heads)]

        k = self.k
        self.pair = [[0] * k for _ in range(k)]
        for a in range(k):
            for b in range(a + 1, k):
                self.pair[a][b] = self.pair[b][a] = self.swap_cost((1 << a) | (1 << b))

        best = self.local_search()
        best_score = self.score_of(best)
        self.last_nodes = 0
        best, best_score, proven = self.branch_and_bound(best, best_score)
        self.last_proven = proven
        if best is None:
            return None, None
        return self.expand(best)

    # ---- costs (both monotone: adding a color to a head never lowers them) ----------
    def swap_cost(self, mask):
        v = self.swap_memo.get(mask)
        if v is not None:
            return v
        last = -1; n = 0; fg = 0
        seq = self.seq
        prev = -1
        for c in seq:
            if (mask >> c) & 1:
                if last != -1 and last != c:
                    n += 1
                    if prev == last:   # previous change was on this head too: no background time
                        fg += 1
                last = c
            prev = c
        v = self.w_bg * n + self.w_fg * fg
        if len(self.swap_memo) >= MEMO_CAP:
            self.swap_memo.clear()
        self.swap_memo[mask] = v
        return v

    def last_only_color(self, mask):
        f = [c for c in self.seq if (mask >> c) & 1]
        if not f:
            return -1
        last = f[-1]
        first = f.index(last)
        for x in f[first:]:
            if x != last:
                return -1
        return last

    # best (moves*W + src) for the colors in mask on distinct tools of head h; -1 if they don't fit
    def assign_cost(self, h, mask):
        memo = self.assign_memo[h]
        v = memo.get(mask)
        if v is not None:
            return v
        cols = [c for c in range(self.k) if (mask >> c) & 1]
        tl = self.head_tools[h]
        if len(cols) > len(tl):
            memo[mask] = -1; return -1
        if self.mat is not None:
            for c in cols[1:]:
                if self.mat[c] != self.mat[cols[0]]:
                    memo[mask] = -1; return -1   # mixed materials on one head
        last_only = self.last_only_color(mask) if len(cols) > 1 else -1
        pick = []
        cost = 0
        if cols:
            a = []
            for c in cols:
                row = []
                for t in tl:
                    ok = (len(cols) == 1 or not self.no_retract[t] or c == last_only) and self.move[c][t] < 1000
                    row.append(self.move[c][t] * W + self.src[c][t] if ok else BLOCK)
                a.append(row)
            ass = hungarian(a, len(cols), len(tl))
            for i in range(len(cols)):
                if a[i][ass[i]] >= BLOCK:
                    memo[mask] = -1; return -1
                pick.append(tl[ass[i]]); cost += a[i][ass[i]]
        if len(memo) >= MEMO_CAP:
            memo.clear(); self.assign_pick[h].clear()
        memo[mask] = cost; self.assign_pick[h][mask] = pick
        return cost

    def head_changes(self, head_of):
        seq = self.seq
        return sum(1 for i in range(1, len(seq)) if head_of[seq[i]] != head_of[seq[i - 1]])

    # total score of a head grouping; None if a head can't take its colors
    def score_of(self, head_of):
        if head_of is None:
            return None
        masks = [0] * self.n_heads
        for c in range(self.k):
            masks[head_of[c]] |= 1 << c
        swaps = 0; assign = 0
        for h in range(self.n_heads):
            ac = self.assign_cost(h, masks[h])
            if ac < 0:
                return None
            assign += ac; swaps += self.swap_cost(masks[h])
        return (swaps, assign // W, assign % W, self.head_changes(head_of))

    @staticmethod
    def better(a, b):
        if b is None:
            return a is not None
        if a is None:
            return False
        return a < b

    def elapsed(self):
        return time.monotonic() - self.t0

    # ---- 2. start + improve --------------------------------------------------------
    def local_search(self):
        rnd = random.Random(12345)
        best = None; best_score = None
        k = self.k
        # the first pass may use up to half the time limit, the restarts a quarter;
        # a pass that runs out of time keeps what it has improved so far
        for r in range(20):
            if r > 0 and best is not None and (self.cancel or self.elapsed() > self.time_limit / 4):
                break
            stop_at = self.time_limit / (2 if r == 0 else 4)
            cur = self.start_layout(None if r == 0 else rnd)
            if cur is None:
                continue
            cs = self.score_of(cur)
            improved = True
            while improved:
                improved = False
                if self.cancel or self.elapsed() > stop_at:
                    break
                for c in range(k):
                    if improved or self.elapsed() > stop_at:
                        break
                    old = cur[c]
                    for h in range(self.n_heads):
                        if h == old:
                            continue
                        cur[c] = h
                        s = self.score_of(cur)
                        if self.better(s, cs):
                            cs = s; improved = True; break
                        cur[c] = old
                for a in range(k):
                    if improved or self.elapsed() > stop_at:
                        break
                    for b in range(a + 1, k):
                        if cur[a] == cur[b]:
                            continue
                        cur[a], cur[b] = cur[b], cur[a]
                        s = self.score_of(cur)
                        if self.better(s, cs):
                            cs = s; improved = True; break
                        cur[a], cur[b] = cur[b], cur[a]
            if self.better(cs, best_score):
                best_score = cs; best = list(cur)
        return best

    # most-conflicting color first, each on the head where it adds the fewest swaps
    def start_layout(self, rnd):
        k = self.k
        total = [sum(self.pair[a]) for a in range(k)]
        cur = [0] * k; cnt = [0] * self.n_heads
        placed = [False] * k
        masks = [0] * self.n_heads
        for _ in range(k):
            pick = -1; pick_key = None
            for c in range(k):
                if placed[c]:
                    continue
                to_placed = sum(self.pair[c][d] for d in range(k) if placed[d])
                key = to_placed * 1000000 + total[c]
                if rnd is not None:
                    key = key * 8 + rnd.randrange(8)
                if pick_key is None or key > pick_key:
                    pick_key = key; pick = c
            bh = -1; bv = None
            for h in range(self.n_heads):
                if cnt[h] >= len(self.head_tools[h]):
                    continue
                m = masks[h] | (1 << pick)
                ac = self.assign_cost(h, m)
                if ac < 0:
                    continue
                v = (self.swap_cost(m) - self.swap_cost(masks[h])) * 1000000 + ac - self.assign_cost(h, masks[h])
                if rnd is not None:
                    v = v * 4 + rnd.randrange(4)
                if bv is None or v < bv:
                    bv = v; bh = h
            if bh < 0:
                return None
            cur[pick] = bh; cnt[bh] += 1; masks[bh] |= 1 << pick; placed[pick] = True
        return cur

    # ---- 3. branch and bound ---------------------------------------------------------
    def branch_and_bound(self, best, best_score):
        k = self.k
        total = [sum(self.pair[a]) for a in range(k)]
        self.bb_order = sorted(range(k), key=lambda x: -total[x])   # colors that alternate most first
        self.bb_cur = [0] * k
        self.bb_mask = [0] * self.n_heads
        self.bb_best = best; self.bb_best_score = best_score
        self.bb_aborted = False
        self._bb(0, 0, 0)
        return self.bb_best, self.bb_best_score, not self.bb_aborted

    def _worse(self, swaps, assign):
        bs = self.bb_best_score
        if bs is None:
            return False
        if swaps != bs[0]:
            return swaps > bs[0]
        return assign >= bs[1] * W + bs[2]

    def _bb(self, depth, swaps, assign):
        if self.bb_aborted:
            return
        self.last_nodes += 1
        if (self.cancel or
                ((self.last_nodes & 15) == 0 and self.elapsed() > self.time_limit)):
            self.bb_aborted = True
            return
        k = self.k
        if depth == k:
            s = self.score_of(self.bb_cur)
            if self.better(s, self.bb_best_score):
                self.bb_best_score = s; self.bb_best = list(self.bb_cur)
            return
        nh = self.n_heads
        mask = self.bb_mask
        sc = self.swap_cost; ac_ = self.assign_cost
        # every unplaced color must go somewhere: the total rises by at least the
        # largest "cheapest placement" among them
        extra_sw = 0; extra_as = 0
        for i in range(depth, k):
            c = self.bb_order[i]
            ms = None; ma = None
            for h in range(nh):
                m = mask[h] | (1 << c)
                ac = ac_(h, m)
                if ac < 0:
                    continue
                ds = sc(m) - sc(mask[h])
                da = ac - ac_(h, mask[h])
                if ms is None or ds < ms or (ds == ms and da < ma):
                    ms = ds; ma = da
            if ms is None:
                return   # no head can take this color
            if ms > extra_sw or (ms == extra_sw and ma > extra_as):
                extra_sw = ms; extra_as = ma
        # pigeonhole: only one color per still-empty head can avoid adding a swap
        empty = sum(1 for h in range(nh) if mask[h] == 0 and self.head_tools[h])
        pig = ((k - depth) - empty) * self.w_bg
        if pig > extra_sw:
            extra_sw = pig; extra_as = 0
        if self._worse(swaps + extra_sw, assign + extra_as):
            return

        col = self.bb_order[depth]
        keys = []
        for h in range(nh):
            m = mask[h] | (1 << col)
            ac = ac_(h, m)
            keys.append((INF if ac < 0 else (sc(m) - sc(mask[h])) * 1000000 + ac, h))
        keys.sort()
        for _, h in keys:
            old = mask[h]; m = old | (1 << col)
            ac = ac_(h, m)
            if ac < 0:
                continue
            ns = swaps - sc(old) + sc(m)
            na = assign - ac_(h, old) + ac
            if self._worse(ns, na):
                continue
            mask[h] = m; self.bb_cur[col] = h
            self._bb(depth + 1, ns, na)
            mask[h] = old
            if self.bb_aborted:
                return

    def expand(self, head_of):
        score = self.score_of(head_of)
        tool_of = [0] * self.k
        masks = [0] * self.n_heads
        for c in range(self.k):
            masks[head_of[c]] |= 1 << c
        for h in range(self.n_heads):
            if masks[h] == 0:
                continue
            self.assign_cost(h, masks[h])
            pick = self.assign_pick[h][masks[h]]
            i = 0
            for c in range(self.k):
                if (masks[h] >> c) & 1:
                    tool_of[c] = pick[i]; i += 1
        return tool_of, score


# rows <= cols; returns column per row (classic O(n^2 m) Hungarian)
def hungarian(a, n, m):
    INFL = 1 << 62
    u = [0] * (n + 1); v = [0] * (m + 1)
    p = [0] * (m + 1); way = [0] * (m + 1)
    for i in range(1, n + 1):
        p[0] = i; j0 = 0
        minv = [INFL] * (m + 1); used = [False] * (m + 1)
        while True:
            used[j0] = True; i0 = p[j0]; j1 = 0; delta = INFL
            row = a[i0 - 1]
            for j in range(1, m + 1):
                if not used[j]:
                    cur = row[j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur; way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]; j1 = j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta; v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
            if j0 == 0:
                break
    res = [0] * n
    for j in range(1, m + 1):
        if p[j] != 0:
            res[p[j] - 1] = j - 1
    return res

# ============================ windows (OrcaSlicer plugin: HTML) ===========================
# The windows, built on OrcaSlicer's plugin windows (HTML pages with a message bridge).
# They're opened from the slicing thread, which waits for them; their buttons run on
# OrcaSlicer's UI thread (on_message), so anything slow goes to a background thread and
# the page is redrawn by posting it a fresh view. Windows are modeless: OrcaSlicer's own
# questions (permissions, message boxes) can then still be clicked.
import orca  # noqa: E402  (only inside OrcaSlicer)

CTX = {'ctx': None}          # the slicing context of the export in progress (for cancel)
BULLET = '• '
END_MODES = [('AUTO', 'BMCU decides (Auto)'), ('SLICED', 'As sliced'), ('UNLOAD', 'Unload the BMCU filament'), ('KEEP', 'Keep it loaded')]
ROUTE_STATES = [('LOADED', 'Loaded in the head', 'the filament from this channel is loaded all the way into head %d'),
                ('PARKED', 'Parked in the BMCU', 'head %d and the tube are empty and the filament is pulled back into the BMCU'),
                ('EMPTY', 'Empty', 'head %d, the tube and this BMCU channel are all empty')]


def show_box(msg, title=None, kind='error'):
    try:
        orca.host.ui.message(msg, title=title or TITLE, buttons='ok', icon={'error': 'error', 'warning': 'warning'}.get(kind, 'info'))
    except Exception:
        pass


def ask_ok(msg, title, warn=True):
    try:
        return orca.host.ui.message(msg, title=title, buttons='ok_cancel', icon='warning' if warn else 'question') == 'ok'
    except Exception:
        return False


def ask_yes(msg, title):
    try:
        return orca.host.ui.message(msg, title=title, buttons='yes_no', icon='warning') == 'yes'
    except Exception:
        return False


def permission_hint(err):
    """Explain an OrcaSlicer permission refusal in plain words."""
    if 'without permission' in str(err) or 'PermissionError' in str(err):
        return (' OrcaSlicer hasn\'t allowed this plugin to connect to the printer yet. If it asked you, answer Yes and '
                'try again (restart OrcaSlicer once afterwards so it covers the whole printer), or allow it under '
                'Plugins > BMCU-Klipper Tool Assignment > permissions.')
    return ''


PAGE_CSS = r"""
:root { --bg: var(--orca-bg, #ffffff); --fg: var(--orca-fg, #1f2328); --muted: var(--orca-muted, #656d76);
        --line: var(--orca-border, #d0d7de); --accent: var(--orca-accent, #009688); --accent-fg: var(--orca-accent-fg, #ffffff);
        --band: rgba(127, 127, 127, .08); --warn-bg: rgba(230, 180, 0, .18); --warn-fg: var(--fg);
        --err-bg: rgba(220, 40, 40, .14); --err-fg: var(--fg); }
@media (prefers-color-scheme: dark) { :root { --bg: var(--orca-bg, #2b2d30); --fg: var(--orca-fg, #e4e6e8);
        --muted: var(--orca-muted, #9aa0a6); --line: var(--orca-border, #3d4043); } }
* { box-sizing: border-box; }
body { margin: 0; font: 13px/1.4 var(--orca-font, system-ui, "Segoe UI", sans-serif); background: var(--bg); color: var(--fg); }
#app { padding: 16px 20px 80px; }
h1 { font-size: 19px; margin: 0 0 2px; } h2 { font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin: 18px 0 6px; }
.sub { color: var(--muted); margin-bottom: 10px; } .muted { color: var(--muted); } .head { font-weight: 600; font-size: 14px; margin: 8px 0 10px; }
.note { padding: 7px 10px; border-radius: 4px; margin: 6px 0; } .warn { background: var(--warn-bg); color: var(--warn-fg); }
.err { background: var(--err-bg); color: var(--err-fg); } .row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 4px 0; }
table { border-collapse: collapse; width: 100%; } td, th { text-align: left; vertical-align: top; padding: 6px 10px 6px 0; border-bottom: 1px solid var(--line); }
th { color: var(--muted); font-weight: 600; border-bottom: none; } tr.off td { color: var(--muted); } td.why { font-style: italic; }
.sw { display: inline-block; width: 16px; height: 16px; border: 1px solid #8c959f; border-radius: 3px; vertical-align: middle; margin-right: 6px; }
.color { display: flex; align-items: center; gap: 6px; margin: 2px 0; } .ctext { width: 190px; } .color select { width: 300px; }
select, input[type=text] { font: inherit; padding: 3px 5px; background: var(--bg); color: var(--fg); border: 1px solid var(--line); border-radius: 4px; }
button { font: inherit; padding: 5px 12px; border: 1px solid var(--line); border-radius: 4px; background: var(--band); color: var(--fg); cursor: pointer; }
button.primary { background: var(--accent); border-color: var(--accent); color: var(--accent-fg); } button:disabled { opacity: .45; cursor: default; }
.bar { position: fixed; left: 0; right: 0; bottom: 0; display: flex; gap: 8px; padding: 10px 16px; background: var(--bg); box-shadow: inset 0 0 0 999px var(--band); border-top: 1px solid var(--line); }
.bar .sp { flex: 1; } label { cursor: pointer; } .small { font-size: 12px; }
"""

PAGE_JS = r"""
var V = null;
function h(tag, attrs, kids) {
  var e = document.createElement(tag); attrs = attrs || {};
  for (var k in attrs) { var v = attrs[k];
    if (k === 'on') { for (var ev in v) e.addEventListener(ev, v[ev]); }
    else if (k === 'style') e.setAttribute('style', v);
    else if (k === 'class') e.className = v;
    else if (v === true) e.setAttribute(k, ''); else if (v !== false && v !== null && v !== undefined) e[k] = v; }
  (kids || []).forEach(function (c) { if (c === null || c === undefined) return;
    e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
  return e;
}
function send(m) { orca.postMessage(m); }
function sw(c) { return h('span', {class: 'sw', style: 'background:' + (c || 'transparent')}); }
function btn(text, msg, opts) { opts = opts || {};
  return h('button', {class: opts.primary ? 'primary' : '', disabled: !!opts.disabled, title: opts.title || '',
                      on: {click: function () { send(msg); }}}, [text]); }
function sel(items, cur, onchange, opts) { opts = opts || {};
  var s = h('select', {disabled: !!opts.disabled, style: opts.style || ''});
  items.forEach(function (t, i) { s.appendChild(h('option', {value: i, selected: i === cur, disabled: !!(opts.off && opts.off[i])}, [t])); });
  s.addEventListener('change', function () { onchange(parseInt(s.value)); }); return s; }
function notes(list) { return (list || []).map(function (n) { return h('div', {class: 'note ' + (n.kind || 'warn')}, [n.text]); }); }
function chk(text, on, onchange, disabled) {
  var c = h('input', {type: 'checkbox', checked: !!on, disabled: !!disabled});
  c.addEventListener('change', function () { onchange(c.checked); });
  return h('label', {}, [c, ' ' + text]); }
orca.onMessage(function (m) { if (m && m.view) { V = m.view; render(); } });
window.addEventListener('load', function () { send({cmd: 'ready'}); });
"""


def page(body_js):
    return ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>' + PAGE_CSS + '</style></head><body><div id="app">'
            '<p class="muted">Loading...</p></div><script>' + PAGE_JS + body_js + '</script></body></html>')


class HtmlWindow:
    """One plugin window: Python keeps the state and posts views; the page posts actions.
    run() blocks the calling (slicing) thread until finish() is called or it's closed."""

    def __init__(self, title, js, width, height, view_fn, action_fn):
        self.title = title; self.js = js; self.size = (width, height)
        self.view_fn = view_fn; self.action_fn = action_fn
        self.done = threading.Event(); self.result = None; self.win = None; self.lock = threading.RLock()

    def push(self):
        try:
            with self.lock:
                v = self.view_fn()
            if self.win is not None and not self.done.is_set():
                self.win.post({'view': v})
        except Exception:
            write_log('window update failed: ' + traceback.format_exc())

    def _on_message(self, m):            # UI thread
        if not isinstance(m, dict):
            return
        if m.get('cmd') == 'ready':
            self.push(); return
        try:
            with self.lock:
                self.action_fn(m)
        except Exception:
            write_log('window action failed: ' + traceback.format_exc())
            show_box('Something went wrong in the window:\n\n' + traceback.format_exc(limit=2))
        if not self.done.is_set():
            self.push()

    def _on_close(self):
        if self.result is None:
            self.result = 'closed'
        self.done.set()

    def finish(self, result):
        self.result = result
        self.done.set()
        try:
            if self.win is not None:
                self.win.close()
        except Exception:
            pass

    def run(self):
        self.win = orca.host.ui.create_window(html=page(self.js), title=self.title, width=self.size[0], height=self.size[1],
                                              on_message=self._on_message, on_close=self._on_close,
                                              style=orca.host.ui.WINDOW_MODELESS)
        ctx = CTX['ctx']
        while not self.done.wait(0.3):
            if ctx is not None:
                try:
                    if ctx.cancelled():
                        self.finish('closed')
                except Exception:
                    pass
        return self.result


def in_thread(fn):
    th = threading.Thread(target=fn, daemon=True)
    th.start()
    return th


# --- first setup / add printer ----------------------------------------------------------
SETUP_JS = r"""
function render() { var a = document.getElementById('app'); a.innerHTML = '';
  a.appendChild(h('h1', {}, [V.title]));
  a.appendChild(h('p', {}, ["Pick your U1 from the printers found on the network, or type its IP address or hostname. " +
    "The plugin reads the BMCU-Klipper setup from it (channels, routing, what's loaded) and saves it."]));
  var found = V.found.map(function (f) { return f.label; });
  var again = h('button', {disabled: V.busy}, ['Search again']);
  again.addEventListener('click', function () { send({cmd: 'search', subnet: document.getElementById('subnet').value}); });
  a.appendChild(h('div', {class: 'row'}, [h('span', {}, ['Printers found']),
     found.length ? sel(found, V.pick, function (i) { document.getElementById('host').value = V.found[i].ip; }) : h('span', {class: 'muted'}, [V.searching ? 'searching...' : 'none']),
     again]));
  var sub = h('input', {type: 'text', id: 'subnet', value: V.subnet, style: 'width:220px'});
  a.appendChild(h('div', {class: 'row'}, [h('span', {}, ['Also search subnet']), sub,
     h('span', {class: 'muted small'}, ['e.g. 192.168.10.0/24 or 192.168.10.0 255.255.255.0'])]));
  var host = h('input', {type: 'text', id: 'host', value: V.host, style: 'width:220px'});
  a.appendChild(h('div', {class: 'row'}, [h('span', {}, ['Printer address']), host]));
  if (V.status) a.appendChild(h('div', {class: 'note ' + (V.error ? 'err' : 'warn')}, [V.status]));
  var bar = h('div', {class: 'bar'}, [h('span', {class: 'sp'})]);
  var cancel = h('button', {}, [V.adding ? 'Cancel' : 'Cancel export']);
  cancel.addEventListener('click', function () { send({cmd: 'cancel'}); });
  var conn = h('button', {class: 'primary', disabled: V.busy}, ['Connect']);
  conn.addEventListener('click', function () { send({cmd: 'connect', host: host.value, subnet: sub.value}); });
  bar.appendChild(cancel); bar.appendChild(conn); a.appendChild(bar);
}
"""


def gui_first_setup(host, subnet, adding=False):
    """Find a printer and read its tools. (host, tools, name) or None."""
    st = {'host': host or str(PP_ENV.get('print_host') or ''), 'subnet': subnet or '', 'found': [], 'pick': 0,
          'status': '', 'error': False, 'busy': False, 'searching': False, 'result': None}

    def view():
        return {'title': 'Add a printer' if adding else TITLE + ' - first setup', 'adding': adding,
                'found': [{'ip': f['ip'], 'label': '%s  (%s)%s' % (f['name'], f['ip'], '' if f['bmcu'] else '  - no BMCU-Klipper')}
                          for f in st['found']],
                'pick': st['pick'], 'host': st['host'], 'subnet': st['subnet'], 'status': st['status'],
                'error': st['error'], 'busy': st['busy'], 'searching': st['searching']}

    def search(sub):
        bad = check_subnets(sub)
        if bad:
            st.update(status='Subnet: ' + bad, error=True); return
        st.update(busy=True, searching=True, error=False, subnet=sub,
                  status='Searching the network for printers (a few seconds)...')

        def work():
            try:
                found = find_printers(sub)
                st['found'] = sorted([f for f in found if f['bmcu']], key=lambda f: f['name']) + \
                    sorted([f for f in found if not f['bmcu']], key=lambda f: f['name'])
                if st['found']:
                    st['status'] = 'Found %d printer(s). Pick one, or type an address, then Connect.' % len(st['found'])
                    if not st['host']:
                        st['host'] = st['found'][0]['ip']
                else:
                    st['status'] = "No printers found. Type the printer's IP address (it's on the U1's screen under network settings)."
            except PermissionError:
                st.update(status="Searching the network needs Full access for this plugin (Plugins > BMCU-Klipper Tool "
                                 "Assignment > permissions). Without it, type the printer's address.", error=False)
            except Exception as e:
                st.update(status='Search failed: %s' % e, error=True)
            st.update(busy=False, searching=False)
            w.push()
        in_thread(work)

    def act(m):
        cmd = m.get('cmd')
        if cmd == 'cancel':
            w.finish('cancel')
        elif cmd == 'search':
            search(str(m.get('subnet') or '').strip())
        elif cmd == 'connect':
            h = str(m.get('host') or '').strip(); st['host'] = h; st['subnet'] = str(m.get('subnet') or '')
            if not h:
                st.update(status='Enter the printer address first.', error=True); return
            # First contact with a new address happens HERE, on OrcaSlicer's UI thread, so its
            # permission question can be answered right away (not refused off-thread).
            res, err = get_printer_tools(h, [])
            if err:
                st.update(status=err + permission_hint(err), error=True); return
            names = [f['name'] for f in st['found'] if f['ip'] == h and f['name'] != h]
            st['result'] = (h, res, names[0] if names else printer_hostname(h))
            w.finish('ok')
    w = HtmlWindow(TITLE + ' - ' + ('add printer' if adding else 'first setup'), SETUP_JS, 640, 420, view, act)
    if not st['host']:
        search(st['subnet'])
    w.run()
    return st['result']


# --- busy notice while the layout search runs --------------------------------------------
def gui_solve_wait(solver, k):
    try:
        ui = orca.host.ui
        pd = ui.create_progress_dialog('BMCU tool layout', 'Finding the best tool layout for %d colors...' % k,
                                       100, ui.PD_APP_MODAL | ui.PD_CAN_ABORT | ui.PD_ELAPSED_TIME)
    except Exception:
        pd = None
    t0 = time.time()
    while not solver.wait(0.2):
        if pd is not None:
            try:
                if not pd.pulse('Finding the best tool layout for %d colors... %d s (Cancel = use the best so far; stops by '
                                'itself after %d s)' % (k, int(time.time() - t0) + 1, SEARCH_TIME_MS // 1000)):
                    solver.cancel = True
            except Exception:
                pass
    if pd is not None:
        try:
            pd.close()
        except Exception:
            pass


# --- Printer tools -------------------------------------------------------------------------
TOOLS_JS = r"""
var F = null;
function render() { var a = document.getElementById('app'); a.innerHTML = '';
  if (!F || V.fresh) { F = {name: V.name, opts: V.opts.map(function (o) { return o.on; }),
                            rows: V.rows.map(function (r) { return {on: r.on, slot: r.slot}; })}; }
  a.appendChild(h('h1', {}, ['Printer tools']));
  a.appendChild(h('div', {class: 'sub'}, [V.host]));
  if (V.notice) a.appendChild(h('div', {class: 'note warn'}, [V.notice]));
  a.appendChild(h('p', {class: 'small'}, [V.intro]));
  var nm = h('input', {type: 'text', value: F.name, style: 'width:220px'}); nm.addEventListener('input', function () { F.name = nm.value; });
  a.appendChild(h('div', {class: 'row'}, [h('span', {}, ['Printer name']), nm]));
  var t = h('table', {}, [h('tr', {}, ['', 'Tool', 'Feeds', 'Use', 'Orca slot'].map(function (x) { return h('th', {}, [x]); }))]);
  var slots = ['-']; for (var n = 1; n <= V.nslots; n++) slots.push(String(n));
  V.rows.forEach(function (r, i) {
    var c = h('input', {type: 'checkbox', checked: F.rows[i].on, disabled: r.locked});
    c.addEventListener('change', function () { F.rows[i].on = c.checked; check(); });
    var s = sel(slots, F.rows[i].slot, function (v) { F.rows[i].slot = v; check(); }, {disabled: r.slot_locked});
    t.appendChild(h('tr', {}, [h('td', {}, [sw(r.color)]), h('td', {}, [r.label]), h('td', {}, [r.head]), h('td', {}, [c]), h('td', {}, [s])]));
  });
  a.appendChild(t);
  V.opts.forEach(function (o, i) { a.appendChild(h('div', {class: 'row'}, [chk(o.text, F.opts[i], function (v) { F.opts[i] = v; })])); });
  a.appendChild(h('div', {id: 'status', class: 'row muted'}, [V.status || '']));
  var bar = h('div', {class: 'bar'}, [btn('Refresh from printer', {cmd: 'refresh'}, {disabled: V.busy}), h('span', {class: 'sp'}), btn('Cancel', {cmd: 'cancel'})]);
  var save = h('button', {class: 'primary', id: 'save'}, ['Save']);
  save.addEventListener('click', function () { send({cmd: 'save', form: F}); });
  bar.appendChild(save); a.appendChild(bar); check();
}
function check() { var seen = {}, bad = '', on = 0;
  F.rows.forEach(function (r, i) { if (!r.on || V.rows[i].locked) return; on++;
    if (r.slot > 0) { if (seen[r.slot]) bad = 'Orca slot ' + r.slot + ' is used by two tools.'; seen[r.slot] = 1; } });
  if (!on) bad = 'Enable at least one tool.';
  var s = document.getElementById('status'); if (bad) { s.textContent = bad; s.className = 'note err'; } else { s.textContent = V.status || ''; s.className = 'row muted'; }
  document.getElementById('save').disabled = !!bad; }
"""

TOOL_OPTIONS = [('matchLoaded', "When layouts tie on swaps, prefer tools already loaded with the print's color (from the last refresh)"),
                ('separateMaterials', 'Keep different filament types (PLA, PETG, TPU ...) on separate heads'),
                ('expectMaterial', 'Printer refuses to start if a BMCU channel is labeled with a different filament type than the print needs'),
                ('closeBackups', 'When a spool runs out, continue from an unused spool of the same type and a close color'),
                ('keepSpares', 'Keep duplicate spools (same type and color) free as backups when there are enough other tools'),
                ('purgeFansOff', 'Turn the part cooling fan off before each tool change, so the purge drops as a blob '
                                 'instead of being blown into strings (OrcaSlicer turns it back on after the change)')]


def gui_tools_dialog(host, notice):
    st = {'tools': [tool_record(t) for t in SETTINGS['tools']], 'from': str(SETTINGS['toolsFrom'] or ''),
          'ok': False, 'busy': False, 'fresh': True, 'err': ''}
    intro = ('Untick a tool to keep the optimizer off it. "Orca slot" is the filament slot that normally stands for that tool - '
             "your slot layout. A stock feeder on a head with BMCU channels is locked out (BMCU-Klipper owns that head), and a "
             "head with stock filament already in it is locked to that filament until it's pulled out by hand. BMCU routing to "
             'heads is set in the BMCU panel; press Refresh after changing it.')

    def view():
        tools = st['tools']
        owned = {r['head'] for r in tools if r['source'] == 'bmcu' and r['routed'] and r['head'] > 0}
        locked = {r['head'] for r in tools if r['source'] == 'stock' and r['stockLoaded']}
        rows = []
        for r in tools:
            shared = r['source'] == 'stock' and r['head'] in owned
            is_locked = (r['source'] == 'bmcu' and r['head'] in locked) or shared
            if shared:
                ht = 'Head %d - locked by BMCU' % r['head']
            elif is_locked:
                ht = 'Head %d - locked: stock filament is in this head' % r['head']
            elif r['source'] == 'stock' and r['stockLoaded']:
                ht = 'Head %d - filament in head' % r['head']
            else:
                ht = ('Head %d' % r['head']) if r['head'] > 0 else 'not routed'
            rows.append({'label': 'T%d  %s  [%s]' % (r['tool'], r['label'], filament_where(r)), 'head': ht,
                         'color': to_hex6(r['color']) if r['color'] else '', 'on': bool(r['enabled']) and not is_locked and r['routed'],
                         'locked': (not r['routed']) or is_locked, 'slot': max(0, int(r['slot'])), 'slot_locked': tool_locked(r, tools)})
        status = st['err'] or (('Read from the printer %s.' % st['from']) if st['from'] else 'Not read from the printer yet - press Refresh.')
        v = {'host': host, 'name': SETTINGS['name'], 'notice': notice, 'intro': intro, 'rows': rows, 'nslots': max(8, len(tools)),
             'opts': [{'text': t, 'on': bool(SETTINGS[k])} for k, t in TOOL_OPTIONS], 'status': status, 'busy': st['busy'],
             'fresh': st['fresh']}
        st['fresh'] = False
        return v

    def act(m):
        cmd = m.get('cmd')
        if cmd == 'cancel':
            w.finish('cancel')
        elif cmd == 'refresh':
            st['busy'] = True

            def work():
                res, err = get_printer_tools(host, st['tools'])
                if err:
                    st['err'] = err + permission_hint(err)
                else:
                    st.update(tools=res, err='', fresh=True); st['from'] = now_stamp()
                st['busy'] = False
                w.push()
            in_thread(work)
        elif cmd == 'save':
            f = m.get('form') or {}
            for i, r in enumerate(st['tools']):
                fr = (f.get('rows') or [])[i] if i < len(f.get('rows') or []) else None
                if not fr:
                    continue
                owned = any(o['source'] == 'bmcu' and o['routed'] and o['head'] == r['head'] for o in st['tools'])
                blocked = (r['source'] == 'stock' and owned) or (r['source'] == 'bmcu' and any(
                    o['source'] == 'stock' and o['head'] == r['head'] and o['stockLoaded'] for o in st['tools']))
                if r['routed'] and not blocked:
                    r['enabled'] = bool(fr.get('on'))
                if not tool_locked(r, st['tools']):
                    r['slot'] = int(fr.get('slot') or 0)
            complete_slots(st['tools'])
            opts = f.get('opts') or []
            for n, (k, _) in enumerate(TOOL_OPTIONS):
                if n < len(opts):
                    SETTINGS[k] = bool(opts[n])
            SETTINGS.update(tools=st['tools'], toolsFrom=st['from'], name=str(f.get('name') or '').strip())
            save_settings()
            st['ok'] = True
            w.finish('ok')
    w = HtmlWindow('Printer tools', TOOLS_JS, 860, 680, view, act)
    w.run()
    return st['ok']


# --- tool heads (shared by the assignment window and the BMCU panel) -----------------------------
class HeadControls:
    """Unload queue, uncertain-route confirmation and refresh for the active printer."""

    def __init__(self, get_host, on_changed, on_done):
        self.get_host = get_host; self.on_changed = on_changed; self.on_done = on_done
        self.queue = []; self.running = False; self.current = -1; self.cancel = False
        self.done = set(); self.text = {}; self.errs = []; self.ok = 0; self.busy = ''

    def loaded(self):
        st = SETTINGS['tools']
        return sorted([r for r in st if (r['source'] == 'bmcu' and r['loaded']) or
                       (r['source'] == 'stock' and r['stockLoaded'] and not r['stockPull'])], key=lambda r: (r['head'], r['tool']))

    def view(self):
        st = SETTINGS['tools']
        items = []
        for i, r in enumerate(self.loaded()):
            what = ('%s T%d' % (r['label'], r['tool'])) if r['source'] == 'bmcu' else ('stock feeder T%d' % r['tool'])
            if r['material']:
                what += ' (' + r['material'] + ')'
            lab = 'head %d: %s' % (r['head'], what)
            if i in self.queue:
                txt = 'Queued - ' + lab
            else:
                txt = self.text.get(i, 'Unload ' + lab)
            items.append({'i': i, 'text': txt, 'done': i in self.done})
        pulls = ['Head %d: %sin the stock feeder (T%d) - pull it out to use the BMCU on this head.'
                 % (r['head'], (r['material'] + ' ') if r['material'] else '', r['tool'])
                 for r in sorted(st, key=lambda r: r['head']) if r['source'] == 'stock' and r['stockLoaded'] and r['stockPull']
                 and any(o['source'] == 'bmcu' and o['routed'] and o['head'] == r['head'] for o in st)]
        unc = [{'tool': r['tool'], 'text': 'Head %d: %s (T%d) route is UNCERTAIN - where is its filament?' % (r['head'], r['label'], r['tool'])}
               for r in sorted(st, key=lambda r: r['tool']) if r['source'] == 'bmcu' and r.get('uncertain')]
        return {'unload': items, 'pulls': pulls, 'uncertain': unc, 'states': [[s, t] for s, t, _ in ROUTE_STATES],
                'running': self.running, 'busy': self.busy}

    def action(self, m):
        cmd = m.get('cmd')
        if cmd == 'unload':
            self.click_unload(int(m.get('i', -1)))
        elif cmd == 'route' and not self.running and not self.busy:
            self.confirm_route(int(m.get('tool', -1)), str(m.get('state') or ''))
        elif cmd == 'refresh' and not self.running and not self.busy:
            self.refresh()
        else:
            return False
        return True

    def click_unload(self, i):
        if i in self.queue:
            self.queue.remove(i); return
        if self.current == i:
            if self.text.get(i, '').startswith('Waiting'):
                self.cancel = True
            return
        if i in self.done or i < 0 or i >= len(self.loaded()):
            return
        self.queue.append(i)
        if self.running:
            return
        self.running = True; self.errs = []; self.ok = 0
        recs = self.loaded(); h = self.get_host()
        in_thread(lambda: self._unload_worker(h, recs))

    def _unload_worker(self, h, recs):
        while self.queue:
            jx = self.queue.pop(0)
            self.current = jx; self.cancel = False
            rec = recs[jx]; lab = 'head %d' % rec['head']
            err = ''
            while True:
                act, detail = printer_activity(h)
                if act == 'printing':
                    err = 'head %d: not unloaded - %s' % (rec['head'], detail); break
                if act != 'busy':
                    break
                self.text[jx] = 'Waiting (printer busy: %s) - %s' % (detail, lab); self.on_changed()
                until = time.time() + 3
                while time.time() < until and not self.cancel:
                    time.sleep(0.1)
                if self.cancel:
                    break
            if self.cancel:
                self.current = -1; self.text.pop(jx, None); self.on_changed(); continue
            if not err:
                self.text[jx] = 'Unloading - ' + lab; self.on_changed()
                err = invoke_unload(h, rec)
            self.current = -1
            if err:
                self.errs.append(err + permission_hint(err)); self.text[jx] = 'Failed - ' + lab
            else:
                self.ok += 1; self.done.add(jx); self.text[jx] = 'Unloaded - ' + lab
            self.on_changed()
        live = None
        if self.ok > 0:
            try:
                live = update_live_state(h, True)
            except Exception:
                live = ''
        self.running = False
        if self.errs:
            show_box('\n\n'.join(self.errs), 'Unload failed', 'warning')
        self.on_done(live if self.ok > 0 else None)

    def confirm_route(self, tool, state):
        r = next((x for x in SETTINGS['tools'] if x['tool'] == tool and x['source'] == 'bmcu'), None)
        texts = [x for x in ROUTE_STATES if x[0] == state]
        if r is None or not texts:
            return
        why = texts[0][2] % r['head']
        if not ask_yes('Tell BMCU-Klipper that %s?\n\nOnly confirm this after checking it on the printer: BMCU-Klipper moves '
                       'filament based on it.' % why, 'Confirm route'):
            return
        h = self.get_host()
        cmd = 'BMCU_ROUTE_CONFIRM DEVICE=%s CHANNEL=%d STATE=%s' % (r['device'], r['channel'], state)
        self.busy = 'Confirming the route...'

        def work():
            act, detail = printer_activity(h)
            if act == 'printing':
                err = "Can't confirm a route while %s - cancel the print first." % detail
            else:
                try:
                    http_json(base_url(h) + '/printer/gcode/script', 60, {'script': cmd}, 'POST'); err = ''
                except Exception as e:
                    err = '%s failed: %s' % (cmd, err_text(e)) + permission_hint(e)
            self.busy = ''
            if err:
                show_box(err, 'Route not confirmed', 'warning'); self.on_changed()
            else:
                self._read_printer(h)
        in_thread(work)

    def refresh(self):
        self.busy = 'Reading the printer...'
        h = self.get_host()
        in_thread(lambda: self._read_printer(h))

    def _read_printer(self, h):
        res, err = get_printer_tools(h, SETTINGS['tools'])
        self.busy = ''
        if err:
            show_box(err + permission_hint(err), 'Refresh failed', 'warning'); self.on_changed(); return
        SETTINGS['host'] = h
        self.on_done(apply_printer_tools(res, True))


HEADS_JS = r"""
function heads(H, a) {
  a.appendChild(h('div', {class: 'muted'}, [H.unload.length ? 'Loaded:' : 'Nothing loaded in the heads.']));
  H.pulls.forEach(function (p) { a.appendChild(h('div', {class: 'note warn'}, [p])); });
  var r = h('div', {class: 'row'}); H.unload.forEach(function (u) {
    r.appendChild(btn(u.text, {cmd: 'unload', i: u.i}, {disabled: u.done || !!H.busy})); }); a.appendChild(r);
  H.uncertain.forEach(function (u) { var row = h('div', {class: 'note warn row'}, [h('span', {}, [u.text])]);
    H.states.forEach(function (s) { row.appendChild(btn(s[1], {cmd: 'route', tool: u.tool, state: s[0]}, {disabled: H.running || !!H.busy})); });
    a.appendChild(row); });
  a.appendChild(h('div', {class: 'row'}, [btn(H.busy || 'Refresh from printer', {cmd: 'refresh'}, {disabled: H.running || !!H.busy})]));
}
"""

# --- the assignment window --------------------------------------------------------------------
ASSIGN_JS = HEADS_JS + r"""
function render() { var a = document.getElementById('app'); a.innerHTML = '';
  a.appendChild(h('h1', {}, ['Tool Assignment'])); a.appendChild(h('div', {class: 'sub'}, [V.subtitle]));
  var pr = h('div', {class: 'row'}, [h('span', {}, ['Printer']),
     sel(V.printers, V.printer, function (i) { send({cmd: 'printer', index: i}); }, {disabled: V.locked}),
     btn('Add printer...', {cmd: 'add'}, {disabled: V.locked}), btn('Remove', {cmd: 'remove'}, {disabled: V.locked || V.printers.length < 2})]);
  a.appendChild(pr);
  a.appendChild(h('div', {class: 'head'}, [V.rec]));
  notes(V.notices).forEach(function (n) { a.appendChild(n); });
  a.appendChild(h('h2', {}, ['Tools']));
  var t = h('table', {}, [h('tr', {}, ['Tool', 'Slot layout', 'Colors'].map(function (x) { return h('th', {}, [x]); }))]);
  V.tools.forEach(function (r) {
    var cell = h('td', {});
    if (!r.colors.length) cell.appendChild(h('span', {class: 'muted'}, ['Not used']));
    r.colors.forEach(function (c) {
      cell.appendChild(h('div', {class: 'color'}, [sw(c.hex), h('span', {class: 'ctext'}, [c.text]),
        sel(c.menu, 0, function (i) { send({cmd: 'move', i: c.i, pick: i}); }, {off: c.off, disabled: V.locked})])); });
    if (r.backup) cell.appendChild(h('div', {class: 'color small'}, [h('span', {class: 'muted', style: 'margin-left:22px'}, ['If it runs out']),
        sel(r.backup.items, r.backup.cur, function (i) { send({cmd: 'backup', t: r.t, pick: i}); }, {disabled: V.locked})]));
    t.appendChild(h('tr', {}, [h('td', {}, [r.label]), h('td', {}, [r.slot]), cell]));
  });
  V.unavail.forEach(function (r) { t.appendChild(h('tr', {class: 'off'}, [h('td', {}, [r.label]), h('td', {}, ['-']), h('td', {class: 'why'}, [r.why])])); });
  a.appendChild(t);
  a.appendChild(h('div', {class: 'head'}, [V.status]));
  if (V.warns.length) a.appendChild(h('div', {class: 'note err'}, V.warns.map(function (x) { return h('div', {}, ['• ' + x]); })));
  a.appendChild(h('h2', {}, ['Tool heads'])); heads(V.heads, a);
  a.appendChild(h('div', {class: 'row'}, [h('span', {}, ['After the print, the BMCU filament:']),
     sel(V.ends, V.end, function (i) { send({cmd: 'opt', key: 'end', value: i}); }, {disabled: V.locked})]));
  a.appendChild(h('h2', {}, [V.send_title]));
  var host = h('input', {type: 'text', value: V.host, style: 'width:180px', disabled: V.locked});
  host.addEventListener('change', function () { send({cmd: 'opt', key: 'host', value: host.value}); });
  var r2 = h('div', {class: 'row'}, [h('span', {}, ['Printer address']), host]);
  V.cal.forEach(function (c) { r2.appendChild(chk(c.text, c.on, function (v) { send({cmd: 'opt', key: c.key, value: v}); }, V.locked)); });
  a.appendChild(r2);
  if (V.also.length) { var r3 = h('div', {class: 'row'}, [h('span', {}, ['Also print on'])]);
    V.also.forEach(function (p) { r3.appendChild(chk(p.name, p.on, function (v) { send({cmd: 'also', i: p.i, value: v}); }, V.locked)); });
    a.appendChild(r3); a.appendChild(h('div', {class: 'muted small'}, ['Each printer needs the same tools on the same heads with the right filament loaded; Save & print checks them all first.'])); }
  a.appendChild(h('p', {class: 'muted small'}, [V.footer]));
  var bar = h('div', {class: 'bar'}, [btn('Printer tools...', {cmd: 'tools'}, {disabled: V.locked}), btn('Recommended', {cmd: 'rec'}, {disabled: V.locked}),
     btn('Reset to default', {cmd: 'reset'}, {disabled: V.locked}), h('span', {class: 'sp'}), btn('Cancel export', {cmd: 'cancel'}, {disabled: V.locked}),
     V.uploads ? null : btn(V.printing ? 'Checking printers...' : 'Save & print', {cmd: 'print'}, {disabled: !V.can_print || V.locked}),
     btn(V.uploads ? (V.printing ? 'Checking the printer...' : 'Save & send') : 'Save file', {cmd: 'ok'}, {primary: true, disabled: !V.can_ok || V.locked})]);
  a.appendChild(bar);
}
"""


def gui_assignment(plan, host, opt, orca_uploads, live_note, filename):
    j = plan.job; k = j.k; tools = plan.tools; tr = plan.tool_rec
    sep = '   |   '
    res = {'result': 'cancel', 'assign': None, 'host': host, 'opt': dict(opt), 'live': None, 'index': ACTIVE['i'],
           'also': [], 'backups': {}, 'end': SETTINGS['endMode']}
    S = {'assign': list(plan.rec), 'bk': {}, 'host': host, 'opt': dict(opt), 'printing': False,
         'end': next((n for n, x in enumerate(END_MODES) if x[0] == SETTINGS['endMode']), 0),
         'also': {i for i, p in enumerate(PRINTERS) if i != ACTIVE['i'] and p['host'] and p['host'] in SETTINGS['alsoPrint']},
         'menus': {}}
    tool_slot = {t: s + 1 for s, t in plan.slot_tool.items()}
    color_text = ['Slot %d   %s   %s' % (s + 1, j.types[s] if j.types and s < len(j.types) else '?', j.amount(s)) for s in j.used]

    def est_flags():
        plan.est_bed = S['opt']['bed']
        plan.est_flow = S['opt']['flow']

    def close(result):
        res.update(result=result, assign=list(S['assign']), host=S['host'].strip(), opt=dict(S['opt']),
                   also=sorted(S['also']), backups=plan.backups(S['assign'], S['bk']), end=END_MODES[S['end']][0])
        SETTINGS['alsoPrint'] = [PRINTERS[i]['host'] for i in sorted(S['also'])]
        w.finish(result)

    def on_heads_done(live):
        res['live'] = live
        close('retry')
    hc = HeadControls(lambda: S['host'].strip(), lambda: w.push(), on_heads_done)

    def view():
        est_flags()
        a = S['assign']
        rows = []
        for t in tools:
            mine = [i for i in range(k) if a[i] == t]
            colors = []
            for i in mine:
                txt = color_text[i]
                if plan.use_loaded and plan.move_of.get((i, t)) == 0:
                    txt += '  (spool matches)'
                items = ['Move...']; acts = [None]; shares = []
                for oth in tools:
                    if oth == t:
                        continue
                    there = [x for x in range(k) if a[x] == oth]
                    if not there:
                        items.append('Move to T%d (unused)' % oth); acts.append(('move', oth))
                    else:
                        names = ' + '.join('slot %d' % (j.used[x] + 1) for x in there)
                        items.append('Swap with T%d (%s)' % (oth, names)); acts.append(('swap', oth)); shares.append((oth, names))
                if shares:
                    items.append('--- or share a tool ---'); acts.append(None)
                    for oth, names in shares:
                        items.append('Share T%d (with %s)' % (oth, names)); acts.append(('move', oth))
                S['menus'][i] = acts
                colors.append({'i': i, 'hex': j.hex6(j.used[i]), 'text': txt, 'menu': items,
                               'off': [x is None and n > 0 for n, x in enumerate(acts)]})
            backup = None
            if mine and tr[t]['source'] == 'bmcu':
                cands = plan.backup_candidates(t, a)
                if cands:
                    cur = plan.backups(a, S['bk']).get(t, -1)
                    vals = [-1] + [r['tool'] for r in cands]
                    items = ['Pause the print (no backup)'] + [
                        'Continue from T%d - %s %s%s' % (r['tool'], r['material'], r['color'] or '',
                                                         '' if color_close(tr_color(tr[t]), tr_color(r)) else ' (different color)')
                        for r in cands]
                    S.setdefault('bkvals', {})[t] = vals
                    backup = {'items': items, 'cur': vals.index(cur) if cur in vals else 0}
            rows.append({'t': t, 'label': tool_label(tr[t]), 'slot': ('slot %d' % tool_slot[t]) if t in tool_slot else '-',
                         'colors': colors, 'backup': backup})
        warns = []
        why = plan.stock_rule(a) or plan.nozzle_rule(a)
        if why:
            status = "This assignment can't be used."; warns.append(why)
        else:
            sw, hcn, b2b = plan.measure(a)
            status = 'This assignment:   ' + sep.join(x for x in ['%d swaps (%d back-to-back)' % (sw, b2b), plan.fmt_est(a),
                                                                  '%d spools to load' % plan.moves(a), '%d head changes' % hcn] if x)
            for f in (plan.shared_tool, plan.material_mix):
                x = f(a)
                if x:
                    warns.append(x)
            e = plan.empty_chosen(a)
            if e:
                warns.append('%s had no filament at the last refresh - load it first, or the print will stop at the start.' % ', '.join(e))
        notices = []
        if plan.merged:
            notices.append({'text': "This print has %d colors but only %d tools, so some colors share a tool. The recommendation "
                                    "pairs close colors that alternate the most, which saves the most tool changes." % (k, len(tools))})
        if live_note:
            notices.append({'text': live_note})
        if plan.mat_forced:
            notices.append({'text': "This print has %d filament types and there aren't enough heads to keep them apart, so the "
                                    "recommendation puts different types on the same head." % len(j.mat_ids)})
        frm = ('Tools read from the printer %s.' % SETTINGS['toolsFrom']) if SETTINGS['toolsFrom'] else 'Tools not read from the printer yet.'
        hv = hc.view()
        return {
            'subtitle': '%s%s%d colors%s%d tools available' % (filename, sep, k, sep, len(tools)),
            'printers': [('%s  (%s)' % (p['name'], p['host'])) if p.get('name') else p['host'] for p in PRINTERS],
            'printer': ACTIVE['i'],
            'rec': 'Recommended:   ' + sep.join(x for x in ['%d swaps' % plan.rec_swaps, plan.fmt_est(plan.rec),
                                                         '%d spools to load' % plan.rec_moves] if x),
            'notices': notices, 'tools': rows,
            'unavail': [{'label': tool_label(r), 'why': why_} for r, why_ in plan.unavail],
            'status': status, 'warns': warns, 'heads': hv,
            'ends': [x[1] for x in END_MODES], 'end': S['end'],
            'send_title': ('Print options - OrcaSlicer sends this file itself; these are set on the printer just before it starts'
                           if orca_uploads else 'Send to printer (Save & print)'),
            'host': S['host'], 'uploads': orca_uploads,
            'cal': [{'key': 'bed', 'text': 'Bed leveling', 'on': S['opt']['bed']},
                    {'key': 'flow', 'text': 'Flow calibration', 'on': S['opt']['flow']},
                    {'key': 'tl', 'text': 'Timelapse', 'on': S['opt']['tl']}],
            'also': [] if orca_uploads else [{'i': i, 'name': printer_name(p), 'on': i in S['also']}
                                              for i, p in enumerate(PRINTERS) if i != ACTIVE['i'] and p['host'] and p['host'] != S['host']],
            'footer': 'Load each spool on the tool shown before printing. Colors on different heads switch for free; two colors on '
                      'the same head cost an unload and load each time the print alternates between them. ' + frm,
            'can_ok': not why, 'can_print': (not why) and (not orca_uploads) and bool(S['host'].strip()) and not S['printing'],
            'printing': S['printing'], 'locked': hv['running'] or bool(hv['busy']) or S['printing'],
        }

    def check_all(h, a, picked):
        block, warn = plan.print_ready(h, a)
        if picked:
            block = ['%s: %s' % (printer_name(SETTINGS), x) for x in block]
            warn = ['%s: %s' % (printer_name(SETTINGS), x) for x in warn]
        for p in picked:
            b2, w2 = plan.print_ready(p['host'], a, p)
            block += ['%s: %s' % (printer_name(p), x) for x in b2]
            warn += ['%s: %s' % (printer_name(p), x) for x in w2]
        return block, warn

    def act(m):
        cmd = m.get('cmd')
        locked = hc.running or bool(hc.busy) or S['printing']
        if hc.action(m):
            return
        if locked:
            return
        if cmd == 'move':
            i = int(m.get('i', -1)); acts = S['menus'].get(i) or []
            pick = int(m.get('pick', 0))
            act_ = acts[pick] if 0 <= pick < len(acts) else None
            if act_ is None:
                return
            frm_t = S['assign'][i]; to = act_[1]
            if act_[0] == 'swap':
                for x in range(k):
                    if S['assign'][x] == to:
                        S['assign'][x] = frm_t
            S['assign'][i] = to
        elif cmd == 'backup':
            t = int(m.get('t', -1)); vals = (S.get('bkvals') or {}).get(t) or [-1]
            p = int(m.get('pick', 0)); v = vals[p] if 0 <= p < len(vals) else -1
            S['bk'][t] = v
            for x, b in list(S['bk'].items()):
                if x != t and b == v and b >= 0:
                    del S['bk'][x]
        elif cmd == 'rec':
            S['assign'] = list(plan.rec)
        elif cmd == 'reset':
            S['assign'] = list(plan.reset_of)
        elif cmd == 'opt':
            key = m.get('key')
            if key == 'host':
                S['host'] = str(m.get('value') or '')
            elif key == 'end':
                S['end'] = int(m.get('value') or 0)
            elif key in ('bed', 'flow', 'tl'):
                S['opt'][key] = bool(m.get('value'))
        elif cmd == 'also':
            i = int(m.get('i', -1))
            if m.get('value'):
                S['also'].add(i)
            else:
                S['also'].discard(i)
        elif cmd == 'printer':
            i = int(m.get('index', -1))
            if 0 <= i < len(PRINTERS) and i != ACTIVE['i']:
                res['index'] = i; close('switch')
        elif cmd == 'add':
            close('add')
        elif cmd == 'remove':
            if ask_yes('Remove %s from the saved printers? Its tool setup and slot layout are deleted.' % printer_name(SETTINGS),
                       'Remove printer'):
                close('keep')
                SETTINGS['host'] = res['host']
                remove_printer(ACTIVE['i'])
                res.update(result='retry', host=SETTINGS['host'])
        elif cmd == 'tools':
            close('tools')
        elif cmd == 'cancel':
            close('cancel')
        elif cmd == 'ok' and not orca_uploads:
            close('ok')
        elif cmd in ('print', 'ok'):
            # Save & print, or Save & send when OrcaSlicer prints it: check the printer first
            final = 'ok' if orca_uploads else 'print'
            S['printing'] = True
            h = S['host'].strip(); a = list(S['assign'])
            picked = [] if orca_uploads else [PRINTERS[i] for i in sorted(S['also'])]

            def work():
                try:
                    block, warn = check_all(h, a, picked)
                except Exception as e:
                    block, warn = ['Check failed: %s' % e], []
                S['printing'] = False
                if not block and not warn:
                    close(final); return
                msg = ''
                if block:
                    msg += 'Problems:\n' + '\n'.join(BULLET + x for x in block) + '\n\n'
                if warn:
                    msg += 'Check:\n' + '\n'.join(BULLET + x for x in warn) + '\n\n'
                msg += 'Print anyway?' if block else 'Print?'
                if ask_ok(msg, 'Before printing', bool(block)):
                    close(final)
                else:
                    w.push()
            in_thread(work)
    w = HtmlWindow(TITLE + ' - ' + filename, ASSIGN_JS, 1120, 900, view, act)
    r = w.run()
    if r in ('closed', None):
        res['result'] = 'cancel'
    return res


# --- the docked BMCU panel ------------------------------------------------------------------------
PANEL_JS = HEADS_JS + r"""
function render() { var a = document.getElementById('app'); a.innerHTML = ''; a.style.paddingBottom = '16px';
  a.appendChild(h('div', {class: 'row'}, [h('b', {}, ['Printer']),
     sel(V.printers, V.printer, function (i) { send({cmd: 'printer', index: i}); }, {disabled: V.heads.running || !!V.heads.busy})]));
  if (V.note) a.appendChild(h('div', {class: 'note warn small'}, [V.note]));
  if (!V.tools.length) a.appendChild(h('p', {class: 'muted'}, ['No printer set up yet - export a print once, or add one in the assignment window.']));
  var t = h('table', {class: 'small'}, []);
  V.tools.forEach(function (r) { t.appendChild(h('tr', {class: r.off ? 'off' : ''}, [h('td', {}, [sw(r.color)]), h('td', {}, [r.label]), h('td', {}, [r.where])])); });
  a.appendChild(t); a.appendChild(h('h2', {}, ['Tool heads'])); heads(V.heads, a);
  a.appendChild(h('div', {class: 'muted small'}, [V.from]));
}
"""


class BmcuPanel:
    """Printer status beside the 3D view: what's in each tool, unload, route confirm, refresh."""

    def __init__(self):
        self.note = ''
        self.hc = HeadControls(lambda: SETTINGS['host'], self.push, self.done)
        self.win = None

    def view(self):
        st = SETTINGS['tools']
        return {'printers': [('%s  (%s)' % (p['name'], p['host'])) if p.get('name') else p['host'] for p in PRINTERS],
                'printer': ACTIVE['i'], 'note': self.note,
                'tools': [{'label': 'T%d %s%s' % (r['tool'], r['label'], (' -> head %d' % r['head']) if r['source'] == 'bmcu' and r['head'] > 0 else ''),
                           'where': filament_where(r), 'color': to_hex6(r['color']) if r['color'] and r['present'] else '',
                           'off': tool_locked(r, st) or not r['present']} for r in sorted(st, key=lambda r: r['tool'])],
                'heads': self.hc.view(),
                'from': ('Read from the printer %s.' % SETTINGS['toolsFrom']) if SETTINGS['toolsFrom'] else ''}

    def push(self):
        try:
            if self.win is not None and self.win.is_open():
                self.win.post({'view': self.view()})
        except Exception:
            pass

    def done(self, live):
        if live is not None:
            self.note = live
        self.push()

    def on_message(self, m):
        if not isinstance(m, dict):
            return
        if m.get('cmd') == 'printer':
            i = int(m.get('index', -1))
            if 0 <= i < len(PRINTERS) and i != ACTIVE['i'] and CTX['ctx'] is not None:
                show_box('Finish the export in the %s window first, then switch printers here.' % TITLE,
                         TITLE, 'info')
            elif 0 <= i < len(PRINTERS) and i != ACTIVE['i']:
                switch_printer(i)
                self.hc = HeadControls(lambda: SETTINGS['host'], self.push, self.done)
                self.hc.refresh()
        elif m.get('cmd') != 'ready':
            self.hc.action(m)
        elif SETTINGS['host']:
            self.hc.refresh()       # fresh status every time the panel opens
        self.push()

    def open(self):
        if CTX['ctx'] is None:      # not while an export is using (and changing) the settings
            load_settings()
        if self.win is not None and self.win.is_open():
            self.win.show(); return
        self.win = orca.host.ui.create_dock_panel(html=page(PANEL_JS), title=TITLE, width=360, height=560,
                                                  on_message=self.on_message, on_close=lambda: None, dock='right')


PANEL = {'p': None}

# ============================ G-code job =====================================
class Job:
    """Everything read from the G-code file."""

    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            raw = f.read()
        text = raw.decode('utf-8-sig', errors='replace')
        del raw
        if text.startswith('; bmcu_klipper_remap:') or text.startswith('; bmcu_remap:'):
            fail('this file was already processed')
        self.map_at_commit = re.search(r'(?m)^BMCU_PRINT_COMMIT\r?$', text) is not None
        self.lines = text.split('\n')               # keeps any \r at line ends (the full text isn't kept)

    def footer_list(self, key):
        prefix = '; %s = ' % key
        for l in reversed(self.lines):
            if l.startswith(prefix):
                raw = l[len(prefix):].rstrip('\r')
                return [v.strip().strip('"') for v in raw.split(';')]
        return None

    def analyse(self):
        lines = self.lines
        used = []; used_mm = {}
        for l in lines:
            if l.startswith('; filament used [mm] = '):
                for s, v in enumerate(l.split('=', 1)[1].split(',')):
                    v = v.strip()
                    if v:
                        try:
                            mm = float(v)
                        except ValueError:
                            fail("couldn't read '; filament used [mm]' (%r)" % v)
                        if mm > 0:
                            used.append(s); used_mm[s] = mm
                break
        if not used:
            fail("couldn't find '; filament used [mm]' in the G-code")
        self.types = self.footer_list('filament_type')
        self.colours = self.footer_list('filament_colour')
        seq = []
        rt = re.compile(r'^T(\d+)\s*$')
        for l in lines:
            if l[:1] == 'T':
                m = rt.match(l.rstrip('\r'))
                if m:
                    t = int(m.group(1))
                    if not seq or seq[-1] != t:
                        seq.append(t)
        for s in seq:
            if s not in used:
                used.append(s); used_mm[s] = 0
        used_g = {}
        for l in lines:
            if l.startswith('; filament used [g] = '):
                for s, v in enumerate(l.split('=', 1)[1].split(',')):
                    g = parse_float(v)
                    if g is not None:
                        used_g[s] = g
                break
        self.used = sorted(set(used)); self.used_mm = used_mm; self.used_g = used_g
        self.seq = seq
        self.orca_sec = None; self.orca_change = 5.0
        for l in lines:
            if l.startswith('; estimated printing time (normal mode) = '):
                self.orca_sec = from_duration(l.split('=', 1)[1])
            elif l.startswith('; machine_tool_change_time = '):
                v = parse_float(l.split('=', 1)[1])
                if v is not None:
                    self.orca_change = v
        self.hc_sec = float(HEAD_CHANGE_SECONDS) if HEAD_CHANGE_SECONDS is not None else self.orca_change
        # solver weights: time = H*changes + B*swaps + (S - H - B)*back-to-back swaps
        self.w_swap = max(1, round(BACKGROUND_SWAP_EXTRA))
        self.w_b2b = max(0, round(SWAP_SECONDS - self.hc_sec - BACKGROUND_SWAP_EXTRA))
        self.k = len(self.used)
        idx = {s: i for i, s in enumerate(self.used)}
        self.seq_c = [idx[s] for s in seq]
        self.mat_name = []
        self.mat_ids = {}
        for s in self.used:
            mn = self.slot_type(s).upper() or '?'
            self.mat_name.append(mn)
            if mn not in self.mat_ids:
                self.mat_ids[mn] = len(self.mat_ids)
        self.mat_groups = [self.mat_ids[m] for m in self.mat_name]

    def slot_nozzle(self, s):
        """Nozzle size slot s was sliced for (0 if unknown). Orca lists one per filament slot."""
        if not hasattr(self, '_nozzles'):
            v = [parse_float(x) for x in ','.join(self.footer_list('nozzle_diameter') or []).split(',')]
            n = len(self.colours or [])
            if v and n and len(v) == n:
                self._nozzles = v
            elif v and all(x is not None and abs(x - v[0]) < 0.001 for x in v):
                self._nozzles = [v[0]] * max(n, 64)
            else:
                self._nozzles = []
        return (self._nozzles[s] or 0.0) if s < len(self._nozzles) else 0.0

    def slot_type(self, s):
        if self.types and s < len(self.types):
            return str(self.types[s]).strip()
        return ''

    def hex6(self, s):
        c = self.colours[s] if self.colours and s < len(self.colours) else '#FFFFFF'
        return to_hex6(c)

    def amount(self, s):
        mm = self.used_mm.get(s, 0)
        if s in self.used_g and (self.used_g[s] > 0 or mm <= 0):
            g = self.used_g[s]
            return ('{:,.0f} g' if g >= 10 else '{:,.1f} g').format(g)
        return '{:,.1f} m'.format(mm / 1000.0)


# ============================ live printer state ===============================
def update_live_state(host, quiet=False):
    """Every time the window opens: re-read the whole tool setup from the printer - which
    head each channel is routed to, the filament type and color in each tool, and what's
    loaded where. Your choices (tools turned off, slot layout) are kept. A stock feeder's
    filament sitting in a head the BMCU also feeds locks that head's BMCU channels.
    Returns a note for the window ('' if none)."""
    if not host:
        return ''
    res, err = get_printer_tools(host, SETTINGS['tools'], 4)
    if err:
        if STATE['printer_without_bmcu']:
            return ''
        when = (' from %s' % SETTINGS['toolsFrom']) if SETTINGS['toolsFrom'] else ''
        note = "%s%s - using the tools, routing and colors saved%s." % (err[0].upper(), err[1:], when)
        if not quiet:
            out('%s: WARNING - %s' % (TITLE, note))
        return note
    if not SETTINGS['name']:
        SETTINGS['name'] = printer_hostname(host)   # settings saved before printers had names
    return apply_printer_tools(res, quiet)


@locked
def apply_printer_tools(tools, quiet=False):
    """Save a fresh read of the printer's tools; returns the note about stock filament
    blocking BMCU channels ('' if none)."""
    SETTINGS.update(tools=tools, toolsFrom=now_stamp())
    save_settings()
    loaded_now = []
    for r in tools:
        if r['source'] != 'stock' or not r['stockLoaded']:
            continue
        on = sorted([o['tool'] for o in tools if o['source'] == 'bmcu' and o['routed'] and o['head'] == r['head']])
        if not on:
            continue
        ch = ', '.join('T%d' % t for t in on)
        if r['stockPull']:
            loaded_now.append("head %d's stock feeder (T%d) is unloaded but the filament is still in the feeder: pull it out so %s can be used" % (r['head'], r['tool'], ch))
        else:
            loaded_now.append("head %d's stock feeder (T%d) has filament loaded in the head, so %s can't be used until it's unloaded and pulled out" % (r['head'], r['tool'], ch))
    if not loaded_now:
        return ''
    note = '; '.join(loaded_now) + '.'
    note = note[0].upper() + note[1:]
    if not quiet:
        out('%s: WARNING - %s' % (TITLE, note))
    return note


# ============================ the plan for one tool setup ======================
class Plan:
    def __init__(self, job):
        self.job = job
        st = SETTINGS['tools']
        self.tool_rec = {r['tool']: r for r in st}
        self.tools = sorted(r['tool'] for r in st if r['enabled'] and not tool_locked(r, st))
        # a head with another nozzle size than every color was sliced for can't be used at all
        self.nozzle_off = {t for t in self.tools if job.used and all(self.nozzle_bad(s, t) for s in job.used)}
        self.tools = [t for t in self.tools if t not in self.nozzle_off]
        # "Keep duplicate spools free": a BMCU spool with the same type and a close color as
        # another usable tool is held back as its backup - only while the rest are enough
        # for every color in the print.
        self.spare_for = {}
        if SETTINGS['keepSpares']:
            kept = []
            order = sorted(self.tools, key=lambda t: (not (self.tool_rec[t]['loaded'] or self.tool_rec[t]['stockLoaded']), t))
            for t in order:
                r = self.tool_rec[t]
                twin = next((x for x in kept if r['source'] == 'bmcu' and r['present'] and r['color'] and same_spool(self.tool_rec[x], r)), None)
                if twin is not None and len(self.tools) - len(self.spare_for) - 1 >= job.k:
                    self.spare_for[t] = twin
                else:
                    kept.append(t)
            self.tools = [t for t in self.tools if t not in self.spare_for]
        self.unavail = []
        for r in sorted(st, key=lambda r: r['tool']):
            if r['tool'] in self.tools:
                continue
            if r['tool'] in self.nozzle_off:
                self.unavail.append((r, 'Head %d has a %.2f mm nozzle; this print is sliced for %s mm'
                                     % (r['head'], r['nozzle'], '/'.join(sorted({'%.2f' % job.slot_nozzle(x) for x in job.used})))))
                continue
            if r['tool'] in self.spare_for:
                self.unavail.append((r, 'Kept free as a backup spool for T%d (Printer tools)' % self.spare_for[r['tool']]))
                continue
            h = r['head']
            bmcu_on = any(o['source'] == 'bmcu' and o['routed'] and o['head'] == h for o in st)
            stock_in = any(o['source'] == 'stock' and o['head'] == h and o['stockLoaded'] for o in st)
            if r['source'] == 'stock' and bmcu_on:
                why = 'Head %d is locked by BMCU' % h
            elif not r['routed'] or h <= 0:
                why = 'Not routed to a head'
            elif r['source'] == 'bmcu' and stock_in:
                why = "Head %d's stock feeder has filament in the head - unload it and pull it out to use this channel" % h
            elif not r['enabled']:
                why = 'Turned off in Printer tools'
            else:
                why = 'Not available'
            self.unavail.append((r, why))
        self.slot_tool = {}
        for t in self.tools:
            sl = self.tool_rec[t]['slot']
            if sl > 0:
                self.slot_tool[sl - 1] = t
        self.head_of = {r['tool']: 0 for r in st}
        for t in self.tools:
            self.head_of[t] = self.tool_rec[t]['head']
        self.max_tool = max([r['tool'] for r in st] or [0])
        self.est_bed = False; self.est_flow = False

    # --- assignment checks (tool per color index) ---
    def measure(self, tool_of):
        loaded = {}
        swaps = head_changes = b2b = 0
        prev = -1
        for c in self.job.seq_c:
            t = tool_of[c]; h = self.head_of.get(t, 0)
            if loaded.get(h, -1) != -1 and loaded[h] != t:
                swaps += 1
                if h == prev:
                    b2b += 1
            loaded[h] = t
            if prev != -1 and h != prev:
                head_changes += 1
            prev = h
        return swaps, head_changes, b2b

    def print_seconds(self, tool_of):
        j = self.job
        if j.orca_sec is None:
            return None
        sw, hc, b2b = self.measure(tool_of)
        n = max(0, len(j.seq_c) - 1)
        return j.orca_sec - j.orca_change * n + j.hc_sec * hc + BACKGROUND_SWAP_EXTRA * (sw - b2b) + SWAP_SECONDS * b2b

    def prep_seconds(self, tool_of, bed, flow):
        sec = 0
        if bed:
            sec += BED_LEVEL_SECONDS
        if flow:
            sec += FLOW_CAL_SECONDS_PER_HEAD * len({self.head_of.get(t, 0) for t in tool_of if t >= 0})
        return sec

    def fmt_est(self, tool_of):
        t = self.print_seconds(tool_of)
        if t is None:
            return ''
        prep = self.prep_seconds(tool_of, self.est_bed, self.est_flow)
        if prep > 0:
            return 'est. %s (incl. %s calibration)' % (fmt_duration(t + prep), fmt_duration(prep))
        return 'est. ' + fmt_duration(t)

    def stock_rule(self, tool_of):
        """Stock feeders can't retract: on a shared head a stock-fed color must be the
        last one that head prints. '' or the reason."""
        for i, t in enumerate(tool_of):
            if t < 0 or self.tool_rec[t]['source'] != 'stock':
                continue
            h = self.head_of.get(t, 0)
            seen = False
            for c in self.job.seq_c:
                tc = tool_of[c]
                if tc < 0 or self.head_of.get(tc, 0) != h:
                    continue
                if c == i:
                    seen = True
                elif seen and tc != t:
                    return ("T%d is a stock feeder (can't retract): head %d would have to switch from it to T%d. "
                            "A stock-fed color can only share a head if it's the last one that head prints." % (t, h, tc))
        return ''

    def material_mix(self, tool_of):
        by_head = {}
        for i, t in enumerate(tool_of):
            if t < 0:
                continue
            by_head.setdefault(self.head_of.get(t, 0), set()).add(self.job.mat_name[i])
        mixed = ['head %d (%s)' % (h, ' + '.join(sorted(m))) for h, m in sorted(by_head.items()) if len(m) > 1]
        if not mixed:
            return ''
        return ('Different filament types share a head: %s. Switching material on one head needs a purge between them '
                'and can leave mixed material in the nozzle; check temperatures and purge volumes.' % ', '.join(mixed))

    def shared_tool(self, tool_of):
        by_tool = {}
        for i, t in enumerate(tool_of):
            if t >= 0:
                by_tool.setdefault(t, []).append(i)
        parts = []
        for t, m in by_tool.items():
            if len(m) < 2:
                continue
            parts.append('slots %s -> T%d' % (' + '.join('%d (%s)' % (self.job.used[x] + 1, self.job.hex6(self.job.used[x])) for x in m), t))
        if not parts:
            return ''
        return 'Several colors share one tool: %s. They all print in the filament loaded in that tool.' % '; '.join(parts)

    def empty_chosen(self, tool_of):
        return ['T%d' % t for t in sorted({t for t in tool_of if t >= 0 and not self.tool_rec[t]['present']})]

    def moves(self, tool_of):
        return sum(self.move_of.get((i, t), 1) for i, t in enumerate(tool_of))

    def nozzle_bad(self, s, t):
        """True if slot s was sliced for a different nozzle size than tool t's head has."""
        want = self.job.slot_nozzle(s); have = self.tool_rec[t].get('nozzle') or 0.0
        return bool(want and have and abs(want - have) > 0.001)

    def nozzle_rule(self, tool_of):
        bad = ['slot %d (%.2f mm) -> T%d (head %d has %.2f mm)' % (self.job.used[i] + 1, self.job.slot_nozzle(self.job.used[i]), t,
                                                                  self.tool_rec[t]['head'], self.tool_rec[t]['nozzle'])
               for i, t in enumerate(tool_of) if t >= 0 and self.nozzle_bad(self.job.used[i], t)]
        if not bad:
            return ''
        return 'Sliced for a different nozzle size: %s. Move these colors to a head with the right nozzle.' % '; '.join(bad)

    # --- backup spools (BMCU_PRINT_REFILL) ---
    def backup_candidates(self, t, tool_of):
        """Unused BMCU spools that could take over when tool t's spool runs out: same
        filament type, same nozzle size, filament present. Closest color first."""
        src = self.tool_rec.get(t)
        if not src or src['source'] != 'bmcu' or t not in tool_of:
            return []
        st = SETTINGS['tools']
        out_ = []
        for r in st:
            if (r['source'] != 'bmcu' or r['tool'] == t or r['tool'] in tool_of or not r['present'] or
                    not r['enabled'] or r.get('uncertain') or tool_locked(r, st)):
                continue
            if str(r['material']).strip().upper() != str(src['material']).strip().upper() or not r['material']:
                continue
            if src.get('nozzle') and r.get('nozzle') and abs(src['nozzle'] - r['nozzle']) > 0.001:
                continue      # BMCU refuses refills between different nozzle sizes
            out_.append(r)
        return sorted(out_, key=lambda r: (color_dist(src['color'] or '#FFFFFF', r['color'] or '#FFFFFF'), r['tool']))

    def backups(self, tool_of, chosen=None):
        """{tool: backup tool} - the user's picks (chosen: tool -> backup, or -1 for none),
        and otherwise the closest-color candidate when "close-color backups" is on (or the
        spool kept free for it). Each backup spool covers one tool."""
        chosen = chosen or {}
        res = {}; taken = set()
        used = sorted({t for t in tool_of if t >= 0})
        for t in used:
            b = chosen.get(t)
            if b is not None and b >= 0 and b in [r['tool'] for r in self.backup_candidates(t, tool_of)]:
                res[t] = b; taken.add(b)
        for t in used:
            if t in chosen or t in res:
                continue
            cands = [r for r in self.backup_candidates(t, tool_of) if r['tool'] not in taken]
            spare = [r for r in cands if self.spare_for.get(r['tool']) == t]
            if spare:
                pick = spare[0]
            elif SETTINGS['closeBackups'] and cands and color_close(tr_color(self.tool_rec[t]), tr_color(cands[0])):
                pick = cands[0]
            else:
                continue
            res[t] = pick['tool']; taken.add(pick['tool'])
        return res

    # --- recommended layout ---
    def build(self):
        j = self.job; k = j.k
        tools = self.tools; tr = self.tool_rec
        # slot-layout assignment (may be invalid if a used slot has no enabled tool)
        self.default_of = []; self.default_valid = True; seen = set()
        for s in j.used:
            t = self.slot_tool.get(s)
            if t is not None and t not in seen:
                self.default_of.append(t); seen.add(t)
            else:
                self.default_of.append(-1); self.default_valid = False
        self.default_why = self.stock_rule(self.default_of) if self.default_valid else ''
        if self.default_why:
            self.default_valid = False

        self.use_loaded = bool(SETTINGS['matchLoaded']) and bool(SETTINGS['toolsFrom'])
        nT = len(tools)
        mv = [[0] * nT for _ in range(k)]; sr = [[0] * nT for _ in range(k)]
        self.move_of = {}
        for i, s in enumerate(j.used):
            p_hex = j.hex6(s); p_mat = j.slot_type(s).upper()
            for jj, t in enumerate(tools):
                r = tr[t]
                ready = False
                if self.use_loaded:
                    # tie-break 1: the closer the tool's current color, the better
                    # (0 = same color and type ... 90 = opposite; empty tool = 95)
                    grade = 95
                    if r['present'] and r['color']:
                        l_mat = str(r['material']).strip().upper()
                        same = (not p_mat or not l_mat or p_mat == l_mat)
                        ready = color_close(p_hex, r['color']) and same
                        dist = math.sqrt(color_dist(p_hex, r['color']))
                        grade = 0 if ready else 1 + round(min(441.0, dist) / 441.0 * 84) + (0 if same else 5)
                else:
                    ready = self.default_of[i] == t
                    grade = int(not ready)
                mv[i][jj] = grade
                d = self.default_of[i]
                off = d >= 0 and d != t
                kind = d >= 0 and ((t >= FIRST_BMCU_TOOL) != (d >= FIRST_BMCU_TOOL))
                sr[i][jj] = 100 * int(off) + int(kind)
                self.move_of[(i, t)] = int(not ready)
                if self.nozzle_bad(s, t):
                    mv[i][jj] = 1000          # sliced for another nozzle size: never put it there
        self.mv = mv; self.sr = sr
        self.no_retract = [tr[t]['source'] == 'stock' for t in tools]
        self.use_mat_rule = bool(SETTINGS['separateMaterials']) and len(j.mat_ids) > 1
        self.mat_forced = False

        # More colors than tools: put the closest colors (same type first) on shared tools
        grp_of = list(range(k))
        self.merged = False
        if k > nT:
            self.merged = True
            groups = [[i] for i in range(k)]
            color_ok = 64 * 64
            while len(groups) > nT:
                grp = [0] * k
                for g, members in enumerate(groups):
                    for x in members:
                        grp[x] = g
                nG = len(groups)
                alt = [[0] * nG for _ in range(nG)]
                prev = -1
                for c in j.seq_c:
                    g = grp[c]
                    if prev >= 0 and prev != g:
                        alt[prev][g] += 1; alt[g][prev] += 1
                    prev = g
                dist = [[0] * nG for _ in range(nG)]
                best_d = None
                for a in range(nG):
                    for b in range(a + 1, nG):
                        dab = 0   # farthest pair, so groups stay tight instead of chaining
                        for x in groups[a]:
                            for y in groups[b]:
                                d = color_dist(j.hex6(j.used[x]), j.hex6(j.used[y]))
                                if j.mat_name[x] != j.mat_name[y]:
                                    d += 1000000
                                dab = max(dab, d)
                        dist[a][b] = dab
                        if best_d is None or dab < best_d:
                            best_d = dab
                limit = max(best_d * 2, color_ok)
                if best_d >= 1000000:
                    limit = best_d * 2
                ba = bb = -1; best_alt = -1; best_pair = None
                for use_limit in (True, False):
                    for a in range(nG):
                        for b in range(a + 1, nG):
                            dab = dist[a][b]
                            if use_limit and dab > limit:
                                continue
                            if alt[a][b] > best_alt or (alt[a][b] == best_alt and dab < best_pair):
                                best_alt = alt[a][b]; best_pair = dab; ba = a; bb = b
                    if ba >= 0:
                        break
                if ba < 0:
                    ba, bb = 0, 1
                groups[ba].extend(groups[bb]); del groups[bb]
            for g, members in enumerate(groups):
                for x in members:
                    grp_of[x] = g
        self.grp_of = grp_of
        if self.merged:
            kS = nT
            seq_s = []
            for c in j.seq_c:
                g = grp_of[c]
                if not seq_s or seq_s[-1] != g:
                    seq_s.append(g)
            mv_s = [[0] * nT for _ in range(kS)]; sr_s = [[0] * nT for _ in range(kS)]; mat_s = [0] * kS
            for i in range(k):
                g = grp_of[i]; mat_s[g] = j.mat_groups[i]
                for jj in range(nT):
                    mv_s[g][jj] += mv[i][jj]; sr_s[g][jj] += sr[i][jj]
        else:
            kS = k; seq_s = j.seq_c; mv_s = mv; sr_s = sr; mat_s = j.mat_groups
        self.kS = kS; self.seq_s = seq_s; self.mv_s = mv_s; self.sr_s = sr_s; self.mat_s = mat_s

    def solve_args(self):
        return (self.kS, self.seq_s, [self.head_of[t] for t in self.tools], self.no_retract, self.mv_s, self.sr_s,
                SEARCH_TIME_MS, self.job.w_swap, self.job.w_b2b,
                self.mat_s if self.use_mat_rule else None)

    def finish(self, pick):
        j = self.job
        self.rec = [self.tools[pick[self.grp_of[i]]] for i in range(j.k)]
        self.rec_swaps = self.measure(self.rec)[0]
        self.rec_moves = self.moves(self.rec)
        self.rec_time = self.print_seconds(self.rec)
        if self.default_valid:
            self.def_swaps = self.measure(self.default_of)[0]
            self.def_time = self.print_seconds(self.default_of)
        else:
            self.def_swaps = self.def_time = None
        # "Reset to default": every color on its slot-layout tool; colors whose slot has
        # no tool go on the last tool in the layout
        by_slot = sorted([t for t in self.tools if self.tool_rec[t]['slot'] > 0], key=lambda t: self.tool_rec[t]['slot'])
        spill = by_slot[-1] if by_slot else self.tools[-1]
        self.reset_of = [self.slot_tool.get(s, spill) for s in j.used]

    def print_ready(self, host, tool_of, other=None):
        """Right before Save & print: re-read the printer and check the chosen assignment
        is still printable. (blockers, warnings) other: a second saved printer that's to
        print the same file - its tools must be on the same heads as on this one."""
        j = self.job
        block = []; warn = []
        act, detail = printer_activity(host)
        if act == 'unknown':
            return ["Couldn't reach the printer: %s" % detail], []
        if act == 'printing':
            block.append('The printer is busy: %s.' % detail)
        elif act == 'busy':
            warn.append("The printer is busy (%s); the print will start when it's free." % detail)
        res, err = get_printer_tools(host, other['tools'] if other else SETTINGS['tools'], 6)
        if err:
            return block + ["Couldn't read BMCU-Klipper: %s" % err], warn
        live = {r['tool']: r for r in res}
        done = set()
        for i, t in enumerate(tool_of):
            if t < 0:
                continue
            s = j.used[i]
            slot_txt = 'slot %d' % (s + 1)
            if t not in live:
                block.append('T%d %s (%s).' % (t, "doesn't exist on this printer" if other else 'no longer exists on the printer', slot_txt)); continue
            lr = live[t]; was = self.tool_rec[t]
            if t not in done:
                done.add(t)
                if lr['source'] == 'bmcu' and (not lr['routed'] or lr['head'] <= 0):
                    block.append('T%d is no longer routed to a head.' % t)
                elif lr['head'] != was['head'] and other:
                    block.append('T%d is on head %d here, but on head %d on %s - the tool layout only fits printers set up the same way.'
                                 % (t, lr['head'], was['head'], printer_name(SETTINGS)))
                elif lr['head'] != was['head']:
                    block.append('T%d is now routed to head %d, not head %d - press Refresh from printer.' % (t, lr['head'], was['head']))
                if not lr['present']:
                    block.append('T%d has no filament loaded.' % t)
                for u in res:
                    if u['source'] == 'bmcu' and u['routed'] and u['head'] == lr['head'] and u.get('uncertain'):
                        uk = 'unc%d' % u['tool']
                        if uk in done:
                            continue
                        done.add(uk)
                        block.append('Head %d has an UNCERTAIN BMCU route (%s, T%d): check where that filament is, then confirm it in the BMCU panel '
                                     '(or BMCU_ROUTE_CONFIRM DEVICE=%s CHANNEL=%d STATE=LOADED / PARKED / EMPTY).' % (lr['head'], u['label'], u['tool'], u['device'], u['channel']))
                if lr['source'] == 'bmcu':
                    if any(x['source'] == 'stock' and x['head'] == lr['head'] and x['stockLoaded'] for x in res):
                        block.append("Head %d's stock feeder has filament in the head, so T%d can't load." % (lr['head'], t))
                else:
                    if any(x['source'] == 'bmcu' and x['routed'] and x['head'] == lr['head'] for x in res):
                        block.append("Head %d is locked by BMCU, so T%d can't be used." % (lr['head'], t))
            # the right filament type where it's expected (colors aren't checked)
            if lr['present']:
                p_mat = j.slot_type(s).upper(); l_mat = str(lr['material']).strip().upper()
                if p_mat and l_mat and p_mat != l_mat:
                    block.append('T%d has %s loaded, but %s needs %s.' % (t, l_mat, slot_txt, p_mat))
        return block, warn


# ============================ rewrite ===========================================
RE_META = re.compile(r'^; (filament used \[(?:mm|cm3|g)\]|filament cost|filament_colour_mode|filament_density|filament_diameter|'
                     r'filament_flow_ratio|filament_max_volumetric_speed|filament_volume_type|nozzle_temperature|'
                     r'nozzle_temperature_initial_layer|nozzle_temperature_range_high|nozzle_temperature_range_low|'
                     r'filament_colour|filament_multi_colors|filament_ids|filament_settings_id|filament_type|filament_vendor)( = |: )(.*)$')


def print_map_line(job, plan, dst, slots):
    """BMCU_PRINT_MAP for one tool. Stock heads need nothing more. For a BMCU channel:
    EXPECT_ENDPOINT makes the printer refuse to start if the channel was routed to
    another head since slicing (the tool layout depends on the heads); EXPECT_MATERIAL
    (Printer tools option) does the same for the filament type it's labeled with.
    MATERIAL= / COLOR= permanently relabel the channel, so they're only written where
    they describe what's actually in it: COLOR only when one of its slots' colors is
    close to the channel's own color (or the channel has none) - so colors merged onto
    it, or a color moved onto another spool, don't relabel the spool."""
    if dst < FIRST_BMCU_TOOL:
        return 'BMCU_PRINT_MAP TOOL=%d' % dst
    r = plan.tool_rec.get(dst) or {}
    s0 = slots[0]
    mat = str(job.types[s0]).strip() if job.types and s0 < len(job.types) and str(job.types[s0]).strip() else ''
    parts = ['BMCU_PRINT_MAP TOOL=%d' % dst]
    if r.get('head', 0) > 0:
        parts.append('EXPECT_ENDPOINT=u1_head%d' % (r['head'] - 1))
    have_mat = str(r.get('material') or '').strip().upper()
    if mat and SETTINGS['expectMaterial'] and have_mat:
        parts.append('EXPECT_MATERIAL="%s"' % mat)
    elif mat and not have_mat:
        parts.append('MATERIAL="%s"' % mat)       # unlabeled channel: label it as sliced
    elif mat and have_mat != mat.upper():
        parts.append('MATERIAL="%s"' % mat)       # check off: label it as sliced, like OrcaSlicer does
    cols = [job.colours[x] for x in slots if job.colours and x < len(job.colours) and str(job.colours[x]).strip()]
    if cols:
        if not r.get('color'):
            parts.append('COLOR="%s"' % cols[0])
        else:
            best = min(cols, key=lambda x: color_dist(x, r['color']))
            if color_close(best, r['color']):
                parts.append('COLOR="%s"' % best)
    return ' '.join(parts)


def purge_fan_points(lines):
    """Line numbers to turn the part cooling fan off at, one per BMCU tool change.

    The U1 hands the part fan's speed on to the next head when it switches heads, and a swap
    on the same head keeps it, so the purge after loading would run with the print's fan on
    and blow the filament into strings. A fan at full speed also takes a few seconds to spin
    down, so the fans go off as soon as the old filament stops printing: at the prime tower's
    "; CP TOOLCHANGE START", or else just after the last extrusion before the change. Orca
    turns it back on after the change (its _FORCE_RESUME_FAN_SPEED). The cavity fan (M106 P2)
    is left alone: it only moves chamber air."""
    points = set()
    prev = -1; cp = -1; last_ext = -1
    re_ext = re.compile(r'\sE[0-9.]')
    for i, line in enumerate(lines):
        c0 = line[:1]
        if c0 == 'G':
            if line.startswith('G1 ') and re_ext.search(line):
                last_ext = i
        elif c0 == ';':
            if line.startswith('; CP TOOLCHANGE START'):
                cp = i
        elif c0 == 'B' and line.startswith('BMCU_TOOL_CHANGE'):
            if cp > prev:
                points.add(cp)
            elif last_ext > prev:
                points.add(last_ext + 1)
            else:
                points.add(i)
            prev = i
    return points


def rewrite(job, plan, choice, prep_sec, backups=None, end_mode=''):
    """Returns (new file text, counters dict)."""
    used = job.used
    mp = {s: choice[i] for i, s in enumerate(used)}
    final_sec = plan.print_seconds(choice)
    head_of = plan.head_of
    hc_sec = job.hc_sec; orca_change = job.orca_change; orca_sec = job.orca_sec

    def M(n):
        i = int(n)
        return str(mp[i]) if i in mp else n

    re_t = re.compile(r'^T(\d+)(?=\s|$)')
    re_temp = re.compile(r'^(M10[49]\b[^;]*?\bT)(\d+)')
    re_tool = re.compile(r'\b(TOOL=|INITIAL_TOOL=)(\d+)')
    re_map = re.compile(r'^BMCU_PRINT_MAP TOOL=(\d+)\b.*$')
    re_a = re.compile(r'\bA\d')
    re_guard = re.compile(r'^SET_GCODE_VARIABLE MACRO=BMCU_REMAP_NOT_RUN\b')
    re_m73 = re.compile(r'^M73\s+P(\d+(?:\.\d+)?)\s+R(\d+)(.*)$')
    re_unretract = re.compile(r'^G1 E([0-9]*\.?[0-9]+) F[0-9.]+\s*(;.*)?$')
    re_e = re.compile(r'\bE-?[0-9.]', re.I)
    c = dict(T=0, temp=0, tool=0, map=0, guard=0, idle=0, hdr=0, meta=0, m73=0, est=0, unretract=0, refill=0, end=0, fans=0)
    fans_off = bool(SETTINGS.get('purgeFansOff', True))

    n_slots = len(job.colours) if job.colours else 0
    max_target = max(mp.values())
    remap_needed = any(mp[s] != s for s in used)

    def meta_line(body):
        m = RE_META.match(body)
        if not m:
            return body
        key = m.group(1); val = m.group(3)
        sep = ';' if ';' in val else (', ' if ', ' in val else ',')
        vals = val.split(sep)
        if len(vals) != n_slots:
            return body          # not a per-filament list we understand
        usage = key.startswith('filament used') or key == 'filament cost'
        n = max(len(vals), max_target + 1)
        new = [vals[q] if q < len(vals) else ('0.00' if usage else vals[0]) for q in range(n)]
        if usage:
            for s in used:
                if s < len(vals):
                    new[s] = '0.00'
        set_by = set()
        for s in used:
            if s >= len(vals):
                continue
            d = mp[s]
            if d not in set_by:
                new[d] = vals[s]; set_by.add(d)
            elif usage:
                # two slots merged onto one tool: add their usage
                a = parse_float(new[d]); b = parse_float(vals[s])
                if a is not None and b is not None:
                    new[d] = '%.2f' % (a + b)
        return '; ' + key + m.group(2) + sep.join(new)

    def nums(key):
        v = job.footer_list(key)
        return [x.strip() for x in ','.join(v or []).replace(';', ',').split(',')]
    max_norm = 0.0
    for v in nums('retraction_length'):
        x = parse_float(v)
        if x is not None and x > max_norm:
            max_norm = x
    tc_lens = []
    for v in nums('retract_length_toolchange'):
        x = parse_float(v)
        if x is not None and x > max_norm + 0.001 and x not in tc_lens:
            tc_lens.append(x)
    map_at_commit = job.map_at_commit
    map_written = False
    pend_unretract = False; last_slot_t = -1
    cur_tool = -1; in_change = False; idle_done = False
    tc_loaded = {}; tc_prev_head = -1; tc_cur = -1; extra_so_far = 0.0
    outl = []
    lines = job.lines
    fan_at = purge_fan_points(lines) if fans_off else set()

    for i, line in enumerate(lines):
        if i in fan_at:   # the old filament's last extrusion is done: part fan off from here to the change
            eol = '\r' if line.endswith('\r') else ''
            outl.append('M106 S0' + eol)
            c['fans'] += 1
        c0 = line[:1]
        if c0 == ';':
            if line.startswith(';===== BMCU tool change'):
                in_change = True; idle_done = False
            elif line.startswith('; filament: '):
                # OrcaSlicer 2.5+ header: 1-based list of slots used, read by BMCU-Klipper
                cr = line.endswith('\r')
                vals = []
                for v in line[12:].rstrip('\r').split(','):
                    v = v.strip()
                    try:
                        nn = int(v)
                        v2 = str(mp[nn - 1] + 1) if (nn - 1) in mp else v
                    except ValueError:
                        v2 = v
                    if v2 not in vals:
                        vals.append(v2)
                line = '; filament: ' + ','.join(vals) + ('\r' if cr else '')
                c['hdr'] += 1
            elif final_sec is not None and line.startswith('; estimated printing time (normal mode) = '):
                cr = line.endswith('\r')
                line = '; estimated printing time (normal mode) = ' + fmt_duration(final_sec + prep_sec) + ('\r' if cr else '')
                c['est'] += 1
            elif remap_needed and len(line) > 12 and line[1] == ' ' and line[2] in 'fn':
                cr = line.endswith('\r')
                body = line[:-1] if cr else line
                nb = meta_line(body)
                if nb != body:
                    c['meta'] += 1; line = nb + ('\r' if cr else '')
        elif c0 == 'S' and re_guard.match(line):
            c['guard'] += 1; continue
        elif in_change and line.rstrip('\r').upper() == 'MOVE_TO_XY_IDLE_POSITION_EXTRUDER':
            continue   # re-added below based on the real (remapped) previous tool
        elif c0 == 'G' and pend_unretract and line.startswith('G1 ') and re_e.search(line):
            # the first extrusion move after a tool change: drop it if it's Orca's un-retract
            um = re_unretract.match(line.rstrip('\r'))
            pend_unretract = False
            ev = float(um.group(1)) if um else -1.0
            if um and any(abs(x - ev) < 0.001 for x in tc_lens):
                c['unretract'] += 1
                continue
        elif c0 == 'T' or (c0 == 'B' and line.startswith('BMCU_')) or \
                (c0 == 'M' and (line.startswith('M104') or line.startswith('M109') or line.startswith('M400') or line.startswith('M73 '))):
            cr = line.endswith('\r')
            body = line[:-1] if cr else line
            if in_change and not idle_done and body == 'M400':
                # the profile parks the outgoing head after a stock-head tool
                if 0 <= cur_tool < FIRST_BMCU_TOOL:
                    outl.append('MOVE_TO_XY_IDLE_POSITION_EXTRUDER' + ('\r' if cr else ''))
                    c['idle'] += 1
                idle_done = True
            m73 = re_m73.match(body) if (final_sec is not None and body.startswith('M73 ')) else None
            if m73:
                # progress / remaining time with the real tool-change costs folded in
                p_o = float(m73.group(1))
                elapsed = max(0.0, p_o / 100.0 * orca_sec + extra_so_far)
                remain = max(0.0, final_sec - elapsed)
                p_n = int(min(100, math.floor(100.0 * elapsed / max(1, final_sec))))
                if p_o >= 100:
                    p_n = 100; remain = 0
                body = 'M73 P%d R%d%s' % (p_n, round(remain / 60.0), m73.group(3))
                c['m73'] += 1
            elif body.startswith('M73 '):
                pass
            elif re_map.match(body):
                # rebuilt from the final layout at BMCU_PRINT_COMMIT
                if map_at_commit:
                    continue
            elif body == 'BMCU_PRINT_COMMIT' and map_at_commit and not map_written:
                eol = '\r' if cr else ''
                for dst in sorted(set(mp.values())):
                    slots = [x for x in used if mp[x] == dst]
                    outl.append(print_map_line(job, plan, dst, slots) + eol)
                    c['map'] += 1
                outl.append(body + eol)
                # backup spools for running out (they need the committed plan)
                for src_t, bk in sorted((backups or {}).items()):
                    outl.append('BMCU_PRINT_REFILL TOOL=%d BACKUP=%d PRIORITY=100' % (src_t, bk) + eol)
                    c['refill'] += 1
                map_written = True
                continue
            elif end_mode and body.startswith('BMCU_PRINT_END'):
                nb = re.sub(r'\bMODE=\S+', 'MODE=' + end_mode, body) if re.search(r'\bMODE=', body) else body + ' MODE=' + end_mode
                if nb != body:
                    c['end'] += 1
                body = nb
            else:
                so = re_t.match(body)
                if so:
                    slot_now = int(so.group(1))
                    # only when the new tool is a BMCU channel: stock heads keep their un-retract
                    dst_now = mp.get(slot_now, slot_now)
                    if DROP_TOOLCHANGE_UNRETRACT and last_slot_t >= 0 and slot_now != last_slot_t and tc_lens and dst_now >= FIRST_BMCU_TOOL:
                        pend_unretract = True
                    last_slot_t = slot_now
                n = re_t.sub(lambda g: 'T' + M(g.group(1)), body, count=1)
                if n != body:
                    c['T'] += 1
                tm = re_t.match(n)
                if tm:
                    cur_tool = int(tm.group(1))
                    # running correction: (real cost of this change) - (what Orca assumed)
                    if final_sec is not None and cur_tool != tc_cur and cur_tool <= plan.max_tool:
                        th = head_of.get(cur_tool, 0)
                        if tc_cur >= 0:
                            if th == tc_prev_head:
                                cost = SWAP_SECONDS
                            elif th in tc_loaded and tc_loaded[th] != cur_tool:
                                cost = hc_sec + BACKGROUND_SWAP_EXTRA
                            else:
                                cost = hc_sec
                            extra_so_far += cost - orca_change
                        tc_loaded[th] = cur_tool; tc_prev_head = th; tc_cur = cur_tool
                if not re_a.search(n.split(';', 1)[0]):   # leave "M104 S0 Tn A0" head shutdowns alone
                    n2 = re_temp.sub(lambda g: g.group(1) + M(g.group(2)), n, count=1)
                    if n2 != n:
                        c['temp'] += 1
                    n = n2
                n3 = re_tool.sub(lambda g: g.group(1) + M(g.group(2)), n)
                if n3 != n:
                    c['tool'] += 1
                if n3.startswith('BMCU_TOOL_CHANGE'):
                    in_change = False
                    if fans_off and i not in fan_at:
                        # again right before the change, in case anything turned a fan back on
                        eol = '\r\n' if cr else '\n'
                        n3 = 'M106 S0' + eol + n3
                body = n3
            line = body + ('\r' if cr else '')
        outl.append(line)
    return '\n'.join(outl), c, final_sec


# ============================ main ================================================
PP_ENV = {}    # Orca's export details for this file: host, output (name), print_host


def main(path):
    """Process one exported G-code file. Ends with sys.exit: 0 done, 1 failed or cancelled."""
    STATE['path'] = path
    if not os.path.exists(path):
        fail('file not found: %s' % path)
    path = os.path.abspath(path)
    job = Job(path)
    load_settings()

    # Orca's host is "File" for Export G-code, and the printer connection type when its
    # Print/Send button is about to upload the file itself. Some send paths still say
    # "File" but write a .3mf or a temp file first - those count as Orca sending.
    pp_host = PP_ENV.get('host', '')
    orca_uploads = bool(pp_host) and pp_host != 'File'
    pp_out = PP_ENV.get('output', '')
    if not orca_uploads and pp_out:
        # output is Orca's SLIC3R_PP_OUTPUT_NAME: the full output path, which is in Orca's temp
        # folder when it stages a file to send. (Not tempfile.gettempdir(): that test-writes
        # files, which OrcaSlicer's plugin sandbox refuses off the UI thread.)
        tmpd = os.environ.get('TEMP') or os.environ.get('TMP') or os.environ.get('TMPDIR') or '/tmp'
        if pp_out.lower().endswith('.3mf') or os.path.normcase(pp_out).startswith(os.path.normcase(tmpd)):
            orca_uploads = True
    opt = {'bed': bool(SETTINGS['bedLevel']), 'flow': bool(SETTINGS['flowCalibrate']), 'tl': bool(SETTINGS['timelapse'])}

    # --- which printer: the last one used; Orca's Print / Send goes to its profile's printer ---
    target_host = str(SETTINGS['host'] or '')
    new_host = ''
    orca_host = str(PP_ENV.get('print_host', '') or '').strip() if orca_uploads else ''
    if orca_host:
        i = next((i for i, p in enumerate(PRINTERS) if orca_host.lower() in (p['host'].lower(), p['name'].lower())), -1)
        if i >= 0:
            if i != ACTIVE['i']:
                switch_printer(i)
            target_host = SETTINGS['host']
        else:
            target_host = new_host = orca_host               # not saved yet: read and add it
    also = []

    # --- first run (or a new printer): read its tool setup ---
    first_note = ''; live_note = ''; read_now = True
    if not PRINTERS or new_host:
        r = gui_first_setup(target_host, '')
        if r is None:
            fail('export cancelled at first setup (no printer address)')
        target_host, tools = r[0], r[1]
        first_note = ("First setup: read %d tools from %s. Check them (untick any you don't want used, "
                      "set the slot layout) and press Save." % (len(tools), target_host))
        name = r[2] or printer_hostname(target_host)
        add_printer(target_host, tools, name)
        live_note = apply_printer_tools(tools); read_now = False

    if read_now and target_host:
        live_note = update_live_state(target_host)   # every run: routing, types, colors, what's loaded
    if STATE['printer_without_bmcu']:
        msg = ("BMCU-Klipper isn't running on the printer at %s, so the file was left exactly as OrcaSlicer wrote it "
               "(no tools remapped). If this is a BMCU print, check BMCU-Klipper on the printer and slice again." % target_host)
        out('%s: WARNING - %s' % (TITLE, msg))
        write_log('WARNING %s | file: %s' % (msg, path))
        show_box(msg, TITLE, 'warning')
        sys.exit(0)

    job.analyse()
    k = job.k
    if first_note:
        gui_tools_dialog(target_host, first_note)

    solver = Solver()
    choice = None; do_print = False; want_gui = False; backups = None
    fresh = True            # just read above
    while True:
        if not fresh and target_host:
            live_note = update_live_state(target_host, True)
        fresh = False
        plan = Plan(job)
        if not plan.tools:
            msg = 'This print uses %d colors but no tools are enabled.' % k
            if plan.nozzle_off:
                msg = ('This print uses %d colors but no tool can take them: %s have a different nozzle size than the print '
                       'was sliced for.' % (k, ', '.join('T%d' % t for t in sorted(plan.nozzle_off))))
            if gui_tools_dialog(target_host, msg):
                continue
            fail(msg + ' Enable more tools in the Printer tools window.')
        plan.build()
        while True:
            solver.start(*plan.solve_args())
            if not solver.wait(1.0):
                gui_solve_wait(solver, plan.kS)
            if solver.error is not None:
                fail('tool layout search failed: %s' % solver.error)
            pick = solver.result
            if pick is None and plan.use_mat_rule:
                # not enough heads to keep every material apart: allow sharing and say so
                plan.use_mat_rule = False; plan.mat_forced = True
                continue
            break
        if pick is None:
            if solver.last_proven:
                msg = ("No possible layout for this print's %d colors: stock feeders can't retract, so a stock-fed color must be "
                       "the last color on its head, and the remaining tools can't take the rest." % k)
            else:
                msg = ("Couldn't find a layout for this print's %d colors before the search stopped. Stock feeders can only take a "
                       "color that's the last one on its head; enable more BMCU channels, or let the search run longer." % k)
            if plan.nozzle_off:
                msg += ' (%s are left out: their head has a different nozzle size than the print was sliced for.)' % \
                    ', '.join('T%d' % t for t in sorted(plan.nozzle_off))
            if gui_tools_dialog(target_host, msg):
                continue
            fail(msg)
        plan.finish(pick)
        if plan.rec_time is not None and plan.def_time is not None:
            better = plan.rec_time < plan.def_time
        else:
            better = plan.def_swaps is None or plan.rec_swaps < plan.def_swaps
        want_gui = ALWAYS_SHOW_GUI or not plan.default_valid or better
        if not want_gui:     # the slot layout is already the best: no window needed
            choice = plan.default_of
            break
        r = gui_assignment(plan, target_host, opt, orca_uploads, live_note, os.path.basename(path))
        target_host = r['host']; opt = r['opt']; also = r['also']
        SETTINGS['host'] = target_host
        if r['result'] == 'switch':
            switch_printer(r['index'])          # also remembered as the printer to open with next time
            target_host = SETTINGS['host']
            continue
        if r['result'] == 'tools':        # windows that can't nest (the plugin's) ask for these here
            gui_tools_dialog(target_host, '')
            continue
        if r['result'] == 'add':
            na = gui_first_setup('', '', adding=True)
            if na:
                add_printer(na[0], na[1], na[2])
                target_host = SETTINGS['host']
            continue
        if r['result'] == 'retry':
            save_settings()
            if r.get('live') is not None:
                live_note = r['live']; fresh = True   # Refresh / unload already re-read it
            continue
        if r['result'] not in ('ok', 'print'):
            fail('export cancelled in the BMCU-Klipper Tool Assignment window')
        do_print = r['result'] == 'print'
        SETTINGS.update(bedLevel=opt['bed'], flowCalibrate=opt['flow'], timelapse=opt['tl'])
        save_settings()
        choice = list(r['assign'])
        backups = r['backups']
        SETTINGS['endMode'] = r['end']
        save_settings()
        break

    # --- report + rewrite ---
    final = plan.measure(choice)
    prep_sec = plan.prep_seconds(choice, opt['bed'], opt['flow']) if (do_print or orca_uploads) else 0
    w = plan.shared_tool(choice)
    if w:
        out('%s: WARNING - %s' % (TITLE, w))
    w = plan.material_mix(choice)
    if w:
        out('%s: WARNING - %s' % (TITLE, w))
    e = plan.empty_chosen(choice)
    if e:
        out('%s: WARNING - %s had no filament at the last refresh; load it before printing' % (TITLE, ', '.join(e)))
    if backups is None:
        backups = plan.backups(choice)
    end_mode = str(SETTINGS['endMode'] or 'AUTO').upper()
    if end_mode not in ('SLICED', 'AUTO', 'UNLOAD', 'KEEP'):
        end_mode = 'AUTO'
    if end_mode == 'SLICED':
        end_mode = ''
    new_text, c, final_sec = rewrite(job, plan, choice, prep_sec, backups, end_mode)
    mp = {s: choice[i] for i, s in enumerate(job.used)}
    summary = ', '.join('slot %d->T%d' % (s + 1, mp[s]) for s in job.used)
    if c['refill']:
        summary += ' (backups %s)' % ', '.join('T%d->T%d' % kv for kv in sorted(backups.items()))
    def_note = ('slot layout %d' % plan.def_swaps) if plan.default_valid else 'slot layout n/a'
    proof = 'proven best' if solver.last_proven else 'best found'
    swap_note = 'swaps %d (recommended %d, %s; %s)' % (final[0], plan.rec_swaps, proof, def_note)
    if final_sec is not None:
        swap_note += ' | est. %s' % fmt_duration(final_sec + prep_sec)
        if prep_sec > 0:
            swap_note += ' incl. %s calibration' % fmt_duration(prep_sec)
        swap_note += ' (Orca said %s)' % fmt_duration(job.orca_sec)
    STATE['summary'] = '%s: %s | %s' % (TITLE, summary, swap_note)
    out('%s: %s | %s | rewrote %d T, %d temp, %d TOOL=, %d PRINT_MAP, %d idle moves, %d header + %d metadata lines, '
        '%d M73 + %d time lines, %d end-of-print mode, %d fans-off before tool changes, removed %d guard + '
        '%d tool-change un-retracts'
        % (TITLE, summary, swap_note, c['T'], c['temp'], c['tool'], c['map'], c['idle'], c['hdr'], c['meta'],
           c['m73'], c['est'], c['end'], c['fans'], c['guard'], c['unretract']))
    data = ('; %s: %s | %s\n' % (NAME, summary, swap_note) + new_text).encode('utf-8')
    tmp = path + '.bmcu_tmp'
    with open(tmp, 'wb') as f:
        f.write(data)
    os.replace(tmp, path)

    if orca_uploads and target_host:
        # OrcaSlicer uploads and starts this file itself, with a plain start that has no
        # print options. The U1 takes them from its print settings, which
        # SDCARD_PRINT_FILE_WITH_PARAMETERS would normally set: set them now instead.
        err = set_print_preferences(target_host, opt)
        onoff = lambda b: 'on' if b else 'off'
        if err:
            out('%s: WARNING - %s' % (TITLE, err))
            if want_gui:
                show_box("The file was saved and OrcaSlicer will send it, but the printer's print options couldn't be set, "
                         "so it starts with whatever the printer last used:\n\n" + err, TITLE + ' - print options', 'warning')
        else:
            out('%s: print options set on %s for OrcaSlicer to start the print (bed leveling %s, flow calibration %s, timelapse %s)'
                % (TITLE, target_host, onoff(opt['bed']), onoff(opt['flow']), onoff(opt['tl'])))
    if do_print:
        src = pp_out or path
        name = re.split(r'[\\/]', src)[-1]
        if not name.lower().endswith('.gcode'):
            name = os.path.splitext(name)[0] + '.gcode'
        targets = [(printer_name(SETTINGS), target_host, None)] + \
            [(printer_name(PRINTERS[i]), PRINTERS[i]['host'], PRINTERS[i]) for i in also if PRINTERS[i]['host'] != target_host]
        multi = len(targets) > 1
        failed = []          # (the window checked every printer before Save & print)
        onoff = lambda b: 'on' if b else 'off'
        opts = 'bed leveling %s, flow calibration %s, timelapse %s' % (onoff(opt['bed']), onoff(opt['flow']), onoff(opt['tl']))
        for pname, h, _ in targets:
            err = send_to_printer(h, path, name, opt['bed'], opt['flow'], opt['tl'])
            if err:
                failed.append(('%s: %s' % (pname, err)) if multi else err)
            else:
                out("%s: print started on %s as '%s' (%s)" % (TITLE, (pname if h in pname else '%s (%s)' % (pname, h)) if multi else h, name, opts))
        for err in failed:
            out('%s: PRINT NOT STARTED - %s' % (TITLE, err))
        if failed:
            show_box('The G-code was saved, but sending it to the printer failed:\n\n' + '\n\n'.join(failed),
                     TITLE + ' - print not started', 'warning')
    sys.exit(0)


# ============================ OrcaSlicer plugin entry points ===============================
STANDALONE_MARKS = ('; bmcu_klipper_remap:', '; bmcu_remap:')
OLD_CAP_NAMES = ('BMCU-Klipper tool assignment',)   # names used by earlier versions


class BmcuToolAssignment(orca.slicing.SlicingPipelineCapabilityBase):
    """Runs at OrcaSlicer's G-code post-processing step, after the classic scripts."""

    def get_name(self):
        return TITLE

    # --- add itself to the process profile in use (Snapmaker U1 printer profiles only) ----------
    # OrcaSlicer only runs the plugins listed in the active process profile's "Slicing Pipeline
    # Plugin" setting; there's no global switch. So whenever a profile is selected with a U1
    # printer profile active, the plugin adds itself there if it's missing. Plugins can't save
    # profiles, so it shows as an unsaved edit until the profile is saved (it works for slicing
    # right away). Turn it off in the Plugins window: Config > add_to_process_profiles = false.
    def get_default_config(self):
        return {'add_to_process_profiles': True}

    def _auto_add_on(self):
        try:
            return bool(json.loads(self.get_config() or '{}').get('add_to_process_profiles', True))
        except Exception:
            return True

    def on_load(self):
        if self._auto_add_on():
            in_thread(lambda: (time.sleep(3), ensure_in_process_profile(self.get_name())))

    def on_lifecycle_event(self, event, ctx):
        # a profile switch, a new or opened project (a .3mf brings its own process settings),
        # or objects added / a plate picked (Orca can keep presets per plate)
        try:
            E = orca.LifecycleEvent
            if event == E.PresetSelected:
                if ctx.msg not in ('print', 'printer'):
                    return
                delay = 0.8
            elif event in PROJECT_EVENTS:
                delay = 1.5      # NewProject fires before the presets are reloaded
            else:
                return
            if self._auto_add_on():
                schedule_profile_check(self.get_name(), delay)
        except Exception:
            write_log('profile check: ' + traceback.format_exc())

    def execute(self, ctx):
        if ctx.step != orca.slicing.Step.psGCodePostProcess:
            return orca.ExecutionResult.success()
        path = ctx.gcode_path
        if not path or not os.path.exists(path):
            return orca.ExecutionResult.success('BMCU: no G-code file to process')
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                first = f.readline()
        except Exception as e:
            return orca.ExecutionResult.failure(orca.PluginResult.RecoverableError, "BMCU: can't read the G-code: %s" % e)
        if first.startswith(STANDALONE_MARKS):
            # the standalone script is still set under Post-processing scripts and already did the work
            notify(TITLE + ': this file was already processed by bmcu_klipper_remap.py. Remove it from Process > '
                   'Post-processing scripts so only the plugin runs.', warning=True)
            return orca.ExecutionResult.success('BMCU: already processed by the standalone script')
        CTX['ctx'] = ctx
        PP_ENV.clear()
        PP_ENV.update(host=str(ctx.host or ''), output=str(ctx.output_name or ''))
        try:
            PP_ENV['print_host'] = str(ctx.config_value('print_host') or '')
        except Exception:
            PP_ENV['print_host'] = ''
        STATE.update(printer_without_bmcu=False, last_out='', last_error='', summary='')
        code = 0
        try:
            main(path)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        except Exception as e:
            write_log(traceback.format_exc())
            return orca.ExecutionResult.failure(orca.PluginResult.RecoverableError,
                                                'BMCU: %s: %s (details in %s)' % (e.__class__.__name__, e, LOG_PATH))
        finally:
            CTX['ctx'] = None
        new_hosts = [u for u in saved_printer_urls() if u not in LOAD_URLS]
        if new_hosts:
            LOAD_URLS.extend(new_hosts)
            notify(TITLE + ': restart OrcaSlicer once so it can approve %s for every request '
                   '(until then it may ask again for some of them).' % ', '.join(new_hosts))
        if code:
            return orca.ExecutionResult.failure(orca.PluginResult.RecoverableError,
                                                TITLE + ': ' + (STATE['last_error'] or 'stopped'))
        msg = STATE.get('summary') or STATE['last_out'] or TITLE + ': done'
        last = STATE['last_out']
        if last and not last.startswith(msg) and STATE.get('summary'):
            msg += ' | ' + last[len(TITLE) + 2:] if last.startswith(TITLE + ': ') else ' | ' + last
        return orca.ExecutionResult.success(msg[:400])


class BmcuPanelScript(orca.script.ScriptPluginCapabilityBase):
    """Plugins window > Run: opens the BMCU panel beside the 3D view."""

    def get_name(self):
        return 'Show the BMCU panel'

    def execute(self):
        if PANEL['p'] is None:
            PANEL['p'] = BmcuPanel()
        PANEL['p'].open()
        return orca.ExecutionResult.success('BMCU panel opened')


PROFILE_CHECK = {'pending': False, 'lock': threading.Lock()}
PROJECT_EVENTS = tuple(getattr(orca.LifecycleEvent, n) for n in
                       ('NewProject', 'ProjectOpened', 'ObjectAdded', 'PlateSelected')
                       if hasattr(orca.LifecycleEvent, n))


def schedule_profile_check(cap_name, delay=0.8):
    """Run one check shortly after the selection settles (several events fire per switch)."""
    with PROFILE_CHECK['lock']:
        if PROFILE_CHECK['pending']:
            return
        PROFILE_CHECK['pending'] = True

    def work():
        time.sleep(delay)
        with PROFILE_CHECK['lock']:
            PROFILE_CHECK['pending'] = False
        ensure_in_process_profile(cap_name)
    in_thread(work)


def ensure_in_process_profile(cap_name):
    """Add the plugin to the active process profile if a Snapmaker U1 printer profile is
    active and it isn't listed yet. Runs on a plugin thread: OrcaSlicer's preset editing
    must not be called from its UI thread."""
    try:
        bundle = orca.host.preset_bundle()
        model = str(bundle.full_config_value('printer_model') or '')
        if 'snapmaker u1' not in model.lower():
            return
        cur = bundle.full_config_value('slicing_pipeline_plugin')
        names = [x.strip().strip('"') for x in str(cur or '').split(';') if x.strip().strip('"')]
        old = [n for n in names if n in OLD_CAP_NAMES]
        if cap_name in names and not old:
            return
        names = [n for n in names if n not in OLD_CAP_NAMES]
        if cap_name not in names:
            names.append(cap_name)
        orca.host.preset.process.update('slicing_pipeline_plugin', ';'.join('"%s"' % n for n in names))
        try:
            proc = bundle.current_process_preset().name
        except Exception:
            proc = 'the process profile'
        notify('%s was %s "%s" (Slicing Pipeline Plugin). Save the profile to keep it.'
               % (cap_name, 'renamed in' if old else 'added to', proc))
    except Exception as e:
        write_log('could not add the plugin to the process profile: %s\n%s' % (e, traceback.format_exc()))


def notify(text, warning=False):
    try:
        lv = orca.host.ui.NotificationLevel
        orca.host.ui.push_notification(lv.WarningNotificationLevel if warning else lv.RegularNotificationLevel, text)
    except Exception:
        pass


def saved_printer_urls():
    """http://host for every saved printer, read straight from the settings file."""
    urls = []
    try:
        with open(SETTINGS_PATH, encoding='utf-8-sig') as f:
            j = json.load(f)
        hosts = [p.get('host') for p in (j.get('printers') or [])] + [j.get('host')]
        for h in hosts:
            b = base_url(h)
            if b and b not in urls:
                urls.append(b)
    except Exception:
        pass
    return urls


def orca_data_dir():
    """OrcaSlicer's data folder: the plugin lives in <data dir>/orca_plugins/..."""
    d = SCRIPT_DIR
    while True:
        up = os.path.dirname(d)
        if os.path.basename(d).lower() == 'orca_plugins':
            return up
        if up == d:
            return ''
        d = up


def orca_u1_printer_urls():
    """http://host for the print host of every Snapmaker U1 printer profile in OrcaSlicer, so
    the first-run permission prompt can cover the printer before any settings exist."""
    root = orca_data_dir()
    if not root:
        return []
    presets = {}
    try:
        for user in os.listdir(os.path.join(root, 'user')):
            mdir = os.path.join(root, 'user', user, 'machine')
            if not os.path.isdir(mdir):
                continue
            for fn in os.listdir(mdir):
                if not fn.lower().endswith('.json'):
                    continue
                try:
                    with open(os.path.join(mdir, fn), encoding='utf-8-sig') as f:
                        j = json.load(f)
                except Exception:
                    continue
                if isinstance(j, dict):
                    presets[str(j.get('name') or fn[:-5])] = j
    except Exception:
        return []

    def is_u1(j, depth=0):
        text = ' '.join(str(j.get(k) or '') for k in ('name', 'inherits', 'printer_model')).lower()
        if 'snapmaker u1' in text:
            return True
        parent = presets.get(str(j.get('inherits') or ''))
        return parent is not None and depth < 8 and is_u1(parent, depth + 1)

    urls = []
    for j in presets.values():
        h = j.get('print_host')
        if isinstance(h, list):
            h = h[0] if h else ''
        b = base_url(h)
        if b and is_u1(j) and b not in urls:
            urls.append(b)
    return urls


LOAD_URLS = []


@orca.plugin
class BmcuKlipperPlugin(orca.base):
    def register_capabilities(self):
        # Ask for everything up front, in OrcaSlicer's one combined prompt when the plugin loads:
        # threads, every saved printer, and the print host of every Snapmaker U1 printer
        # profile (so a fresh install is covered before its first run). Later, OrcaSlicer only
        # asks in the moment on its UI thread, refuses outright on the slicing thread, and keeps
        # those answers per exact URL - an up-front grant covers the whole printer.
        urls = saved_printer_urls()
        for u in orca_u1_printer_urls():
            if u not in urls:
                urls.append(u)
        LOAD_URLS[:] = urls
        orca.request_permissions(threading=True, network=urls)
        orca.register_capability(BmcuToolAssignment)
        orca.register_capability(BmcuPanelScript)
