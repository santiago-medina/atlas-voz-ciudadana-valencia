"""
01_download.py — Descarga reproducible de todos los datasets del Atlas.

Lee data/raw/MANIFEST.json y baja cada recurso a data/raw/<filename>.
Los archivos descargados están en .gitignore: cualquiera puede regenerarlos
ejecutando este script.

Uso:
    python etl/01_download.py
    python etl/01_download.py --only decidim,barrios   # subconjunto
"""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "raw" / "MANIFEST.json"
OUTDIR = ROOT / "data" / "raw"


def fetch(url: str, dest: Path, timeout: int = 120) -> int:
    req = Request(url, headers={"User-Agent": "atlas-voz-ciudadana-valencia/0.1"})
    with urlopen(req, timeout=timeout) as r, dest.open("wb") as out:
        data = r.read()
        out.write(data)
        return len(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Comma-separated dataset filenames (without extension) or roles to fetch")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    datasets = manifest["datasets"]

    if args.only:
        wanted = {w.strip() for w in args.only.split(",")}
        datasets = [d for d in datasets if d["id"] in wanted or d["role"] in wanted or Path(d["filename"]).stem in wanted]

    OUTDIR.mkdir(parents=True, exist_ok=True)

    print(f"Descargando {len(datasets)} datasets a {OUTDIR}\n")
    ok, fail = 0, 0
    for i, d in enumerate(datasets, 1):
        dest = OUTDIR / d["filename"]
        print(f"[{i:2}/{len(datasets)}] {d['id']:50} -> {d['filename']}", flush=True)
        try:
            size = fetch(d["url"], dest)
            print(f"           {size/1024:.1f} KB", flush=True)
            ok += 1
        except (URLError, HTTPError) as e:
            print(f"           FAIL: {e}", flush=True)
            fail += 1
        time.sleep(0.3)

    print(f"\nResumen: {ok} OK, {fail} FAIL")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
