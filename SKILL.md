---
name: kwgt-automation
description: >-
  Comprehensive guide, runbook, architectural rules, and toolset for KWGT (Kustom Widget Maker) development,
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
| **`OverlapLayerModule`** | Stacks child elements on top of each other. Auto-sizes to largest child. | `position_anchor`, `position_x_offset`, `position_y_offset`, `viewgroup_items` |
| **`StackLayerModule`** | Arranges children horizontally or vertically. | `config_stacking` (`HORIZONTAL`, `VERTICAL`, `HORIZONTAL_BOTTOM`, `HORIZONTAL_CENTER`), `config_margin` |
| **`ShapeModule`** | Geometric vector shape (bars, cards, dividers). | `shape_type` (`RECT`, `CIRCLE`, `SLICE`), `shape_width`, `shape_height`, `shape_corners`, `paint_color` |
| **`TextModule`** | Formatted text or dynamic expression. | `text_expression`, `text_size`, `paint_color`, `text_align` |
| **`SeriesModule`** | Built-in repeating sequence/series generator. | `series_type`, `series_count`, `series_mode` |

---

## 3. Critical Kustom Engine Gotchas & Lessons Learned

### Gotcha A: `internal_toggles` is Mandatory for Formulas on Shapes
When writing formulas on numeric or color properties of shapes (like `shape_height`, `shape_width`, `paint_color`), Kustom **completely ignores** `internal_formulas` unless `internal_toggles` has the calculator flag set (`10`):

```json
{
  "internal_type": "ShapeModule",
  "shape_type": "RECT",
  "shape_width": 22.0,
  "shape_height": 180.0,
  "internal_toggles": {
    "shape_height": 10
  },
  "internal_formulas": {
    "shape_height": "$mu(max, 10, mu(round, (wg(\"file:///Kustom/data.json\", json, .v0) - 750) * 12))$"
  }
}
```
* `0` = Default static mode.
* `10` = Calculator / Formula mode (toggled when user taps Calculator in KWGT GUI).
* **Precomputed Static Values**: Always set the static property (e.g. `shape_height: 180.0`) to the precomputed initial value. This guarantees zero visual pop-in or flat bars when the widget first loads or runs offline.

### Gotcha B: Avoid Nesting Multi-Argument Functions in `tc(split)`
Kustom's expression parser splits function arguments naively on commas `,` from left to right.
* **Problem**: Passing `$tc(split, wg("url", json, .path), ",", 0)$` causes the commas inside `wg()` to be interpreted as separators of `tc(split)`. `tc(split)` receives 5+ arguments instead of 3, silently fails, and returns an empty string `""` (resulting in minimum fallback clamps / flat bars).
* **Solution**: Use direct JSON keys (`.v0`, `.v1`, ...) or direct JSONPath array indices (`.values[0]`), OR pass the data through a Global Variable (`gv(raw_data)`) first:
  ```text
  $tc(split, gv(data), ",", 0)$
  ```

### Gotcha C: Modern Android Scoped Storage Paths
On Android 10+ (Scoped Storage / SAF), `file:///sdcard/...` or `/storage/emulated/0/...` can fail if the app lacks global root storage permissions.
* The file must reside inside the primary **`/sdcard/Kustom/`** directory.
* The most reliable URI in Kustom is:
  ```text
  file:///Kustom/filename.json
  ```
* Use a dual-path fallback in widgets for universal compatibility across Android versions:
  ```text
  $if(wg("file:///Kustom/data.json", json, .val), wg("file:///Kustom/data.json", json, .val), wg("file:///sdcard/Kustom/data.json", json, .val))$
  ```

---

## 4. Multi-Bar Chart Architecture (Bars with Numbers)

To build a professional multi-bar chart where numbers sit inside/on the bars:

1. **Stack Container**:
   A `StackLayerModule` with `config_stacking: "HORIZONTAL_BOTTOM"` and `config_margin: 7.0` (anchors all columns along a shared bottom baseline).
2. **Column Structure**:
   Each column is an **`OverlapLayerModule`** containing:
   * **`ShapeModule`** (the vertical bar):
     - `shape_type`: `"RECT"`
     - `shape_width`: `22.0`
     - `internal_toggles`: `{"shape_height": 10}`
     - `internal_formulas`: `{"shape_height": "$mu(max, 10, ...)$"}`
   * **`TextModule`** (the numeric value):
     - `text_expression`: `$mu(round, ..., 0)$`
     - `text_size`: `9.5`
     - `position_anchor`: `"TOP"`
     - `position_y_offset`: `6.0`
     - *Why this works*: The `OverlapLayerModule` automatically resizes its height to match the dynamic `ShapeModule`. Anchoring text to `"TOP"` with an offset of 6px ensures the numbers dynamically track the moving tops of the bars across all data fluctuations!
3. **Contrast Styling**:
   * Past bars: Translucent accent (`#7700E5FF`) with white text (`#E6FFFFFF`).
   * Latest bar: Bright solid accent (`#FF00E5FF`) with dark contrast text (`#FF10141C`).

---

## 5. Hardware Sensor Logging & Calibration

Android's built-in barometer (`LPS22HH`, etc.) provides raw **station pressure** at current elevation, plus a zero-point shift from motherboard surface-mount solder stress.

### Sea-Level Calibration Equation
$$\text{Offset} = \text{Official Sea-Level Pressure (MSL)} - \text{Raw Sensor Reading}$$
* Example for 351m elevation (339m terrain + 12m for 5th floor):
  - Expected surface delta: $\approx -41.6\text{ hPa}$
  - Hardware mechanical stress shift: $\approx -40.1\text{ hPa}$
  - Total Calibration Offset: **$+81.7\text{ hPa}$ ($+61.3\text{ mmHg}$)**

### Background Daemon via `termux-job-scheduler`
Schedule lightweight logging every 15 minutes that persists across reboots:
```bash
termux-job-scheduler \
    -s /data/data/com.termux/files/home/barometer-kwgt-logger/record.sh \
    --job-id 777 \
    --period-ms 900000 \
    --battery-not-low false \
    --persisted true
```

### Clean Single-File JSON Feed Format
Store history as direct `.v0`..`.v23` keys for instant, bug-free Kustom evaluation:
```json
{
  "updated": "21:47",
  "latest_mmhg": 758.6,
  "latest_hpa": 1011.4,
  "v0": 768.9,
  "v1": 769.0,
  "v23": 758.6
}
```

---

## 6. Built-in Skill Scripts

This skill includes standalone helper scripts in `scripts/`:

### Inspecting a Preset
```bash
python3 scripts/inspect_kwgt.py /sdcard/Kustom/widgets/pressure.kwgt
```
Outputs complete metadata, view tree hierarchy, text expressions, static property values, and `internal_formulas`.

### Compiling a Preset
```bash
python3 scripts/compile_kwgt.py <source_dir_or_json> <output_preset.kwgt>
```
Compiles and verifies root ZIP structure for instant importing into KWGT.
