#!/usr/bin/env python3
"""
Inspect KWGT / Kustom Presets (.kwgt, .komp, .klwp).
Displays metadata, view hierarchy, and active formulas.
"""

import json
import os
import sys
import zipfile

def inspect_preset(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    print(f"\n=======================================================")
    print(f" Inspecting Kustom Package: {os.path.basename(file_path)}")
    print(f"=======================================================")

    with zipfile.ZipFile(file_path, "r") as z:
        namelist = z.namelist()
        print(f"Archive contents: {', '.join(namelist)}")

        json_name = None
        for candidate in ["preset.json", "komponent.json"]:
            if candidate in namelist:
                json_name = candidate
                break

        if not json_name:
            print("Error: Neither preset.json nor komponent.json found in archive root.")
            return

        with z.open(json_name) as jf:
            data = json.load(jf)

    info = data.get("preset_info", {})
    print(f"\n--- Metadata ---")
    print(f"Title       : {info.get('title', 'Untitled')}")
    print(f"Author      : {info.get('author', 'Unknown')}")
    print(f"Description : {info.get('description', 'N/A')}")
    print(f"Dimensions  : {info.get('width', '?')} x {info.get('height', '?')}")
    print(f"Version     : {info.get('version', '?')} (Release: {info.get('release', '?')})")

    root = data.get("preset_root", {})
    items = root.get("viewgroup_items", [])
    print(f"\n--- Layer Hierarchy ({len(items)} top-level items) ---")

    def print_items(item_list, indent=0):
        prefix = "  " * indent
        for idx, item in enumerate(item_list):
            title = item.get("internal_title", f"Item {idx + 1}")
            itype = item.get("internal_type", "UnknownModule")
            formulas = item.get("internal_formulas", {})
            expr = item.get("text_expression")

            detail = ""
            if expr:
                detail = f" -> text: '{expr}'"
            print(f"{prefix}- [{itype}] \"{title}\"{detail}")

            if formulas:
                for prop, fml in formulas.items():
                    print(f"{prefix}    formula({prop}): {fml}")

            children = item.get("viewgroup_items", [])
            if children:
                print_items(children, indent + 1)

    print_items(items)
    print("\n=======================================================\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path_to_preset.kwgt>")
        sys.exit(1)
    inspect_preset(sys.argv[1])
