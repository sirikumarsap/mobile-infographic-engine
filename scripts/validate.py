#!/usr/bin/env python3
"""Check a generated infographic against the project's hard rules.

Usage:
    python3 validate.py infographic/output/infographic.html \
        --content infographic/output/content.json

Exit code 0 means every check passed. Exit code 1 means re-render.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DESIGN = PLUGIN_ROOT / "configs" / "design_system.json"
DEFAULT_STATE = Path("infographic/system_state.json")
STOPWORDS = {"the", "and", "for", "with", "that", "this", "from", "into", "your"}
COVERAGE_THRESHOLD = 0.8  # share of a point's key words that must survive


def visible_text(markup: str) -> str:
    markup = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", markup)
    text = re.sub(r"(?s)<[^>]+>", " ", markup)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def key_words(text: str):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower())
            if (len(w) > 3 or w.isdigit()) and w not in STOPWORDS]


def check_forbidden(text: str, tokens):
    low = text.lower()
    return [t for t in tokens if t.lower() in low]  # substring, so "notices" also fails


def check_points(text: str, points):
    present = set(re.findall(r"[a-z0-9]+", text.lower()))
    failures = []
    for point in points:
        words = key_words(point)
        if not words:
            continue
        ratio = sum(w in present for w in words) / len(words)
        if ratio < COVERAGE_THRESHOLD:
            failures.append(f"{point!r} ({ratio:.0%} of key words found)")
    return failures


def check_fonts(markup: str, minimum: float):
    return [m.group(0) for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", markup)
            if float(m.group(1)) < minimum]


def check_canvas(markup: str):
    return bool(re.search(r"width\s*:\s*1080px", markup)
                and re.search(r"height\s*:\s*1920px", markup))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an infographic.")
    parser.add_argument("html", type=Path)
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    args = parser.parse_args()

    state = json.loads(args.state.read_text(encoding="utf-8"))["dynamic_restrictions"]
    design = json.loads(args.design.read_text(encoding="utf-8"))
    tokens = list(dict.fromkeys(state.get("locked_tokens", []) + state.get("forbidden_tokens", [])))
    minimum = float(re.sub(r"[^\d.]", "", design["typography"]["base_font_size"]))

    markup = args.html.read_text(encoding="utf-8")
    content = json.loads(args.content.read_text(encoding="utf-8"))
    text = visible_text(markup)

    failures = []
    hits = check_forbidden(text, tokens)
    if hits:
        failures.append(f"Forbidden words present: {', '.join(hits)}")
    if not check_canvas(markup):
        failures.append("Canvas must declare width 1080px and height 1920px")
    small = check_fonts(markup, minimum)
    if small:
        failures.append(f"Font sizes below {minimum:g}px: {', '.join(small[:5])}")
    failures += [f"Content point missing or weakened: {p}"
                 for p in check_points(text, content.get("points", []))]

    if failures:
        print("FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: forbidden words, canvas, font size, and content coverage are all OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())