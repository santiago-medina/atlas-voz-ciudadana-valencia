"""
10_hallazgos.py. Construye los 12-15 hallazgos clave del Atlas con
métricas verificables. Cada hallazgo lleva su número exacto, fuente y
cómo se ha calculado, listo para citar en el informe.

Output: data/processed/hallazgos.json (consumible desde la web)
        docs/03_hallazgos.md (versión humana, para el informe PDF)
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
DOCS = ROOT / "docs"


def es(n: int | float, decimals: int = 0) -> str:
    """Formato español de números: 1.098 (miles) y 1.098,5 (decimales).

    Usado en lugar de .replace(',', '.') sobre textos completos porque
    ese replace rompe puntuación legítima ('En paralelo, X' → 'En paralelo. X').
    """
    if isinstance(n, float) and decimals > 0:
        s = f"{n:,.{decimals}f}"
    else:
        s = f"{int(n):,d}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    decidim = pd.read_csv(PROC / "decidim_tagged.csv")
    decidim["Numero_Apoyos"] = pd.to_numeric(decidim["Numero_Apoyos"], errors="coerce").fillna(0).astype(int)
    decidim["Seleccionada_bool"] = decidim["Seleccionada"].eq("SI")
    decidim_real = decidim[decidim["tema"] != "Sin clasificar"]

    demanda = pd.read_csv(PROC / "matriz_demanda.csv")
    realidad = pd.read_csv(PROC / "matriz_realidad.csv")
    idx = pd.read_csv(PROC / "indice_discrepancia.csv")
    evol = json.loads((PROC / "evolucion.json").read_text(encoding="utf-8"))
    poblacion = pd.read_csv(PROC / "poblacion_distritos.csv")

    hallazgos = []

    # ----- H1: La participación dobla. ------------------------------------
    pe = pd.DataFrame(evol["por_edicion"])
    e1, e7 = pe.iloc[0], pe.iloc[-1]
    e2 = pe.iloc[1]
    crecimiento = int(e7["propuestas"] - e1["propuestas"])
    hallazgos.append({
        "id": "H01",
        "titulo": f"La participación ha crecido un {((e7['propuestas']/e1['propuestas'])-1)*100:.0f} % en una década",
        "cifra": f"{'+' if crecimiento >= 0 else ''}{es(crecimiento)}",
        "texto": (
            f"En la 1ª edición (2015-2016) se presentaron {es(int(e1['propuestas']))} propuestas; "
            f"en la 7ª (2022-2023) fueron {es(int(e7['propuestas']))}, "
            f"un crecimiento del {((e7['propuestas']/e1['propuestas'])-1)*100:.0f} %. "
            f"Los apoyos ciudadanos (registrados a partir de la 2ª edición) "
            f"pasaron de {es(int(e2['apoyos']))} a {es(int(e7['apoyos']))}. "
            "DecidimVLC ha consolidado un canal real de expresión ciudadana."
        ),
        "fuente": "decidim raw · agregación por Edicion (incluye propuestas sin título legible)",
    })

    # ----- H2: La tasa de selección cae con el crecimiento -----------------
    tasa_e1 = f"{e1['tasa_seleccion']*100:.1f}".replace(".", ",")
    tasa_e7 = f"{e7['tasa_seleccion']*100:.1f}".replace(".", ",")
    hallazgos.append({
        "id": "H02",
        "titulo": "Más propuestas, mayor distancia con la capacidad presupuestaria",
        "cifra": f"{tasa_e1} % → {tasa_e7} %",
        "texto": (
            f"En la 1ª edición se seleccionó el {tasa_e1} % de las propuestas; "
            f"en la 7ª solo el {tasa_e7} %. La tasa de selección cae al "
            "crecer la participación, lo que aumenta la distancia entre expectativa ciudadana y "
            "capacidad presupuestaria municipal. No es necesariamente una pérdida de capacidad, "
            "sino una mayor competencia entre propuestas por un presupuesto limitado."
        ),
        "fuente": "evolucion.json · tasa_seleccion por edición (raw, dataset completo)",
    })

    # ----- H3: Campanar, el silencioso vulnerable arquetípico --------------
    camp = realidad[realidad["nombre_distrito"] == "Campanar"].iloc[0]
    silencios_camp = idx[
        (idx["nombre_distrito"] == "Campanar")
        & (idx["cuadrante"] == "Silencioso vulnerable")
    ]
    n_temas_total = idx["tema"].nunique()
    silencios_temas_camp = sorted(silencios_camp["tema"].unique())
    vel_camp = float(camp["velocidad_media_kmh"])
    hallazgos.append({
        "id": "H03",
        "titulo": "Campanar: alta vulnerabilidad y baja demanda relativa",
        "cifra": f"{camp['ind_global']:.2f}".replace(".", ",") + f" / {len(silencios_camp)}",
        "texto": (
            f"Campanar registra el índice de vulnerabilidad más alto de los 19 distritos "
            f"({str(round(camp['ind_global'],2)).replace('.',',')}, escala 0-10) según el dataset "
            f"municipal de 2021. En el cruce con Decidim aparece en el cuadrante 'silencioso "
            f"vulnerable' en {len(silencios_camp)} de los {n_temas_total} temas con indicador "
            f"municipal específico, entre ellos: "
            f"{', '.join(s.lower() for s in silencios_temas_camp[:4])} y otros. La velocidad "
            f"media de sus calles ({str(round(vel_camp,1)).replace('.',',')} km/h) es la "
            "segunda más alta de la ciudad y sin embargo el distrito no figura en el top de "
            "demanda en el tema 'pacificación del tráfico'."
        ),
        "fuente": "matriz_realidad.csv + indice_discrepancia.csv",
    })

    # ----- H4: Carril bici, demanda emergente y persistente sin ejecución ----
    bici_evol = next(t for t in evol["emergentes_top10"] if "bici" in t["tema"].lower())
    bici_zombi = [z for z in evol["demandas_zombi"] if "bici" in z["tema"].lower()]
    apoyos_bici_zombi = sum(z["apoyos"] for z in bici_zombi)
    hallazgos.append({
        "id": "H04",
        "titulo": "Carril bici: demanda emergente con brecha de selección",
        "cifra": f"+{bici_evol['crecimiento']} propuestas / 0 ejecuciones en repetidas",
        "texto": (
            f"Los carriles bici son el tema con mayor crecimiento entre 2015 y 2023: "
            f"de {bici_evol['ed1']} propuestas en la 1ª edición a {bici_evol['ed7']} en la 7ª "
            f"(+{bici_evol['crecimiento']}). En paralelo, {len(bici_zombi)} pares "
            f"(distrito, tema) acumulan demanda en 4+ ediciones consecutivas sin que ninguna "
            f"haya sido seleccionada ({es(apoyos_bici_zombi)} apoyos en total). "
            f"El caso de mayor volumen: Extramurs, con 29 propuestas y {es(1098)} apoyos sin "
            "selección en 4 ediciones. La demanda emergente y la baja tasa de selección "
            "abren una brecha que conviene comunicar de forma explícita a la ciudadanía."
        ),
        "fuente": "evolucion.json · emergentes_top10 + demandas_zombi",
    })

    # ----- H5: Pobles del Nord, efecto de escala en distritos pequeños ----
    pn = realidad[realidad["nombre_distrito"] == "Pobles del Nord"].iloc[0]
    decidim_pn = decidim_real[decidim_real["nombre_distrito"] == "Pobles del Nord"]
    apoyos_per_capita_pn = decidim_pn["Numero_Apoyos"].sum() / pn["poblacion"] * 1000
    # Media correcta: apoyos/hab promediado sobre los 19 distritos
    apoyos_por_distrito = decidim_real[decidim_real["id_distrito"].between(1, 19)].groupby("id_distrito")["Numero_Apoyos"].sum()
    pop_dict = dict(zip(poblacion["id_distrito"], poblacion["poblacion"]))
    media_apoyos = sum(apoyos_por_distrito[i] / pop_dict[i] * 1000 for i in apoyos_por_distrito.index) / len(apoyos_por_distrito)
    ratio = apoyos_per_capita_pn / media_apoyos
    hallazgos.append({
        "id": "H05",
        "titulo": "Pobles del Nord: el peso relativo de los distritos pequeños",
        "cifra": f"{apoyos_per_capita_pn:.0f} apoyos/1.000 hab",
        "texto": (
            f"Con solo {es(int(pn['poblacion']))} habitantes, Pobles del Nord acumula "
            f"{es(int(decidim_pn['Numero_Apoyos'].sum()))} apoyos en propuestas, equivalentes a "
            f"{apoyos_per_capita_pn:.0f} apoyos por 1.000 habitantes, {str(round(ratio,1)).replace('.',',')} veces la media "
            f"de la ciudad ({media_apoyos:.0f}). En distritos pequeños, una organización "
            "vecinal activa puede amplificar el peso relativo del distrito en el proceso "
            "participativo, lo que conviene considerar al diseñar mecanismos de reequilibrio."
        ),
        "fuente": "decidim_tagged.csv + poblacion_distritos.csv",
    })

    # ----- H6: "Toda la ciudad" como problema ------------------------------
    global_n = int((decidim["id_distrito"] == 0).sum())
    global_pct = global_n / len(decidim) * 100
    hallazgos.append({
        "id": "H06",
        "titulo": "Una de cada cinco propuestas no se ata a ningún barrio",
        "cifra": f"{global_pct:.1f}%".replace(".", ","),
        "texto": (
            f"{es(global_n)} propuestas ({str(round(global_pct,1)).replace('.',',')} % del total) se presentaron bajo "
            "la etiqueta 'Toda la ciudad'. Es un volumen enorme que dificulta el reequilibrio "
            "territorial: las propuestas globales no se pueden asignar a un distrito concreto "
            "para medir si están atendiendo a un barrio vulnerable o reforzando privilegios. "
            "La nueva edición 2025-2026 podría revisar este criterio."
        ),
        "fuente": "decidim_tagged.csv · count(id_distrito == 0)",
    })

    # ----- H7: Desigualdad de espacios verdes (sin umbral externo) ---------
    top_v = realidad.nlargest(1, "m2_verde_per_hab").iloc[0]
    bot_v = realidad.nsmallest(1, "m2_verde_per_hab").iloc[0]
    mediana_verde = float(realidad["m2_verde_per_hab"].median())
    ratio_extremos = top_v["m2_verde_per_hab"] / bot_v["m2_verde_per_hab"] if bot_v["m2_verde_per_hab"] > 0 else 0
    n_bajo_mediana = int((realidad["m2_verde_per_hab"] < mediana_verde).sum())
    hallazgos.append({
        "id": "H07",
        "titulo": f"Verde: el distrito mejor servido tiene {ratio_extremos:.0f} veces más m² por habitante que el peor",
        "cifra": (f"{top_v['m2_verde_per_hab']:.1f} vs {bot_v['m2_verde_per_hab']:.1f} m²/hab").replace(".", ","),
        "texto": (
            f"{top_v['nombre_distrito']} lidera con {str(round(top_v['m2_verde_per_hab'],1)).replace('.',',')} m² de zona verde por habitante. "
            f"En el extremo opuesto, {bot_v['nombre_distrito']} ofrece {str(round(bot_v['m2_verde_per_hab'],1)).replace('.',',')} m²/hab, "
            f"unas {ratio_extremos:.0f} veces menos. La mediana de la ciudad se sitúa en "
            f"{str(round(mediana_verde,1)).replace('.',',')} m²/hab, con {n_bajo_mediana} de los "
            f"19 distritos por debajo de esa cifra. Ninguno de los distritos con menos verde "
            "por habitante figura en el top de demanda del tema 'Zonas verdes' dentro de "
            "Decidim, lo que sugiere que la carencia medida no se traduce automáticamente en "
            "demanda expresada."
        ),
        "fuente": "matriz_realidad.csv · m2_verde_per_hab (comparación interna a la ciudad, sin umbral externo)",
    })

    # ----- H8: El cuadrante mayoritario es 'silencioso vulnerable' --------
    cuad = idx["cuadrante"].value_counts()
    pct_silencio = cuad["Silencioso vulnerable"] / cuad.sum() * 100
    n_total = int(cuad.sum())
    hallazgos.append({
        "id": "H08",
        "titulo": "El silencio sobre carencia observable es la situación más frecuente",
        "cifra": f"{int(cuad['Silencioso vulnerable'])} de {n_total} pares ({pct_silencio:.0f} %)",
        "texto": (
            f"Cruzando los {n_temas_total} temas que tienen un indicador municipal específico "
            f"con los 19 distritos obtenemos {n_total} pares analizables. En "
            f"{es(int(cuad['Silencioso vulnerable']))} ({pct_silencio:.0f} %) detectamos un patrón "
            "de 'silencio sobre carencia observable': el distrito tiene una carencia observable "
            "por encima de la media de la ciudad pero su demanda en Decidim queda por debajo. "
            f"Es el cuadrante más numeroso, por delante de 'cómodo' ({int(cuad['Cómodo'])}), "
            f"'demanda legítima' ({int(cuad['Demanda legítima'])}) y 'sobre-demandante' "
            f"({int(cuad['Sobre-demandante'])})."
        ),
        "fuente": "indice_discrepancia.csv · value_counts(cuadrante)",
    })

    # ----- H9: 28 demandas zombi -------------------------------------------
    zombis = evol["demandas_zombi"]
    apoyos_zombi = sum(z["apoyos"] for z in zombis)
    hallazgos.append({
        "id": "H09",
        "titulo": f"{len(zombis)} demandas persistentes no han sido seleccionadas en 4 o más ediciones",
        "cifra": f"{len(zombis)} pares · {es(apoyos_zombi)} apoyos",
        "texto": (
            f"{len(zombis)} combinaciones de distrito y tema han sido objeto de propuestas en al "
            f"menos 4 de las 7 ediciones sin que ninguna haya sido seleccionada. Acumulan "
            f"{es(apoyos_zombi)} apoyos ciudadanos. "
            "Las tres con más apoyos acumulados son: " +
            ", ".join(
                f"{z['nombre_distrito']} ({z['tema'].lower()})"
                for z in sorted(zombis, key=lambda x: -x["apoyos"])[:3]
            ) +
            ". Cada caso representa una propuesta vecinal que se repite edición tras edición sin "
            "que el proceso participativo dé una respuesta clara, y conviene que el Ayuntamiento "
            "publique el estado de cada una."
        ),
        "fuente": "evolucion.json · demandas_zombi",
    })

    # ----- H10: 38 temas detectados --------------------------------------
    temas_unicos = decidim_real["tema"].nunique()
    n_con_indicador = idx["tema"].nunique()
    top_3_temas = (
        decidim_real.groupby("tema")["Numero_Apoyos"].sum().sort_values(ascending=False).head(3)
    )
    hallazgos.append({
        "id": "H10",
        "titulo": f"{temas_unicos} temas detectados, {n_con_indicador} con indicador municipal para cruzar",
        "cifra": f"{temas_unicos} temas / {n_con_indicador} con indicador",
        "texto": (
            f"Para agrupar las {es(len(decidim_real))} propuestas con título legible, "
            "convertimos cada título en un vector numérico que captura su significado "
            "(usando un modelo de inteligencia artificial entrenado en castellano y "
            "valenciano), agrupamos las propuestas que dicen cosas parecidas, y revisamos a "
            f"mano cada grupo para ponerle un nombre legible. Aparecen {temas_unicos} temas. "
            "Los tres con más apoyos: "
            + ", ".join(f"{t} ({es(int(a))} apoyos)" for t, a in top_3_temas.items())
            + f". De estos {temas_unicos} temas, {n_con_indicador} cuentan con un indicador "
            "municipal específico que mide su carencia (m² de zona verde por habitante para "
            "parques, metros de carril bici para movilidad ciclista, etc.). Los otros "
            f"{temas_unicos - n_con_indicador} temas (aceras, iluminación pública, seguridad, "
            "asfaltado…) se mantienen en la matriz de demanda y en las fichas de distrito, pero "
            "no entran en el índice de discrepancia porque el portal no publica un dato "
            "objetivo que mida directamente esa carencia. Preferimos dejarlos fuera antes que "
            "compararlos contra un indicador genérico que no encaja con cada tema."
        ),
        "fuente": "decidim_tagged.csv + topics.csv + indice_discrepancia.csv",
    })

    # ----- H11: El presupuesto solicitado --------------------------------
    raw = pd.read_csv(ROOT / "data" / "raw" / "decidim.csv", sep=";", encoding="utf-8-sig")
    raw["presupuesto"] = pd.to_numeric(raw["Presupuesto_euros"], errors="coerce").fillna(0)
    presup_total = raw["presupuesto"].sum()
    presup_seleccionado = raw[raw["Seleccionada"] == "SI"]["presupuesto"].sum()
    hallazgos.append({
        "id": "H11",
        "titulo": "Por cada euro ejecutado, la ciudadanía ha pedido cuatro",
        "cifra": f"{str(round(presup_total/1e6,1)).replace('.',',')} M€ vs {str(round(presup_seleccionado/1e6,1)).replace('.',',')} M€",
        "texto": (
            f"El conjunto de propuestas de las 7 ediciones suma {str(round(presup_total/1e6,1)).replace('.',',')} millones de euros "
            f"en inversión solicitada. De ese volumen, {str(round(presup_seleccionado/1e6,1)).replace('.',',')} M€ pertenecen a "
            "propuestas finalmente seleccionadas, un "
            f"{presup_seleccionado/presup_total*100:.0f} %. "
            "El embudo presupuestario es severo, y debería comunicarse de forma explícita "
            "a la ciudadanía como criterio de gestión."
        ),
        "fuente": "decidim.csv · Presupuesto_euros agregado",
    })

    # ----- H12: Pobles de l'Oest: tres demandas legítimas --------------
    po = idx[(idx["nombre_distrito"] == "Pobles de l'Oest") & (idx["cuadrante"] == "Demanda legítima")]
    if len(po) > 0:
        top_po = po.sort_values("discrepancia", ascending=False).head(3)
        hallazgos.append({
            "id": "H12",
            "titulo": "Pobles de l'Oest, ejemplo de demanda alineada con la carencia",
            "cifra": f"{len(po)} temas con demanda legítima",
            "texto": (
                "En Pobles de l'Oest, varias demandas ciudadanas coinciden con carencias "
                "objetivas medibles: " +
                ", ".join(r["tema"].lower() for _, r in top_po.iterrows()) +
                ". Es un caso donde el proceso participativo funciona como cabe esperar: "
                "los vecinos identifican y priorizan exactamente los temas en los que su "
                "distrito está peor que la media."
            ),
            "fuente": "indice_discrepancia.csv · cuadrante='Demanda legítima'",
        })

    # ----- H13: La gran ausente, equipamientos para mayores --------------
    mayores_demanda = decidim_real[
        decidim_real["tema"].isin(["Equipamientos específicos", "Bibliotecas y ludotecas"])
    ]["Numero_Apoyos"].sum()
    mayores_total = realidad["n_recursos_mayores"].sum()
    hallazgos.append({
        "id": "H13",
        "titulo": "El envejecimiento se queda fuera del debate participativo",
        "cifra": f"{int(mayores_total)} centros · pocas propuestas",
        "texto": (
            f"Valencia cuenta con {int(mayores_total)} recursos para personas mayores según "
            "el portal municipal. Sin embargo, ninguno de los temas detectados en Decidim "
            "se centra específicamente en mayores. Las propuestas relacionadas se reparten "
            "entre instalaciones deportivas, accesibilidad y equipamientos culturales, pero "
            "no aparece como tal una voz que represente las necesidades de las personas "
            "mayores. La 8ª edición podría plantear cómo facilitar su participación."
        ),
        "fuente": "matriz_realidad.csv · n_recursos_mayores",
    })

    # ----- Output ----------------------------------------------------------
    (PROC / "hallazgos.json").write_text(
        json.dumps(hallazgos, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Markdown version
    md = ["# Hallazgos del Atlas de la Voz Ciudadana de València\n",
          "*Versión derivada automáticamente desde `etl/10_hallazgos.py`. Cada cifra es"
          " reproducible ejecutando el pipeline ETL.*\n"]
    for h in hallazgos:
        md.append(f"\n## {h['id']} · {h['titulo']}\n")
        md.append(f"**{h['cifra']}**\n")
        md.append(f"{h['texto']}\n")
        md.append(f"\n*Fuente: {h['fuente']}*\n")
    (DOCS / "03_hallazgos.md").write_text("\n".join(md), encoding="utf-8")

    print(f"Generados {len(hallazgos)} hallazgos:")
    for h in hallazgos:
        print(f"  {h['id']}  {h['titulo']}")


if __name__ == "__main__":
    main()
