---
title: "Memoria resumen del proyecto"
subtitle: "Atlas de la Voz Ciudadana de València"
author: "Santiago Medina"
date: "Mayo de 2026"
lang: es
geometry: margin=2.4cm
fontsize: 11pt
---

## Datos identificativos

| Campo | Contenido |
|---|---|
| **Título del proyecto** | Atlas de la Voz Ciudadana de València |
| **Categoría** | Datos Abiertos |
| **Modalidad** | Aplicación web · Análisis · Visualización |
| **Autor/a** | Santiago Medina |
| **Web del proyecto** | `https://santiago-medina.github.io/atlas-voz-ciudadana-valencia` |
| **Repositorio (código y datos)** | `https://github.com/santiago-medina/atlas-voz-ciudadana-valencia` |
| **Licencia del código** | MIT |
| **Fecha** | Mayo 2026 |

---

## Resumen del proyecto (300 palabras)

El **Atlas de la Voz Ciudadana de València** cruza por primera vez las
**{{N_PROPUESTAS_BRUTAS|int}} propuestas brutas** registradas en las siete
ediciones publicadas de DecidimVLC ({{EDICIONES_PERIODO}}) con los datasets
municipales del Portal de Datos Abiertos, para responder a una pregunta
políticamente relevante: **¿la voz ciudadana refleja las carencias observables
en los datos municipales para cada distrito?**

A través de embeddings semánticos sobre los títulos de propuestas, las
**{{N_PROPUESTAS_LEGIBLES|int}} con título legible** se agrupan en
{{N_TEMAS_DETECTADOS|raw}} temas (carriles bici, aceras, parques infantiles,
recogida de residuos…). De ellas, **{{N_PROPUESTAS_DISTRITO|int}} están
asignadas a un distrito concreto** y **{{N_PROPUESTAS_GLOBAL|int}} figuran bajo
"Toda la ciudad"**. La Matriz de Demanda resultante se contrasta con una
Matriz de Realidad construida a partir de **{{N_DATASETS_REALIDAD|raw}} datasets
municipales de "realidad urbana"** (vulnerabilidad oficial, espacios verdes
m²/hab, carril bici, velocidad media de calles, paradas EMT, contenedores de
residuos, patrimonio BIC, equipamientos, centros educativos, recursos para
mayores y juventud, ruido y ZAS, parkings, aparcabicis, fuentes de agua,
pipicanes, juegos infantiles, paneles informativos, fallas y otros). La
normalización por habitante usa el padrón municipal 2022
({{POBLACION_TOTAL|int}} habitantes).

De los {{N_TEMAS_DETECTADOS|raw}} temas detectados, **{{N_TEMAS_CON_INDICADOR|raw}}
disponen de un indicador municipal específico** y entran en el índice de
discrepancia. Los {{N_TEMAS_SIN_INDICADOR|raw}} temas sin indicador directo (p. ej.
iluminación pública, seguridad ciudadana, aceras y movilidad peatonal) se
mantienen en la matriz de demanda pero quedan fuera del cuadrante: preferimos
cobertura honesta antes que usar una proxy genérica repetida.

El cruce arroja un índice de discrepancia que clasifica cada par (distrito,
tema) en cuatro cuadrantes: **demanda legítima**, **sobre-demandante**,
**silencioso vulnerable** y **cómodo**. El cuadrante más numeroso es el de los
**silenciosos vulnerables ({{PCT_SILENCIO|pct0}})**: distritos con carencia
observable por encima de la media pero demanda en Decidim por debajo.
**{{DISTRITO_VUL_MAX}}** (índice de vulnerabilidad {{N_VUL_MAX|float2}}, el más alto
de la ciudad) aparece como silencioso vulnerable en **{{N_CAMPANAR_SILENCIOS|raw}}
de los {{N_TEMAS_CON_INDICADOR|raw}} temas con cruce honesto**, incluida
pacificación del tráfico (velocidad media {{VEL_CAMPANAR|float}} km/h, la
#{{CAMPANAR_VEL_RANK|raw}} más alta de la ciudad). **Extramurs** acumula
{{EXTRAMURS_BICI_APOYOS|raw}} apoyos en {{EXTRAMURS_BICI_EDICIONES|raw}} ediciones pidiendo
carriles bici sin haber visto ejecutar ninguno.

---

## Objetivos del proyecto

1. **Operativo**: convertir los {{N_PROPUESTAS_BRUTAS|int}} registros de DecidimVLC en
   una matriz accionable de demanda ciudadana por distrito y tema, agregando
   por semántica y no solo por etiquetas literales.
2. **Analítico**: medir la coincidencia entre la voz ciudadana y las
   carencias objetivas medibles en otros datasets municipales.
3. **Comunicativo**: ofrecer al Ayuntamiento, asociaciones vecinales y
   ciudadanía una herramienta visual y un informe que permita interpretar el
   proceso participativo más allá del ránking de propuestas.
4. **Reproducible**: liberar el código y la metodología para que cualquier
   persona pueda actualizar el análisis cuando se publique la 8ª edición y
   verificar todas las cifras.

---

## Datasets utilizados

Origen: **Portal de Datos Abiertos del Ayuntamiento de València**
(`opendata.vlci.valencia.es`).

| ID dataset | Función en el análisis |
|---|---|
| `apoyo-propuestas-decidimvlc` | Fuente principal: propuestas, apoyos, selección. |
| `districtes-distritos` | {{N_DISTRITOS|raw}} distritos como unidad de análisis. |
| `barris-barrios` | 88 barrios para sub-vista. |
| `vulnerabilidad-por-barrios` | Índices oficiales de vulnerabilidad 2021. |
| `equipamients-municipals` | {{N_EQUIPAMIENTOS|int}} equipamientos municipales. |
| `espais-verds` | {{N_ESPACIOS_VERDES|int}} jardines y zonas verdes (m²). |
| `velocitat-carrers` | {{N_TRAMOS_CALLES|int}} tramos con velocidad oficial. |
| `contenidors-residus-solids` | {{N_CONTENEDORES|int}} contenedores de residuos. |
| `emt` | {{N_PARADAS_EMT|int}} paradas de bus EMT. |
| `catalogo-urbano` | {{N_BIC|int}} BIC/BRL/CH protegidos. |
| `fonts-daigua-publica` | {{N_FUENTES_AGUA|int}} fuentes de agua pública. |
| `pipicans` | {{N_PIPICANS|int}} zonas caninas. |
| `zones-jocs-infantils` | {{N_JUEGOS_INFANTILES|int}} zonas de juego infantil. |
| `itinerarios-ciclistas` | Red de carril bici (longitud por tramo). |
| `aparcaments-bicicletes` | {{N_APARCABICIS_PLAZAS|int}} plazas de aparcabicis. |
| `parkings` | {{N_PARKING_PLAZAS|int}} plazas de parking. |
| `centros-educativos` | {{N_CENTROS_EDUCATIVOS|int}} centros educativos. |
| `majors-mayores`, `joventut-juventud` | Recursos sociales. |
| `estacions-de-soroll`, `zones-zas` | Ruido y zonas acústicamente saturadas. |
| `falles-fallas` | {{N_FALLAS|int}} fallas. |
| (complemento) Padrón municipal 2022 | {{POBLACION_TOTAL|int}} habitantes por distrito. |

---

## Metodología

El pipeline son **once scripts Python autocontenidos** con licencia MIT (ver
README del repositorio):

```
01_download.py            Descarga reproducible de los {{N_DATASETS_TOTALES|raw}} datasets
02_load_and_normalize.py  Unidad de análisis = {{N_DISTRITOS|raw}} distritos (dissolve).
                          Resolución de Decidim a id_distrito 99,2%.
03_topic_modeling.py      Embeddings multilingües + UMAP + HDBSCAN → 50 clusters
04_label_and_merge_topics Mapeo manual a {{N_TEMAS_DETECTADOS|raw}} temas legibles
05_matriz_demanda.py      Matriz Demanda normalizada per cápita
06_matriz_realidad.py     Indicadores por distrito desde {{N_DATASETS_REALIDAD|raw}} datasets
07_indice_discrepancia.py Z-score(demanda) - z-score(carencia)
                          → 4 cuadrantes, {{N_TEMAS_CON_INDICADOR|raw}} temas cruzables
08_evolucion.py           Análisis longitudinal 7 ediciones
09_export_to_web.py       JSON estáticos (<260 KB total)
10_hallazgos.py           13 hallazgos verificables
11_numeros.py             Single source of truth: 80+ números clave → JSON
                          que alimenta esta memoria y el informe.
```

Stack técnico:

- **ETL**: Python + Pandas + GeoPandas + scikit-learn + sentence-transformers
  + UMAP + HDBSCAN.
- **Geoespacial**: GeoPandas en EPSG:25830 para distancias/áreas (no requiere
  PostGIS).
- **Web**: Next.js 14 (App Router, static export) + Leaflet + tiles CartoDB.
- **Hosting**: GitHub Pages, **coste recurrente: 0 €**.

---

## Resultados principales

| Hallazgo | Cifra |
|---|---|
| Propuestas brutas analizadas | **{{N_PROPUESTAS_BRUTAS|int}}** ({{N_EDICIONES|raw}} ediciones, {{EDICIONES_PERIODO}}) |
| Propuestas con título legible | **{{N_PROPUESTAS_LEGIBLES|int}}** |
| Propuestas asignadas a distrito | **{{N_PROPUESTAS_DISTRITO|int}}** |
| Apoyos ciudadanos | **{{N_APOYOS_TOTAL|int}}** |
| Tasa de selección global | **{{PCT_TASA_SELECCION|pct}}** |
| Presupuesto solicitado | **{{PRESUP_SOLICITADO_MEUR|float0}} M €** |
| Presupuesto seleccionado | **{{PRESUP_SELECCIONADO_MEUR|float0}} M €** ({{PCT_PRESUP_NO_SELECCIONADO|pct0}} no seleccionado) |
| Distritos cubiertos | **{{N_DISTRITOS|raw}}** |
| Temas detectados | **{{N_TEMAS_DETECTADOS|raw}}** ({{N_TEMAS_CON_INDICADOR|raw}} con cruce honesto) |
| Pares (distrito × tema) analizables | **{{N_PARES_TOTAL|raw}}** ({{N_TEMAS_CON_INDICADOR|raw}} × {{N_DISTRITOS|raw}}) |
| Cuadrante "silencioso vulnerable" | **{{PCT_SILENCIO|pct0}} de los pares ({{N_PARES_SILENCIO|raw}}/{{N_PARES_TOTAL|raw}})** |
| Demandas persistentes (≥4 ediciones, 0 selección) | **{{N_DEMANDAS_ZOMBI|raw}}** |
| Distrito con más patrones de silencio | **{{DISTRITO_VUL_MAX}}** ({{N_CAMPANAR_SILENCIOS|raw}} temas; vulnerabilidad {{N_VUL_MAX|float2}}) |

Los 13 hallazgos completos están en el informe técnico adjunto y en
`docs/03_hallazgos.md` del repositorio.

---

## Encaje con los criterios de valoración del concurso

| Criterio (25 pts) | Cómo lo cubre el proyecto |
|---|---|
| **Innovación** | Cruce inédito en València de Decidim + {{N_DATASETS_REALIDAD|raw}} datasets municipales con topic modeling automático, indicadores específicos por tema y matriz de discrepancia z-score. |
| **Impacto social** | Identifica los "silenciosos vulnerables" — los distritos donde el proceso participativo falla y hay que actuar de oficio. Recomendaciones directas a la 8ª edición. |
| **Viabilidad** | Producto desplegado y accesible en GitHub Pages con coste cero. Pipeline reproducible en <5 minutos. Sin dependencias propietarias. |
| **Colaboración** | Código y datos abiertos (MIT). Diseñado para que cualquier asociación vecinal, periodista o investigador/a pueda extender el análisis. |

---

## Mantenimiento futuro

El pipeline está pensado para reejecutarse cuando se publique la **8ª edición**
de DecidimVLC (previsiblemente 2027). Bastará con relanzar
`python etl/01_download.py` y los pasos sucesivos: las matrices y el mapa
web se actualizarán automáticamente con los datos nuevos.

---

## Anexos en este expediente

1. `informe.pdf` — Informe técnico completo (≈15 páginas)
2. `MEMORIA_RESUMEN.pdf` — Este documento
3. URL del proyecto, accesible permanentemente
4. URL del repositorio público de código y datos
