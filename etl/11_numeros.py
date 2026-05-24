"""
11_numeros.py — Extrae TODOS los números clave del proyecto a un único JSON.

Cualquier número que aparezca en la web, el README, el informe o la memoria
debe salir de aquí. Si un número está en un .md fijo, es un bug.

Output: data/processed/numeros.json

Convención de nombrado:
  N_*         = conteos (enteros)
  PCT_*       = porcentajes (float 0-100, redondeados a 1 decimal)
  AVG_*       = medias
  PAR_*       = pares clave (distrito_tema_*)
  TOP_*       = listas top-N
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"


def to_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0


def to_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


def es_num(n: int | float, decimals: int = 0) -> str:
    """Formatear número con punto de miles y coma decimal estilo español."""
    if isinstance(n, float):
        s = f"{n:,.{decimals}f}"
    else:
        s = f"{n:,d}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    # -------- Carga -------------------------------------------------------
    raw = pd.read_csv(RAW / "decidim.csv", sep=";", encoding="utf-8-sig")
    raw["presupuesto"] = pd.to_numeric(raw["Presupuesto_euros"], errors="coerce").fillna(0)
    raw["apoyos"] = pd.to_numeric(raw["Numero_Apoyos"], errors="coerce").fillna(0).astype(int)
    raw["seleccionada"] = raw["Seleccionada"].eq("SI")

    tagged = pd.read_csv(PROC / "decidim_tagged.csv")
    tagged["Numero_Apoyos"] = pd.to_numeric(tagged["Numero_Apoyos"], errors="coerce").fillna(0).astype(int)
    tagged["sel"] = tagged["Seleccionada"].eq("SI")
    tagged_real = tagged[tagged["tema"] != "Sin clasificar"]

    pob = pd.read_csv(PROC / "poblacion_distritos.csv")
    pop = dict(zip(pob["id_distrito"], pob["poblacion"]))

    realidad = pd.read_csv(PROC / "matriz_realidad.csv")
    demanda = pd.read_csv(PROC / "matriz_demanda.csv")
    idx = pd.read_csv(PROC / "indice_discrepancia.csv")
    temas = pd.read_csv(PROC / "temas.csv")

    evol = json.loads((PROC / "evolucion.json").read_text(encoding="utf-8"))
    por_edicion = pd.DataFrame(evol["por_edicion"])
    zombis = evol["demandas_zombi"]

    # -------- Decidim: volumen y reparto ---------------------------------
    N_PROPUESTAS_BRUTAS = len(raw)
    N_PROPUESTAS_LEGIBLES = int((raw["Titulo"].notna() & (raw["Titulo"] != "NA")).sum())
    N_PROPUESTAS_DISTRITO = int(tagged_real["id_distrito"].between(1, 19).sum())
    N_PROPUESTAS_GLOBAL = int((tagged["id_distrito"] == 0).sum())
    N_PROPUESTAS_NO_CONSTA = int((tagged["id_distrito"] == 20).sum())
    N_APOYOS_TOTAL = int(raw["apoyos"].sum())
    N_SELECCIONADAS = int(raw["seleccionada"].sum())
    TASA_SELECCION = N_SELECCIONADAS / N_PROPUESTAS_BRUTAS if N_PROPUESTAS_BRUTAS else 0.0
    PRESUP_SOLICITADO = float(raw["presupuesto"].sum())
    PRESUP_SELECCIONADO = float(raw[raw["seleccionada"]]["presupuesto"].sum())
    PRESUP_RATIO = PRESUP_SOLICITADO / PRESUP_SELECCIONADO if PRESUP_SELECCIONADO else 0
    PCT_PRESUP_NO_SELECCIONADO = (
        (PRESUP_SOLICITADO - PRESUP_SELECCIONADO) / PRESUP_SOLICITADO * 100
    ) if PRESUP_SOLICITADO else 0

    N_EDICIONES = int(tagged["Edicion"].nunique())
    EDICIONES_PERIODO = "2015-2023"

    # -------- Temas y clusters --------------------------------------------
    N_TEMAS_DETECTADOS = int((temas["tema"] != "Sin clasificar").sum())
    N_TEMAS_CON_INDICADOR = int(idx["tema"].nunique())
    N_TEMAS_SIN_INDICADOR = N_TEMAS_DETECTADOS - N_TEMAS_CON_INDICADOR

    # -------- Distritos y población ---------------------------------------
    N_DISTRITOS = int(realidad["id_distrito"].nunique())
    POBLACION_TOTAL = int(pob["poblacion"].sum())
    DISTRITO_MAYOR_POBLACION = pob.loc[pob["poblacion"].idxmax(), "nombre_distrito"]
    POBLACION_DISTRITO_MAYOR = int(pob["poblacion"].max())
    DISTRITO_MENOR_POBLACION = pob.loc[pob["poblacion"].idxmin(), "nombre_distrito"]
    POBLACION_DISTRITO_MENOR = int(pob["poblacion"].min())

    # -------- Cuadrantes --------------------------------------------------
    cuad = idx["cuadrante"].value_counts().to_dict()
    N_PARES_TOTAL = int(idx.shape[0])
    N_PARES_SILENCIO = int(cuad.get("Silencioso vulnerable", 0))
    N_PARES_LEGITIMA = int(cuad.get("Demanda legítima", 0))
    N_PARES_SOBREDEMANDA = int(cuad.get("Sobre-demandante", 0))
    N_PARES_COMODO = int(cuad.get("Cómodo", 0))
    PCT_SILENCIO = N_PARES_SILENCIO / N_PARES_TOTAL * 100 if N_PARES_TOTAL else 0

    # -------- Realidad: extremos ------------------------------------------
    distrito_max_vul = realidad.loc[realidad["ind_global"].idxmax()]
    N_VUL_MAX = float(distrito_max_vul["ind_global"])
    DISTRITO_VUL_MAX = distrito_max_vul["nombre_distrito"]

    distrito_max_verde = realidad.loc[realidad["m2_verde_per_hab"].idxmax()]
    distrito_min_verde = realidad.loc[realidad["m2_verde_per_hab"].idxmin()]
    M2_VERDE_MAX = float(distrito_max_verde["m2_verde_per_hab"])
    M2_VERDE_MIN = float(distrito_min_verde["m2_verde_per_hab"])
    DISTRITO_VERDE_MAX = distrito_max_verde["nombre_distrito"]
    DISTRITO_VERDE_MIN = distrito_min_verde["nombre_distrito"]
    N_DISTRITOS_BAJO_9_VERDE = int((realidad["m2_verde_per_hab"] < 9).sum())

    distrito_max_vel = realidad.loc[realidad["velocidad_media_kmh"].idxmax()]
    VEL_MAX_DISTRITO = distrito_max_vel["nombre_distrito"]
    VEL_MAX_KMH = float(distrito_max_vel["velocidad_media_kmh"])

    # Campanar
    camp = realidad[realidad["nombre_distrito"] == "Campanar"].iloc[0]
    N_CAMPANAR_SILENCIOS = int(
        ((idx["nombre_distrito"] == "Campanar") & (idx["cuadrante"] == "Silencioso vulnerable")).sum()
    )
    camp_silencios = idx[(idx["nombre_distrito"] == "Campanar") & (idx["cuadrante"] == "Silencioso vulnerable")]["tema"].tolist()
    VEL_CAMPANAR = float(camp["velocidad_media_kmh"])
    # Rank de velocidad de Campanar (1 = más rápido)
    rank_vel = realidad.sort_values("velocidad_media_kmh", ascending=False).reset_index(drop=True)
    CAMPANAR_VEL_RANK = int(rank_vel[rank_vel["nombre_distrito"] == "Campanar"].index[0]) + 1

    # Pobles del Nord
    pn = realidad[realidad["nombre_distrito"] == "Pobles del Nord"].iloc[0]
    POBLES_NORD_POBLACION = int(pn["poblacion"])
    apoyos_pn = int(tagged_real[tagged_real["nombre_distrito"] == "Pobles del Nord"]["Numero_Apoyos"].sum())
    POBLES_NORD_APOYOS = apoyos_pn
    POBLES_NORD_APOYOS_POR_1000 = apoyos_pn / pn["poblacion"] * 1000
    # Media por distrito
    apoyos_por_distrito = tagged_real[
        tagged_real["id_distrito"].between(1, 19)
    ].groupby("id_distrito")["Numero_Apoyos"].sum()
    media_apoyos_1000 = sum(
        apoyos_por_distrito[i] / pop[i] * 1000 for i in apoyos_por_distrito.index
    ) / len(apoyos_por_distrito)
    MEDIA_APOYOS_1000 = float(media_apoyos_1000)
    RATIO_POBLES_NORD = POBLES_NORD_APOYOS_POR_1000 / MEDIA_APOYOS_1000

    # -------- Evolución --------------------------------------------------
    e1 = por_edicion.iloc[0]
    e7 = por_edicion.iloc[-1]
    e2 = por_edicion.iloc[1]
    N_PROPUESTAS_ED1 = int(e1["propuestas"])
    N_PROPUESTAS_ED7 = int(e7["propuestas"])
    PCT_CRECIMIENTO_PROPUESTAS = (e7["propuestas"] - e1["propuestas"]) / e1["propuestas"] * 100
    APOYOS_ED2 = int(e2["apoyos"])
    APOYOS_ED7 = int(e7["apoyos"])
    TASA_SEL_ED1 = float(e1["tasa_seleccion"]) * 100
    TASA_SEL_ED7 = float(e7["tasa_seleccion"]) * 100

    # Demandas persistentes
    N_DEMANDAS_ZOMBI = len(zombis)
    APOYOS_ZOMBI = sum(z["apoyos"] for z in zombis)
    top_zombi = sorted(zombis, key=lambda z: -z["apoyos"])[:3]

    # Caso Extramurs / carril bici
    extramurs_bici = next(
        (z for z in zombis if z["nombre_distrito"] == "Extramurs" and "bici" in z["tema"].lower()),
        None,
    )
    EXTRAMURS_BICI_PROP = int(extramurs_bici["propuestas"]) if extramurs_bici else 0
    EXTRAMURS_BICI_APOYOS = int(extramurs_bici["apoyos"]) if extramurs_bici else 0
    EXTRAMURS_BICI_EDICIONES = int(extramurs_bici["ediciones"]) if extramurs_bici else 0

    # Carril bici emergente
    bici_evol = next((t for t in evol["emergentes_top10"] if "bici" in t["tema"].lower()), None)
    BICI_ED1 = int(bici_evol["ed1"]) if bici_evol else 0
    BICI_ED7 = int(bici_evol["ed7"]) if bici_evol else 0
    BICI_CRECIMIENTO = int(bici_evol["crecimiento"]) if bici_evol else 0

    # -------- Datasets en el pipeline -------------------------------------
    manifest = json.loads((RAW / "MANIFEST.json").read_text(encoding="utf-8"))
    N_DATASETS_TOTALES = len(manifest["datasets"])
    N_DATASETS_REALIDAD = len([d for d in manifest["datasets"] if d["role"].startswith("realidad-")])

    # Conteos features (counts en cada GeoJSON ya cargado, sacamos de realidad)
    N_EQUIPAMIENTOS = int(realidad["n_equipamientos"].sum())
    N_ESPACIOS_VERDES = int(realidad["n_jardines"].sum())
    N_CENTROS_EDUCATIVOS = int(realidad["n_centros_educativos"].sum())
    N_FALLAS = int(realidad["n_fallas"].sum())
    N_PARADAS_EMT = int(realidad["n_paradas_emt"].sum())
    N_CONTENEDORES = int(realidad["n_contenedores_residuos"].sum())
    N_BIC = int(realidad["n_bic"].sum())
    N_PIPICANS = int(realidad["n_pipicans"].sum())
    N_FUENTES_AGUA = int(realidad["n_fuentes_agua"].sum())
    N_JUEGOS_INFANTILES = int(realidad["n_juegos_infantiles"].sum())
    N_PANELES = int(realidad["n_paneles_total"].sum())
    N_APARCABICIS_PLAZAS = int(realidad["n_plazas_aparcabici"].sum())
    N_PARKING_PLAZAS = int(realidad["n_plazas_parking"].sum())
    # Tramos calles con velocidad: lo leemos del raw
    try:
        vc = gpd.read_file(RAW / "velocidad_calles.geojson")
        N_TRAMOS_CALLES = len(vc)
    except Exception:
        N_TRAMOS_CALLES = 0

    # -------- Output -----------------------------------------------------
    nums: dict[str, object] = {
        # Volumen Decidim
        "N_PROPUESTAS_BRUTAS": N_PROPUESTAS_BRUTAS,
        "N_PROPUESTAS_LEGIBLES": N_PROPUESTAS_LEGIBLES,
        "N_PROPUESTAS_DISTRITO": N_PROPUESTAS_DISTRITO,
        "N_PROPUESTAS_GLOBAL": N_PROPUESTAS_GLOBAL,
        "N_PROPUESTAS_NO_CONSTA": N_PROPUESTAS_NO_CONSTA,
        "PCT_PROPUESTAS_GLOBAL": N_PROPUESTAS_GLOBAL / N_PROPUESTAS_BRUTAS * 100,
        "N_APOYOS_TOTAL": N_APOYOS_TOTAL,
        "N_SELECCIONADAS": N_SELECCIONADAS,
        "PCT_TASA_SELECCION": TASA_SELECCION * 100,
        "PRESUP_SOLICITADO": PRESUP_SOLICITADO,
        "PRESUP_SOLICITADO_MEUR": PRESUP_SOLICITADO / 1_000_000,
        "PRESUP_SELECCIONADO": PRESUP_SELECCIONADO,
        "PRESUP_SELECCIONADO_MEUR": PRESUP_SELECCIONADO / 1_000_000,
        "PRESUP_RATIO": PRESUP_RATIO,
        "PCT_PRESUP_NO_SELECCIONADO": PCT_PRESUP_NO_SELECCIONADO,
        # Ediciones
        "N_EDICIONES": N_EDICIONES,
        "EDICIONES_PERIODO": EDICIONES_PERIODO,
        "N_PROPUESTAS_ED1": N_PROPUESTAS_ED1,
        "N_PROPUESTAS_ED7": N_PROPUESTAS_ED7,
        "PCT_CRECIMIENTO_PROPUESTAS": PCT_CRECIMIENTO_PROPUESTAS,
        "APOYOS_ED2": APOYOS_ED2,
        "APOYOS_ED7": APOYOS_ED7,
        "TASA_SEL_ED1": TASA_SEL_ED1,
        "TASA_SEL_ED7": TASA_SEL_ED7,
        # Temas y clusters
        "N_TEMAS_DETECTADOS": N_TEMAS_DETECTADOS,
        "N_TEMAS_CON_INDICADOR": N_TEMAS_CON_INDICADOR,
        "N_TEMAS_SIN_INDICADOR": N_TEMAS_SIN_INDICADOR,
        # Distritos y población
        "N_DISTRITOS": N_DISTRITOS,
        "POBLACION_TOTAL": POBLACION_TOTAL,
        "DISTRITO_MAYOR_POBLACION": DISTRITO_MAYOR_POBLACION,
        "POBLACION_DISTRITO_MAYOR": POBLACION_DISTRITO_MAYOR,
        "DISTRITO_MENOR_POBLACION": DISTRITO_MENOR_POBLACION,
        "POBLACION_DISTRITO_MENOR": POBLACION_DISTRITO_MENOR,
        # Cuadrantes
        "N_PARES_TOTAL": N_PARES_TOTAL,
        "N_PARES_SILENCIO": N_PARES_SILENCIO,
        "N_PARES_LEGITIMA": N_PARES_LEGITIMA,
        "N_PARES_SOBREDEMANDA": N_PARES_SOBREDEMANDA,
        "N_PARES_COMODO": N_PARES_COMODO,
        "PCT_SILENCIO": PCT_SILENCIO,
        # Vulnerabilidad
        "N_VUL_MAX": N_VUL_MAX,
        "DISTRITO_VUL_MAX": DISTRITO_VUL_MAX,
        # Verde
        "M2_VERDE_MAX": M2_VERDE_MAX,
        "M2_VERDE_MIN": M2_VERDE_MIN,
        "DISTRITO_VERDE_MAX": DISTRITO_VERDE_MAX,
        "DISTRITO_VERDE_MIN": DISTRITO_VERDE_MIN,
        "N_DISTRITOS_BAJO_9_VERDE": N_DISTRITOS_BAJO_9_VERDE,
        "RATIO_VERDE_EXTREMOS": M2_VERDE_MAX / M2_VERDE_MIN if M2_VERDE_MIN else 0,
        # Velocidad
        "VEL_MAX_DISTRITO": VEL_MAX_DISTRITO,
        "VEL_MAX_KMH": VEL_MAX_KMH,
        # Campanar
        "N_CAMPANAR_SILENCIOS": N_CAMPANAR_SILENCIOS,
        "VEL_CAMPANAR": VEL_CAMPANAR,
        "CAMPANAR_VEL_RANK": CAMPANAR_VEL_RANK,
        "CAMPANAR_SILENCIO_TEMAS": camp_silencios,
        # Pobles del Nord
        "POBLES_NORD_POBLACION": POBLES_NORD_POBLACION,
        "POBLES_NORD_APOYOS": POBLES_NORD_APOYOS,
        "POBLES_NORD_APOYOS_POR_1000": POBLES_NORD_APOYOS_POR_1000,
        "MEDIA_APOYOS_1000": MEDIA_APOYOS_1000,
        "RATIO_POBLES_NORD": RATIO_POBLES_NORD,
        # Demandas persistentes
        "N_DEMANDAS_ZOMBI": N_DEMANDAS_ZOMBI,
        "APOYOS_ZOMBI": APOYOS_ZOMBI,
        "TOP_ZOMBI": top_zombi,
        # Bici
        "BICI_ED1": BICI_ED1,
        "BICI_ED7": BICI_ED7,
        "BICI_CRECIMIENTO": BICI_CRECIMIENTO,
        "EXTRAMURS_BICI_PROP": EXTRAMURS_BICI_PROP,
        "EXTRAMURS_BICI_APOYOS": EXTRAMURS_BICI_APOYOS,
        "EXTRAMURS_BICI_EDICIONES": EXTRAMURS_BICI_EDICIONES,
        # Datasets pipeline
        "N_DATASETS_TOTALES": N_DATASETS_TOTALES,
        "N_DATASETS_REALIDAD": N_DATASETS_REALIDAD,
        # Conteos en datasets de realidad (sumas absolutas)
        "N_EQUIPAMIENTOS": N_EQUIPAMIENTOS,
        "N_ESPACIOS_VERDES": N_ESPACIOS_VERDES,
        "N_CENTROS_EDUCATIVOS": N_CENTROS_EDUCATIVOS,
        "N_FALLAS": N_FALLAS,
        "N_PARADAS_EMT": N_PARADAS_EMT,
        "N_CONTENEDORES": N_CONTENEDORES,
        "N_BIC": N_BIC,
        "N_PIPICANS": N_PIPICANS,
        "N_FUENTES_AGUA": N_FUENTES_AGUA,
        "N_JUEGOS_INFANTILES": N_JUEGOS_INFANTILES,
        "N_PANELES": N_PANELES,
        "N_APARCABICIS_PLAZAS": N_APARCABICIS_PLAZAS,
        "N_PARKING_PLAZAS": N_PARKING_PLAZAS,
        "N_TRAMOS_CALLES": N_TRAMOS_CALLES,
    }

    (PROC / "numeros.json").write_text(
        json.dumps(nums, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )

    # Print sanity check
    print(f"→ {len(nums)} números calculados → numeros.json")
    print()
    print(f"  N_PROPUESTAS_BRUTAS:      {N_PROPUESTAS_BRUTAS:,}".replace(",", "."))
    print(f"  N_PROPUESTAS_LEGIBLES:    {N_PROPUESTAS_LEGIBLES:,}".replace(",", "."))
    print(f"  N_APOYOS_TOTAL:           {N_APOYOS_TOTAL:,}".replace(",", "."))
    print(f"  TASA_SELECCION:           {TASA_SELECCION*100:.1f}%")
    print(f"  PRESUP_SOLICITADO:        {PRESUP_SOLICITADO/1e6:.1f} M€")
    print(f"  PRESUP_SELECCIONADO:      {PRESUP_SELECCIONADO/1e6:.1f} M€")
    print(f"  RATIO presup:             {PRESUP_RATIO:.1f}×  ({PCT_PRESUP_NO_SELECCIONADO:.0f}% no seleccionado)")
    print(f"  N_TEMAS_DETECTADOS:       {N_TEMAS_DETECTADOS}")
    print(f"  N_TEMAS_CON_INDICADOR:    {N_TEMAS_CON_INDICADOR}")
    print(f"  N_PARES_TOTAL:            {N_PARES_TOTAL}")
    print(f"  PCT_SILENCIO:             {PCT_SILENCIO:.1f}%  ({N_PARES_SILENCIO}/{N_PARES_TOTAL})")
    print(f"  Campanar silencios:       {N_CAMPANAR_SILENCIOS}  (vel {VEL_CAMPANAR:.1f} km/h, rank #{CAMPANAR_VEL_RANK})")
    print(f"  Pobles Nord ratio:        {RATIO_POBLES_NORD:.2f}× la media")
    print(f"  Crecimiento ed1→ed7:      +{PCT_CRECIMIENTO_PROPUESTAS:.0f}%")
    print(f"  N_DEMANDAS_ZOMBI:         {N_DEMANDAS_ZOMBI}  ({APOYOS_ZOMBI:,} apoyos)".replace(",", "."))
    print(f"  Extramurs bici:           {EXTRAMURS_BICI_PROP} props, {EXTRAMURS_BICI_APOYOS} apoyos, {EXTRAMURS_BICI_EDICIONES} eds")
    print(f"  N_DATASETS_REALIDAD:      {N_DATASETS_REALIDAD}")


if __name__ == "__main__":
    main()
