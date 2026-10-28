# mobile-infographic-engine

A Claude Code plugin that turns a content prompt into a polished 9:16 mobile infographic (1080×1920, optionally 8K) for WhatsApp full-screen previews and phone scrolling. It enforces restricted words, keeps every content point, places your screenshots or tables in a dedicated visual section, and checks the result automatically before delivering it.

- **Output:** a self-contained HTML file, plus an optional PNG
- **Audience:** residents viewing on a 6.5–7 inch phone
- **License:** Apache 2.0

---

## Contents

1. [What it does](#what-it-does)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Quick start](#quick-start)
5. [Commands](#commands)
6. [Workspace layout](#workspace-layout)
7. [Step-by-step: creating a final image](#step-by-step-creating-a-final-image)
8. [Using references](#using-references)
9. [Using assets](#using-assets)
10. [Forbidden words and asserts](#forbidden-words-and-asserts)
11. [Design rules](#design-rules)
12. [Examples](#examples)
13. [Troubleshooting](#troubleshooting)
14. [Project structure](#project-structure)
15. [Limitations](#limitations)

---

## What it does

- **Restricted words.** Words such as "Notice" and "Warning" never appear in the design. They are locked, and you can add more with `/restrict`. Matching is case-insensitive, so "notices" is also caught.
- **Complete content.** Every point from your prompt appears in the design. If wording is shortened to fit one screen, the plugin lists each change so you can review it.
- **Visual section.** Screenshots and data tables are cropped, cleaned, sharpened, and placed in a dedicated panel.
- **References.** A style guide or sample infographic is analysed. Its grid, colors, and look are adapted when it matches the content. Otherwise a fallback palette is used.
- **Automatic checks (asserts).** Every output is validated before delivery. A failed check triggers a re-render, up to three attempts.

---

## Requirements

| Requirement | Needed for | Check |
|---|---|---|
| Claude Code (current version) | Running the plugin | `claude --version` |
| Python 3.9+ | Validation and asset scripts | `python3 --version` |
| Pillow | Cropping and cleaning images | `python3 -c "import PIL"` |
| `pdftoppm` (poppler-utils) | Converting PDF tables to images | `pdftoppm -v` |
| Node.js + Playwright | Optional PNG export and 8K output | `npx playwright --version` |

Install Pillow:

```bash
pip install pillow
# If your system Python blocks global installs:
pip install pillow --break-system-packages
```

Install poppler (only if you use PDF tables):

```bash
# macOS
brew install poppler
# Debian/Ubuntu
sudo apt install poppler-utils
# Windows: install poppler and add its bin folder to PATH
```

Install Playwright (only for PNG export):

```bash
npm install -g playwright && npx playwright install chromium
```

---

## Installation

Choose one method.

### Method 1: Local directory (testing and development)

Use this while developing or to try the plugin without publishing it.

```bash
git clone <your-repo-url> mobile-infographic-engine
cd your-project
claude --plugin-dir /path/to/mobile-infographic-engine
```

Each session needs the flag. For a longer-lived setup, use Method 2 or 3.

### Method 2: From a marketplace

If the plugin is listed in a marketplace you have added:

```bash
claude plugin marketplace add <marketplace-source>
claude plugin install mobile-infographic-engine@<marketplace-name>
```

Then restart Claude Code. Run `/plugin` to confirm it is enabled.

### Method 3: Team-wide, through the project

Add the plugin to a project's `.claude/settings.json` so everyone who opens the project gets it:

```json
{
  "extraKnownMarketplaces": {
    "your-team": {
      "source": { "source": "github", "repo": "your-org/your-marketplace" }
    }
  },
  "enabledPlugins": {
    "mobile-infographic-engine@your-team": true
  }
}
```

Commit this file. Members are prompted to install the plugin when they trust the folder.

### Method 4: Copy the commands only (short command names)

Plugin commands are namespaced, so they appear as `/mobile-infographic-engine:infographic`. To use short names (`/infographic`), copy the command files into a project:

```bash
mkdir -p .claude/commands
cp /path/to/mobile-infographic-engine/commands/*.md .claude/commands/
```

In the copied files, replace `${CLAUDE_PLUGIN_ROOT}` with the absolute path to the plugin folder. Commands then appear as `/restrict`, `/upload-ref`, `/upload-asset`, and `/infographic`.

### Verify the install

Start Claude Code and type `/`. You should see the four commands. Then run:

```
/mobile-infographic-engine:restrict
```

It should show the current forbidden list (at minimum "Notice" and "Warning").

---

## Quick start

From your project folder:

```
/mobile-infographic-engine:upload-ref  path/to/style-guide.png
/mobile-infographic-engine:upload-asset path/to/grid-screenshot.png
/mobile-infographic-engine:infographic "Title: Water Bill Update
- New rate starts 1 Dec, ₹45 per kilolitre
- Pay online before 15 Dec to avoid a late fee
- Helpline: 1800-000-000"
```

Output lands in `infographic/output/`:

```
infographic/output/infographic.html
infographic/output/infographic.png     (if Playwright is installed)
infographic/output/content.json
```

Open `infographic.html` in a browser, or view the PNG on your phone.

---

## Commands

### `/mobile-infographic-engine:restrict`

Sets the words that must never appear in the infographic.

**Usage**

```
/mobile-infographic-engine:restrict "Alert" "Attention" "Stop"
/mobile-infographic-engine:restrict Alert, Attention, Stop
/mobile-infographic-engine:restrict            (shows the current list)
```

**Behaviour**

- Replaces the forbidden list with the new one. Duplicates are removed (case-insensitively).
- "Notice" and "Warning" are locked. They are always kept, even if you leave them out.
- Saves to `infographic/system_state.json`. Other settings are unchanged.
- Creates the workspace on first use.

**Example**

```
> /mobile-infographic-engine:restrict "Alert", "Stop"
Active restricted words:
  Locked:    Notice, Warning
  Forbidden: Alert, Stop
```

---

### `/mobile-infographic-engine:upload-ref`

Stores style guides or sample infographics for future designs.

**Usage**

```
/mobile-infographic-engine:upload-ref path/to/style-guide.png
/mobile-infographic-engine:upload-ref ~/Downloads/sample-poster.jpg
```

You can also attach files to the message instead of giving paths.

**Accepted types:** png, jpg, jpeg, webp, pdf

**Behaviour**

- Copies files to `infographic/reference/`.
- Renames files so spaces and special characters become underscores.
- Existing references are kept unless you ask to remove them.

---

### `/mobile-infographic-engine:upload-asset`

Stores the data your infographic shows: screenshots, charts, price tables.

**Usage**

```
/mobile-infographic-engine:upload-asset path/to/camera-grid.png
/mobile-infographic-engine:upload-asset path/to/quotation.pdf
```

**Behaviour**

- Copies files to `infographic/assets/`.
- For PDFs, renders the page at 200 dpi with `pdftoppm`. Pass the page number when the PDF has several pages (for example, `quotation.pdf page 2`).
- For PNG and JPG files, creates a cleaned version in `infographic/assets/prepared/`:
  - removes uniform margins (status bars, page borders)
  - adjusts contrast
  - sharpens slightly
  - scales to a maximum width of 960px so it fits the visual section

**Tip:** Upload a cropped screenshot if you can. Less surrounding UI means a clearer result on a phone.

---

### `/mobile-infographic-engine:infographic`

Generates the infographic. This is the main command.

**Usage**

```
/mobile-infographic-engine:infographic "<content>"
```

For longer content, write it as a block:

```
/mobile-infographic-engine:infographic "
Heading: Festival Schedule
- Gates open 5 PM on Saturday
- Parking at Lot B, free after 6 PM
- Food stalls in Hall 2
Asset: camera grid
"
```

**What it does**

1. Loads the restricted words and design settings.
2. Looks for references in `infographic/reference/` and uses them if they match the content.
3. Uses prepared assets from `infographic/assets/prepared/`.
4. Splits the content into points and keeps every one.
5. Writes the HTML design.
6. Runs the validator. Fixes and re-validates on failure (up to three attempts).
7. Exports a PNG if Playwright is available.
8. Reports the file paths and every shortened point.

**Example report**

```
Files:
  infographic/output/infographic.html
  infographic/output/infographic.png

Shortened:
  "Pay online before 15 December to avoid any late fee"
  → "Pay online by 15 Dec to avoid late fee"

Validation: PASS (forbidden words, canvas, font size, content coverage)
Note: text inside raster assets is not checked automatically. Please review the visual section.
```

---

## Workspace layout

The plugin creates this folder in your project. It holds your data and is not part of the plugin.

```
infographic/
├── system_state.json      Restricted words (created by the plugin)
├── reference/             Style guides and sample designs
├── assets/                Original uploaded data files
│   └── prepared/          Cleaned images used in the design
└── output/
    ├── infographic.html   Final design (self-contained)
    ├── infographic.png    Image export (optional)
    └── content.json       Points checked by the validator
```

Keep `infographic/` out of version control unless you want to share it. The default `.gitignore` in the plugin already excludes it.

---

## Step-by-step: creating a final image

This is the full workflow, from raw material to delivered image.

### Step 1: Prepare the content

Write every point you want in the image, with its numbers, prices, dates, and steps. Keep the wording as close to final as you can. The validator checks that each point's key words appear in the design, so vague or missing details will be flagged.

Remove any leftover template text such as `[INSERT YOUR CONTENT HERE]`. The plugin will stop and ask you if it finds it.

### Step 2: Set the restricted words

```
/mobile-infographic-engine:restrict "Notice", "Warning", "Alert"
```

Check the list with `/mobile-infographic-engine:restrict` before generating.

### Step 3: Add references (optional)

```
/mobile-infographic-engine:upload-ref brand-guide.png
/mobile-infographic-engine:upload-ref last-month-announcement.jpg
```

Use references that show the look you want: colors, grid, and spacing. If a reference clearly does not suit the content (for example, a dense spreadsheet for a two-line announcement), the plugin will use its own layout instead.

### Step 4: Add assets (optional)

```
/mobile-infographic-engine:upload-asset camera-grid.png
/mobile-infographic-engine:upload-asset rate-table.pdf
```

Check the `infographic/assets/prepared/` version. If the crop is wrong, edit the original, delete it, and upload again. Preparation is repeated on each upload.

### Step 5: Generate

```
/mobile-infographic-engine:infographic "<your content>"
```

Name any asset the design should use: "Asset: camera grid". If you leave it out, the plugin will ask.

### Step 6: Review the report

Check three things in the report:

1. **Shortened list.** Read each change. Reject any that lose meaning and ask for a rewrite, for example: "Restore the original wording for the late fee point and shorten the line above it instead."
2. **Validation result.** It should say PASS.
3. **Visual section.** Open the PNG or HTML. The validator cannot read text inside screenshots, so confirm any numbers in them yourself.

### Step 7: Revise if needed

Ask in plain language:

```
Make the heading larger and move the helpline to the bottom panel.
```

The plugin updates `infographic.html`, re-validates, and re-exports.

### Step 8: Deliver

- **WhatsApp:** send the PNG as an image so it opens full-screen.
- **Web or print:** use the HTML, or the 8K PNG if you exported it with `--device-scale-factor=4`.

Check the final image on a real phone before sending. Text should be readable without zooming.

---

## Using references

A reference is a style guide or a sample infographic. The plugin looks at its:

- **Grid:** how sections are arranged
- **Palette:** the main colors, which replace the fallback palette
- **Look:** spacing, panel shapes, and icon style

**The reference is used only if it matches the content.** A sample for a school notice will not be used for a dense price list. Otherwise the plugin falls back to:

| Setting | Fallback value |
|---|---|
| Primary | `#1E293B` |
| Accent | `#0EA5E9` |
| Background | `#F8FAFC` |
| Text | `#0F172A` |

**Good references:** clear images, one per style, at least 1000px wide.
**Weak references:** cluttered screenshots or images with a lot of small text.

To see which reference was used, look at the report. It names the reference, or says that none was used.

---

## Using assets

Assets are the data or visuals placed in the dedicated visual section.

| Asset type | How to prepare | Notes |
|---|---|---|
| Screenshot (app UI) | Crop to the content area | Remove the phone status bar |
| Data table (PDF) | Pass the page number | Rendered at 200 dpi |
| Chart (PNG/JPG) | Export at high resolution | Keep text large |

**Naming an asset in the prompt.** Refer to it by its filename without the extension, for example `Asset: camera-grid`. This tells the plugin which file goes in the visual section. If you leave it out and there is one asset, the plugin uses it. If there are several, it asks.

**Image quality.** The asset is scaled to 960px wide. Larger originals are downscaled, and very small ones are shown at their original size. Avoid uploads under 600px wide, since they will look soft on a phone.

---

## Forbidden words and asserts

Every output must pass these checks before it is delivered. The validator script (`scripts/validate.py`) runs them.

| Assert | Rule | If it fails |
|---|---|---|
| **A1. Restricted words** | No restricted word appears in the visible text, in any case or inside another word | Re-render without the word |
| **A2. Content coverage** | At least 80% of the key words from each content point appear in the design | Restore the omitted detail |
| **A3. Font size** | Every `font-size` is at least 28px | Increase the size or shorten the text |
| **A4. Canvas** | The page declares 1080px width and 1920px height | Fix the layout dimensions |

**Things to know about the checks**

- **Shortening is allowed.** A2 looks for key words, not exact sentences, so a shortened point passes if its important words remain.
- **Restricted words inside images are not checked.** Screenshots and table images are raster files. Review them by eye.
- **Overflow is not measured by the validator.** The plugin checks text fit while writing the design. The PNG export shows the final result, so review it.

To run the validator yourself:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py infographic/output/infographic.html \
  --content infographic/output/content.json
```

A passing run prints:

```
PASS: forbidden words, canvas, font size, and content coverage are all OK.
```

A failing run lists each problem:

```
FAIL
  - Forbidden words present: Notice
  - Font sizes below 28px: font-size: 24px
```

---

## Design rules

These come from `configs/design_system.json` and are applied to every design.

| Rule | Value |
|---|---|
| Canvas | 1080 × 1920 (9:16). 8K is 4320 × 7680 |
| Safe margin | 40px on all sides |
| Element spacing | 24px |
| Body text | 28px minimum, generous line height |
| Alignment | Left |
| Font | Inter, Roboto, Arial, or another sans-serif |
| Contrast | WCAG AAA |
| Bullets | Colored icons matching the theme |
| Sections | One card or panel per section |

---

## Examples

### Example 1: Simple announcement (no references or assets)

```
/mobile-infographic-engine:infographic "
Title: Water Supply Maintenance
- Supply paused on Sunday 2 Nov from 8 AM to 2 PM
- Store water for drinking and cooking
- Updates at 1800-000-000
"
```

Result: a single-column design using the fallback palette. Four sections, all points kept.

### Example 2: With a reference and a table

```
/mobile-infographic-engine:upload-ref community-board-style.png
/mobile-infographic-engine:upload-asset rate-card.pdf page 1

/mobile-infographic-engine:infographic "
Title: New Water Rates from 1 Dec
- Household: ₹45 per kilolitre up to 15 kl
- Commercial: ₹80 per kilolitre
- Pay online by 15 Dec to avoid late fee
Asset: rate-card
"
```

Result: the reference's grid and colors are used if the layout suits the content. The rate card goes in the visual section below the three points.

### Example 3: With restricted words and a screenshot

```
/mobile-infographic-engine:restrict "Alert", "Attention"
/mobile-infographic-engine:upload-asset camera-grid.png

/mobile-infographic-engine:infographic "
Heading: Camera Monitoring Update
- Eight cameras are online at the main gate
- Two cameras at Block C need repair
- Report faults to the security office
Asset: camera-grid
"
```

Result: "Notice", "Warning", "Alert", and "Attention" are kept out of the design. The cleaned screenshot is placed in the visual section.

### Example 4: Revising a design

```
Make the heading larger, and put the helpline in its own panel at the bottom.
```

The plugin edits `infographic.html`, re-validates, and re-exports the PNG.

### Example 5: Checking what is saved

```
/mobile-infographic-engine:restrict
/mobile-infographic-engine:upload-ref
```

Run without arguments, each command shows its current state.

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| Commands do not appear | Plugin not loaded | Restart Claude Code. Check with `/plugin`. |
| "Pillow not found" | Python package missing | `pip install pillow` |
| PDF upload fails | poppler not installed | Install poppler, or export the table as PNG |
| Validation keeps failing on A2 | A point's key words were changed | Restore the wording, or shorten around the key words |
| Validation fails on A1 | A restricted word is in the text | Rephrase, or remove the word from `/restrict` only if it is not locked |
| Text looks too small | Long content at 28px | Split into two designs, or cut wording |
| Asset is blurry | Source image is small | Upload a larger original |
| Wrong asset placed | Filename not named in the prompt | Add `Asset: <name>` to the prompt |
| No PNG produced | Playwright missing | Install Playwright, or open the HTML |
| Reference ignored | It does not match the content | Use a closer reference, or accept the fallback layout |

---

## Project structure

The plugin repository:

```
mobile-infographic-engine/
├── .claude-plugin/
│   └── plugin.json              Plugin manifest
├── commands/
│   ├── restrict.md              /restrict
│   ├── upload-ref.md            /upload-ref
│   ├── upload-asset.md          /upload-asset
│   └── infographic.md           /infographic
├── configs/
│   ├── design_system.json       Canvas, typography, palette, and spacing rules
│   └── system_state.default.json Default restricted words
├── scripts/
│   ├── validate.py              Asserts A1–A4
│   └── prepare_assets.py        Crops, cleans, and resizes images
├── .gitignore
├── LICENSE
└── README.md
```

---

## Limitations

- **One infographic at a time.** Each run produces one design. For a series, run the command once per image.
- **Text in images is not validated.** Restricted words and numbers inside screenshots must be checked by eye.
- **Layout fit is judged while writing.** The validator does not measure overflow. Review the PNG.
- **English and Indian-language fonts.** The plugin uses Latin sans-serif fonts. For Hindi, Telugu, or other scripts, add a font that supports them to `design_system.json` and check the rendering.
- **Single-user state.** `system_state.json` is per project, not per user. Teams sharing a project share its restricted words.

---

## Support and contributing

Report problems or suggest changes through the repository's issue tracker. When reporting a rendering problem, include:

1. The command you ran (with content removed if sensitive)
2. The validation output
3. The HTML file or a screenshot of the problem

Contributions are welcome. Run `python3 scripts/validate.py` against your change before opening a pull request.

## License

Apache License 2.0. See [LICENSE](LICENSE).
