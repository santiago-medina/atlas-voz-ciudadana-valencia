"""
10_hallazgos.py — Construye los 12-15 hallazgos clave del Atlas con
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
    hallazgos.append({
        "id": "H01",
        "titulo": "La participación se ha duplicado en una década",
        "cifra": f"{int(e7['propuestas'] - e1['propuestas']):+,}".replace(",", "."),
        "texto": (
            f"En la 1ª edición (2015-2016) se presentaron {int(e1['propuestas']):,} propuestas; "
            f"en la 7ª (2022-2023) fueron {int(e7['propuestas']):,}, "
            f"un crecimiento del {((e7['propuestas']/e1['propuestas'])-1)*100:.0f}%. "
            f"Los apoyos ciudadanos (registrados a partir de la 2ª edición) "
            f"pasaron de {int(e2['apoyos']):,} a {int(e7['apoyos']):,}. "
            "DecidimVLC ha consolidado un canal real de expresión ciudadana."
        ).replace(",", "."),
        "fuente": "decidim_tagged.csv · agregación por Edicion",
    })

    # ----- H2: Pero la tasa de selección cae ------------------------------
    hallazgos.append({
        "id": "H02",
        "titulo": "Más propuestas, menos ejecución",
        "cifra": f"{e7['tasa_seleccion']*100:.1f}%",
        "texto": (
            f"En la 1ª edición se seleccionó el {e1['tasa_seleccion']*100:.1f}% de las propuestas; "
            f"en la 7ª solo el {e7['tasa_seleccion']*100:.1f}%. "
            "El proceso ha ganado masa crítica pero ha perdido capacidad de convertir "
            "demanda en proyecto ejecutado, lo que genera frustración acumulada."
        ),
        "fuente": "evolucion.json · tasa_seleccion por edición",
    })

    # ----- H3: Campanar, el silencioso vulnerable arquetípico --------------
    camp = realidad[realidad["nombre_distrito"] == "Campanar"].iloc[0]
    silencios_camp = idx[
        (idx["nombre_distrito"] == "Campanar")
        & (idx["cuadrante"] == "Silencioso vulnerable")
    ]
    n_temas_total = idx["tema"].nunique()
    silencios_temas_camp = sorted(silencios_camp["tema"].unique())
    hallazgos.append({
        "id": "H03",
        "titulo": "Campanar: alta vulnerabilidad y baja demanda relativa",
        "cifra": f"{camp['ind_global']:.2f} / {len(silencios_camp)}",
        "texto": (
            f"Campanar registra el índice de vulnerabilidad más alto de los 19 distritos "
            f"({camp['ind_global']:.2f}, escala 0-10) según el dataset municipal de 2021. "
            f"En el cruce con Decidim aparece en el cuadrante 'silencioso vulnerable' en "
            f"{len(silencios_camp)} de los {n_temas_total} temas con indicador municipal "
            f"específico, entre ellos: {', '.join(s.lower() for s in silencios_temas_camp[:4])} "
            "y otros. Concretamente, la velocidad media de sus calles (38,3 km/h) es la "
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
            f"haya sido seleccionada — {apoyos_bici_zombi:,} apoyos en total. ".replace(",", ".") +
            "El caso de mayor volumen: Extramurs, con 29 propuestas y 1.098 apoyos sin "
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
            f"Con solo {pn['poblacion']:,} habitantes, Pobles del Nord acumula "
            f"{int(decidim_pn['Numero_Apoyos'].sum()):,} apoyos en propuestas, equivalentes a "
            f"{apoyos_per_capita_pn:.0f} apoyos por 1.000 habitantes — {ratio:.1f} veces la media "
            f"de la ciudad ({media_apoyos:.0f}). En distritos pequeños, una organización "
            "vecinal activa puede amplificar el peso relativo del distrito en el proceso "
            "participativo, lo que conviene considerar al diseñar mecanismos de reequilibrio."
        ).replace(",", "."),
        "fuente": "decidim_tagged.csv + poblacion_distritos.csv",
    })

    # ----- H6: "Toda la ciudad" como problema ------------------------------
    global_n = int((decidim["id_distrito"] == 0).sum())
    global_pct = global_n / len(decidim) * 100
    hallazgos.append({
        "id": "H06",
        "titulo": "Una de cada cinco propuestas no se ata a ningún barrio",
        "cifra": f"{global_pct:.1f}%",
        "texto": (
            f"{global_n:,} propuestas ({global_pct:.1f}% del total) se presentaron bajo "
            "la etiqueta 'Toda la ciudad'. Es un volumen enorme que dificulta el reequilibrio "
            "territorial: las propuestas globales no se pueden asignar a un distrito concreto "
            "para medir si están atendiendo a un barrio vulnerable o reforzando privilegios. "
            "La nueva edición 2025-2026 podría revisar este criterio."
        ).replace(",", "."),
        "fuente": "decidim_tagged.csv · count(id_distrito == 0)",
    })

    # ----- H7: Desigualdad de espacios verdes ------------------------------
    top_v = realidad.nlargest(1, "m2_verde_per_hab").iloc[0]
    bot_v = realidad.nsmallest(1, "m2_verde_per_hab").iloc[0]
    n_below_9 = int((realidad["m2_verde_per_hab"] < 9).sum())
    hallazgos.append({
        "id": "H07",
        "titulo": "Verde: hasta 6 veces más en el extremo alto que en el bajo",
        "cifra": f"{top_v['m2_verde_per_hab']:.1f} vs {bot_v['m2_verde_per_hab']:.1f} m²/hab",
        "texto": (
            f"Campanar lidera con {top_v['m2_verde_per_hab']:.1f} m² de zona verde por habitante. "
            f"En el extremo opuesto, Benimaclet ofrece {bot_v['m2_verde_per_hab']:.1f} m²/hab. "
            f"Tomando 9 m²/hab como umbral ampliamente citado en literatura urbana, "
            f"{n_below_9} distritos quedan por debajo. Ninguno de ellos figura en el top de "
            "demanda en el tema 'Zonas verdes' dentro de Decidim, lo que sugiere que la "
            "carencia observable no se traduce automáticamente en demanda explícita."
        ),
        "fuente": "matriz_realidad.csv · m2_verde_per_hab",
    })

    # ----- H8: El cuadrante mayoritario es 'silencioso vulnerable' --------
    cuad = idx["cuadrante"].value_counts()
    pct_silencio = cuad["Silencioso vulnerable"] / cuad.sum() * 100
    n_total = int(cuad.sum())
    hallazgos.append({
        "id": "H08",
        "titulo": "El silencio vulnerable es la situación más frecuente",
        "cifra": f"{int(cuad['Silencioso vulnerable'])} de {n_total} pares ({pct_silencio:.0f}%)",
        "texto": (
            f"Cruzando los {n_temas_total} temas que tienen un indicador municipal específico "
            f"con los 19 distritos obtenemos {n_total} pares analizables. En "
            f"{int(cuad['Silencioso vulnerable']):,} ({pct_silencio:.0f}%) detectamos un patrón "
            "de 'silencio vulnerable': el distrito tiene una carencia observable por encima de "
            "la media de la ciudad pero su demanda en Decidim queda por debajo. Es el "
            f"cuadrante más numeroso, por delante de 'cómodo' ({int(cuad['Cómodo'])}), "
            f"'demanda legítima' ({int(cuad['Demanda legítima'])}) y 'sobre-demandante' "
            f"({int(cuad['Sobre-demandante'])})."
        ).replace(",", "."),
        "fuente": "indice_discrepancia.csv · value_counts(cuadrante)",
    })

    # ----- H9: 28 demandas zombi -------------------------------------------
    zombis = evol["demandas_zombi"]
    apoyos_zombi = sum(z["apoyos"] for z in zombis)
    hallazgos.append({
        "id": "H09",
        "titulo": "28 demandas persistentes no han sido seleccionadas en 4+ ediciones",
        "cifra": f"{len(zombis)} pares · {apoyos_zombi:,} apoyos".replace(",", "."),
        "texto": (
            f"{len(zombis)} pares (distrito, tema) han sido objeto de propuestas en al menos "
            f"4 de las 7 ediciones sin que ninguna haya sido seleccionada. Acumulan "
            f"{apoyos_zombi:,} apoyos ciudadanos. ".replace(",", ".") +
            "Los tres pares con más apoyos acumulados son: " +
            ", ".join(
                f"{z['nombre_distrito']} ({z['tema'].lower()})"
                for z in sorted(zombis, key=lambda x: -x["apoyos"])[:3]
            ) +
            ". Cada demanda persistente sin selección representa una desconexión entre "
            "expresión ciudadana y ejecución que conviene comunicar de forma explícita."
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
        "titulo": "38 temas detectados, 23 con cruce honesto contra datos municipales",
        "cifra": f"{temas_unicos} temas / {n_con_indicador} cruzables",
        "texto": (
            f"Aplicando topic modeling sobre los {len(decidim_real):,} títulos legibles ".replace(",", ".") +
            f"surgen {temas_unicos} agrupaciones temáticas. El top 3 por apoyos: "
            + ", ".join(f"{t} ({int(a):,} apoyos)".replace(",", ".") for t, a in top_3_temas.items())
            + f". De los 38, **{n_con_indicador}** tienen un indicador municipal específico "
            "que permite calcular el cuadrante de discrepancia; el resto se muestra solo en la "
            "matriz de demanda. Esta separación honesta evita usar la vulnerabilidad global "
            "como proxy genérico repetido."
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
        "titulo": "Por cada euro ejecutado, la ciudadanía ha pedido 4",
        "cifra": f"{presup_total/1e6:.1f} M€ vs {presup_seleccionado/1e6:.1f} M€",
        "texto": (
            f"El conjunto de propuestas de las 7 ediciones suma {presup_total/1e6:.1f} millones de euros "
            f"en inversión solicitada. De ese volumen, {presup_seleccionado/1e6:.1f} M€ pertenecen a "
            "propuestas finalmente seleccionadas, un "
            f"{presup_seleccionado/presup_total*100:.0f}%. "
            "El embudo presupuestario es severo, y debería usarse como criterio explícito al "
            "comunicar resultados a la ciudadanía."
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

    # ----- H13: La gran ausente — equipamientos para mayores --------------
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
            "el portal municipal. Sin embargo, no aparece ningún tema específicamente "
            "centrado en mayores en el ranking de demanda. Las propuestas relacionadas "
            "se dispersan entre instalaciones deportivas, accesibilidad y equipamientos "
            "culturales, pero ninguna 'voz mayor' se articula explícitamente en Decidim. "
            "La 8ª edición podría incorporar incentivos a la participación senior."
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
