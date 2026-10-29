#!/usr/bin/env python3
"""Static site generator for www.icpclatam.org.

Content was recovered from the Wayback Machine (captures of Jan-Jun 2026).
Run from anywhere:  python3 tools/build.py
It writes index.html + one <section>/index.html per page into the project root,
mirroring the original Google Sites URLs (/regionals/lar2025, /masters/masters2024, ...).
"""
import json
import os
import shutil
from html import escape as esc
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
RESULTS = json.loads((ROOT / "tools/results.json").read_text(encoding="utf-8"))  # see tools/fetch_results.py
SITE_URL = "https://www.icpclatam.org/"
MARATONA_LINUX_WIKI = "https://github.com/maratona-linux/maratona-linux/wiki"
MARATONA_LINUX_FEATURES = MARATONA_LINUX_WIKI + "/The-features-of-Maratona-Linux-24.04"
MARATONA_LINUX_TEST = MARATONA_LINUX_WIKI + "/How-to-Test-the-Competition-System"
RULES_2026_27 = "2026-2027 ICPC Latin America - Promotion Rules.pdf"
RULES_2026_27_LABEL = "2026-2027 Rules: LAR 2026 Regionals & Promotion to the LAC 2027 Championship"
SCORELATAM = "https://scorelatam.naquadah.com.br/"
MARATONA_HIST = "https://maratona.sbc.org.br/hist/index.html"

# ---------------------------------------------------------------- site data --
BANNER = ("The upcoming ICPC Latin America Regionals 2026 - November 7, 2026", "regionals/lar2026", "Click here")

NAV = [
    ("Home", "home", []),
    ("News (Archive)", "home/news-archive", []),
    ("Regionals", "regionals", [("LAR2026", "regionals/lar2026"), ("LAR2025", "regionals/lar2025"), ("LAR2024", "regionals/lar2024"),
                                ("LARs1996-2023", "regionals/lars1996-2023")]),
    ("Championships", "championships", [("LAC2027", "championships/lac2027"), ("LAC2026", "championships/lac2026"), ("LAC2025", "championships/lac2025"),
                                         ("LAC2024", "championships/lac2024")]),
    ("Masters", "masters", [("Masters2024", "masters/masters2024"), ("Masters2023", "masters/masters2023"),
                            ("Masters2022", "masters/masters2022"), ("Masters2020-2021", "masters/masters2020-2021"),
                            ("Masters2019", "masters/masters2019")]),
    ("Training", "training", []),
    ("History", "history", []),
    ("Contact", "contact", []),
]

SOCIAL = [
    ("YouTube", "https://www.youtube.com/@ICPCLatamSocial"),
    ("LinkedIn", "https://www.linkedin.com/company/icpc-latam-social/"),
    ("Facebook", "https://web.facebook.com/icpclatamsocial"),
    ("Instagram", "https://www.instagram.com/icpclatamsocial"),
]

# ISO code for flags (assets/img/flags/<code>.png)
CC = {
    "Brazil": "br", "Mexico": "mx", "Argentina": "ar", "Chile": "cl", "Colombia": "co", "Venezuela": "ve",
    "Cuba": "cu", "Peru": "pe", "Uruguay": "uy", "Guatemala": "gt", "Puerto Rico": "pr", "Bolivia": "bo",
    "Ecuador": "ec", "Costa Rica": "cr", "Dominican Republic": "do", "Jamaica": "jm", "Paraguay": "py",
    "Haiti": "ht", "Trinidad and Tobago": "tt", "US Virgin Islands": "vi", "Panama": "pa", "Grenada": "gd",
    "El Salvador": "sv", "Nicaragua": "ni", "Antigua and Barbuda": "ag",
}

REGIONAL_COUNTRIES = [
    ("Brazil", 1996), ("Mexico", 1996), ("Argentina", 1997), ("Chile", 1997), ("Colombia", 1997),
    ("Venezuela", 1997), ("Cuba", 1999), ("Peru", 1999), ("Uruguay", 1999), ("Guatemala", 2000),
    ("Puerto Rico", 2000), ("Bolivia", 2003), ("Ecuador", 2003), ("Costa Rica", 2005),
    ("Dominican Republic", 2009), ("Jamaica", 2010), ("Paraguay", 2012), ("Haiti", 2013),
    ("Trinidad and Tobago", 2013), ("US Virgin Islands", 2013), ("Panama", 2014), ("Grenada", 2014),
    ("El Salvador", 2016), ("Nicaragua", 2017), ("Antigua and Barbuda", 2023),
]
CHAMP_COUNTRIES = [
    ("Argentina", 2024), ("Bolivia", 2024), ("Brazil", 2024), ("Chile", 2024), ("Colombia", 2024),
    ("Costa Rica", 2024), ("Cuba", 2024), ("Dominican Republic", 2024), ("El Salvador", 2024),
    ("Guatemala", 2024), ("Mexico", 2024), ("Peru", 2024), ("Puerto Rico", 2024),
    ("Trinidad and Tobago", 2024), ("Uruguay", 2024), ("Venezuela", 2024),
    ("Antigua and Barbuda", 2026),
]
MASTERS_COUNTRIES = [
    ("Mexico", 2019), ("Costa Rica", 2019), ("Argentina", 2021), ("Bolivia", 2021), ("Peru", 2021),
    ("Chile", 2023), ("Colombia", 2023), ("Cuba", 2023), ("Brazil", 2024), ("Dominican Republic", 2024),
]


# ----------------------------------------------------------------- helpers --
class Page:
    def __init__(self, path, title, code, body, desc=""):
        self.path, self.title, self.code, self.body, self.desc = path, title, code, body, desc

    @property
    def depth(self):
        return len([p for p in self.path.split("/") if p])


def rel(page, target):
    """Relative URL from `page` to site path `target` ('' = home)."""
    up = "../" * page.depth
    if target == "":
        return up or "./"
    return f"{up}{target}/"


def asset(page, name):
    return "../" * page.depth + "assets/" + quote(name)


def ext(url, text, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{esc(url, quote=True)}" target="_blank" rel="noopener">{text}</a>'


def flag(page, country, cls=""):
    return f'<img src="{asset(page, "img/flags/" + CC[country] + ".png")}" alt="Flag of {esc(country)}" loading="lazy">'


def countries_grid(page, items):
    out = ['<div class="countries">']
    for name, since in items:
        out.append(f'<div class="country">{flag(page, name)}{esc(name)}<small>(since {since})</small></div>')
    out.append("</div>")
    return "".join(out)


def pdf(page, filename, label=None):
    size = (ROOT / "assets/docs" / filename).stat().st_size
    mb = f"{size / 1_000_000:.1f} MB" if size >= 1_000_000 else f"{size // 1000} KB"
    return (f'<a class="pdf" href="{asset(page, "docs/" + filename)}" target="_blank" rel="noopener">'
            f'<span class="ic">PDF</span><span class="nm">{esc(label or filename)}<small>{esc(filename) if label else ""}'
            f'{" · " if label else ""}{mb}</small></span></a>')


def yt(vid, title):
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{vid}" title="{esc(title, quote=True)}" '
            f'loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen></iframe></div>')


def event_card(href, when, title, sub, photo="", past=False):
    cls = "event past" if past else "event"
    return (f'<article class="{cls}">{photo}<div class="ev-body"><span class="when">{when}</span>'
            f'<a class="ev-link" href="{href}">{title}</a><span class="sub">{sub}</span></div></article>')


def anchors(items):
    return '<div class="anchors">' + "".join(f'<a href="#{i}">{esc(t)}</a>' for i, t in items) + "</div>"


def wrap(inner, cls="block"):
    return f'<section class="{cls}"><div class="wrap">{inner}</div></section>'


def band(title, anchor=""):
    a = f' id="{anchor}"' if anchor else ""
    return f'<div class="band-title"{a}><h2>{esc(title)}</h2></div>'


def intro(text_html):
    return f'<p class="intro">{text_html}</p>'


def facts(rows):
    return '<ul class="facts">' + "".join(f"<li><b>{esc(k)}</b> {v}</li>" for k, v in rows) + "</ul>"


CODE_NAMES = {v.upper(): k for k, v in CC.items()}


def flag_cc(page, cc):
    name = CODE_NAMES.get(cc.upper(), cc)
    if cc.lower() + ".png" not in {p.name for p in (ROOT / "assets/img/flags").iterdir()}:
        return esc(cc)
    return (f'<img class="mini" src="{asset(page, "img/flags/" + cc.lower() + ".png")}" '
            f'alt="{esc(name, quote=True)}" title="{esc(name, quote=True)}" loading="lazy">')


def thumb(page, r, cls="thumb"):
    """Small linked team photo (from ScoreLatam) or empty string."""
    if not r.get("photo"):
        return ""
    alt = esc(f'Team photo: {r.get("inst", "")} {r.get("team", "")}'.strip(), quote=True)
    return (f'<a class="{cls}" href="{asset(page, r["photo"])}" target="_blank" rel="noopener">'
            f'<img src="{asset(page, r["photo"])}" alt="{alt}" loading="lazy"></a>')


def team_photo(page, key, idx=0, alt=""):
    r = RESULTS[key]["top"][idx]
    if not r.get("photo"):
        return ""
    return f'<img src="{asset(page, r["photo"])}" alt="{esc(alt or "Team photo", quote=True)}" loading="lazy">'


def winner_block(page, key, heading, lines):
    r = RESULTS[key]["top"][0]
    items = "".join(f"<li>{x}</li>" for x in lines)
    return (f'<div class="result">{team_photo(page, key, 0, "Winning team: " + r["inst"] + " " + r["team"])}'
            f'<div><h3>{heading}</h3><ul>{items}'
            f'<li>Problems solved: <strong>{r["solved"]}</strong> ({r["penalty"]} penalty minutes)</li></ul></div></div>')


MEDAL = {"gold": "&#129351;", "silver": "&#129352;", "bronze": "&#129353;"}


def results_table(page, key, note_col=True):
    """Top-N scoreboard rows from tools/results.json (ScoreLatam)."""
    data = RESULTS[key]
    head = '<th>#</th><th>Team</th><th>Solved</th><th>Penalty</th>' + ('<th></th>' if note_col else "")
    body = []
    for r in data["top"]:
        notes = []
        if r.get("medal"):
            notes.append(MEDAL[r["medal"]])
        notes += [esc(t) for t in r.get("tags", []) if t and t != "\U0001F396\ufe0f"]
        if key.startswith("lar") and r.get("promoted"):
            notes.append("&#127894;&#65039; Promoted to the Latin American Championship")
        team = esc(r["team"])
        body.append(f'<tr><td>{r["rank"]}</td><td><div class="team-cell">{thumb(page, r)}<div>{flag_cc(page, r["cc"])}<strong>{esc(r["inst"])}</strong> &middot; {team}</div></div></td>'
                    f'<td>{r["solved"]}</td><td>{r["penalty"]}</td>' + (f'<td class="notes">{" ".join(notes)}</td>' if note_col else "") + "</tr>")
    return (f'<div class="tbl-wrap"><table class="tbl"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'
            f'<p class="src">Top {len(data["top"])} of {data["teams"]} ranked teams. '
            f'{ext(data["source"], "Full scoreboard and problemset at ScoreLatam")}.</p>')


def region_table(page, key):
    regs = RESULTS[key]["regions"]
    rows = "".join(
        f'<tr><td>{esc(name)}</td><td><div class="team-cell">{thumb(page, r)}<div>{flag_cc(page, r["cc"])}<strong>{esc(r["inst"])}</strong> &middot; {esc(r["team"])}</div></div></td>'
        f'<td>{r["solved"]}</td><td>{r["penalty"]}</td><td>{r["rank"]}</td><td>{r["teams"]}</td></tr>'
        for name, r in regs.items())
    return ('<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Region</th><th>Best team</th><th>Solved</th><th>Penalty</th>'
            f'<th>Global #</th><th>Teams</th></tr></thead><tbody>{rows}</tbody></table></div>')


def report(paragraphs, source_html):
    return '<div class="report">' + "".join(f"<p>{p}</p>" for p in paragraphs) + f'<p class="src">Source: {source_html}</p></div>'


MARATONA_SRC = ext(MARATONA_HIST, "Maratona SBC de Programação &ndash; history") + " and " + ext(SCORELATAM, "ScoreLatam")


# -------------------------------------------------------------------- pages --
def page_home(path=""):
    p = Page(path, "Home", "icpc.latam->new_home()", "")

    def news(date, text, media="", link=None, label="Results"):
        if not link:
            more = ""
        elif link.startswith("http"):
            more = f' <a class="more" href="{esc(link, quote=True)}" target="_blank" rel="noopener">{label} &rarr;</a>'
        else:
            more = f' <a class="more" href="{rel(p, link)}">{label} &rarr;</a>'
        return f'<article class="news">{media}<div class="body"><span class="date">{esc(date)}</span>{text}{more}</div></article>'

    regions = [
        ("r-mexico", "Mexico", "https://eventos.iteso.mx/acm/"),
        ("r-central", "Central America", "https://icpccentroamerica.org/"),
        ("r-caribbean", "Caribbean", "https://icpccaribe.org/"),
        ("r-north", "SouthAmerica/North", "https://icpc.global/regionals/finder/South-America-North"),
        ("r-south", "SouthAmerica/South", "https://icpc.global/regionals/finder/SouthAmerica-South"),
        ("r-brazil", "SouthAmerica/Brazil", "https://maratona.sbc.org.br/"),
    ]
    regions_html = "".join(f'<li class="{c}">{ext(u, esc(n))}</li>' for c, n, u in regions)

    wf46 = "https://zibada.guru/finals/2022/"
    wf47 = "https://zibada.guru/finals/2023/"
    news_cards = "".join([
        news("October 2026", "<strong>MOJ</strong> (Melhor Online Judge) is the new contest management system of ICPC Latin America. "
             "Visit moj.naquadah.com.br&hellip;", "", "https://moj.naquadah.com.br/", "Visit MOJ"),
        news("March 2026", "&ldquo;ooga booga&rdquo; team, from UFMG - Universidade Federal de Minas Gerais, got Latin America Champion "
             "title at ICPC Latam Championship in Santiago, Chile &ndash; the second Latam title for UFMG&hellip;",
             f'<img class="pic" src="{asset(p, RESULTS["lac2026"]["top"][0]["photo"])}" alt="UFMG team ooga booga, Latin America champion 2026" loading="lazy">',
             "championships/lac2026"),
        news("November 8, 2025", "&ldquo;Naim continua dentro de nós&rdquo; team, from UNICAMP, ranked first at the ICPC Latin America "
             "Regionals 2025 with 10 problems solved; 44 teams were promoted to the Latam Championship&hellip;",
             f'<img class="pic" src="{asset(p, RESULTS["lar2025"]["top"][0]["photo"])}" alt="UNICAMP team, winner of the Regionals 2025" loading="lazy">',
             "regionals/lar2025"),
        news("March 17, 2025", "&ldquo;Faça o WM&rdquo; team, from USP - Universidade de São Paulo, got Latin America Champion "
             "title at ICPC Latam Championship in Salvador de Bahía, Brasil&hellip;", ""),
        news("March, 2024", "Candidacy of Universidad da Bahía, Salvador de Bahía, Brasil as a venue for the ICPC Latam "
             "Championship&hellip;", yt("YpX3AWOueVE", "Programadores da América 2025")),
        news("April 19, 2024", "&ldquo;InChaVoLa&rdquo; team, from Universidad de Buenos Aires - FCEN, got Latam champion "
             "title at ICPC World Finals no. 48 in Astana, Kazakhstan&hellip;"),
        news("September 26, 2024", "Candidacy of ITESO, Guadalajara, Mexico as a potential venue for the ICPC World Finals&hellip;",
             yt("EEUEOUMyQVk", "Candidacy of ITESO, Guadalajara, Mexico as a potential venue for the ICPC World Finals")),
        news("April 20, 2024", "&ldquo;Chilaquiles con pollo&rdquo; team, from Escuela Superior De Computo Instituto Politécnico "
             "Nacional, got Latam champion title at ICPC World Finals no. 46 in Luxor, Egypt&hellip;", "", wf46),
        news("April 20, 2024", "&ldquo;InChaVoLa&rdquo; team, from Universidad de Buenos Aires - FCEN, got Latam champion title "
             "at ICPC World Finals no. 47 in Luxor, Egypt&hellip;", "", wf47),
    ])

    def sponsor(name, tag, url, logo):
        img = ""
        for ext_ in ("svg", "png", "webp", "jpg"):
            if (ROOT / f"assets/img/sponsors/{logo}.{ext_}").exists():
                img = f'<img src="{asset(p, f"img/sponsors/{logo}.{ext_}")}" alt="">'
                break
        return f'<a class="sponsor" href="{url}" target="_blank" rel="noopener">{img}<strong>{name}</strong><span>{tag}</span></a>'

    p.body = (
        f'<div class="lead">&#127880; ICPC Latam is part of the global community of the '
        f'{ext("https://icpc.global/", "International Collegiate Programming Contest (ICPC)")} &#127880;</div>'
        + band("Our Regions")
        + wrap(f'<div class="regions"><img src="{asset(p, "img/logo.png")}" alt="Map of the ICPC Latin America regions">'
               f'<ul>{regions_html}</ul></div>'
               f'<p class="more-link"><a href="{rel(p, "regionals")}#websites">Websites of all regions and countries &hellip;</a></p>')
        + band("Upcoming Events")
        + wrap('<div class="event-cards">'
               + event_card(rel(p, "regionals/lar2026"), "November 6-7, 2026", "ICPC Latin American Regionals 2026 (LAR)",
                            "Contest on Saturday, November 7th &middot; live on the Maratona SBC channel")
               + event_card(rel(p, "championships/lac2027"), "July 13-17, 2027", "ICPC Latin American Championship 2027 (LAC)",
                            "Monterrey, Mexico &middot; 80 teams")
               + "</div>")
        + band("Latest Events")
        + wrap('<div class="event-cards">'
               + event_card(rel(p, "championships/lac2026"), "March 4-8, 2026 &middot; Santiago, Chile",
                            "ICPC Latin American Championship 2026 &ndash; results",
                            "Champion: UFMG (Brazil) &ndash; &ldquo;ooga booga&rdquo;", thumb(p, RESULTS["lac2026"]["top"][0], "ev-thumb"), True)
               + event_card(rel(p, "regionals/lar2025"), "November 8, 2025", "ICPC Latin American Regionals 2025 &ndash; results",
                            "Winner: UNICAMP (Brazil) &ndash; 558 teams", thumb(p, RESULTS["lar2025"]["top"][0], "ev-thumb"), True)
               + "</div>")
        + band("Our News")
        + wrap(f'<div class="news-grid">{news_cards}</div>'
               f'<p class="more-link"><a href="{rel(p, "home/news-archive")}">More news here &hellip;</a></p>')
        + band("Our Sponsors")
        + wrap('<div class="sponsors">'
               + sponsor("JetBrains", "ICPC Global Sponsor Programming Tools", "https://www.jetbrains.com/icpc/", "jetbrains")
               + sponsor("Huawei", "ICPC Diamond Sponsor", "https://www.huawei.com/", "huawei")
               + sponsor("ICPC Foundation", "Advancing the art and science of competitive programming", "https://icpc.foundation/", "icpc-foundation")
               + "</div>"
               + '<div class="videos">'
               + yt("9RMtur_eUUY", "Huawei promo video for LATAM. ICPC LATAM sponsor.")
               + yt("rDY50LRcfSE", "We are JetBrains. ICPC LATAM sponsor.")
               + "</div>")
    )
    return p


def page_news_archive():
    p = Page("home/news-archive", "News (Archive)", "icpc.latam->archived_news()", "")

    def news(date, text, media=""):
        return f'<article class="news">{media}<div class="body"><span class="date">{esc(date)}</span>{text}</div></article>'

    n2024 = "".join([
        news("April 1, 2024", "After a successful PdA2024, ITESO and Mexico are running for a future World Finals&hellip; the first "
             "one in ICPC history to be celebrated in Latin America&hellip;", yt("EDrtfb4bYKk", "Candidacy of ITESO, Guadalajara, Mexico as a potential venue for the ICPC World Finals")),
        news("March 17, 2024", "Celebrated with success our First ICPC Latin America Championships LAC, in Guadalajara, Mexico&hellip; "
             "see the Real contest broadcast!", yt("fULkdtVQdX0", "Programadores de América 2024. The ICPC Latin America Championship.")),
        news("June 14, 2024", "Maratona Feminina de Programação with 150 finalists, including participation of females from Brazil, "
             "Chile, Peru, Colombia&hellip;"),
    ])
    n2023 = news("October 21, 2023", "The South American giant, Brazil, celebrates its &ldquo;Final Brasileira 2023&rdquo;&hellip; "
                 "see fantastic images on this world-class video streaming!", yt("FoqWXgmCUpw", "Maratona SBC 2023 - Final Brasileira"))
    p.body = (band("2024 News") + wrap(f'<div class="news-grid">{n2024}</div>')
              + band("2023 News") + wrap(f'<div class="news-grid">{n2023}</div>'))
    return p


# Regional and national websites, by sub-region. Only links that were opened and checked (Oct 2026) are listed;
# a country without a link shows "TBA" until a national site is found. (region, regional sites, [(country, national sites)])
REGION_FILES = ['brazil', 'mexico', 'central-america', 'caribbean', 'south-america-north', 'south-america-south']  # data/regions/<name>.json, in page order


def load_websites():
    """Regional and national websites, one small JSON file per region (edited by pull requests; see CONTRIBUTING.md)."""
    out = []
    for name in REGION_FILES:
        path = ROOT / "data/regions" / f"{name}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        for site in d["websites"] + [w for c in d["countries"] for w in c["websites"]]:
            if not site.get("label") or not site.get("url", "").startswith("https://"):
                raise SystemExit(f"{path}: every website needs a \"label\" and an https:// \"url\" (got {site})")
        for c in d["countries"]:
            if c["country"] not in CC:
                raise SystemExit(f"{path}: unknown country {c['country']!r}; use one of: {', '.join(sorted(CC))}")
        out.append((name, d))
    return out


def websites_block(page):
    out = []
    for name, d in load_websites():
        sites = " &middot; ".join(ext(w["url"], esc(w["label"])) for w in d["websites"])
        cards = "".join(
            stream_block(page, c["country"], [(w["label"], w["url"]) for w in c["websites"]] or [("National website: TBA", None)])
            for c in d["countries"])
        out.append(f'<h3 id="{name}">{esc(d["region"])}</h3><p>Regional website: {sites}</p><div class="streams">{cards}</div>')
    return "".join(out)


def page_regionals():
    p = Page("regionals", "Regionals", "icpc.latam->regionals()", "")
    p.body = (
        anchors([("editions", "Editions"), ("countries", "Participating Countries"), ("websites", "Regional & National Websites")])
        + intro("The ICPC Latin American Regionals (LAR) is organized to be held multi-sites, with centralized judging "
                "through MOJ (computers running Maratona Linux), same problemset, same timeframe (November&rsquo;s 2nd saturday, starting 17:00 hrs UTC/GMT, "
                f'5 hours of duration). Best teams will advance to the <a href="{rel(p, "championships")}">Latam Championship</a>&hellip;')
        + band("Editions", "editions")
        + wrap('<ul class="editions">'
               f'<li>Edition #31 - <a href="{rel(p, "regionals/lar2026")}">The 2026 ICPC Latin American Regionals LAR - November 7, 2026</a></li>'
               f'<li>Edition #30 - <a href="{rel(p, "regionals/lar2025")}">The 2025 ICPC Latin American Regionals LAR - November 8, 2025</a></li>'
               f'<li>Edition #29 - <a href="{rel(p, "regionals/lar2024")}">The 2024 ICPC Latin American Regionals LAR - November 9, 2024</a></li>'
               f'<li class="plain"><a href="{rel(p, "regionals/lars1996-2023")}">All previous editions here&hellip;</a></li></ul>')
        + band("Participating Countries", "countries")
        + wrap(countries_grid(p, REGIONAL_COUNTRIES))
        + band("Regional & National Websites", "websites")
        + wrap("<p>Each of the six regionals has its own website, and some countries also run a national contest (and site) that "
               "selects the teams for the Regionals. Entries marked <span class=\"tba\">TBA</span> are national websites we have not "
               f'found yet. Every region and country can fix or add its links with a pull request: see '
               f'{ext("https://github.com/icpc-latam/icpc-latam.github.io/blob/main/CONTRIBUTING.md", "how to contribute")}, or '
               f'<a href="{rel(p, "contact")}">contact us</a>.</p>'
               + websites_block(p)
               + '<p class="note">ICPC Bolivia is a community-maintained website, not an official site of the ICPC Foundation.</p>')
    )
    return p


def pdf_pair(page, *names):
    return "".join(pdf(page, n) for n in names)


def stream_block(page, country, links, header_url=None, flag_country=None):
    fc = flag_country or country
    items = "".join(
        f'<li>{ext(u, esc(t)) if u else f"<span class=tba>{esc(t)}</span>"}</li>' for t, u in links)
    name = ext(header_url, esc(country)) if header_url else esc(country)
    return f'<div class="stream"><h4>{flag(page, fc)}{name}</h4><ul>{items}</ul></div>'


def teams_links(slug_suffix, year_label, last, finder_kind="teams"):
    regs = [("Brazil", f"South-America-Brazil-{slug_suffix}"), ("Mexico", f"Mexico-{slug_suffix}"),
            ("Caribbean", f"CaribFinals-{slug_suffix}"), ("Central America", f"Central-America-{slug_suffix}"),
            ("SouthAmerican/South", f"SouthAmerica-South-{slug_suffix}"),
            ("SouthAmerican/North", f"South-America-North-{slug_suffix}")]
    return regs


def systems_block(page, moj_text="", ram="", keyboard=""):
    """Contest systems + invitation to test the competition image (Maratona Linux wiki)."""
    cards = ""
    if moj_text:
        cards += ('<a class="card" href="https://moj.naquadah.com.br/" target="_blank" rel="noopener"><strong>MOJ</strong>'
                  f'<span>{moj_text}</span></a>')
    cards += (f'<a class="card" href="{MARATONA_LINUX_WIKI}" target="_blank" rel="noopener"><strong>Maratona Linux</strong>'
              '<span>Official operating system for the contest computers</span></a>'
              f'<a class="card" href="{MARATONA_LINUX_FEATURES}" target="_blank" rel="noopener"><strong>Maratona Linux 24.04 features</strong>'
              '<span>Tools, editors and resources available in the contest system</span></a>'
              f'<a class="card test" href="{MARATONA_LINUX_TEST}" target="_blank" rel="noopener"><strong>Test the competition system</strong>'
              '<span>Step-by-step guide: download the practice image, write the USB drive and boot it</span></a>')
    env = facts([("Operating system", f'{ext(MARATONA_LINUX_FEATURES, "Maratona Linux 24.04")} (official contest system)'),
                 ("Memory (RAM)", ram), ("Keyboard layout", keyboard)])
    return (f'<h3>Computing environment</h3>{env}<div class="cards">{cards}</div>'
            '<p><strong>Teams can test the image that will be used in the contest.</strong> The practice image boots the same '
            'environment as the contest (Maratona Linux, from a USB drive), with one difference: it has free access to the internet, '
            'while on contest day the firewall allows only the contest systems. Testing lets teams learn the editors and tools and find '
            'hardware problems while there is still time to fix them. '
            f'See {ext(MARATONA_LINUX_TEST, "How to Test the Competition System")}.</p>')


def page_lar2026():
    p = Page("regionals/lar2026", "LAR2026", "icpc.latam->regionals(LAR2026)", "")
    live = stream_block(p, "Brasil", [("Live on the Maratona SBC channel", "https://www.youtube.com/@MaratonaSBC/")],
                        "https://www.youtube.com/@MaratonaSBC/", "Brazil")
    p.body = (
        intro("The 2026 ICPC Latin America Regionals will be held on <strong>November 6-7, 2026</strong>; "
              "the contest is on <strong>Saturday November 7th, 2026</strong>")
        + anchors([("rules", "Official Rules"), ("systems", "Systems"), ("teams", "Registered Teams"),
                   ("streams", "Streamings"), ("results", "Results")])
        + band("Official Rules", "rules")
        + wrap(pdf(p, RULES_2026_27, RULES_2026_27_LABEL)
               + "<p>The contest is distributed across the six regions, on the same date and time, with the same problem set. "
                 "Results are aggregated at three levels: super-region, region and country. The best teams are promoted to the "
                 f'<a href="{rel(p, "championships/lac2027")}">2027 ICPC Latin America Championship</a> in Monterrey, Mexico.</p>')
        + band("Systems", "systems") + wrap(systems_block(p, "Judging is centralized through MOJ", "At least 8 GB; varies from site to site",
                                                                       "US layout recommended; may vary from site to site"))
        + band("Registered Teams", "teams") + wrap('<p class="tba">TBA&hellip;</p>')
        + band("Streamings", "streams") + wrap(f'<div class="streams">{live}</div><p class="tba">Other regions: TBA&hellip;</p>')
        + band("Results", "results") + wrap('<p class="tba">TBD&hellip;</p>')
    )
    return p


def page_lar2025():
    p = Page("regionals/lar2025", "LAR2025", "icpc.latam->regionals(LAR2025)", "")
    teams = "".join(f'<li>{ext(f"https://icpc.global/regionals/finder/{slug}/teams", esc(n))}</li>'
                    for n, slug in teams_links("2026", "2025", True))
    yt_ = lambda x: f"https://www.youtube.com/watch?v={x}"
    streams = "".join([
        stream_block(p, "Brasil", [("Inauguración", yt_("B7HktgMUIQo")), ("Warmup", yt_("YqQec-VU5z8")),
                                   ("Real contest", yt_("TbL1dM8hvtg")), ("Clausura", yt_("I0hu5uMHq4M"))],
                     "https://www.youtube.com/@MaratonaSBC", "Brazil"),
        stream_block(p, "Caribe", [("Warmup", yt_("LR9mgTdLxvw")), ("Real contest", yt_("ULOABWyCBVo"))],
                     yt_("ULOABWyCBVo"), "Dominican Republic"),
        stream_block(p, "Chile", [("Warmup", "https://www.youtube.com/live/UYIL9V13olo"),
                                  ("Real contest", "https://www.youtube.com/live/4_-PJqRMRAc")]),
        stream_block(p, "México", [("Inauguración", yt_("wekW-IT_Ads")), ("Premiación y Clausura", yt_("IKm2do-Km50"))],
                     "https://eventos.iteso.mx/acm/", "Mexico"),
        stream_block(p, "Colombia", [("Ceremonia", "https://www.youtube.com/@poligran")]),
        stream_block(p, "Costa Rica", [("Warmup", yt_("8fdSWi07oRw")), ("Real contest", yt_("73wmh7mJ0VA"))]),
        stream_block(p, "Argentina", [("Live Streamings", yt_("cVo_ogh0de4"))]),
        stream_block(p, "Rep. Dominicana", [("Live Streamings", "https://www.youtube.com/live/FiEmN2Iqnk0")],
                     None, "Dominican Republic"),
    ])
    p.body = (
        intro("The 2025 ICPC Latin America Regionals was held on <strong>Saturday November 8th, 2025</strong>")
        + anchors([("rules", "Official Rules"), ("systems", "Systems"), ("teams", "Registered Teams"),
                   ("streams", "Streamings"), ("results", "Results")])
        + band("Official Rules", "rules") + wrap(pdf(p, "LAR2025 - Rules.pdf"))
        + band("Systems", "systems") + wrap(pdf(p, "LAR2025 - info_sheet.pdf"))
        + band("Registered Teams", "teams")
        + wrap(f'<p>Registered &amp; Accepted teams at icpc.global website:</p><ul class="links">{teams}</ul>')
        + band("Streamings", "streams") + wrap(f'<div class="streams">{streams}</div>')
        + band("Results", "results")
        + wrap(facts([("Teams on the final scoreboard", str(RESULTS["lar2025"]["teams"])),
                      ("Promoted to the Latin American Championship", str(RESULTS["lar2025"]["promoted"]))])
               + winner_block(p, "lar2025", "UNICAMP &ndash; Naim continua dentro de nós", ["&#129351; Global winner of the Regionals", "&#127894;&#65039; Promoted to the Latin American Championship"])
               + "<h3>Global top 10</h3>" + results_table(p, "lar2025")
               + "<h3>Best team of each region</h3>" + region_table(p, "lar2025")
               + report(["The Brazilian regional contest (Final Brasileira) was held in the Liberdade district of São Paulo, hosted by FECAP, "
                         "with 66 teams. Regions run the same problemset at the same time with centralized judging."], MARATONA_SRC))
    )
    return p


def page_lar2024():
    p = Page("regionals/lar2024", "LAR2024", "icpc.latam->regionals(LAR2024)", "")
    teams = "".join(f'<li>{ext(f"https://icpc.global/regionals/finder/{slug}/teams", esc(n))}</li>'
                    for n, slug in teams_links("2025", "2024", False))
    standings = "".join(
        f'<li>{ext(f"https://icpc.global/regionals/finder/{slug}/standings", "The 2024 ICPC " + esc(n) + " Finals")}</li>'
        for n, slug in [("Mexico", "Mexico-2025"), ("Central America", "Central-America-2025"),
                        ("Caribbean", "CaribFinals-2025"), ("South America-North", "South-America-North-2025"),
                        ("South America/South", "SouthAmerica-South-2025"), ("South America/Brazil", "South-America-Brazil-2025")])
    yt_ = lambda x: f"https://www.youtube.com/watch?v={x}"
    live = lambda x: f"https://www.youtube.com/live/{x}"
    s = [
        stream_block(p, "João Pessoa", [("Opening", live("3IjvnlQ387A")), ("Warmup", live("zaHee2yDRl0")),
                                         ("Real contest", yt_("KIiczEYSpOQ"))], None, "Brazil"),
        stream_block(p, "Santiago de los Caballeros", [("Youtube link", live("bUChUbI3llA"))], None, "Dominican Republic"),
        stream_block(p, "Buenos Aires", [("Youtube link", live("rTCGnrx9Dt8"))], None, "Argentina"),
        stream_block(p, "Coquimbo", [("Warmup", yt_("XMwEYQosIcc")), ("Real contest", yt_("9PRD-NJgzKs"))], None, "Chile"),
        stream_block(p, "Monterrey", [("Youtube link", live("cRITn5FGjnE"))], None, "Mexico"),
        stream_block(p, "Ciudad de Guatemala", [("Youtube link", live("rae6ePOrHKg"))], None, "Guatemala"),
        stream_block(p, "Mayagüez", [("Youtube link", live("h_VO0REMHJA"))], None, "Puerto Rico"),
        stream_block(p, "Alajuela", [("Youtube link", live("rae6ePOrHKg"))], None, "Costa Rica"),
        stream_block(p, "Tarija", [("Youtube link (not available)", None)], None, "Bolivia"),
        stream_block(p, "San Salvador", [("Youtube link", live("rae6ePOrHKg"))], None, "El Salvador"),
        stream_block(p, "Bogotá", [("Youtube link (not available)", None)], None, "Colombia"),
    ]
    p.body = (
        intro("The 2024 ICPC Latin America Regionals was held on <strong>Saturday November 9th, 2024</strong>")
        + anchors([("rules", "Official Rules"), ("systems", "Systems"), ("teams", "Registered Teams"),
                   ("streams", "Streamings"), ("results", "Official Results")])
        + band("Official Rules", "rules") + wrap(pdf(p, "ICPC Latin America Regionals Rules (2024-2025).pdf"))
        + band("Systems", "systems") + wrap(pdf(p, "ICPC LATAM Regionals 2024 - info_sheet__contest.pdf"))
        + band("Registered Teams", "teams")
        + wrap(f'<p>Registered &amp; Accepted teams at icpc.global website:</p><ul class="links">{teams}</ul>')
        + band("Streamings", "streams") + wrap(f'<div class="streams">{"".join(s)}</div>')
        + band("Official Results", "results")
        + wrap(f'<p>{ext("https://scorelatam.naquadah.com.br/latam-2024/", "Ranking at BOCA")}</p>'
               + facts([("Teams on the final scoreboard", str(RESULTS["lar2024"]["teams"]))])
               + winner_block(p, "lar2024", "USP &ndash; Faça o WM", ["&#129351; Global winner of the Regionals"])
               + "<h3>Global top 10</h3>" + results_table(p, "lar2024")
               + "<h3>Best team of each region</h3>" + region_table(p, "lar2024")
               + report(["Maratona SBC reports 524 participating teams (65 in the Brazilian final, 120 in Mexico, 46 in Central America, "
                         "23 in the Caribbean, 56 in South America/North and 219 in South America/South), 26 of them made of three women. "
                         "The Brazilian final was hosted by IFPB in João Pessoa."], MARATONA_SRC)
               + f'<p>Standings at icpc.global website:</p><ul class="links">{standings}</ul>'
               + pdf(p, "ICPC Latam Championship 2025 - Promoted Teams.pdf"))
    )
    return p


def page_lars_old():
    p = Page("regionals/lars1996-2023", "LARs1996-2023", "icpc.latam->regionals(LARs1996-2023)", "")
    hist = [(1996, "The 1996 Programming Contest South America"), (1997, "The 1997 ACM Programming Contest South America"),
            (1998, "The 1998 ACM Programming Contest South America"), (1999, "The 1999 ACM South American Regional Programming"),
            (2000, "The 2000 ACM South America Programming Contest"), (2001, "The 2001 ACM South America Programming Contest"),
            (2002, "The 2002 ACM South American Regional Programming Contest"), (2003, "The 2003 ACM South America Programming Contest")]
    caribe = "https://www.icpccaribe.org/"
    others = [
        ("CONCURSOS REGIONALES ACM-ICPC DE SUDAMÉRICA 1996-2003", "icpc-latam/concursos-regionales-acm-icpc-de-sudam%C3%A9rica-1996-2003"),
        ("CONCURSOS REGIONALES ACM-ICPC DE SUDAMÉRICA (SIN BRASIL) 2004-2007", "icpc-latam/concursos-regionales-acm-icpc-de-sudam%C3%A9rica-sin-brasil-2004-2007"),
        ("CONCURSOS REGIONALES ACM-ICPC DE SUDAMÉRICA/SUR 2008-2016", "icpc-latam/concursos-regionales-acm-icpc-de-sudam%C3%A9ricasur-2008-2016"),
        ("CONCURSOS REGIONALES ACM-ICPC DE SUDAMÉRICA/NORTE 2008-2016", "icpc-latam/concursos-regionales-acm-icpc-de-sudam%C3%A9ricanorte-2008-2016"),
        ("CONCURSOS REGIONALES ACM-ICPC DE BRASIL 2004-2016", "icpc-latam/concursos-regionales-acm-icpc-de-brasil-2004-2016"),
        ("CONCURSOS REGIONALES ACM-ICPC DE MÉXICO Y CENTROAMÉRICA 1997-2016", "icpc-latam/concursos-regionales-acm-icpc-de-m%C3%A9xico-y-centroam%C3%A9rica-1997-2016"),
        ("CONCURSOS REGIONALES [ACM-]ICPC DEL CARIBE 2009+", "icpc-caribe/podios-de-los-concursos-regionales-caribe%C3%B1os-del-icpc"),
    ]
    h = "".join(f'<li>{ext(f"https://maratona.sbc.org.br/hist/{y}/index.html", esc(t))}</li>' for y, t in hist)
    o = "".join(f'<li>{ext(caribe + u, esc(t))}</li>' for t, u in others)
    s = "".join(f'<li>{ext(f"https://scorelatam.naquadah.com.br/latam-{y}/", f"The {y} ICPC Latin America Regional Contests")}</li>'
                for y in range(2019, 2024))
    p.body = band("Official Results") + wrap(f'<ul class="links" style="columns:1">{h}{o}{s}</ul>')
    return p


def page_championships():
    p = Page("championships", "Championships", "icpc.latam->championships()", "")
    p.body = (
        anchors([("editions", "Editions"), ("countries", "Participating Countries")])
        + intro('The ICPC Latin American Championships (LAC), also known as &ldquo;Programadores de América PdA&rdquo;, is organized '
                'to be held on-site &amp; single-site, with the best 40+2 teams from the previous competition level '
                f'(&ldquo;<a href="{rel(p, "regionals")}">The Regionals</a>&rdquo;). Best teams from LAC competition will advance to the ICPC World Finals&hellip;')
        + band("Editions", "editions")
        + wrap('<ul class="editions">'
               f'<li>Edition #4 - <a href="{rel(p, "championships/lac2027")}">The 2027 ICPC Latin American Championship LAC - July 13-17, 2027</a></li>'
               f'<li>Edition #3 - <a href="{rel(p, "championships/lac2026")}">The 2026 ICPC Latin American Championship LAC - March 4-8, 2026</a></li>'
               f'<li>Edition #2 - <a href="{rel(p, "championships/lac2025")}">The 2025 ICPC Latin American Championship LAC - March 12-17, 2025</a></li>'
               f'<li>Edition #1 - <a href="{rel(p, "championships/lac2024")}">The 2024 ICPC Latin American Championship LAC - March 13-18, 2024</a></li></ul>')
        + band("Participating Countries", "countries") + wrap(countries_grid(p, CHAMP_COUNTRIES))
    )
    return p


def page_lac2027():
    p = Page("championships/lac2027", "LAC2027", "icpc.latam->championships(LAC2027)", "")
    p.body = (
        anchors([("info", "Event"), ("rules", "Official Rules"), ("systems", "Systems"), ("teams", "Qualified Teams"),
                 ("results", "Official Results")])
        + band("The 2027 ICPC Latin American Championship", "info")
        + wrap(facts([("Location", "Monterrey, Mexico"), ("Dates", "July 13-17, 2027"),
                      ("Official website", '<span class="tba">TBA&hellip;</span>')]))
        + band("Official Rules", "rules")
        + wrap(pdf(p, RULES_2026_27, RULES_2026_27_LABEL)
               + f'<p>Teams qualify through the <a href="{rel(p, "regionals/lar2026")}">2026 Regionals (LAR)</a>, held on November 7th, 2026. '
                 "Under the standard criteria 42 teams qualify (40 base slots plus 2 all-female slots); the hosts provide 38 additional slots. "
                 "In total, <strong>80 teams</strong> will qualify for the 2027 Championship.</p>")
        + band("Systems", "systems") + wrap(systems_block(p, "Judging is centralized through MOJ", "16 GB", "US layout"))
        + band("Qualified Teams", "teams") + wrap('<p class="tba">TBA&hellip;</p>')
        + band("Official Results", "results") + wrap('<p class="tba">TBD&hellip;</p>')
    )
    return p


def page_lac2026():
    p = Page("championships/lac2026", "LAC2026", "icpc.latam->championships(LAC2026)", "")
    p.body = (
        anchors([("info", "Event"), ("rules", "Official Rules"), ("teams", "Qualified Teams"), ("results", "Official Results")])
        + band("The 2026 ICPC Latin American Championship", "info")
        + wrap(facts([("Official website", ext("https://latam2026.icpc.cl/en/", "latam2026.icpc.cl")),
                      ("Organizing ICPC country", "Chile"), ("Dates", "March 4 - 8, 2026")]))
        + band("Official Rules", "rules")
        + wrap(pdf(p, "LAR2025 - Rules.pdf", "2025-2026 Rules: LAR 2025 Regionals & Promotion to the LAC 2026 Championship")
               + f'<p>The same document defines the rules of the <a href="{rel(p, "regionals/lar2025")}">2025 Regionals (LAR)</a> and the '
                 "promotion of teams to this Championship (and from it to the ICPC World Finals).</p>")
        + band("Qualified Teams", "teams")
        + wrap(f'<p>{ext("https://icpc.global/regionals/finder/Latin-America-Champ-2026/teams", "Registration list at icpc.global website")}</p>')
        + band("Official Results", "results")
        + wrap(f'<div class="result">{team_photo(p, "lac2026", 0, "UFMG team \'ooga booga\', Latin America champion 2026")}<div><h3>UFMG &ndash; ooga booga</h3><ul>'
               "<li>&#129351; Gold Medalist</li><li>&#127942; Latin America Champion</li><li>&#127942; Brazil Region Champion</li>"
               "<li>&#127894;&#65039; Qualified for the World Finals in Dubai</li><li>Problems solved: <strong>8</strong></li></ul>"
               f'<p>{ext(RESULTS["lac2026"]["source"], "Detailed results here (+ problemset)&hellip;")}</p></div></div>'
               + results_table(p, "lac2026")
               + report(["The Latin American Championship was held in Santiago, Chile. Maratona SBC reports 44 participating teams, "
                         "12 of them Brazilian; the final scoreboard lists 41 ranked teams. UFMG, which also won the first edition in "
                         "Guadalajara (2024), became two-time Latin American champion. Gold medals went to UFMG (Brazil), UP GDL (Mexico), "
                         "UNC (Argentina) and UChile (Chile)."], MARATONA_SRC))
    )
    return p


def result_block(page, img_html, name, solved, wf, extra_link):
    return (f'<div class="result">{img_html}<div><h3>{esc(name)}</h3><ul>'
            f'<li>&#129351; Gold Medalist</li><li>&#127942; Latin America Champion</li><li>&#127942; Brazil Region Champion</li>'
            f'<li>&#127894;&#65039; Qualified for the World Finals in {esc(wf)}</li><li>Problems solved: <strong>{solved}</strong></li></ul>'
            f'<p>{ext(extra_link, "Detailed results here (+ problemset)&hellip;")}</p></div></div>')


def page_lac2025():
    p = Page("championships/lac2025", "LAC2025", "icpc.latam->championships(LAC2025)", "")
    res = (f'<div class="result">{team_photo(p, "lac2025", 0, "USP team Faça o WM, Latin America champion 2025")}<div><h3>Faça o WM</h3><ul>'
           "<li>&#129351; Gold Medalist</li><li>&#127942; Latin America Champion</li><li>&#127942; Brazil Region Champion</li>"
           "<li>&#127894;&#65039; Qualified for the World Finals in Azerbaijan</li><li>Problems solved: <strong>9</strong></li></ul>"
           f'<p>{ext("https://scorelatam.naquadah.com.br/pda25/", "Detailed results here (+ problemset)&hellip;")}</p></div></div>')
    p.body = (
        anchors([("info", "Event"), ("rules", "Official Rules"), ("teams", "Qualified Teams"), ("results", "Official Results")])
        + band("The 2025 ICPC Latin American Championship", "info")
        + wrap(facts([("Hosted by", ext("https://ufba.br/", "Federal University of Bahia (UFBA)")),
                      ("Official website", ext("https://pda2025.gruproufba.com.br/", "pda2025.gruproufba.com.br")),
                      ("Organizing ICPC region", ext("https://maratona.sbc.org.br/", "Brazil")),
                      ("Dates", "March 12-17, 2025 (for ICPC Leaders)<br>March 13-17, 2025 (for Teams, including its guests)")]))
        + band("Official Rules", "rules")
        + wrap(pdf(p, "ICPC_Latin_America_Promotion_Rules_to_the_World_Finals_2024_2025.pdf"))
        + band("Qualified Teams", "teams")
        + wrap(f'<p>{ext("https://icpc.global/regionals/finder/Latin-America-Champ-2025/teams", "Registration list at icpc.global website")}</p>')
        + band("Official Results", "results")
        + wrap(res + results_table(p, "lac2025")
               + report(["The second Latin American Championship was hosted by UFBA in Salvador, Bahia. Maratona SBC reports 42 "
                         "participating teams, 13 of them Brazilian (the final scoreboard lists 40 ranked teams). The champion, USP's "
                         "&ldquo;Faça o WM&rdquo;, solved 9 problems.",
                         "At the 2024/25 ICPC World Finals in Baku, Azerbaijan (August 31 - September 5, 2025), 18 Latin American teams took part. "
                         "UFMG solved 6 problems and was the best Latin American team."], MARATONA_SRC))
    )
    return p


def page_lac2024():
    p = Page("championships/lac2024", "LAC2024", "icpc.latam->championships(LAC2024)", "")
    photo = f'<img src="{asset(p, "img/pda2024-champions.jpg")}" alt="UFMG team celebrating at PdA2024" loading="lazy">'
    res = (f'<div class="result">{photo}<div><h3>UFMG</h3><ul>'
           "<li>&#129351; Gold Medalist</li><li>&#127942; Latin America Champion</li><li>&#127942; Brazil Region Champion</li>"
           "<li>&#127894;&#65039; Qualified for the World Finals in Kazakhstan</li><li>Problems solved: <strong>8</strong></li></ul>"
           f'<p>{ext("https://scorelatam.naquadah.com.br/pda24/", "Detailed results here (+ problemset)&hellip;")}</p></div></div>')
    p.body = (
        anchors([("info", "Event"), ("rules", "Official Rules"), ("teams", "Qualified Teams"), ("results", "Official Results")])
        + band("The 2024 ICPC Latin American Championship", "info")
        + wrap(facts([("Hosted by", ext("https://www.iteso.mx/", "ITESO Universidad Jesuita de Guadalajara")),
                      ("Organizing ICPC region", ext("https://blogs.iteso.mx/acm/", "Mexico")),
                      ("Dates", "March 14-18, 2024"),
                      ("Website", ext("https://pda2024.icpcmexico.org/en/", "pda2024.icpcmexico.org/en"))]))
        + band("Official Rules", "rules") + wrap(pdf(p, "PdA2024 - Official Rules.pdf"))
        + band("Qualified Teams", "teams") + wrap(pdf(p, "PdA2024 - Teams stats.pdf"))
        + band("Official Results", "results")
        + wrap(res + results_table(p, "lac2024")
               + report(["The first Latin American Championship was held on the ITESO campus in Guadalajara, Mexico. UFMG won with 8 problems "
                         "solved and 900 penalty minutes; UBA-FCEN (&ldquo;InChaVoLa&rdquo;), also with 8 problems, was second with a penalty "
                         "just one minute higher. Brazil sent 16 teams.",
                         "At the 2023/24 ICPC World Finals in Astana, Kazakhstan (September 15-20, 2024), 18 Latin American teams took part. "
                         "UBA was the best Latin American team (17th place, 7 problems solved)."], MARATONA_SRC))
    )
    return p


RULES = [
    ("INTRODUCTION", "<p>The Latin American Masters Championship will have a duration of five (5) hours and take place on a Saturday, "
     "some weeks before of the {champ}ICPC Latin American Championship &ldquo;Programmers of America&rdquo;</a>.</p>"),
    ("TEAM COMPOSITION", "<p>The official COMPOSITION of a team will consist of three (3) contestants. One of the contestants will assume "
     "the dual role of coach and contestant.</p><p>The DESIRED COMPOSITION is the ORIGINAL COMPOSITION, meaning the three contestants of "
     "the team at the stage when they were student competitors of the ICPC. In case the ORIGINAL COMPOSITION cannot be assembled, the "
     "alternatives would be:</p><ul>"
     "<li>Teams representing an EDUCATIONAL INSTITUTION. They would be composed of former competitors who graduated from the same "
     "institution, coaches, and former coaches collaborating in the same institution, and combinations of the above.</li>"
     "<li>Teams representing an ORGANIZATION that is NOT an EDUCATIONAL INSTITUTION. The ORGANIZATION can be a TECHNOLOGY COMPANY or "
     "another type, a GOVERNMENTAL entity, or other types of organizations. The teams would be formed by former competitors, coaches, "
     "or former coaches currently collaborating in the same ORGANIZATION.</li>"
     "<li>Teams formed by members of the same FAMILY.</li></ul>"
     "<p>Exceptions to the aforementioned composition alternatives may be approved to raise the competitive level of the event.</p>"),
    ("CONTESTANTS ELIGIBILITY", "<p>The three (3) contestants must be INELIGIBLE for the current competition cycle and the following ones, "
     "according to the rules of the ICPC Regional Contests. They can be former competitors from any competition level (Preliminaries, "
     "Regionals, or World Finals) and former trainers and currently active trainers from any competition level. Exceptions may be approved.</p>"),
    ("COMPETITION FORMAT", "<p>The competition format will be ONLINE, based on the CODE OF CONDUCT adopted for ICPC competitions in Latin "
     "America during the pandemic. This code allows the three contestants of each team to participate from different locations, each "
     "using a computer. However, it is desirable for the three contestants to participate from a single location, using a single computer.</p>"),
    ("PRIZES", "<p>The Trophy for the winning team will be awarded during the {champ}ICPC Latin American Championship "
     "&ldquo;Programmers of America&rdquo;</a>.</p>"),
]


def page_masters():
    p = Page("masters", "Masters", "icpc.latam->masters()", "")
    champ = f'<a href="{rel(p, "championships")}">'
    rules = "".join(f"<h3>{t}</h3>{b.replace('{champ}', champ)}" for t, b in RULES)
    p.body = (
        anchors([("editions", "Editions"), ("rules", "Official Rules"), ("countries", "Participating Countries")])
        + intro("The Latin American Masters is organized to be held online with teams of ICPC alumni only. "
                "This competition has its origins in the ICPC Mexico region&hellip;")
        + band("Editions", "editions")
        + wrap('<ul class="editions">'
               '<li class="plain">Edition #6 - The 2025 ICPC Latin American Masters - February, 2025</li>'
               f'<li>Edition #5 - <a href="{rel(p, "masters/masters2024")}">The 2024 ICPC Latin American Masters - February 17, 2024</a></li>'
               f'<li>Edition #4 - <a href="{rel(p, "masters/masters2023")}">The 2023 ICPC Latin American Masters - October 14, 2023</a></li>'
               f'<li>Edition #3 - <a href="{rel(p, "masters/masters2022")}">The 2022 ICPC Masters Mexico - March 5, 2022</a></li>'
               f'<li>Edition #2 - <a href="{rel(p, "masters/masters2020-2021")}">ICPC Masters Mexico 2020-2021 - January 30, 2021</a></li>'
               f'<li>Edition #1 - <a href="{rel(p, "masters/masters2019")}">The ICPC Masters Mexico 2019 - September 28, 2019</a></li></ul>')
        + band("Official Rules", "rules") + wrap(f'<div class="rules">{rules}</div>')
        + band("Participating Countries", "countries") + wrap(countries_grid(p, MASTERS_COUNTRIES))
    )
    return p


def masters_page(slug, label, code, date, site_url, standings, teams, insts, countries, podium):
    p = Page(f"masters/{slug}", label, code, "")
    places = ""
    for i, (team, inst, country) in enumerate(podium, 1):
        names = {1: "First Place", 2: "Second Place", 3: "Third Place"}
        cc = flag(p, country).replace("<img", '<img class="mini"') if country in CC else ""
        places += (f'<div class="place"><div class="medal m{i}">{i}</div><h4>{names[i]}</h4>'
                   f'<div class="team">{esc(team)}</div><div class="meta">{esc(inst)}</div>'
                   f'<div class="meta" style="margin-top:8px">{cc}{esc(country)}</div></div>')
    p.body = (
        anchors([("info", "Event"), ("podium", "Podium (Top3)")])
        + band("Event", "info")
        + wrap(facts([("Organizing ICPC region", ext("https://blogs.iteso.mx/acm/", "Mexico")), ("Dates", esc(date)),
                      ("Website", ext(site_url, "Website here")),
                      ("Standings", ext(standings, "Official standings here")),
                      ("Number of teams", str(teams)), ("Number of institutions", str(insts)),
                      ("Participating countries", esc(countries))]))
        + band("Podium (Top3)", "podium") + wrap(f'<div class="podium">{places}</div>')
    )
    return p


def page_training():
    p = Page("training", "Training", "icpc.latam->training_resources()", "")

    def card(name, note, url):
        return f'<a class="card" href="{esc(url, quote=True)}" target="_blank" rel="noopener"><strong>{esc(name)}</strong><span>{esc(note)}</span></a>'

    camps = "".join([
        card("Training Camp Caribe", "started January 11, 2010", "https://campcarib.wordpress.com/"),
        card("Training Camp Argentina", "started August 5, 2010", "https://www.pc-arg.com/tc-arg"),
        card("Brazilian ICPC Summer School", "started January 16, 2012", "https://maratona.ic.unicamp.br/"),
        f'<div class="card"><strong>Training Camp Mexico</strong><span>{ext("https://tcmx.icpcmexico.org/", "2023 (Jan.)")} · '
        f'{ext("https://tcmx2023summer.icpcmexico.org/", "2023 (Summer)")} · {ext("https://www.acmmty.com/tcmx/", "2024")}</span></div>',
        card("Training Camp Colombia", "started July 11, 2016", "https://acis.org.co/portal/content/training-camp-colombia-2024"),
        card("Training Camp Medellín", "started July 4, 2023", "https://www.tcmedellin.com/"),
    ])
    longterm = "".join([
        card("Entrenamientos CCPL", "started April, 2003", "https://www.programmingleague.org/"),
        card("Entrenamientos CPC", "started October, 2022", "https://www.clubesdeprogramacioncompetitiva.com/servicios/Programacion"),
    ])
    courses = "".join([
        card("Google Classroom course", "classroom.google.com", "https://classroom.google.com/c/NTUzNDI1MjcwNTE1?cjc=oui2lvv"),
        f'<a class="card" href="{asset(p, "docs/C++ Programación Competitiva (Bolivia).pdf")}" target="_blank" rel="noopener">'
        f'<strong>C++ Programación Competitiva (Bolivia)</strong><span>PDF book · 2.5 MB</span></a>',
        card("Intro a la programación competitiva v2", "YouTube playlist · Club de Algoritmia ESCOM", "https://www.youtube.com/playlist?list=PL9wiQuRDQP0r-ks8l2XZsLw_W2jHAyjiI"),
        card("Clases C++ Basico (Introducción a la Programación Competitiva)", "YouTube playlist · Club de Programación Competitiva UMSA", "https://www.youtube.com/playlist?list=PLlxixWE2N_g67xOTBXM2Xr-AOlvw3JQuE"),
        card("Maratona Feminina de Programação", "YouTube playlist · Maratona SBC · specific videos: AULA 1, 2, 3, … 11", "https://www.youtube.com/playlist?list=PL_LXOen7bfUBq-1_dduDaibACuWJfycPR"),
        card("ICPC - Data Structures", "YouTube playlist", "https://www.youtube.com/playlist?list=PLZPnEQWVYB6hUybC9bzkaLPovS0r2iSB5"),
    ])
    judges = "".join([
        card("MOJ - Melhor Online Judge", "moj.naquadah.com.br · free training, problem management and contests (beta)", "https://moj.naquadah.com.br/"),
        card("omegaUp", "omegaup.com", "https://omegaup.com/"),
        card("Red de Programación Competitiva", "registro.redprogramacioncompetitiva.com", "https://registro.redprogramacioncompetitiva.com/contests"),
        card("beecrowd", "beecrowd.com", "https://beecrowd.com/es/"),
        card("MatCom Grader", "matcomgrader.com", "https://matcomgrader.com/"),
        card("DMOJ UCLV", "dmoj.uclv.edu.cu", "https://dmoj.uclv.edu.cu/"),
    ])
    tools = "".join([
        card("MOJ", "New contest management system of ICPC Latin America · moj.naquadah.com.br", "https://moj.naquadah.com.br/"),
        card("Maratona Linux", "github.com/maratona-linux", MARATONA_LINUX_WIKI),
        card("BOCA Online Contest Administrator", "github.com/cassiopc/boca", "https://github.com/cassiopc/boca"),
        card("ScoreLatam", "Public & detailed results of Latam Regionals", "https://scorelatam.naquadah.com.br/"),
        card("Animeitor Maratona", "Live Scoreboard to use with BOCA", "https://github.com/wuerges/maratona-animeitor-rust"),
        card("Huronos", "GNU/Linux distribution for competitive programming", "https://huronos.org/"),
        card("neoSaris", "A standing resolver", "https://neosaris.huronos.org/"),
    ])
    p.body = (
        anchors([("camps", "Training Camps"), ("longterm", "Long-term"), ("courses", "Courses & Books"),
                 ("judges", "Online Judges"), ("tools", "Contest Tools")])
        + band("Training Camps (short-term)", "camps") + wrap(f'<div class="cards">{camps}</div>')
        + band("Other Training Initiatives (long-term)", "longterm") + wrap(f'<div class="cards">{longterm}</div>')
        + band("(free) Courses & Books", "courses") + wrap(f'<div class="cards">{courses}</div>')
        + band("Online Judges", "judges") + wrap(f'<div class="cards">{judges}</div>')
        + band("Other Contest Tools", "tools") + wrap(f'<div class="cards">{tools}</div>')
    )
    return p


def page_history():
    p = Page("history", "History", "icpc.latam->history()", "")
    c = "https://www.icpccaribe.org/"
    p.body = (
        band("ICPC Latam: The roots & The heroes")
        + wrap('<ul class="links" style="columns:1">'
               f'<li>{ext("https://maratona.sbc.org.br/hist/index.html", "ICPC Latin America started in the year 1996")}</li>'
               f'<li>{ext(c + "icpc-latam/latam-champions-at-icpc-regional-contests", "Latam Champions at ICPC Regional Contests")}</li>'
               f'<li>{ext(c + "icpc-latam/latam-champions-at-icpc-world-finals", "Latam Champions at ICPC World Finals")}</li>'
               f'<li>{ext(c + "icpc-latam/latam-participations-at-icpc-world-finals", "Latam participations at ICPC World Finals")}</li>'
               f'<li>{ext(c + "icpc-caribe/breve-historia-de-cuba-en-el-acm-icpc-hasta-2008", "Breve historia de Cuba en el ACM-ICPC hasta 2008")}</li></ul>')
        + band("ICPC Latam: The stats")
        + wrap(pdf(p, "ICPC Latam stats until PdA2024.pdf"))
        + band("Latin American Championship (PdA): brief reports")
        + wrap(
            f'<p class="src">Based on the {ext(MARATONA_HIST, "Maratona SBC de Programação history")} and {ext(SCORELATAM, "ScoreLatam")}. '
            f'Full results on each edition page.</p>'
            f'<h3><a href="{rel(p, "championships/lac2026")}">2026 &ndash; Santiago, Chile</a></h3>'
            "<p>UFMG &ldquo;ooga booga&rdquo; won with 8 problems (786 penalty minutes) and became two-time Latin American champion. "
            "Gold: UFMG (BR), UP GDL (MX), UNC (AR), UChile (CL). 44 teams, 12 of them Brazilian. World Finals: Dubai.</p>"
            f'<h3><a href="{rel(p, "championships/lac2025")}">2025 &ndash; Salvador, Bahia, Brazil</a></h3>'
            "<p>Hosted by UFBA, March 13-17, 2025. USP &ldquo;Faça o WM&rdquo; won with 9 problems; UNICAMP and UNI-FC (Peru) completed the "
            "top 3. 42 teams, 13 of them Brazilian. At the World Finals in Baku UFMG was the best Latin American team (6 problems).</p>"
            f'<h3><a href="{rel(p, "championships/lac2024")}">2024 &ndash; Guadalajara, Mexico</a></h3>'
            "<p>First edition, hosted by ITESO, March 14-18, 2024. UFMG won with 8 problems and 900 minutes; UBA-FCEN &ldquo;InChaVoLa&rdquo; "
            "was second, one minute behind. At the World Finals in Astana UBA was the best Latin American team (17th place).</p>")
    )
    return p


def page_contact():
    p = Page("contact", "Contact", "icpc.latam->contact()", "")
    people = [
        ("Federico Meza", "Latin America Contests Director", "federico.meza@acm.org",
         ["Voice: +56-223-037-211", "Mobile: +56-982-333-804", "Departamento de Informática", "Universidad Técnica Federico Santa María",
          "Campus San Joaquín", "Ave. Vicuña Mackenna 3939, San Joaquín, Santiago, Chile"]),
        ("Carlos E. Ferreira", "Latin American Contests Deputy Director & South America/Brazil Regional Contest Director", "cef@ime.usp.br",
         ["Voice: (5511) 30916079", "Mobile: (5511) 998766134", "FAX: (5511) 30916134", "Instituto de Matemática e Estatística, Universidade de São Paulo",
          "Rua do Matão, 1010, 05508-090 - São Paulo - SP, Brazil"]),
        ("Dovier Antonio Ripoll Méndez", "Caribbean Regional Contest Director", "icpc.caribe@gmail.com",
         ["Voice: +1 829-853-4871", "Clubes de Programación Competitiva (CPC)", "Santiago de los Caballeros, Santiago, Dominican Republic"]),
        ("Eddy Ramírez", "Central America Regional Contest Director", "edramirez@itcr.ac.cr",
         ["Voice: +506 88431783", "Instituto Tecnológico de Costa Rica", "Sede Interuniversitaria de Alajuela, Costa Rica"]),
        ("Carlos Guillot", "Mexico Regional Contest Director", "carlosf@iteso.mx",
         ["Voice: +52(33)3669-3434 Ext. 3268", "ITESO University", "Periferico Sur 8585 Col. ITESO, Edificio T, Tercer Piso",
          "School of Electronic, Systems and Informatics", "Tlaquepaque, JAL. 45604, Mexico"]),
        ("Rodrigo Cardoso", "South America/North Regional Contest Director", "rcardoso@uniandes.edu.co",
         ["Voice: (+571) 3394949 Ext. 2871", "Depto. de Ingeniería de Sistemas y Computación", "Universidad de los Andes",
          "Cra 1 # 18A - 12, 111711 Bogotá, D.C., Colombia"]),
        ("Cristian Ruz", "South America/South Regional Contest Director", "cruz@ing.puc.cl",
         ["Voice: +56 9 5504 7048", "Depto. de Ciencia de la Computación", "Escuela de Ingeniería", "Pontificia Universidad Católica de Chile",
          "Santiago, Chile"]),
    ]
    cards = ""
    for name, role, mail, lines in people:
        initials = "".join(w[0] for w in name.replace(".", "").split()[:2]).upper()
        body = "".join(f"<p>{esc(l)}</p>" for l in lines)
        cards += (f'<div class="person"><div class="avatar" aria-hidden="true">{esc(initials)}</div><div><h3>{esc(name)}</h3>'
                  f'<div class="role">{esc(role)}</div><p><a href="mailto:{esc(mail)}">{esc(mail)}</a></p>{body}</div></div>')
    p.body = wrap(f'<div class="people">{cards}</div>')
    return p


def build_pages():
    pages = [
        page_home(), page_news_archive(), page_regionals(), page_lar2026(), page_lar2025(), page_lar2024(), page_lars_old(),
        page_championships(), page_lac2027(), page_lac2026(), page_lac2025(), page_lac2024(), page_masters(),
        masters_page("masters2024", "Masters2024", "icpc.latam->masters(2024)", "February 17, 2024",
                     "https://pda2024.icpcmexico.org/es/masters/", "https://icpc.global/regionals/finder/MMXLATAM-2024/standings",
                     22, 15, "Argentina, Bolivia, Brazil, Cuba, Dominican Republic, Mexico, Peru",
                     [("POR****DOS", "Universidad Nacional de Córdoba - FaMAF", "Argentina"),
                      ("Chilaquiles con Huevo", "Escuela Superior De Computo Instituto Politecnico Nacional", "Mexico"),
                      ("CPCoaches", "Clubes de Programación Competitiva", "Dominican Republic")]),
        masters_page("masters2023", "Masters2023", "icpc.latam->masters(2023)", "October 14, 2023",
                     "https://regional2023.icpcmexico.org/masters", "https://icpc.global/regionals/finder/MMXLATAM-2023/standings",
                     33, 21, "Argentina, Chile, Colombia, Cuba, Mexico, Peru",
                     [("GGDem", "Universidad Nacional de Córdoba - FaMAF", "Argentina"),
                      ("AMQ Team", "Pontificia Universidad Católica de Chile", "Chile"),
                      ("Team Microsoft", "Escuela Superior De Computo Instituto Politecnico Nacional", "Mexico")]),
        masters_page("masters2022", "Masters2022", "icpc.latam->masters(2022)", "March 5, 2022",
                     "https://blogs.iteso.mx/acm/2022/01/19/convocatoria-y-agenda-del-icpcmastersmx2022/",
                     "https://icpc.global/regionals/finder/ICPCMAMX-2022/standings", 12, 9, "Argentina, Bolivia, Mexico, Peru",
                     [("Rating Miserable", "Universidad Nacional de Ingeniería - FC", "Peru"),
                      ("GG Dem", "Universidad Nacional de Córdoba - FaMAF", "Argentina"),
                      ("Team Microsoft", "Escuela Superior De Computo Instituto Politecnico Nacional", "Mexico")]),
        masters_page("masters2020-2021", "Masters2020-2021", "icpc.latam->masters(2020-2021)", "January 30, 2021",
                     "https://blogs.iteso.mx/acm/2021/01/01/convocatoria-icpcmastersmx2020-2021/",
                     "https://icpc.global/regionals/finder/ICPCMAMX-2021/standings", 18, 14, "Argentina, Bolivia, Mexico, Peru",
                     [("Norman is Hunting [2019-2020]", "Escuela Superior De Computo Instituto Politecnico Nacional", "Mexico"),
                      ("Rating MiSeRable", "Universidad Nacional de Ingeniería - FC", "Peru"),
                      ("La cuconeta", "Universidad Nacional de Córdoba - FaMAF", "Argentina")]),
        masters_page("masters2019", "Masters2019", "icpc.latam->masters(2019)", "September 28, 2019",
                     "https://blogs.iteso.mx/acm/2019/05/21/convocatoria-icpc-masters-mexico/",
                     "https://icpc.global/regionals/finder/ICPCMAMX-2020/standings", 19, 10, "Costa Rica, Mexico",
                     [("Legendary Hackings Locos", "ITESM Campus Monterrey", "Mexico"),
                      ("Los Románticos", "Instituto Tecnológico Autónomo de México", "Mexico"),
                      ("Los Angeles de Charlie", "Universidad de Guanajuato - CIMAT", "Mexico")]),
        page_training(), page_history(), page_contact(),
    ]
    return pages


def render(page):
    nav = []
    for label, path, sub in NAV:
        active = " active" if (page.path == path or (path == "home" and page.path == "")
                               or (sub and page.path.startswith(path + "/"))) else ""
        subhtml = ""
        if sub:
            subhtml = '<div class="sub">' + "".join(f'<a href="{rel(page, sp)}">{esc(sl)}</a>' for sl, sp in sub) + "</div>"
        target = "" if path == "home" else path
        nav.append(f'<li><a class="top{active}" href="{rel(page, target)}">{esc(label)}</a>{subhtml}</li>')
    social = "".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in SOCIAL)
    ban_text, ban_path, ban_cta = BANNER
    title = "ICPC Latin America" if page.path == "" else f"{page.title} · ICPC Latin America"
    hero_style = ""
    if page.path in ("", "home"):
        hero_style = f' style="background-image:linear-gradient(rgba(60,45,5,.80),rgba(60,45,5,.80)),url({asset(page, "img/pda2024-champions.jpg")})"'
    canon = SITE_URL + (page.path + "/" if page.path and page.path != "home" else "")
    desc = "ICPC Latin America: Regionals, Championships, Masters, training resources and history of the International Collegiate Programming Contest in Latin America."
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc, quote=True)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ICPC Latin America">
<meta property="og:title" content="{esc(title, quote=True)}">
<meta property="og:description" content="{esc(desc, quote=True)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE_URL}assets/img/logo.png">
<link rel="icon" href="{asset(page, 'img/logo.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;0,900;1,400&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset(page, 'css/style.css')}">
</head>
<body>
<div class="announce">{esc(ban_text)} <a href="{rel(page, ban_path)}">{esc(ban_cta)}</a></div>
<header class="site-header"><div class="wrap">
<a class="brand" href="{rel(page, '')}"><img src="{asset(page, 'img/logo.png')}" alt="">icpc latin america</a>
<button class="nav-toggle" aria-label="Menu" aria-expanded="false" onclick="var n=document.getElementById('nav');var o=n.classList.toggle('open');this.setAttribute('aria-expanded',o)">&#9776;</button>
<nav id="nav" aria-label="Main"><ul>{''.join(nav)}</ul></nav>
</div></header>
<main>
<div class="hero"{hero_style}><h1>{esc(page.code)}</h1></div>
{page.body}
</main>
<footer class="site-footer"><div class="wrap">
<div class="social">{social}</div>
<small>ICPC Latin America &middot; part of the global community of the <a href="https://icpc.global/" target="_blank" rel="noopener">International Collegiate Programming Contest</a></small>
</div></footer>
</body>
</html>
"""


def main():
    pages = build_pages()
    for pg in pages:
        out = ROOT / pg.path / "index.html" if pg.path else ROOT / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(pg), encoding="utf-8")
    # The old site served the home page at both / and /home
    home = page_home("home")
    (ROOT / "home").mkdir(exist_ok=True)
    (ROOT / "home/index.html").write_text(render(home), encoding="utf-8")
    # sitemap, robots, 404 (404 uses absolute paths because it is served from any URL)
    urls = [SITE_URL] + [SITE_URL + pg.path + "/" for pg in pages if pg.path]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    links = "".join(f'<li><a href="/{path}">{esc(label)}</a></li>' for label, path, _ in NAV)
    (ROOT / "404.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<base href="/"><title>Page not found · ICPC Latin America</title>
<link rel="stylesheet" href="assets/css/style.css"></head>
<body><div class="hero"><h1>icpc.latam-&gt;not_found()</h1></div>
<main><section class="block"><div class="wrap center"><p>We could not find that page.</p><ul class="events">{links}</ul></div></section></main></body></html>
""", encoding="utf-8")
    print(f"wrote {len(pages) + 1} pages")


if __name__ == "__main__":
    main()
