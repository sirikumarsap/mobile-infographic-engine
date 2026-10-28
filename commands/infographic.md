---
description: Generate a 9:16 mobile infographic (1080x1920) from a content prompt
argument-hint: "<content, points, prices, steps>"
allowed-tools: Read, Write, Bash, Glob
---

Build a mobile infographic for the content below.

Content: $ARGUMENTS

If the content is empty or still contains placeholder text like "[INSERT", stop and ask the user for the real content. Do not invent points.

## Inputs
1. Load `infographic/system_state.json` (run `/restrict` setup if it is missing) and `${CLAUDE_PLUGIN_ROOT}/configs/design_system.json`.
2. Forbidden words come only from `system_state.json`. Use `locked_tokens` plus `forbidden_tokens`.
3. Look in `infographic/reference/`. If a reference exists and its style matches the content, adapt its grid, colors, and aesthetic. Otherwise use `fallback_palette`.
4. Look in `infographic/assets/prepared/`. Use prepared images for the visual section. If an asset is named in the prompt but not found, ask for it.

## Content
5. Split the content into points. Keep every point. Each point must appear in the design.
6. If you shorten a point, keep its meaning and record the original and new text. You will report these.
7. Write `infographic/output/content.json`:
   `{"points": ["...shortened or original text..."], "originals": {"shortened text": "original text"}}`

## Design
8. Write one self-contained file, `infographic/output/infographic.html`:
   - `body` is exactly 1080px wide and 1920px tall. Declare both in CSS.
   - 40px outer padding (safe zone). 24px spacing between elements.
   - Left-aligned, modern sans-serif. Every font-size is at least 28px, including labels.
   - Generous line-height. High contrast (WCAG AAA) text on background.
   - Colored bullet icons (inline SVG or emoji) matching the theme.
   - One card or panel per section. The visual asset goes in its own dedicated section.
   - No external resources. Embed images as base64 or reference relative files in `infographic/`.
9. Check that text fits. If content would overflow 1920px, shorten wording (log it) or split the design. Do not drop points.

## Validate
10. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py infographic/output/infographic.html --content infographic/output/content.json`.
11. On failure, fix the reported problems and run it again. Stop after 3 attempts and report what still fails.

## Optional PNG
12. If Playwright is available, run `npx playwright screenshot --viewport-size=1080,1920 --full-page infographic/output/infographic.html infographic/output/infographic.png`. For 8K output, add `--device-scale-factor=4` and check the result.

## Reply
13. Give the paths to the HTML and PNG files (if created).
14. List every shortened point as original → new.
15. Say that the validator passed, and note that text inside raster assets is not checked automatically, so look at them yourself.