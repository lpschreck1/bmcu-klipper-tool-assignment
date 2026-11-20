# BMCU-Klipper Tool Assignment

An [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) 2.5+ plugin for the **Snapmaker U1** running [BMCU-Klipper](https://github.com/jarczakpawel/BMCU-Klipper).

Each time you export or send a print, it reads the printer's current tool setup and puts the print's colors on the tools that need the fewest filament swaps. A window opens so you can check and adjust the choice, and then it rewrites the G-code to match.

On the U1, switching between heads is quick. Two colors on the **same** head need a full unload and load every time the print alternates between them. The plugin finds the layout with the fewest of those swaps, so you don't have to work it out for every print.

## Features

- **Live printer setup.** On every export it reads which head each BMCU channel is routed to, the filament type and color in each tool, and what's loaded in each head.
- **Best tool layout.** A search finds the layout with the fewest swaps and the shortest print time, then proves no better layout exists. It stops after 30 seconds and keeps the best layout it found. Ties go to tools already holding the closest color and the same filament type.
- **More colors than tools.** The closest colors, same filament type first, are combined onto shared tools, only as many as needed.
- **Assignment window.** Swap, move or share colors per tool, see why a tool can't be used, and compare the recommended layout with your slot layout, including swaps and estimated print time.
- **Printer checks.** Before printing it checks for the right filament and type in the right place, correct routing, and uncertain routes. The printer refuses to start if a channel was moved to another head since slicing.
- **Backup spools.** If a spool runs out, the print continues from a spool you pick, or automatically from a same-type, close-color spool.
- **End of print.** You choose what happens to the BMCU filament: BMCU decides, Unload, Keep loaded, or As sliced.
- **Head controls.** Unload filament from a head, confirm uncertain routes, and refresh from the printer.
- **Several printers.** Each printer keeps its own tools and options. Switch between them in the window, or send the same file to several printers at once.
- **Orca's Print button.** It sets bed leveling, flow calibration and timelapse on the U1 before Orca uploads and starts the print.
- **Cleaner tool changes.**
  - It removes the un-retract Orca adds after a change to a BMCU tool, which pushes a blob out at the prime tower.
  - It turns the part cooling fan off before each tool change, so the purge drops as a blob instead of being blown into strings. Orca turns the fan back on after the change.
- **Accurate time estimates.** The estimated print time and the M73 progress lines are rewritten to include swap, bed-leveling and calibration time.
- **BMCU panel.** A panel beside the 3D view shows routing and loaded filament, and has unload buttons.
- **Adds itself to U1 process profiles** when a Snapmaker U1 printer profile is used.

## Requirements

- OrcaSlicer **2.5.0 or newer**, which added plugin support.
- A Snapmaker U1 with BMCU-Klipper installed and running.
- A Snapmaker U1 printer profile in OrcaSlicer with the printer's address set as its print host. BMCU-Klipper's own U1 profile is in its repository under `printers/Snapmaker_U1/Snapmaker_Orca`.

Nothing else needs installing. The plugin is a single Python file and uses only OrcaSlicer's built-in Python.

## Installation

1. Download `bmcu_klipper_plugin.py` from the latest release.
2. In OrcaSlicer, open **Plugins > Install from file** and pick the file.
3. Approve the permission prompt. OrcaSlicer asks once, when the plugin loads, for:
   - permission to run background threads;
   - network access to your saved printers and to the print host of each Snapmaker U1 printer profile.

   Each person is asked about their own printers; no address is built into the file.
4. Select a Snapmaker U1 printer profile. The plugin adds itself to the process profile's **Slicing Pipeline Plugin** setting and shows a notification. **Save the process profile** to keep the change.

To update, delete the old plugin in the Plugins window and install the new file. Installing over the top can fail. Deleting the plugin also deletes its settings, so copy `bmcu_klipper_remap.settings.json` out of the plugin folder first and put it back afterwards.

### Recommended: safety guard

Add this as the **first line** of **Printer settings > Machine G-code > Machine start G-code**:

```
SET_GCODE_VARIABLE MACRO=BMCU_REMAP_NOT_RUN VARIABLE=x VALUE=0
```

The plugin deletes this line from every file it processes. If a file ever reaches the printer without going through the plugin, Klipper stops on that line before heating, and the print doesn't start with the wrong tools.

## First run

With no saved printer, a setup window opens. It offers the address from your printer profile, or it can search your network for U1s running BMCU-Klipper. The search needs **Full access** for this plugin in the Plugins window, because it has to reach every address on your network. Without Full access, type the address instead.

The plugin then reads BMCU-Klipper's setup from the printer, saves it, and opens **Printer tools** so you can check it.

After you add a printer that wasn't covered by the first permission prompt, restart OrcaSlicer once so it can approve that printer as a whole.

## Using it

**Export G-code:** the window offers **Save file** and **Save & print**. Save & print makes the plugin upload the file and start the print itself, after checking the printer.

**Orca's Print / Send button:** the window offers **Save & send**. It checks the printer and sets the ticked bed leveling, flow calibration and timelapse options. OrcaSlicer then uploads and starts the file.

**Cancel export** stops the export.

### Printer tools

**Printer tools…** shows BMCU-Klipper's live setup: which T number each channel is, which head it's routed to, and what's loaded. Untick tools the plugin must not use, and set your slot layout. Options:

- Prefer tools already holding the print's colors.
- Keep different filament types on separate heads.
- Have the printer refuse to start if a channel is labeled with another filament type.
- Continue from a same-type, close-color spool when one runs out.
- Keep duplicate spools free as backups when there are enough other tools.
- Turn the part cooling fan off before each tool change.

Heads with a different nozzle size than the print was sliced for are never used.

### BMCU panel

Open it with **Plugins > BMCU-Klipper Tool Assignment > "Show the BMCU panel" > Run**. It docks beside the 3D view and shows routing and loaded filament, with unload buttons.

## Settings and logs

Both files are in the plugin's folder inside OrcaSlicer's data folder:

- `bmcu_klipper_remap.settings.json`: saved printers, tools, slot layouts and options.
- `bmcu_klipper_remap.log`: errors and warnings. Include it when reporting a problem.

To stop the plugin adding itself to process profiles, set `add_to_process_profiles = false` under **Plugins > BMCU-Klipper Tool Assignment > Config**.

## How the G-code is changed

- **Tool numbers** are re-indexed to the chosen tools: `T`, `M104`/`M109 T`, `TOOL=` and `INITIAL_TOOL=`.
- **Filament header and metadata:** the `; filament:` header and the per-filament metadata are re-indexed, and merged colors' usage is added together.
- **BMCU print plan:** it's rebuilt for every tool used.
  - Each BMCU tool gets `EXPECT_ENDPOINT`, and optionally `EXPECT_MATERIAL`, so the printer refuses to start if routing or filament changed since slicing.
  - `MATERIAL` / `COLOR` permanently relabel a channel, so they're only written where they describe what's actually loaded.
- **Backups** become `BMCU_PRINT_REFILL`, and the end-of-print choice becomes `BMCU_PRINT_END`.
- **Tool changes:** the un-retract after a change to a BMCU tool is removed, and part-fan-off commands are added before each tool change, if that option is on.
- **Time estimates:** the estimated printing time and the `M73` progress lines are updated.

## Credits

Built for [BMCU-Klipper](https://github.com/jarczakpawel/BMCU-Klipper), which does the real work on the printer. This plugin only plans the tool layout and sends BMCU-Klipper's own commands.

Written with the help of Claude (Anthropic).

## License

Licensed under the GNU General Public License v3.0 (GPL-3.0), the same license as BMCU-Klipper. See [LICENSE](LICENSE).
