"""
06_matriz_realidad.py — Matriz Realidad (distrito × indicador).

Para cada distrito, calcular indicadores objetivos de carencia/saturación a
partir de los datasets municipales. La carencia se normaliza por habitante.

Indicadores construidos:
  - equipamientos_per_1000hab          (más equipamientos = MENOS carencia)
  - centros_educativos_per_1000hab
  - bibliotecas_per_1000hab            (proxy desde equipamientos filtrado)
  - centros_mayores_per_1000hab
  - centros_juventud_per_1000hab
  - parques_per_1000hab                (count de jardines)
  - m2_verde_per_hab                   (área sumada / habitantes)
  - parkings_per_1000hab               (plazas de aparcamiento)
  - aparcabicis_per_1000hab            (plazas de aparcamiento bici)
  - km_carril_bici_per_1000hab
  - estaciones_ruido_count             (4 totales, suele estar en 0)
  - zones_zas_count                    (ZAS = zonas saturadas de ruido)
  - vulnerabilidad_global              (índice oficial 2021, 0-10)
  - vulnerabilidad_equip
  - vulnerabilidad_dem
  - vulnerabilidad_econom

Output: data/processed/matriz_realidad.csv (largo) y matriz_realidad_wide.csv (ancho)
"""

import json
import math
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"

POBLACION = pd.read_csv(PROC / "poblacion_distritos.csv")
POP = dict(zip(POBLACION["id_distrito"], POBLACION["poblacion"]))


def to_metric_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Project to UTM zone 30N (EPSG:25830) for accurate length/area measurements in Valencia."""
    return gdf.to_crs(25830)


def assign_points_to_distritos(gdf: gpd.GeoDataFrame, distritos: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    g = gdf.to_crs(4326).copy()
    if g.geom_type.iloc[0] in ("LineString", "MultiLineString", "Polygon", "MultiPolygon"):
        g["geometry"] = g.geometry.representative_point()
    return gpd.sjoin(g, distritos[["id_distrito", "geometry"]], how="left", predicate="within")


def count_per_distrito(gdf: gpd.GeoDataFrame, distritos: gpd.GeoDataFrame) -> pd.Series:
    joined = assign_points_to_distritos(gdf, distritos)
    return joined.dropna(subset=["id_distrito"]).groupby("id_distrito").size()


def sum_length_per_distrito(gdf: gpd.GeoDataFrame, distritos: gpd.GeoDataFrame) -> pd.Series:
    """Total length in meters of line features clipped to each distrito."""
    g = gdf.to_crs(4326)
    distritos_4326 = distritos[["id_distrito", "geometry"]]
    clipped = gpd.overlay(g, distritos_4326, how="intersection", keep_geom_type=False)
    clipped = to_metric_crs(clipped)
    clipped["length_m"] = clipped.geometry.length
    return clipped.groupby("id_distrito")["length_m"].sum()


def sum_area_per_distrito(gdf: gpd.GeoDataFrame, distritos: gpd.GeoDataFrame) -> pd.Series:
    g = gdf.to_crs(4326)
    distritos_4326 = distritos[["id_distrito", "geometry"]]
    clipped = gpd.overlay(g, distritos_4326, how="intersection", keep_geom_type=False)
    clipped = to_metric_crs(clipped)
    clipped["area_m2"] = clipped.geometry.area
    return clipped.groupby("id_distrito")["area_m2"].sum()


def sum_plazas(gdf: gpd.GeoDataFrame, distritos: gpd.GeoDataFrame, plaza_col: str) -> pd.Series:
    joined = assign_points_to_distritos(gdf, distritos)
    joined[plaza_col] = pd.to_numeric(joined.get(plaza_col), errors="coerce").fillna(0)
    return joined.dropna(subset=["id_distrito"]).groupby("id_distrito")[plaza_col].sum()


def vulnerabilidad_por_distrito(distritos: gpd.GeoDataFrame) -> pd.DataFrame:
    """Aggregate barrio-level vulnerability to district level by area-weighted mean."""
    v = gpd.read_file(RAW / "vulnerabilidad.geojson").to_crs(4326)
    # Join: assign each barrio to the distrito that contains its centroid
    v["centroid"] = v.geometry.representative_point()
    v_pts = v.set_geometry("centroid")
    joined = gpd.sjoin(v_pts, distritos[["id_distrito", "geometry"]], how="left", predicate="within")
    # Area-weighted mean of each index
    joined["weight"] = joined["shape_area"]
    for col in ("ind_equip", "ind_dem", "ind_econom", "ind_global"):
        joined[col] = pd.to_numeric(joined[col], errors="coerce")
    g = joined.dropna(subset=["id_distrito"]).copy()

    def w_mean(s, w):
        s = pd.to_numeric(s, errors="coerce")
        w = pd.to_numeric(w, errors="coerce").fillna(1)
        mask = s.notna()
        if mask.sum() == 0:
            return float("nan")
        return float((s[mask] * w[mask]).sum() / w[mask].sum())

    out = (
        g.groupby("id_distrito")
        .apply(
            lambda d: pd.Series(
                {
                    "ind_equip": w_mean(d["ind_equip"], d["weight"]),
                    "ind_dem": w_mean(d["ind_dem"], d["weight"]),
                    "ind_econom": w_mean(d["ind_econom"], d["weight"]),
                    "ind_global": w_mean(d["ind_global"], d["weight"]),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )
    return out


def main() -> None:
    distritos = gpd.read_file(PROC / "distritos.geojson").to_crs(4326)
    print(f"→ {len(distritos)} distritos")

    base = pd.DataFrame({"id_distrito": list(POP.keys())})
    base["nombre_distrito"] = base["id_distrito"].map(
        dict(zip(POBLACION["id_distrito"], POBLACION["nombre_distrito"]))
    )
    base["poblacion"] = base["id_distrito"].map(POP)

    print("→ Equipamientos municipales")
    eq = gpd.read_file(RAW / "equipamientos.geojson")
    base["n_equipamientos"] = base["id_distrito"].map(count_per_distrito(eq, distritos)).fillna(0).astype(int)

    print("→ Centros educativos")
    edu = gpd.read_file(RAW / "centros_educativos.geojson")
    base["n_centros_educativos"] = base["id_distrito"].map(count_per_distrito(edu, distritos)).fillna(0).astype(int)

    print("→ Recursos mayores y juventud")
    may = gpd.read_file(RAW / "mayores.geojson")
    base["n_recursos_mayores"] = base["id_distrito"].map(count_per_distrito(may, distritos)).fillna(0).astype(int)
    jov = gpd.read_file(RAW / "juventud.geojson")
    base["n_recursos_juventud"] = base["id_distrito"].map(count_per_distrito(jov, distritos)).fillna(0).astype(int)

    print("→ Espacios verdes (área m²)")
    verde = gpd.read_file(RAW / "espacios_verdes.geojson")
    base["m2_espacios_verdes"] = base["id_distrito"].map(sum_area_per_distrito(verde, distritos)).fillna(0)
    base["n_jardines"] = base["id_distrito"].map(count_per_distrito(verde, distritos)).fillna(0).astype(int)

    print("→ Parkings (plazas)")
    pk = gpd.read_file(RAW / "parkings.geojson")
    plaza_col = "plazastota" if "plazastota" in pk.columns else "plazas_total"
    base["n_plazas_parking"] = base["id_distrito"].map(sum_plazas(pk, distritos, plaza_col)).fillna(0).astype(int)

    print("→ Aparcamientos bici (plazas)")
    ab = gpd.read_file(RAW / "aparcabicis.geojson")
    base["n_plazas_aparcabici"] = base["id_distrito"].map(sum_plazas(ab, distritos, "numplazas")).fillna(0).astype(int)

    print("→ Itinerarios ciclistas (longitud)")
    ic = gpd.read_file(RAW / "itinerarios_ciclistas.geojson")
    base["m_carril_bici"] = base["id_distrito"].map(sum_length_per_distrito(ic, distritos)).fillna(0)

    print("→ Estaciones de ruido + ZAS")
    er = gpd.read_file(RAW / "estaciones_ruido.geojson")
    base["n_estaciones_ruido"] = base["id_distrito"].map(count_per_distrito(er, distritos)).fillna(0).astype(int)
    zas = gpd.read_file(RAW / "zones_zas.geojson")
    base["n_zonas_zas"] = base["id_distrito"].map(count_per_distrito(zas, distritos)).fillna(0).astype(int)

    print("→ Fallas (intensidad cultural)")
    fa = gpd.read_file(RAW / "fallas.geojson")
    base["n_fallas"] = base["id_distrito"].map(count_per_distrito(fa, distritos)).fillna(0).astype(int)

    # ---- Indicadores específicos añadidos en la fase de cruce honesto -----
    print("→ Velocidad media de calles (km/h)")
    vc = gpd.read_file(RAW / "velocidad_calles.geojson").to_crs(4326)
    vc["velocidad"] = pd.to_numeric(vc["velocidad"], errors="coerce")
    # Para cada calle, asignar al distrito que contiene su punto medio
    vc_pts = vc.copy()
    vc_pts["geometry"] = vc.geometry.representative_point()
    vc_join = gpd.sjoin(vc_pts, distritos[["id_distrito", "geometry"]], how="left", predicate="within")
    vel_media = vc_join.dropna(subset=["id_distrito", "velocidad"]).groupby("id_distrito")["velocidad"].mean().round(2)
    base["velocidad_media_kmh"] = base["id_distrito"].map(vel_media).fillna(0)

    print("→ Paneles informativos + Mupis")
    pi = gpd.read_file(RAW / "paneles_informativos.geojson")
    mp = gpd.read_file(RAW / "mupis.geojson")
    base["n_paneles_total"] = (
        base["id_distrito"].map(count_per_distrito(pi, distritos)).fillna(0).astype(int)
        + base["id_distrito"].map(count_per_distrito(mp, distritos)).fillna(0).astype(int)
    )

    print("→ Contenedores de residuos")
    cr = gpd.read_file(RAW / "contenedores_residuos.geojson")
    base["n_contenedores_residuos"] = base["id_distrito"].map(count_per_distrito(cr, distritos)).fillna(0).astype(int)

    print("→ Patrimonio urbano (BIC/BRL/CH)")
    pu = gpd.read_file(RAW / "patrimonio_urbano.geojson")
    base["n_bic"] = base["id_distrito"].map(count_per_distrito(pu, distritos)).fillna(0).astype(int)

    print("→ Paradas EMT")
    emt = gpd.read_file(RAW / "emt_paradas.geojson")
    base["n_paradas_emt"] = base["id_distrito"].map(count_per_distrito(emt, distritos)).fillna(0).astype(int)

    print("→ Fuentes de agua pública")
    fu = gpd.read_file(RAW / "fuentes_agua.geojson")
    base["n_fuentes_agua"] = base["id_distrito"].map(count_per_distrito(fu, distritos)).fillna(0).astype(int)

    print("→ Pipicanes")
    pp = gpd.read_file(RAW / "pipicans.geojson")
    base["n_pipicans"] = base["id_distrito"].map(count_per_distrito(pp, distritos)).fillna(0).astype(int)

    print("→ Juegos infantiles")
    ji = gpd.read_file(RAW / "juegos_infantiles.geojson")
    base["n_juegos_infantiles"] = base["id_distrito"].map(count_per_distrito(ji, distritos)).fillna(0).astype(int)

    print("→ Zonas de actividades")
    za = gpd.read_file(RAW / "zonas_actividades.geojson")
    base["n_zonas_actividades"] = base["id_distrito"].map(count_per_distrito(za, distritos)).fillna(0).astype(int)

    print("→ Vulnerabilidad (índice por barrio agregado por área)")
    vul = vulnerabilidad_por_distrito(distritos)
    base = base.merge(vul, on="id_distrito", how="left")

    # Per-capita normalizations
    print("→ Normalizaciones per cápita")
    for col, denom in [
        ("n_equipamientos", 1000),
        ("n_centros_educativos", 1000),
        ("n_recursos_mayores", 1000),
        ("n_recursos_juventud", 1000),
        ("n_jardines", 1000),
        ("n_plazas_parking", 1000),
        ("n_plazas_aparcabici", 1000),
        ("n_fallas", 1000),
        ("n_paneles_total", 1000),
        ("n_contenedores_residuos", 1000),
        ("n_bic", 1000),
        ("n_paradas_emt", 1000),
        ("n_fuentes_agua", 1000),
        ("n_pipicans", 1000),
        ("n_juegos_infantiles", 1000),
        ("n_zonas_actividades", 1000),
    ]:
        base[f"{col[2:]}_per_1000hab"] = (base[col] / base["poblacion"] * denom).round(3)
    base["m2_verde_per_hab"] = (base["m2_espacios_verdes"] / base["poblacion"]).round(2)
    base["m_carril_bici_per_1000hab"] = (base["m_carril_bici"] / base["poblacion"] * 1000).round(1)

    base = base.sort_values("id_distrito").reset_index(drop=True)
    base.to_csv(PROC / "matriz_realidad.csv", index=False)
    print(f"\nFilas matriz_realidad: {len(base)} distritos × {len(base.columns)} indicadores")

    # Print key readings
    print("\n=== Indicadores per cápita más significativos ===")
    print("\nm² de verde por habitante (top 5 + bottom 5):")
    sorted_v = base.sort_values("m2_verde_per_hab", ascending=False)
    for _, r in pd.concat([sorted_v.head(5), sorted_v.tail(5)]).iterrows():
        print(f"  {r['m2_verde_per_hab']:7.1f}  {r['nombre_distrito']}")

    print("\nMetros de carril bici por 1.000 hab (top 5 + bottom 5):")
    sorted_b = base.sort_values("m_carril_bici_per_1000hab", ascending=False)
    for _, r in pd.concat([sorted_b.head(5), sorted_b.tail(5)]).iterrows():
        print(f"  {r['m_carril_bici_per_1000hab']:7.1f}  {r['nombre_distrito']}")

    print("\nÍndice global de vulnerabilidad (mayor = más vulnerable):")
    sorted_iv = base.sort_values("ind_global", ascending=False)
    for _, r in sorted_iv.head(10).iterrows():
        print(f"  {r['ind_global']:5.2f}  {r['nombre_distrito']}")


if __name__ == "__main__":
    main()
