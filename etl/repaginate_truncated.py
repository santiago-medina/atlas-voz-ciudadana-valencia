"""
repaginate_truncated.py — Re-bajar datasets de ArcGIS truncados a 2000.

Los endpoints de geoportal.valencia.es devuelven máximo 2000 features por
llamada. Si el dataset tiene más, hay que iterar con resultOffset.
"""

import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# Datasets observed at exactly 2000 features → likely truncated.
TARGETS = [
    "equipamientos.geojson",
    "aparcabicis.geojson",
    "velocidad_calles.geojson",
    "contenedores_residuos.geojson",
]
PAGE = 1000  # Conservative below the typical 2000 maxRecordCount.


def fetch_page(base_url: str, offset: int) -> dict:
    parsed = urlparse(base_url)
    q = parse_qs(parsed.query)
    flat = {k: v[0] for k, v in q.items()}
    flat["resultOffset"] = str(offset)
    flat["resultRecordCount"] = str(PAGE)
    new_url = urlunparse(parsed._replace(query=urlencode(flat)))
    req = Request(new_url, headers={"User-Agent": "atlas-voz-ciudadana-valencia/0.1"})
    with urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def fetch_all(base_url: str) -> dict:
    out = None
    offset = 0
    while True:
        page = fetch_page(base_url, offset)
        feats = page.get("features", [])
        if out is None:
            out = page
            out["features"] = list(feats)
        else:
            out["features"].extend(feats)
        print(f"   offset={offset}  +{len(feats)} (total {len(out['features'])})")
        if len(feats) < PAGE:
            break
        offset += PAGE
        time.sleep(0.3)
        # safety cap
        if offset > 100_000:
            print("   safety stop at offset 100k")
            break
    return out


def main() -> None:
    manifest = json.loads((RAW / "MANIFEST.json").read_text(encoding="utf-8"))
    by_file = {d["filename"]: d for d in manifest["datasets"]}
    for target in TARGETS:
        d = by_file.get(target)
        if not d:
            print(f"SKIP {target}: not in manifest")
            continue
        print(f"→ Repaginating {target} ({d['id']})")
        data = fetch_all(d["url"])
        (RAW / target).write_text(json.dumps(data, ensure_ascii=False))
        print(f"   wrote {len(data['features'])} features")


if __name__ == "__main__":
    main()
