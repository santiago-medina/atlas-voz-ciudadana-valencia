"""
04_label_and_merge_topics.py — Etiquetar y fusionar los 50 clusters
en ~25 temas semánticos legibles con un mapeo manual revisado.

El mapeo de cluster_id → tema canónico está al inicio del archivo y
puede editarse a mano. Cuando se ejecuta este script:
  - Reasigna cada propuesta a su tema canónico.
  - Genera data/processed/temas.csv con (tema_id, tema, n_propuestas, n_apoyos).
  - Genera data/processed/decidim_tagged.csv con la columna `tema` añadida.
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"


# ---------------------------------------------------------------------------
# Mapeo manual derivado de inspeccionar topics.csv (output de 03_topic_modeling.py)
# Cada cluster_id se asigna a un tema canónico. Clusters muy específicos a una
# calle/barrio se asignan al tema más cercano (urbanización_calles).
# ---------------------------------------------------------------------------
CLUSTER_TO_TEMA: dict[int, str] = {
    # Movilidad ciclista
    1:  "Carriles bici y movilidad ciclista",

    # Movilidad peatonal y aceras
    42: "Aceras y movilidad peatonal",
    35: "Asfalto y pavimentación",
    44: "Repavimentación de calzadas",
    41: "Reurbanización de calles",
    22: "Accesibilidad peatonal",

    # Movilidad motorizada / tráfico
    9:  "Aparcamiento para vehículos",
    24: "Reducción de velocidad y zonas 30",
    14: "Pacificación del tráfico",
    43: "Pacificación del tráfico",
    8:  "Transporte público (EMT)",

    # Espacios verdes y parques
    34: "Parques y plazas",
    37: "Parques y plazas",
    33: "Parques infantiles",
    31: "Jardines y arbolado",
    25: "Zonas verdes",
    0:  "Pipicanes y zonas caninas",
    46: "Pipicanes y zonas caninas",

    # Solares vacíos / suelo disponible
    3:  "Solares y suelo disponible",

    # Equipamientos comunitarios
    39: "Centros cívicos y huertos urbanos",
    36: "Equipamientos culturales",
    4:  "Bibliotecas y ludotecas",
    29: "Centros educativos",
    18: "Centros de salud",
    21: "Instalaciones deportivas",
    27: "Instalaciones deportivas",
    5:  "Instalaciones deportivas",
    15: "Seguridad ciudadana",
    20: "Seguridad ciudadana",

    # Servicios urbanos
    7:  "Iluminación pública",
    32: "Recogida de residuos",
    48: "Recogida de residuos",
    49: "Recogida de residuos",
    12: "Fuentes y aseos públicos",
    38: "Paneles informativos",

    # Medio ambiente / contaminación
    23: "Reducción del ruido",
    13: "Río Turia y litoral",
    11: "Litoral y puerto",

    # Patrimonio histórico / rehabilitación
    19: "Rehabilitación del patrimonio",
    17: "Rehabilitación de mercados",
    10: "Puentes y vías peatonales",

    # Animales / convivencia
    2:  "Bienestar animal",
    47: "Convivencia y mobiliario urbano",

    # Pedanías y barrios específicos (señal de demanda muy localizada)
    30: "Pedanías y barrios periféricos",
    45: "Pedanías y barrios periféricos",
    16: "Pedanías y barrios periféricos",
    26: "Pedanías y barrios periféricos",
    40: "Pedanías y barrios periféricos",

    # Otros
    6:  "Equipamientos específicos",
    28: "Mobiliario urbano deportivo",
}


def main() -> None:
    df = pd.read_csv(PROC / "decidim_topics.csv")
    topics = pd.read_csv(PROC / "topics.csv")

    df["tema"] = df["cluster_id"].map(CLUSTER_TO_TEMA).fillna("Sin clasificar")
    df.loc[df["cluster_id"] == -1, "tema"] = "Sin clasificar"

    # Numeric tema ID for the frontend
    temas_sorted = sorted(df["tema"].unique())
    tema_to_id = {t: i for i, t in enumerate(temas_sorted, start=1)}
    df["tema_id"] = df["tema"].map(tema_to_id)

    df["Numero_Apoyos"] = pd.to_numeric(df["Numero_Apoyos"], errors="coerce").fillna(0).astype(int)
    df["Seleccionada_bool"] = df["Seleccionada"].eq("SI")

    df.to_csv(PROC / "decidim_tagged.csv", index=False)

    agg = (
        df.groupby(["tema_id", "tema"], as_index=False)
        .agg(
            n_propuestas=("Titulo", "count"),
            n_apoyos=("Numero_Apoyos", "sum"),
            n_seleccionadas=("Seleccionada_bool", "sum"),
        )
        .sort_values("n_propuestas", ascending=False)
        .reset_index(drop=True)
    )
    agg.to_csv(PROC / "temas.csv", index=False)

    print(f"Total propuestas etiquetadas: {len(df)}")
    print(f"Total temas únicos: {agg['tema'].nunique()}")
    print()
    print("=== Temas por nº propuestas (top 20) ===")
    for _, r in agg.head(20).iterrows():
        print(f"  {r['n_propuestas']:5}  apoyos={int(r['n_apoyos']):6}  sel={int(r['n_seleccionadas']):3}   {r['tema']}")
    print(f"\nGuardado: temas.csv, decidim_tagged.csv")


if __name__ == "__main__":
    main()
