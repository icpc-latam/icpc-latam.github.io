#!/usr/bin/env python3
"""Check that every local href/src in the generated site exists, and that no web.archive.org /
Google Sites leftovers remain.   Usage: python3 tools/check_links.py"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LEFTOVERS = ("web.archive.org", "google.com/url?q=", "lh3.googleusercontent")
bad = checked = 0
for page in sorted(ROOT.rglob("*.html")):
    text = page.read_text(encoding="utf-8")
    for m in re.finditer(r'(?:href|src)="([^"]+)"', text):
        url = m.group(1)
        if re.match(r"(https?:|mailto:|#|data:)", url) or (url.startswith("/") and page.name == "404.html"):
            continue
        checked += 1
        target = (page.parent / unquote(url.split("#")[0])).resolve()
        if target.is_dir():
            target /= "index.html"
        if not target.exists():
            bad += 1
            print("MISSING", page.relative_to(ROOT), url)
    for key in LEFTOVERS:
        if key in text:
            bad += 1
            print("LEFTOVER", key, page.relative_to(ROOT))
print(f"checked {checked} local references; problems: {bad}")
sys.exit(1 if bad else 0)
