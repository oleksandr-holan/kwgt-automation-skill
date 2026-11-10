#!/usr/bin/env python3
"""
Compile a folder or preset.json into a valid Kustom package (.kwgt / .komp).
Ensures preset.json is stored at the root of the ZIP archive.
"""

import json
import os
import sys
import zipfile

def compile_preset(source_path, output_path):
    if not os.path.exists(source_path):
        print(f"Error: Source '{source_path}' does not exist.")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        if os.path.isdir(source_path):
            for root, _, files in os.walk(source_path):
                for f in files:
                    if f.endswith(".kwgt") or f.endswith(".komp") or f.endswith(".bak"):
                        continue
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, source_path)
                    z.write(full_p, arcname=rel_p)
        else:
            # Single file (preset.json or komponent.json)
            arcname = os.path.basename(source_path)
            z.write(source_path, arcname=arcname)

    print(f"Successfully compiled '{output_path}' ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <source_folder_or_preset_json> <output_preset.kwgt>")
        sys.exit(1)
    compile_preset(sys.argv[1], sys.argv[2])
