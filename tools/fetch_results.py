#!/usr/bin/env python3
"""Fetch final scoreboards from https://scorelatam.naquadah.com.br/ and write tools/results.json.

PdA  = ICPC Latin America Championship (LAC)      -> pda24, pda25, pda26
LATAM = ICPC Latin America Regionals (LAR)        -> latam-2024, latam-2025

Only the overall ("group 1") scoreboard is used; the out-of-competition "CCL"
teams are not part of the ranking. Re-run whenever a new edition is published:
    python3 tools/fetch_results.py && python3 tools/build.py
"""
import html
import io
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

BASE = "https://scorelatam.naquadah.com.br/"
OUT = Path(__file__).resolve().parent / "results.json"
PHOTOS = Path(__file__).resolve().parent.parent / "assets/img/teams"
PHOTO_WIDTH = 720

EDITIONS = {
    # key: (scorelatam folder, how many rows to keep)
    "lac2024": ("pda24", 12),
    "lac2025": ("pda25", 12),
    "lac2026": ("pda26", 13),
    "lar2024": ("latam-2024", 10),
    "lar2025": ("latam-2025", 10),
}

REGIONS = {
    "Brazil": {"BR"},
    "Mexico": {"MX"},
    "Central America": {"CR", "SV", "GT", "HN", "NI", "PA"},
    "Caribbean": {"CU", "DO", "PR", "TT", "AG", "JM", "HT", "VI", "GD"},
    "South America/North": {"CO", "VE"},
    "South America/South": {"AR", "BO", "CL", "PE", "PY", "UY", "EC"},
}


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def photo_url(folder, cell_html):
    m = re.search(r"href=['\"]([^'\"]*photos/[^'\"]+)['\"]", cell_html)
    return urljoin(f"{BASE}{folder}/", m.group(1)) if m else ""


def download_photo(url, dest):
    """Download a team photo and store it as a ~720px-wide WebP (falls back to the original bytes)."""
    if dest.exists():
        return True
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    except Exception as exc:  # missing photo is fine
        print("  no photo:", url, exc)
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("RGB")
        if im.width > PHOTO_WIDTH:
            im = im.resize((PHOTO_WIDTH, round(im.height * PHOTO_WIDTH / im.width)))
        im.save(dest, "WEBP", quality=78)
    except ImportError:
        dest.write_bytes(data)
    return True


def fetch(folder):
    req = urllib.request.Request(f"{BASE}{folder}/", headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")


def parse(page, folder):
    rows = []
    for m in re.finditer(r'<tr class="sitegroup(\d+)"[^>]*>(.*?)</tr>', page, re.S):
        if m.group(1) != "1":          # overall scoreboard only
            continue
        cells = re.findall(r"<td[^>]*>(.*?)</td>", m.group(2), re.S)
        if len(cells) < 4:
            continue
        user = clean(cells[1])
        name_html = cells[2]
        head = re.split(r"<\/?br", name_html)[0]
        label = clean(head)
        inst = re.match(r"\[([^\]]+)\]\s*(.*)", label)
        extra = [clean(x) for x in re.findall(r"<\/?br\s*/?>(?:<b>)?([^<]+)", name_html)]
        total = clean(cells[-1])
        t = re.match(r"(\d+)\s*\((\d+)\)", total)
        rows.append({
            "rank": int(clean(cells[0])),
            "id": user.split("/")[0].strip(),
            "photo_url": photo_url(folder, cells[1]),
            "cc": user.split("/")[-1],
            "inst": inst.group(1) if inst else "",
            "team": (inst.group(2) if inst else label).strip(),
            "solved": int(t.group(1)) if t else 0,
            "penalty": int(t.group(2)) if t else 0,
            "medal": next((k for k, e in (("gold", "\U0001F947"), ("silver", "\U0001F948"), ("bronze", "\U0001F949"))
                           if any(e in x for x in extra) or e in label), ""),
            "tags": [x for x in extra if "Medalist" not in x],
            "promoted": "\U0001F396" in " ".join(extra) or "\U0001F396" in name_html,
        })
    return rows


def main():
    out = {}
    for key, (folder, keep) in EDITIONS.items():
        rows = parse(fetch(folder), folder)
        entry = {
            "source": f"{BASE}{folder}/",
            "teams": len(rows),
            "promoted": sum(1 for r in rows if r["promoted"]),
            "top": rows[:keep],
        }
        champs = {}
        if key.startswith("lar"):
            for region, ccs in REGIONS.items():
                best = next((r for r in rows if r["cc"] in ccs), None)
                if best:
                    champs[region] = {k: best[k] for k in ("id", "rank", "cc", "inst", "team", "solved", "penalty")}
                    champs[region]["teams"] = sum(1 for r in rows if r["cc"] in ccs)
            entry["regions"] = champs
        # photos for every team that is shown on the site
        by_id = {r["id"]: r for r in rows}
        for r in entry["top"] + [by_id[c["id"]] for c in champs.values() if c.get("id") in by_id]:
            if r["photo_url"] and download_photo(r["photo_url"], PHOTOS / key / f'{r["id"]}.webp'):
                r["photo"] = f'img/teams/{key}/{r["id"]}.webp'
        for c in champs.values():
            if c.get("id") in by_id and by_id[c["id"]].get("photo"):
                c["photo"] = by_id[c["id"]]["photo"]
        for r in entry["top"]:
            r.pop("photo_url", None)
        out[key] = entry
        print(key, folder, entry["teams"], "teams;", entry["promoted"], "promoted")
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
