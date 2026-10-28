---
description: Store style-guide or layout reference images for future infographics
argument-hint: "[file paths, or attach files to the message]"
allowed-tools: Bash, Read
---

Copy the reference files to `infographic/reference/`.

Input: $ARGUMENTS and any files attached to this message.

1. Run `mkdir -p infographic/reference`.
2. For each file, copy it to `infographic/reference/` using a filename with spaces and special characters replaced by underscores. Only accept png, jpg, jpeg, webp, or pdf.
3. Reply with the stored filenames. Note any files that were skipped and why.

Do not change or delete existing references unless the user asks.