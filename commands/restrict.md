---
description: Set the words that must never appear in the infographic
argument-hint: "\"Alert\" \"Attention\" \"Stop\""
allowed-tools: Read, Write, Bash
---

Update the forbidden-word list in `infographic/system_state.json`.

Input: $ARGUMENTS

1. If `infographic/system_state.json` is missing, create the `infographic/` folder and copy `${CLAUDE_PLUGIN_ROOT}/configs/system_state.default.json` into it.
2. Parse the words from $ARGUMENTS. Accept quoted, comma-separated, or space-separated input. Trim them, drop empties, and remove case-insensitive duplicates.
3. Always keep the `locked_tokens` ("Notice", "Warning"). They cannot be removed. Say so if the user tried to remove them.
4. Replace `dynamic_restrictions.forbidden_tokens` with the new list. Leave every other key unchanged.
5. Reply with the active list: locked tokens plus forbidden tokens.

If $ARGUMENTS is empty, show the current list and ask what to add.