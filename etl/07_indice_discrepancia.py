"""
07_indice_discrepancia.py — Índice de discrepancia entre Demanda y Realidad.

Para cada par (distrito, tema) calculamos:

  demanda_z  = z-score (apoyos / 1.000 hab para ese tema, vs media de distritos)
  carencia_z = z-score (INVERSO del indicador de realidad, normalizado per cápita)

  discrepancia = demanda_z - carencia_z

Los temas se mapean a indicadores concretos de la matriz realidad:

  tema "Carriles bici…"        → m_carril_bici_per_1000hab (más alto = MENOS carencia)
  tema "Aparcamiento…"         → n_plazas_parking_per_1000hab + plazas_aparcabici
  tema "Parques y plazas"      → m2_verde_per_hab
  tema "Parques infantiles"    → n_jardines_per_1000hab
  tema "Centros educativos"    → n_centros_educativos_per_1000hab
  ... (ver MAPEO abajo)

Para los temas sin indicador directo de realidad, se usa el índice global
de vulnerabilidad como proxy (carencia genérica).

Cuadrantes resultantes (cruzando demanda y carencia, alrededor de la mediana):

  Demanda ALTA + Carencia ALTA  → "Demanda legítima"          (rojo)
  Demanda ALTA + Carencia BAJA  → "Sobre-demandante"          (ámbar)
  Demanda BAJA + Carencia ALTA  → "Silencioso vulnerable"     (morado) ← hallazgo clave
  Demanda BAJA + Carencia BAJA  → "Cómodo"                    (verde)
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"


# Mapeo de tema → indicador(es) de carencia.
# Si el indicador es "más es mejor" usar "less_is_worse=True" (default).
# Si el indicador es "más es peor" (ej. vulnerabilidad), usar "more_is_worse=True".
TEMA_TO_INDICADORES: dict[str, dict] = {
    "Carriles bici y movilidad ciclista": {"col": "m_carril_bici_per_1000hab", "more_is_worse": False},
    "Aceras y movilidad peatonal":        {"col": "ind_global",                "more_is_worse": True},
    "Reurbanización de calles":           {"col": "ind_global",                "more_is_worse": True},
    "Asfalto y pavimentación":            {"col": "ind_global",                "more_is_worse": True},
    "Repavimentación de calzadas":        {"col": "ind_global",                "more_is_worse": True},
    "Accesibilidad peatonal":             {"col": "ind_global",                "more_is_worse": True},
    "Aparcamiento para vehículos":        {"col": "plazas_parking_per_1000hab","more_is_worse": False},
    "Pacificación del tráfico":           {"col": "ind_global",                "more_is_worse": True},
    "Reducción de velocidad y zonas 30":  {"col": "ind_global",                "more_is_worse": True},
    "Transporte público (EMT)":           {"col": "ind_global",                "more_is_worse": True},
    "Parques y plazas":                   {"col": "m2_verde_per_hab",          "more_is_worse": False},
    "Parques infantiles":                 {"col": "jardines_per_1000hab",      "more_is_worse": False},
    "Jardines y arbolado":                {"col": "m2_verde_per_hab",          "more_is_worse": False},
    "Zonas verdes":                       {"col": "m2_verde_per_hab",          "more_is_worse": False},
    "Pipicanes y zonas caninas":          {"col": "m2_verde_per_hab",          "more_is_worse": False},
    "Centros educativos":                 {"col": "centros_educativos_per_1000hab", "more_is_worse": False},
    "Centros de salud":                   {"col": "ind_equip",                 "more_is_worse": True},
    "Bibliotecas y ludotecas":            {"col": "equipamientos_per_1000hab", "more_is_worse": False},
    "Equipamientos culturales":           {"col": "equipamientos_per_1000hab", "more_is_worse": False},
    "Centros cívicos y huertos urbanos":  {"col": "equipamientos_per_1000hab", "more_is_worse": False},
    "Instalaciones deportivas":           {"col": "equipamientos_per_1000hab", "more_is_worse": False},
    "Mobiliario urbano deportivo":        {"col": "equipamientos_per_1000hab", "more_is_worse": False},
    "Equipamientos específicos":          {"col": "equipamientos_per_1000hab", "more_is_worse": False},
    "Seguridad ciudadana":                {"col": "ind_global",                "more_is_worse": True},
    "Iluminación pública":                {"col": "ind_global",                "more_is_worse": True},
    "Recogida de residuos":               {"col": "ind_global",                "more_is_worse": True},
    "Fuentes y aseos públicos":           {"col": "equipamientos_per_1000hab", "more_is_worse": False},
    "Paneles informativos":               {"col": "ind_global",                "more_is_worse": True},
    "Reducción del ruido":                {"col": "n_zonas_zas",               "more_is_worse": True},
    "Río Turia y litoral":                {"col": "ind_global",                "more_is_worse": True},
    "Litoral y puerto":                   {"col": "ind_global",                "more_is_worse": True},
    "Rehabilitación del patrimonio":     {"col": "ind_global",                "more_is_worse": True},
    "Rehabilitación de mercados":         {"col": "ind_global",                "more_is_worse": True},
    "Puentes y vías peatonales":         {"col": "ind_global",                "more_is_worse": True},
    "Bienestar animal":                   {"col": "ind_global",                "more_is_worse": True},
    "Convivencia y mobiliario urbano":   {"col": "ind_global",                "more_is_worse": True},
    "Pedanías y barrios periféricos":    {"col": "ind_global",                "more_is_worse": True},
    "Solares y suelo disponible":         {"col": "ind_global",                "more_is_worse": True},
}


def zscore(s: pd.Series) -> pd.Series:
    mu, sd = s.mean(), s.std(ddof=0)
    return (s - mu) / sd if sd else s * 0


def main() -> None:
    demanda = pd.read_csv(PROC / "matriz_demanda.csv")
    realidad = pd.read_csv(PROC / "matriz_realidad.csv")

    real_cols_idx = realidad.set_index("id_distrito")

    rows = []
    for tema, mapping in TEMA_TO_INDICADORES.items():
        col = mapping["col"]
        more_is_worse = mapping["more_is_worse"]
        if col not in real_cols_idx.columns:
            print(f"  WARN: columna {col!r} no encontrada para tema {tema!r}")
            continue
        # Carencia: si "more is worse" tomamos el valor; si "more is better" lo invertimos
        raw = real_cols_idx[col].astype(float)
        carencia = raw if more_is_worse else -raw
        carencia_z = zscore(carencia)

        # Demanda: apoyos_per_1000hab del tema en cada distrito
        d = demanda[demanda["tema"] == tema].set_index("id_distrito")
        d = d.reindex(real_cols_idx.index, fill_value=0)
        demanda_z = zscore(d["apoyos_per_1000hab"].astype(float))

        for did in real_cols_idx.index:
            dz = float(demanda_z.loc[did])
            cz = float(carencia_z.loc[did])
            cuadrante = (
                "Demanda legítima"
                if dz >= 0 and cz >= 0
                else "Sobre-demandante"
                if dz >= 0 and cz < 0
                else "Silencioso vulnerable"
                if dz < 0 and cz >= 0
                else "Cómodo"
            )
            rows.append(
                {
                    "id_distrito": int(did),
                    "nombre_distrito": real_cols_idx.loc[did, "nombre_distrito"],
                    "tema": tema,
                    "indicador_realidad": col,
                    "valor_realidad": round(raw.loc[did], 3) if pd.notna(raw.loc[did]) else None,
                    "more_is_worse": bool(more_is_worse),
                    "n_apoyos": int(d.loc[did, "n_apoyos"]) if "n_apoyos" in d.columns else 0,
                    "n_propuestas": int(d.loc[did, "n_propuestas"]) if "n_propuestas" in d.columns else 0,
                    "apoyos_per_1000hab": float(d.loc[did, "apoyos_per_1000hab"]) if "apoyos_per_1000hab" in d.columns else 0.0,
                    "demanda_z": round(dz, 3),
                    "carencia_z": round(cz, 3),
                    "discrepancia": round(dz - cz, 3),
                    "cuadrante": cuadrante,
                }
            )

    out = pd.DataFrame(rows).sort_values(["tema", "discrepancia"]).reset_index(drop=True)
    out.to_csv(PROC / "indice_discrepancia.csv", index=False)
    print(f"Filas: {len(out)} ({out['tema'].nunique()} temas × 19 distritos)")

    print("\n=== TOP 10 'Silenciosos vulnerables' (alta carencia, baja demanda) ===")
    sv = out[out["cuadrante"] == "Silencioso vulnerable"].sort_values(
        ["carencia_z", "demanda_z"], ascending=[False, True]
    )
    for _, r in sv.head(10).iterrows():
        print(
            f"  carencia={r['carencia_z']:+.2f} demanda={r['demanda_z']:+.2f}  "
            f"{r['nombre_distrito']:22} :: {r['tema']}"
        )

    print("\n=== TOP 10 'Sobre-demandantes' (alta demanda, baja carencia) ===")
    od = out[out["cuadrante"] == "Sobre-demandante"].sort_values("demanda_z", ascending=False)
    for _, r in od.head(10).iterrows():
        print(
            f"  carencia={r['carencia_z']:+.2f} demanda={r['demanda_z']:+.2f}  "
            f"{r['nombre_distrito']:22} :: {r['tema']}"
        )

    print("\n=== TOP 10 'Demanda legítima' (alta carencia, alta demanda) ===")
    dl = out[out["cuadrante"] == "Demanda legítima"].sort_values("discrepancia", ascending=False)
    for _, r in dl.head(10).iterrows():
        print(
            f"  carencia={r['carencia_z']:+.2f} demanda={r['demanda_z']:+.2f}  "
            f"{r['nombre_distrito']:22} :: {r['tema']}"
        )

    counts = out["cuadrante"].value_counts().to_dict()
    print(f"\n=== Distribución de cuadrantes ===\n{counts}")


if __name__ == "__main__":
    main()
