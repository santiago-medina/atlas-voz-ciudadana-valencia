"""
02_load_and_normalize.py — Carga todos los datasets, normaliza nombres
y asigna cada punto a su distrito mediante join espacial.

Output: data/processed/
  - distritos.geojson  (19 distritos, EPSG:4326, con nombre y código normalizados)
  - decidim.csv        (5.795 propuestas con id_distrito y nombre_distrito resueltos)
  - poi_<role>.csv     (un CSV por dataset de puntos, con id_distrito asignado)
  - load_report.json   (resumen de filas, % asignación, distritos sin features, etc.)
"""

import json
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape
from unidecode import unidecode

# Canonical mapping of distrito id (1-19) → canonical name.
# Source: empirical cross-tab of Decidim's Codigo_Ambito_Referencia × Ambito_Referencia.
CODIGO_TO_NOMBRE: dict[int, str] = {
    1: "Ciutat Vella",
    2: "l'Eixample",
    3: "Extramurs",
    4: "Campanar",
    5: "la Saïdia",
    6: "el Pla del Real",
    7: "l'Olivereta",
    8: "Patraix",
    9: "Jesús",
    10: "Quatre Carreres",
    11: "Poblats Marítims",
    12: "Camins al Grau",
    13: "Algirós",
    14: "Benimaclet",
    15: "Rascanya",
    16: "Benicalap",
    17: "Pobles del Nord",
    18: "Pobles de l'Oest",
    19: "Pobles del Sud",
    20: "No consta",
}

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slug(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unidecode(s.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def normalize_distrito_name(name: str) -> str:
    """Canonical form for matching Decidim 'Ambito_Referencia' to distrito polygons."""
    if not isinstance(name, str):
        return ""
    s = unidecode(name.lower())
    s = re.sub(r"[\s'`´]+", " ", s)
    s = re.sub(r"^(el|la|los|las|l|els|la)\s+", "", s)
    s = s.replace("-", " ").strip()
    return s


# ---------------------------------------------------------------------------
# 1. Distritos polygon layer
# ---------------------------------------------------------------------------

def load_distritos() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(RAW / "distritos.geojson").to_crs(4326)
    gdf["id_distrito"] = gdf["coddistrit"].astype(int)
    # Some distritos (Pobles del Nord) are split across multiple polygons.
    # Dissolve so each distrito is a single MultiPolygon row.
    gdf = gdf.dissolve(by="id_distrito", as_index=False)
    gdf["nombre_distrito"] = gdf["id_distrito"].map(CODIGO_TO_NOMBRE)
    gdf["match_key"] = gdf["nombre_distrito"].map(normalize_distrito_name)
    return gdf[["id_distrito", "nombre_distrito", "match_key", "geometry"]].sort_values("id_distrito").reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. Decidim — resolve Ambito_Referencia to id_distrito
# ---------------------------------------------------------------------------

def load_decidim(distritos: gpd.GeoDataFrame) -> pd.DataFrame:
    df = pd.read_csv(RAW / "decidim.csv", sep=";", encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    # Use Codigo_Ambito_Referencia as canonical key (1-20). Missing codes → 0 = global.
    def to_int(x):
        try:
            return int(float(x))
        except (TypeError, ValueError):
            return 0

    df["id_distrito"] = df["Codigo_Ambito_Referencia"].map(to_int)
    df["nombre_distrito"] = df["id_distrito"].map(
        lambda i: CODIGO_TO_NOMBRE.get(i, "Toda la ciudad") if i != 0 else "Toda la ciudad"
    )

    def status(i: int) -> str:
        if i == 0:
            return "global"
        if i == 20:
            return "missing"
        if 1 <= i <= 19:
            return "matched"
        return "unknown"

    df["match_status"] = df["id_distrito"].map(status)
    return df


# ---------------------------------------------------------------------------
# 3. POI datasets — assign each feature to a distrito by spatial join
# ---------------------------------------------------------------------------

POI_DATASETS = {
    "equipamientos": "equipamientos.geojson",
    "centros_educativos": "centros_educativos.geojson",
    "fallas": "fallas.geojson",
    "espacios_verdes": "espacios_verdes.geojson",
    "aparcabicis": "aparcabicis.geojson",
    "parkings": "parkings.geojson",
    "mayores": "mayores.geojson",
    "juventud": "juventud.geojson",
    "estaciones_ruido": "estaciones_ruido.geojson",
    "zones_zas": "zones_zas.geojson",
    "itinerarios_ciclistas": "itinerarios_ciclistas.geojson",
}


def assign_pois_to_distritos(distritos: gpd.GeoDataFrame) -> dict:
    """For each POI dataset, return per-distrito feature counts."""
    summary: dict[str, dict] = {}
    distritos_idx = distritos[["id_distrito", "nombre_distrito", "geometry"]]

    for role, fname in POI_DATASETS.items():
        path = RAW / fname
        if not path.exists():
            summary[role] = {"error": "file_missing"}
            continue
        try:
            gdf = gpd.read_file(path)
        except Exception as e:
            summary[role] = {"error": f"read_failed: {e}"}
            continue
        if gdf.empty:
            summary[role] = {"features": 0}
            continue

        gdf = gdf.to_crs(4326)
        # For lines/polygons we use representative_point()
        if gdf.geom_type.iloc[0] in ("LineString", "MultiLineString", "Polygon", "MultiPolygon"):
            gdf = gdf.copy()
            gdf["geometry"] = gdf.geometry.representative_point()

        joined = gpd.sjoin(gdf, distritos_idx, how="left", predicate="within")
        total = len(joined)
        unassigned = int(joined["id_distrito"].isna().sum())
        per_distrito = (
            joined.dropna(subset=["id_distrito"])
            .groupby(["id_distrito", "nombre_distrito"])
            .size()
            .reset_index(name="count")
        )
        summary[role] = {
            "features": total,
            "assigned": total - unassigned,
            "unassigned": unassigned,
            "per_distrito": per_distrito.to_dict(orient="records"),
        }
        per_distrito.to_csv(OUT / f"poi_{role}.csv", index=False)

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("→ Cargando distritos…")
    distritos = load_distritos()
    distritos.to_file(OUT / "distritos.geojson", driver="GeoJSON")
    print(f"   {len(distritos)} distritos cargados")

    print("→ Resolviendo ámbitos de Decidim a id_distrito…")
    decidim = load_decidim(distritos)
    decidim.to_csv(OUT / "decidim.csv", index=False)
    by_status = decidim["match_status"].value_counts().to_dict()
    print(f"   {len(decidim)} propuestas → {by_status}")

    print("→ Asignando puntos a distritos por join espacial…")
    poi_summary = assign_pois_to_distritos(distritos)
    for role, data in poi_summary.items():
        if "error" in data:
            print(f"   {role:25} {data['error']}")
        else:
            assigned = data.get("assigned", 0)
            total = data.get("features", 0)
            pct = 100 * assigned / total if total else 0
            print(f"   {role:25} {total:5} features  {pct:5.1f}% asignados")

    report = {
        "distritos": {"count": int(len(distritos))},
        "decidim": {
            "total": int(len(decidim)),
            "by_status": {k: int(v) for k, v in by_status.items()},
            "by_distrito": decidim["nombre_distrito"]
            .value_counts()
            .head(25)
            .to_dict(),
        },
        "pois": poi_summary,
    }
    (OUT / "load_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\nReporte completo en {OUT/'load_report.json'}")


if __name__ == "__main__":
    main()
