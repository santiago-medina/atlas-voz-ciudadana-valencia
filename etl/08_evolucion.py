"""
08_evolucion.py — Análisis longitudinal de las 7 ediciones (2015-2023).

Calcula:
  - Evolución de propuestas y apoyos por edición.
  - Tasa de selección por edición (¿se ejecutan más propuestas con el tiempo?).
  - Top 10 temas emergentes (mayor crecimiento ed1 vs ed7).
  - Top 10 temas decrecientes.
  - "Propuestas zombi": temas que el mismo distrito repite ediciones consecutivas
    sin ser seleccionado en ninguna.

Output: data/processed/evolucion.json (compacto, para frontend + informe)
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"


EDICION_PERIODO = {
    1: "2015-2016",
    2: "2016-2017",
    3: "2017-2018",
    4: "2018-2019",
    5: "2019-2020",
    6: "2020-2022",
    7: "2022-2023",
}


def main() -> None:
    df = pd.read_csv(PROC / "decidim_tagged.csv")
    df["Numero_Apoyos"] = pd.to_numeric(df["Numero_Apoyos"], errors="coerce").fillna(0).astype(int)

    real = df[df["tema"] != "Sin clasificar"].copy()

    # By edition
    por_edicion = (
        real.groupby("Edicion")
        .agg(
            propuestas=("Titulo", "count"),
            apoyos=("Numero_Apoyos", "sum"),
            seleccionadas=("Seleccionada_bool", "sum"),
        )
        .reset_index()
    )
    por_edicion["tasa_seleccion"] = (por_edicion["seleccionadas"] / por_edicion["propuestas"]).round(3)
    por_edicion["periodo"] = por_edicion["Edicion"].map(EDICION_PERIODO)

    # Tema × edición
    tema_edicion = (
        real.groupby(["tema", "Edicion"])
        .agg(propuestas=("Titulo", "count"), apoyos=("Numero_Apoyos", "sum"))
        .reset_index()
    )
    # Pivot for "emerging vs declining" comparison
    pivot = tema_edicion.pivot(index="tema", columns="Edicion", values="propuestas").fillna(0)
    pivot["total"] = pivot.sum(axis=1)
    if 1 in pivot.columns and 7 in pivot.columns:
        pivot["crecimiento"] = pivot[7] - pivot[1]
        pivot["ratio_7_1"] = (pivot[7] / pivot[1].replace(0, 1)).round(2)
    pivot = pivot.sort_values("crecimiento", ascending=False)

    print("=== Por edición ===")
    print(por_edicion.to_string(index=False))

    print("\n=== Top 10 temas emergentes (ed7 - ed1) ===")
    for tema, row in pivot.head(10).iterrows():
        print(f"  {int(row[1]):>4} → {int(row[7]):>4}  Δ={int(row['crecimiento']):+5}   {tema}")

    print("\n=== Top 10 temas decrecientes ===")
    for tema, row in pivot.tail(10).iloc[::-1].iterrows():
        print(f"  {int(row[1]):>4} → {int(row[7]):>4}  Δ={int(row['crecimiento']):+5}   {tema}")

    # Persistent un-selected pairs (distrito, tema) — at least 4 editions with proposals, never selected
    grp = (
        real[(real["id_distrito"] >= 1) & (real["id_distrito"] <= 19)]
        .groupby(["id_distrito", "nombre_distrito", "tema"])
        .agg(
            ediciones=("Edicion", "nunique"),
            propuestas=("Titulo", "count"),
            apoyos=("Numero_Apoyos", "sum"),
            seleccionadas=("Seleccionada_bool", "sum"),
        )
        .reset_index()
    )
    zombis = grp[(grp["ediciones"] >= 4) & (grp["seleccionadas"] == 0)].sort_values(
        ["ediciones", "apoyos"], ascending=[False, False]
    )

    print(f"\n=== 'Demandas zombi' (≥4 ediciones, 0 seleccionadas): {len(zombis)} pares ===")
    for _, r in zombis.head(15).iterrows():
        print(
            f"  ed={int(r['ediciones'])}  prop={int(r['propuestas']):3}  apoyos={int(r['apoyos']):4}   "
            f"{r['nombre_distrito']:22} :: {r['tema']}"
        )

    out = {
        "por_edicion": por_edicion.to_dict(orient="records"),
        "tema_por_edicion": tema_edicion.to_dict(orient="records"),
        "emergentes_top10": [
            {"tema": t, "ed1": int(row[1]), "ed7": int(row[7]), "crecimiento": int(row["crecimiento"])}
            for t, row in pivot.head(10).iterrows()
        ],
        "decrecientes_top10": [
            {"tema": t, "ed1": int(row[1]), "ed7": int(row[7]), "crecimiento": int(row["crecimiento"])}
            for t, row in pivot.tail(10).iloc[::-1].iterrows()
        ],
        "demandas_zombi": [
            {
                "id_distrito": int(r["id_distrito"]),
                "nombre_distrito": r["nombre_distrito"],
                "tema": r["tema"],
                "ediciones": int(r["ediciones"]),
                "propuestas": int(r["propuestas"]),
                "apoyos": int(r["apoyos"]),
            }
            for _, r in zombis.iterrows()
        ],
    }
    (PROC / "evolucion.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado: evolucion.json  ({sum(len(v) if isinstance(v, list) else 1 for v in out.values())} elementos top-level)")


if __name__ == "__main__":
    main()
