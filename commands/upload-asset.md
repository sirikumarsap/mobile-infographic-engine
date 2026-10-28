---
description: Store data charts, tables, or screenshots to embed in the infographic
argument-hint: "[file paths, or attach files to the message]"
allowed-tools: Bash, Read
---

Store asset files in `infographic/assets/`, then prepare images for the visual section.

Input: $ARGUMENTS and any files attached to this message.

1. Run `mkdir -p infographic/assets`.
2. Copy each file into `infographic/assets/` with safe filenames.
3. For PDF tables, first rasterize the page to PNG at 200 dpi, for example with `pdftoppm -png -r 200 -f N -l N file.pdf infographic/assets/name`.
4. For each PNG or JPG, run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prepare_assets.py infographic/assets/<file> infographic/assets/prepared/<file>.png`.
5. Reply with the stored and prepared filenames.