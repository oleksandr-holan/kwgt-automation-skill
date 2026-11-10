# KWGT Automation & Widget Engineering Skill for Antigravity

An [Antigravity](https://github.com/google-deepmind) agent skill providing complete documentation, runbooks, schemas, and automation scripts for building and programmatically generating **KWGT (Kustom Widget Maker)** presets, dynamic charts, and hardware sensor integrations.

---

## What This Skill Enables

- **Programmatic Widget Generation**: Unpack, modify, and compile `.kwgt` and `.komp` archives without touching the phone screen.
- **Hardware Sensor History**: Bridge Android hardware sensors (Barometer, Light, Temperature) into KWGT via Termux and native `termux-job-scheduler`.
- **Dynamic Chart Architectures**: Construct multi-bar time-series charts using `StackLayerModule`, `ShapeModule`, and `internal_formulas`.
- **Inspector Tooling**: Deeply inspect existing KWGT widgets, print module trees, and view active formulas.

---

## Included Tools

- **[`scripts/inspect_kwgt.py`](scripts/inspect_kwgt.py)**: Inspect any `.kwgt` or `.komp` archive and print its complete layout hierarchy and formulas.
- **[`scripts/compile_kwgt.py`](scripts/compile_kwgt.py)**: Compile a directory or `preset.json` into a valid Kustom package adhering to root-level archive constraints.

---

## Installation in Antigravity

To install this skill into your Antigravity environment:

```bash
git clone https://github.com/oleksandr-holan/kwgt-automation-skill.git ~/.gemini/config/skills/kwgt-automation
```

Once installed, Antigravity will automatically activate this skill whenever you ask questions or execute tasks involving KWGT widgets, Kustom formulas, or sensor automation!
