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

El **Atlas de la Voz Ciudadana de València** cruza por primera vez las **5.795
propuestas brutas** registradas en las siete ediciones publicadas de
DecidimVLC (2015-2023) con los datasets municipales del Portal de Datos
Abiertos, para responder a una pregunta políticamente relevante: **¿la voz
ciudadana refleja las carencias observables en los datos municipales para
cada distrito?**

A través de embeddings semánticos sobre los títulos de propuestas, las **5.285
con título legible** se agrupan en 38 temas (carriles bici, aceras, parques
infantiles, recogida de residuos…). De ellas, **4.043 están asignadas a un
distrito concreto** y **1.195 figuran bajo "Toda la ciudad"**. La Matriz de
Demanda resultante se contrasta con una Matriz de Realidad construida a partir
de **22 datasets municipales de "realidad urbana"** (vulnerabilidad oficial,
espacios verdes m²/hab, carril bici, velocidad media de calles, paradas EMT,
contenedores de residuos, patrimonio BIC, equipamientos, centros educativos,
recursos para mayores y juventud, ruido y ZAS, parkings, aparcabicis, fuentes
de agua, pipicanes, juegos infantiles, paneles informativos, fallas y otros).
La normalización por habitante usa el padrón municipal 2022.

De los 38 temas detectados, **23 disponen de un indicador municipal específico**
y entran en el índice de discrepancia. Los 15 temas sin indicador directo (p.
ej. iluminación pública, seguridad ciudadana, aceras y movilidad peatonal) se
mantienen en la matriz de demanda pero quedan fuera del cuadrante: preferimos
cobertura honesta antes que usar una proxy genérica repetida.

El cruce arroja un índice de discrepancia que clasifica cada par (distrito,
tema) en cuatro cuadrantes: **demanda legítima**, **sobre-demandante**,
**silencioso vulnerable** y **cómodo**. El cuadrante más numeroso es el de los
**silenciosos vulnerables (45%)**: distritos con carencia observable por encima
de la media pero demanda en Decidim por debajo. **Campanar** (índice de
vulnerabilidad 3,77, el más alto de la ciudad) aparece como silencioso
vulnerable en **6 de los 23 temas con cruce honesto**, incluida pacificación
del tráfico (velocidad media 38,3 km/h, la segunda más alta de la ciudad).
**Extramurs** acumula 1.098 apoyos en cuatro ediciones pidiendo carriles bici
sin haber visto ejecutar ninguno.

El proyecto entrega: (1) una **web interactiva** con mapa coroplético, fichas
por distrito y timeline 2015-2023; (2) un **informe técnico** en formato
periodismo de datos con 13 hallazgos verificables y tres recomendaciones para
la 8ª edición en curso; (3) un **repositorio público MIT** con código y datos
transformados. Todo el pipeline es reproducible en menos de cinco minutos.

---

## Objetivos del proyecto

1. **Operativo**: convertir los 5.795 registros de DecidimVLC en una matriz
   accionable de demanda ciudadana por distrito y tema, agregando por
   semántica y no solo por etiquetas literales.
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
| `districtes-distritos` | 19 distritos como unidad de análisis. |
| `barris-barrios` | 88 barrios para sub-vista. |
| `vulnerabilidad-por-barrios` | Índices oficiales de vulnerabilidad 2021. |
| `equipamients-municipals` | 2.915 equipamientos municipales. |
| `espais-verds` | 807 jardines y zonas verdes (m²). |
| `itinerarios-ciclistas` | Red de carril bici (longitud por tramo). |
| `aparcaments-bicicletes` | 4.297 plazas de aparcabicis. |
| `parkings` | Parkings públicos. |
| `centros-educativos` | 534 centros educativos. |
| `majors-mayores`, `joventut-juventud` | Recursos sociales. |
| `estacions-de-soroll`, `zones-zas` | Ruido y zonas acústicamente saturadas. |
| `falles-fallas` | 351 fallas. |
| (complemento) Padrón municipal 2022 | Población por distrito. |

---

## Metodología

El pipeline son diez scripts Python autocontenidos con licencia MIT (ver
README del repositorio):

```
01_download.py            Descarga reproducible de los 17 datasets
02_load_and_normalize.py  Unidad de análisis = 19 distritos (dissolve)
                          Resolución de Decidim a id_distrito 99,2%
03_topic_modeling.py      Embeddings multilingües + UMAP + HDBSCAN
                          → 50 clusters
04_label_and_merge_topics Mapeo manual a 38 temas legibles
05_matriz_demanda.py      Matriz Demanda normalizada per cápita
06_matriz_realidad.py     45 indicadores por distrito desde 22 datasets
07_indice_discrepancia.py Z-score demanda - z-score carencia
                          → 4 cuadrantes
08_evolucion.py           Análisis longitudinal 7 ediciones
09_export_to_web.py       JSON estáticos (<260 KB total)
10_hallazgos.py           13 hallazgos verificables
```

Stack técnico:

- **ETL**: Python + Pandas + GeoPandas + scikit-learn + sentence-transformers
  + UMAP + HDBSCAN.
- **Geoespacial**: PostGIS *no necesario* — todo se resuelve con
  `geopandas.sjoin` y proyección a EPSG:25830 para medir longitudes/áreas
  en metros.
- **Web**: Next.js 14 (App Router, static export) + Leaflet + tiles CartoDB.
- **Hosting**: GitHub Pages, **coste recurrente: 0 €**.

---

## Resultados principales

| Hallazgo | Cifra |
|---|---|
| Propuestas analizadas | **5.795** (7 ediciones, 9 años) |
| Apoyos ciudadanos | **180.000+** |
| Tasa de selección global | **11,4%** |
| Distritos cubiertos | **19** |
| Temas detectados | **38** (23 con cruce honesto) |
| Pares (distrito × tema) analizables | **437** (23 × 19) |
| Cuadrante "silencioso vulnerable" | **45% de los pares (199/437)** |
| Demandas persistentes (≥4 ediciones, 0 selección) | **28** |
| Distrito con más patrones de silencio | **Campanar** (6 temas; vulnerabilidad 3,77) |

Los 13 hallazgos completos están en el informe técnico adjunto y en
`docs/03_hallazgos.md` del repositorio.

---

## Encaje con los criterios de valoración del concurso

| Criterio (25 pts) | Cómo lo cubre el proyecto |
|---|---|
| **Innovación** | Cruce inédito en València de Decidim + 22 datasets municipales con topic modeling automático, indicadores específicos por tema y matriz de discrepancia z-score. |
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
