"""
05_matriz_demanda.py — Matriz Demanda (distrito × tema).

Para cada par (distrito, tema): cuenta propuestas, suma de apoyos,
suma de presupuesto solicitado, % seleccionadas. La métrica principal
es **apoyos por habitante**, no nº de propuestas (más representativo).

Excluye:
  - "Toda la ciudad" (id_distrito = 0) — no permite asignación a distrito.
  - "Sin clasificar" — propuestas en ruido de HDBSCAN.

Output: data/processed/matriz_demanda.csv (largo: una fila por (distrito, tema))
        data/processed/matriz_demanda_wide.csv (ancho: distritos en filas, temas en columnas)
"""

from pathlib import Path

import pandas as pd
import json

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"


def load_population_by_distrito() -> dict[int, int]:
    """Load district population from data/processed/poblacion_distritos.csv.

    Source: Padrón municipal del Ayuntamiento de València (datos 2022).
    El portal de datos abiertos no publica esta tabla en CSV/JSON, solo en
    geometría (sin valores). Los números se han transcrito desde la página
    estadística municipal y se mantienen como dataset derivado del proyecto.
    """
    df = pd.read_csv(PROC / "poblacion_distritos.csv")
    return dict(zip(df["id_distrito"], df["poblacion"]))


def main() -> None:
    df = pd.read_csv(PROC / "decidim_tagged.csv")
    # Bring presupuesto column from raw Decidim
    raw = pd.read_csv(ROOT / "data" / "raw" / "decidim.csv", sep=";", encoding="utf-8-sig")
    raw_presup = raw[["id", "Presupuesto_euros"]].rename(columns={"Presupuesto_euros": "presupuesto_eur"})
    df = df.merge(raw_presup, on="id", how="left")
    df["presupuesto_eur"] = pd.to_numeric(df["presupuesto_eur"], errors="coerce").fillna(0)

    # Exclude noise + "Toda la ciudad" for the per-distrito matrix
    real = df[
        (df["id_distrito"] >= 1)
        & (df["id_distrito"] <= 19)
        & (df["tema"] != "Sin clasificar")
    ].copy()

    print(f"Propuestas en la matriz: {len(real)} (excluidos {len(df) - len(real)})")

    # Aggregate
    agg = (
        real.groupby(["id_distrito", "nombre_distrito", "tema_id", "tema"], as_index=False)
        .agg(
            n_propuestas=("Titulo", "count"),
            n_apoyos=("Numero_Apoyos", "sum"),
            n_seleccionadas=("Seleccionada_bool", "sum"),
            presupuesto_solicitado=("presupuesto_eur", "sum"),
        )
    )

    # Add population for per-capita normalization
    pop = load_population_by_distrito()
    agg["poblacion"] = agg["id_distrito"].map(pop)
    agg["apoyos_per_1000hab"] = (agg["n_apoyos"] / agg["poblacion"] * 1000).round(2)
    agg["propuestas_per_1000hab"] = (agg["n_propuestas"] / agg["poblacion"] * 1000).round(3)
    agg["tasa_seleccion"] = (agg["n_seleccionadas"] / agg["n_propuestas"]).round(3)

    agg = agg.sort_values(["id_distrito", "n_apoyos"], ascending=[True, False]).reset_index(drop=True)
    agg.to_csv(PROC / "matriz_demanda.csv", index=False)
    print(f"Filas matriz_demanda: {len(agg)} (19 distritos × {agg['tema'].nunique()} temas)")

    # Wide version (apoyos por 1000 hab)
    wide = agg.pivot_table(
        index=["id_distrito", "nombre_distrito", "poblacion"],
        columns="tema",
        values="apoyos_per_1000hab",
        fill_value=0,
    ).reset_index()
    wide.to_csv(PROC / "matriz_demanda_wide.csv", index=False)

    # Stats output
    print("\n=== Población por distrito (top + bottom 5) ===")
    pop_df = (
        agg[["id_distrito", "nombre_distrito", "poblacion"]]
        .drop_duplicates()
        .sort_values("poblacion", ascending=False)
    )
    for _, r in pop_df.head(5).iterrows():
        print(f"  {r['poblacion']:7,d}  {r['nombre_distrito']}")
    print("  ...")
    for _, r in pop_df.tail(5).iterrows():
        print(f"  {r['poblacion']:7,d}  {r['nombre_distrito']}")

    print("\n=== Top 10 (distrito, tema) por apoyos/1000hab ===")
    top10 = agg.sort_values("apoyos_per_1000hab", ascending=False).head(10)
    for _, r in top10.iterrows():
        print(f"  {r['apoyos_per_1000hab']:6.1f}  {r['nombre_distrito']:25} :: {r['tema']}")

    # Findings JSON for the report
    findings = {
        "n_propuestas_analizadas": int(len(real)),
        "n_distritos": int(agg["id_distrito"].nunique()),
        "n_temas": int(agg["tema"].nunique()),
        "poblacion_total": int(pop_df["poblacion"].sum()),
        "top_temas_por_apoyos": (
            real.groupby("tema")["Numero_Apoyos"].sum().sort_values(ascending=False).head(10).to_dict()
        ),
    }
    (PROC / "demanda_findings.json").write_text(
        json.dumps(findings, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
