"""
09_export_to_web.py — Exporta los outputs procesados como JSON estáticos
listos para el frontend Next.js. Salida: web/public/data/.

Archivos generados (todos <2 MB gzip):
  distritos.geojson       — polígonos + id + nombre + población
  temas.json              — listado de temas con id, nombre y métricas globales
  matriz.json             — { tema → { id_distrito → { demanda_z, carencia_z, ... } } }
  evolucion.json          — análisis longitudinal (copiado, ya está compacto)
  resumen.json            — KPIs de portada (cifras clave)
  fichas_distrito.json    — top demandas, carencias y zombi por distrito
"""

import json
import math
from pathlib import Path

import geopandas as gpd
import pandas as pd


def _clean(o):
    """Replace NaN/Inf with None so the output is valid JSON."""
    if isinstance(o, float):
        if math.isnan(o) or math.isinf(o):
            return None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o]
    return o

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
OUT = ROOT / "web" / "public" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    # 1. Distritos GeoJSON enriquecido
    distritos = gpd.read_file(PROC / "distritos.geojson").to_crs(4326)
    poblacion = pd.read_csv(PROC / "poblacion_distritos.csv")
    distritos = distritos.merge(
        poblacion[["id_distrito", "poblacion"]], on="id_distrito", how="left"
    )
    distritos["id_distrito"] = distritos["id_distrito"].astype(int)
    distritos["nombre_distrito"] = distritos["id_distrito"].map(
        dict(zip(poblacion["id_distrito"], poblacion["nombre_distrito"]))
    )
    # Simplify geometries to shrink GeoJSON
    distritos["geometry"] = distritos.geometry.simplify(0.0003, preserve_topology=True)
    out_gj = distritos[["id_distrito", "nombre_distrito", "poblacion", "geometry"]]
    out_gj.to_file(OUT / "distritos.geojson", driver="GeoJSON")
    # Also write a .json copy so it can be imported directly from TypeScript
    (OUT / "distritos.json").write_text((OUT / "distritos.geojson").read_text(encoding="utf-8"), encoding="utf-8")

    # 2. Temas
    temas = pd.read_csv(PROC / "temas.csv").sort_values("n_apoyos", ascending=False)
    temas_clean = temas[temas["tema"] != "Sin clasificar"].copy()
    temas_payload = [
        {
            "id": int(r["tema_id"]),
            "nombre": r["tema"],
            "n_propuestas": int(r["n_propuestas"]),
            "n_apoyos": int(r["n_apoyos"]),
            "n_seleccionadas": int(r["n_seleccionadas"]),
        }
        for _, r in temas_clean.iterrows()
    ]
    (OUT / "temas.json").write_text(
        json.dumps(_clean(temas_payload), ensure_ascii=False), encoding="utf-8"
    )

    # 3. Matriz: tema → distrito → métricas
    idx = pd.read_csv(PROC / "indice_discrepancia.csv")
    matriz: dict[str, dict[str, dict]] = {}
    for tema, group in idx.groupby("tema"):
        matriz[tema] = {}
        for _, r in group.iterrows():
            matriz[tema][str(int(r["id_distrito"]))] = {
                "demanda_z": float(r["demanda_z"]),
                "carencia_z": float(r["carencia_z"]),
                "discrepancia": float(r["discrepancia"]),
                "cuadrante": r["cuadrante"],
                "n_apoyos": int(r["n_apoyos"]),
                "n_propuestas": int(r["n_propuestas"]),
                "apoyos_per_1000hab": float(r["apoyos_per_1000hab"]),
                "indicador_realidad": r["indicador_realidad"],
                "valor_realidad": (
                    float(r["valor_realidad"]) if pd.notna(r["valor_realidad"]) else None
                ),
            }
    (OUT / "matriz.json").write_text(json.dumps(_clean(matriz), ensure_ascii=False), encoding="utf-8")

    # 4. Evolución
    evolucion = json.loads((PROC / "evolucion.json").read_text(encoding="utf-8"))
    (OUT / "evolucion.json").write_text(
        json.dumps(_clean(evolucion), ensure_ascii=False), encoding="utf-8"
    )

    # 5. Ficha por distrito (top demandas, top carencias, demandas zombi)
    realidad = pd.read_csv(PROC / "matriz_realidad.csv")
    demanda = pd.read_csv(PROC / "matriz_demanda.csv")
    zombi_df = pd.DataFrame(evolucion["demandas_zombi"])

    fichas = {}
    for _, drow in realidad.iterrows():
        did = int(drow["id_distrito"])
        nombre = drow["nombre_distrito"]
        # Top 5 demandas en este distrito
        d_local = demanda[demanda["id_distrito"] == did].sort_values(
            "apoyos_per_1000hab", ascending=False
        ).head(5)
        # Top 3 "silencios vulnerables" (carencia_z alto, demanda_z bajo)
        i_local = idx[idx["id_distrito"] == did]
        silencios = i_local[i_local["cuadrante"] == "Silencioso vulnerable"].sort_values(
            "carencia_z", ascending=False
        ).head(3)
        # Demandas zombi en el distrito
        zb = zombi_df[zombi_df.get("id_distrito", -1) == did] if not zombi_df.empty else pd.DataFrame()

        fichas[str(did)] = {
            "id_distrito": did,
            "nombre_distrito": nombre,
            "poblacion": int(drow["poblacion"]),
            "vulnerabilidad_global": (
                float(drow["ind_global"]) if pd.notna(drow["ind_global"]) else None
            ),
            "vulnerabilidad_equip": (
                float(drow["ind_equip"]) if pd.notna(drow["ind_equip"]) else None
            ),
            "m2_verde_per_hab": float(drow["m2_verde_per_hab"]),
            "m_carril_bici_per_1000hab": float(drow["m_carril_bici_per_1000hab"]),
            "n_equipamientos": int(drow["n_equipamientos"]),
            "n_centros_educativos": int(drow["n_centros_educativos"]),
            "n_fallas": int(drow["n_fallas"]),
            "top_demandas": [
                {"tema": r["tema"], "apoyos": int(r["n_apoyos"]), "propuestas": int(r["n_propuestas"])}
                for _, r in d_local.iterrows()
            ],
            "silencios_vulnerables": [
                {
                    "tema": r["tema"],
                    "carencia_z": float(r["carencia_z"]),
                    "demanda_z": float(r["demanda_z"]),
                }
                for _, r in silencios.iterrows()
            ],
            "demandas_zombi": [
                {
                    "tema": r["tema"],
                    "ediciones": int(r["ediciones"]),
                    "apoyos": int(r["apoyos"]),
                }
                for _, r in zb.iterrows()
            ],
        }
    (OUT / "fichas_distrito.json").write_text(
        json.dumps(_clean(fichas), ensure_ascii=False), encoding="utf-8"
    )

    # 6. Resumen para portada — todos los números desde numeros.json para
    #    garantizar consistencia con informe y memoria
    numeros_path = PROC / "numeros.json"
    nums = json.loads(numeros_path.read_text(encoding="utf-8")) if numeros_path.exists() else {}

    cuadrante_counts = idx["cuadrante"].value_counts().to_dict()
    resumen = {
        # Nombrado legacy (usado por la web) → valores oficiales de numeros.json
        "n_propuestas_total": int(nums.get("N_PROPUESTAS_LEGIBLES", 0)),
        "n_propuestas_brutas": int(nums.get("N_PROPUESTAS_BRUTAS", 0)),
        "n_propuestas_legibles": int(nums.get("N_PROPUESTAS_LEGIBLES", 0)),
        "n_propuestas_distrito": int(nums.get("N_PROPUESTAS_DISTRITO", 0)),
        "n_propuestas_global": int(nums.get("N_PROPUESTAS_GLOBAL", 0)),
        "n_apoyos_total": int(nums.get("N_APOYOS_TOTAL", 0)),
        "n_seleccionadas_total": int(nums.get("N_SELECCIONADAS", 0)),
        "n_distritos": int(nums.get("N_DISTRITOS", 19)),
        "n_temas": int(nums.get("N_TEMAS_DETECTADOS", 38)),
        "n_temas_con_indicador": int(nums.get("N_TEMAS_CON_INDICADOR", 23)),
        "n_temas_sin_indicador": int(nums.get("N_TEMAS_SIN_INDICADOR", 15)),
        "n_ediciones": int(nums.get("N_EDICIONES", 7)),
        "periodo": nums.get("EDICIONES_PERIODO", "2015-2023"),
        "tasa_seleccion_global": float(nums.get("PCT_TASA_SELECCION", 0)) / 100,
        "cuadrante_counts": {k: int(v) for k, v in cuadrante_counts.items()},
        "presupuesto_total_solicitado_eur": int(nums.get("PRESUP_SOLICITADO", 0)),
        "presupuesto_seleccionado_eur": int(nums.get("PRESUP_SELECCIONADO", 0)),
        "n_datasets_realidad": int(nums.get("N_DATASETS_REALIDAD", 22)),
        "pct_silencio": float(nums.get("PCT_SILENCIO", 0)),
    }
    (OUT / "resumen.json").write_text(
        json.dumps(_clean(resumen), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 7. Hallazgos (regenerar para web si existe el archivo)
    hallazgos_path = PROC / "hallazgos.json"
    if hallazgos_path.exists():
        (OUT / "hallazgos.json").write_text(
            hallazgos_path.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # 8. Numeros (single source of truth — la web lo importa para evitar
    # cifras a mano en JSX). Genera numeros.json si está disponible.
    numeros_path = PROC / "numeros.json"
    if numeros_path.exists():
        (OUT / "numeros.json").write_text(
            numeros_path.read_text(encoding="utf-8"), encoding="utf-8"
        )

    # Report sizes
    for f in sorted(OUT.glob("*")):
        size = f.stat().st_size / 1024
        print(f"  {f.name:30}  {size:7.1f} KB")


if __name__ == "__main__":
    main()
