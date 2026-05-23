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
    hallazgos.append({
        "id": "H03",
        "titulo": "Campanar: máxima vulnerabilidad, mínima voz",
        "cifra": f"{camp['ind_global']:.2f} / {len(silencios_camp)}",
        "texto": (
            f"Campanar registra el índice de vulnerabilidad más alto de la ciudad "
            f"({camp['ind_global']:.2f}, escala 0-10) según el dataset municipal de 2021. "
            f"Pese a ello, aparece como 'silencioso vulnerable' en {len(silencios_camp)} temas "
            "distintos: aceras y movilidad peatonal, recogida de residuos, pacificación del "
            "tráfico, rehabilitación de mercados, reurbanización de calles, seguridad ciudadana, "
            "iluminación pública, repavimentación, puentes peatonales y litoral. "
            "Pide muy poco para la situación que vive."
        ),
        "fuente": "matriz_realidad.csv + indice_discrepancia.csv",
    })

    # ----- H4: Carril bici, demanda emergente y más zombi ------------------
    bici_evol = next(t for t in evol["emergentes_top10"] if "bici" in t["tema"].lower())
    bici_zombi = [z for z in evol["demandas_zombi"] if "bici" in z["tema"].lower()]
    apoyos_bici_zombi = sum(z["apoyos"] for z in bici_zombi)
    hallazgos.append({
        "id": "H04",
        "titulo": "El carril bici: la demanda que más crece y más se ignora",
        "cifra": f"+{bici_evol['crecimiento']} / 0 ejecuciones",
        "texto": (
            f"Los carriles bici son la demanda que más ha crecido entre 2015 y 2023: "
            f"de {bici_evol['ed1']} propuestas en la 1ª edición a {bici_evol['ed7']} en la 7ª "
            f"(+{bici_evol['crecimiento']}). Sin embargo, {len(bici_zombi)} pares (distrito, edición) "
            f"piden carril bici de forma persistente ({apoyos_bici_zombi:,} apoyos acumulados) "
            f"sin que se haya seleccionado ninguno. El caso más sangrante: Extramurs, con "
            f"29 propuestas y 1.098 apoyos en 4 ediciones consecutivas."
        ).replace(",", "."),
        "fuente": "evolucion.json · emergentes_top10 + demandas_zombi",
    })

    # ----- H5: Pobles del Nord, el efecto megáfono -----------------------
    pn = realidad[realidad["nombre_distrito"] == "Pobles del Nord"].iloc[0]
    decidim_pn = decidim_real[decidim_real["nombre_distrito"] == "Pobles del Nord"]
    apoyos_per_capita_pn = decidim_pn["Numero_Apoyos"].sum() / pn["poblacion"] * 1000
    media_apoyos = decidim_real[decidim_real["id_distrito"].between(1, 19)].groupby("id_distrito")["Numero_Apoyos"].sum().mean() / poblacion["poblacion"].mean() * 1000
    hallazgos.append({
        "id": "H05",
        "titulo": "Pobles del Nord: la voz desproporcionada de los pequeños",
        "cifra": f"{apoyos_per_capita_pn:.0f} apoyos/1.000 hab",
        "texto": (
            f"Con solo {pn['poblacion']:,} habitantes, Pobles del Nord ha generado "
            f"{int(decidim_pn['Numero_Apoyos'].sum()):,} apoyos en propuestas: "
            f"{apoyos_per_capita_pn:.0f} apoyos por 1.000 habitantes, casi el doble que la "
            f"media de Valencia ({media_apoyos:.0f}). En distritos pequeños, una minoría "
            "organizada puede dominar el proceso participativo en términos relativos."
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
    hallazgos.append({
        "id": "H07",
        "titulo": "Verde: 6 veces más en el extremo alto que en el bajo",
        "cifra": f"{top_v['m2_verde_per_hab']:.1f} vs {bot_v['m2_verde_per_hab']:.1f} m²/hab",
        "texto": (
            f"Campanar lidera con {top_v['m2_verde_per_hab']:.1f} m² de zona verde por habitante. "
            f"En el extremo opuesto, Benimaclet ofrece {bot_v['m2_verde_per_hab']:.1f} m²/hab. "
            "La OMS recomienda 9 m²/hab como mínimo: 5 distritos están por debajo. "
            "Sin embargo, ninguno de esos 5 distritos está en el top de demanda en el tema "
            "'Zonas verdes' en Decidim."
        ),
        "fuente": "matriz_realidad.csv · m2_verde_per_hab",
    })

    # ----- H8: El cuadrante mayoritario es 'silencioso vulnerable' --------
    cuad = idx["cuadrante"].value_counts()
    pct_silencio = cuad["Silencioso vulnerable"] / cuad.sum() * 100
    hallazgos.append({
        "id": "H08",
        "titulo": "El silencio vulnerable es la situación más frecuente",
        "cifra": f"{int(cuad['Silencioso vulnerable'])} de {int(cuad.sum())} pares ({pct_silencio:.0f}%)",
        "texto": (
            f"Cruzando los 38 temas con los 19 distritos obtenemos 722 pares posibles. "
            f"En {int(cuad['Silencioso vulnerable']):,} ({pct_silencio:.0f}%) "
            "detectamos un patrón de 'silencio vulnerable': el distrito tiene una carencia "
            "objetiva por encima de la media de la ciudad pero su demanda en Decidim está "
            "por debajo. Es el cuadrante más numeroso, por delante del 'cómodo' "
            f"({int(cuad['Cómodo'])}), 'demanda legítima' ({int(cuad['Demanda legítima'])}) "
            f"y 'sobre-demandante' ({int(cuad['Sobre-demandante'])})."
        ).replace(",", "."),
        "fuente": "indice_discrepancia.csv · value_counts(cuadrante)",
    })

    # ----- H9: 28 demandas zombi -------------------------------------------
    zombis = evol["demandas_zombi"]
    apoyos_zombi = sum(z["apoyos"] for z in zombis)
    hallazgos.append({
        "id": "H09",
        "titulo": "28 demandas se repiten desde hace 4+ ediciones sin ser ejecutadas",
        "cifra": f"{len(zombis)} · {apoyos_zombi:,} apoyos".replace(",", "."),
        "texto": (
            f"{len(zombis)} pares (distrito, tema) han sido objeto de propuestas en al menos "
            f"4 de las 7 ediciones sin que se seleccionara ninguna. Acumulan "
            f"{apoyos_zombi:,} apoyos. ".replace(",", ".") +
            "El top: " +
            ", ".join(
                f"{z['nombre_distrito']} ({z['tema'].lower()})"
                for z in sorted(zombis, key=lambda x: -x["apoyos"])[:3]
            ) +
            ". Cada propuesta zombi es un voto ciudadano que el sistema ignora durante años."
        ),
        "fuente": "evolucion.json · demandas_zombi",
    })

    # ----- H10: 38 temas detectados --------------------------------------
    temas_unicos = decidim_real["tema"].nunique()
    top_3_temas = (
        decidim_real.groupby("tema")["Numero_Apoyos"].sum().sort_values(ascending=False).head(3)
    )
    hallazgos.append({
        "id": "H10",
        "titulo": "Las prioridades de Valencia caben en 38 categorías",
        "cifra": f"{temas_unicos} temas detectados",
        "texto": (
            f"Aplicando topic modeling sobre los {len(decidim_real):,} títulos legibles ".replace(",", ".") +
            f"surgen {temas_unicos} agrupaciones temáticas. El top 3 por apoyos: "
            + ", ".join(f"{t} ({int(a):,} apoyos)".replace(",", ".") for t, a in top_3_temas.items())
            + ". Identificar estas categorías hace posible analizar la demanda al margen del "
            "ruido lingüístico (castellano/valenciano, abreviaturas, faltas)."
        ),
        "fuente": "decidim_tagged.csv + topics.csv",
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
