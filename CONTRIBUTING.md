# Contributing: regional and national websites

Every region and country can keep its own links up to date on the
[Regionals page](https://www.icpclatam.org/regionals/#websites) with a pull request.
You only edit **one small JSON file**; the page is rebuilt automatically after the merge.

| Region | File |
|---|---|
| Brazil | [`data/regions/brazil.json`](data/regions/brazil.json) |
| Mexico | [`data/regions/mexico.json`](data/regions/mexico.json) |
| Central America | [`data/regions/central-america.json`](data/regions/central-america.json) |
| Caribbean | [`data/regions/caribbean.json`](data/regions/caribbean.json) |
| South America/North | [`data/regions/south-america-north.json`](data/regions/south-america-north.json) |
| South America/South | [`data/regions/south-america-south.json`](data/regions/south-america-south.json) |

## Fastest way (no tools needed)
1. Open your region's file above and click the pencil icon (**Edit this file**), or use the **Edit this region** link on the page.
2. Make your change (see the format below) and click **Commit changes → Propose changes**. GitHub creates the pull request for you.
3. A check validates the file (valid JSON, `https://` links, known country names). A maintainer reviews and merges.

## File format
```json
{
  "region": "South America/South",
  "websites": [ { "label": "ICPC South America/South", "url": "https://example.org/" } ],
  "countries": [
    { "country": "Chile", "websites": [ { "label": "ICPC Chile", "url": "https://icpc.cl/" } ] },
    { "country": "Peru",  "websites": [] }
  ]
}
```
* `websites` (top level): the regional website(s).
* `countries`: one entry per country, with its national website(s). An empty list `[]` shows **National website: TBA**.
* To **add a country**, add an entry in `countries`. The name must be spelled as in the list of participating countries on the Regionals page
  (e.g. `Dominican Republic`, `Trinidad and Tobago`); a new country also needs a flag, so open an issue for that.
* Links must start with `https://`, point to an official or community site you maintain, and be checked and working. No tracking links or shorteners.

## Changing more than links?
Other pages are generated from `tools/build.py`. Run `python3 tools/build.py` and `python3 tools/check_links.py` locally, and commit the result
(`index.html` files are generated: never edit them by hand). See `README.md`.
