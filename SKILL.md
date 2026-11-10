---
name: kwgt-automation
description: >-
  Comprehensive guide, runbook, and toolset for KWGT (Kustom Widget Maker) development,
  programmatic preset modification, .kwgt/.komp packaging, sensor data logging, and formula reference.
  Activate when designing, modifying, debugging, or automating KWGT widgets, custom series charts,
  flows, globals, or external data feeds.
---

# KWGT Automation & Widget Engineering Skill

## Overview
KWGT (Kustom Widget Maker) and the Kustom ecosystem (KLWP, KLCK) create rich, dynamic Android widgets. While users traditionally configure widgets via the mobile GUI touch interface, presets and components are stored as JSON archives that can be programmatically inspected, modified, generated, and paired with automated Android background services.

---

## 1. Package Architecture & Anatomy

KWGT presets (`.kwgt`) and Komponents (`.komp`) are standard **ZIP archives** containing:
* `preset.json` (or `komponent.json`): The core JSON document describing metadata, layout, layers, and formulas.
* `preset_thumb_portrait.jpg` / `preset_thumb_landscape.jpg`: Preview snapshots shown in the KWGT preset picker.
* `bitmaps/` (optional): Embedded raster assets.
* `fonts/` (optional): Custom TTF/OTF fonts.

> **CRITICAL RULE**: When repacking, `preset.json` MUST be located at the root of the ZIP archive without an enclosing parent directory, otherwise KWGT will fail to import the preset.

### Core JSON Hierarchy
```
preset_info: { title, author, description, width, height, version, release, locked }
preset_root: {
  internal_type: "RootLayerModule",
  viewgroup_items: [
    { ... modules ... }
  ]
}
```

---

## 2. Module Types & Properties

Inside `viewgroup_items`:

| Module Type | Purpose | Key Attributes |
| :--- | :--- | :--- |
| **`OverlapLayerModule`** | Stacks child elements on top of each other. | `position_anchor`, `position_x_offset`, `position_y_offset`, `viewgroup_items` |
| **`StackLayerModule`** | Arranges children horizontally or vertically. | `config_stacking` (`HORIZONTAL`, `VERTICAL`, `HORIZONTAL_BOTTOM`, `HORIZONTAL_CENTER`), `config_margin` |
| **`ShapeModule`** | Geometric vector shape (bars, cards, dividers). | `shape_type` (`RECT`, `CIRCLE`, `SLICE`), `shape_width`, `shape_height`, `shape_corners`, `paint_color` |
| **`TextModule`** | Formatted text or dynamic expression. | `text_expression`, `text_size`, `paint_color` |
| **`SeriesModule`** | Built-in repeating sequence/series generator. | `series_type`, `series_count`, `series_mode` |

### Dynamic Formulas via `internal_formulas`
Static values (like `shape_height: 30.0` or `paint_color: "#FFFFFFFF"`) can be replaced with dynamic formulas using the **`internal_formulas`** dictionary:
```json
{
  "internal_type": "ShapeModule",
  "shape_type": "RECT",
  "shape_width": 18.0,
  "shape_height": 20.0,
  "internal_formulas": {
    "shape_height": "$mu(max, 10, mu(round, (tc(split, wg(\"file:///sdcard/Kustom/baro_values_chrono.txt\", raw), \",\", 0) - 694) * 16))$",
    "paint_color": "$if(tc(split, ...) > 700, #FFFF0000, #FF00E5FF)$"
  }
}
```

---

## 3. Automation with Termux & Hardware Sensors

Android's built-in sensors (barometer, light, accelerometer) only provide live readings and no historical logs. Background daemons in Termux solve this limitation:

### Reading Hardware Sensors
```bash
# Discover sensors
termux-sensor -l

# Read single pressure sample (e.g. lps22hh Pressure Sensor)
termux-sensor -s "lps22hh Pressure Sensor Non-wakeup" -n 1
```

### Scheduling with Native Android JobScheduler
Never use while-sleep loops in background terminals; Android will kill them. Use Android's native JobScheduler:
```bash
termux-job-scheduler \
    -s /data/data/com.termux/files/home/scripts/record.sh \
    --job-id 777 \
    --period-ms 900000 \
    --battery-not-low false \
    --persisted true
```
* Minimum period on Android N+: 900,000 ms (15 minutes).
* `--persisted true`: Persists across phone reboots.

### Exporting Feeds for KWGT
Save feeds to `/sdcard/Kustom/` (or `/sdcard/Documents/`):
1. **`baro_values.txt`**: Comma-separated newest-first values: `697.4,697.3,697.2`
2. **`baro_values_chrono.txt`**: Comma-separated oldest-to-newest values (for left-to-right charts): `697.0,697.2,697.4`
3. **`barometer_history.json`**: Structured JSON for multi-field queries.

---

## 4. KWGT Formula Patterns & Cheatsheet

### File Loading via `$wg()`
* **Raw text / CSV**:
  ```text
  $wg("file:///sdcard/Kustom/baro_values_chrono.txt", raw)$
  ```
* **JSON extraction**:
  ```text
  $wg("file:///sdcard/Kustom/barometer_history.json", json, .latest.mmhg)$
  $wg("file:///sdcard/Kustom/barometer_history.json", json, .readings[0].time)$
  ```

### Array Slicing via `$tc(split)`
Extract a specific index from a comma-separated string:
```text
$tc(split, wg("file:///sdcard/Kustom/baro_values_chrono.txt", raw), ",", 0)$
```

### Chart Scaling and Clamping
Formula to compute bar heights with baseline subtraction, multiplier, and minimum clamp:
```text
$mu(max, 6, mu(round, (tc(split, wg("file:///sdcard/Kustom/baro_values_chrono.txt", raw), ",", index) - 694) * 14))$
```

---

## 5. Built-in Skill Scripts

This skill includes standalone helper scripts in `scripts/`:

### Inspecting a Preset
```bash
python3 scripts/inspect_kwgt.py /sdcard/Kustom/widgets/pressure.kwgt
```
Outputs complete metadata, view tree hierarchy, text expressions, and `internal_formulas`.

### Compiling a Preset
```bash
python3 scripts/compile_kwgt.py <source_dir_or_json> <output_preset.kwgt>
```
Compiles and verifies root ZIP structure for instant importing into KWGT.
