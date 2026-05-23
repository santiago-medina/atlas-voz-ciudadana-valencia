---
title: "Atlas de la Voz Ciudadana de València"
subtitle: "Análisis cruzado entre las propuestas de Decidim VLC y los datasets municipales (2015-2023)"
author: "Santiago Medina"
date: "Mayo de 2026"
lang: es
geometry: margin=2.4cm
fontsize: 11pt
linkcolor: "{HTML}{B03A2E}"
---

\pagebreak

## Resumen ejecutivo

Entre 2015 y 2023, **9.131 personas** generaron **5.795 propuestas** y **180.000 apoyos**
en las siete ediciones de los presupuestos participativos DecidimVLC. Ese caudal
de información ha sido publicado por el Ayuntamiento de València como dataset
abierto, pero hasta hoy no se había cruzado con el resto del portal para
contestar a una pregunta sencilla y políticamente relevante:

> **¿La voz ciudadana refleja las carencias reales de cada distrito?**

Este Atlas responde con datos. Sus principales conclusiones:

1. La participación se ha **duplicado** entre la 1ª y la 7ª edición, pero la
   **tasa de ejecución** ha caído al 9,6%. Más voz, menos respuesta.
2. **El 39% de los pares (distrito × tema) analizados muestra un patrón de
   "silencio vulnerable"**: el distrito tiene una carencia objetiva por encima
   de la media pero su demanda en Decidim está por debajo. Es la situación
   más frecuente.
3. **28 demandas son "zombi"**: combinaciones (distrito × tema) que se repiten
   en al menos cuatro ediciones consecutivas sin que se haya seleccionado
   ninguna. El caso más sangrante: Extramurs reclama carriles bici desde 2015
   con 1.098 apoyos acumulados, 0 ejecuciones.
4. Los **carriles bici** son la demanda que más crece (+103 propuestas entre
   2015 y 2023) y, a la vez, la más desatendida.
5. **Campanar concentra la mayor vulnerabilidad oficial de la ciudad** (índice
   3,77 sobre 10) pero aparece como "silencioso vulnerable" en diez temas
   distintos. La voz que más debería oírse es la que menos se oye.
6. La **8ª edición de DecidimVLC**, abierta en mayo de 2026 con un mecanismo
   nuevo de reequilibrio territorial, debería tener en cuenta estos hallazgos
   para corregir patrones acumulados desde hace casi una década.

El proyecto entrega tres piezas: una **web interactiva**
(`atlas-voz-ciudadana-valencia`), este **informe** y un **repositorio público en
GitHub** con todo el código y los datos transformados. Todos los hallazgos son
reproducibles ejecutando el pipeline ETL en menos de cinco minutos.

\pagebreak

## 1. Por qué este Atlas

### 1.1 El contexto

Valencia lleva una década apostando por los presupuestos participativos. A través
de **DecidimVLC**, cada año vecinas y vecinos proponen inversiones para su
distrito, las apoyan, y un porcentaje pequeño termina ejecutándose. El proceso
genera además un activo invisible para quien no lo mira con lupa: **un mapa
detallado de las prioridades reales de cada barrio**.

El Ayuntamiento publica los datos de cada edición un año después de cerrarla.
A día de hoy están disponibles las **siete ediciones completas** (2015-2016 a
2022-2023). La octava está abierta en este momento (29 abril–22 junio 2026),
con un mecanismo nuevo de "reequilibrio territorial" pensado para que los
distritos pequeños no queden desplazados.

### 1.2 La pregunta

Las decisiones políticas del Ayuntamiento sobre DecidimVLC se basan en una
hipótesis implícita: que las propuestas y los apoyos miden la **prioridad real**
de cada barrio. Pero esa hipótesis no se ha verificado. Pueden ocurrir varias
cosas:

- Que un distrito **se queje porque tiene un problema**: la voz refleja la
  carencia.
- Que un distrito **se queje porque está organizado**, no porque tenga el
  problema más grave: la voz amplifica privilegios.
- Que un distrito **no se queje aunque tenga el problema**: la voz falla en el
  sitio donde más se necesita.

Para saber cuál de estas dinámicas predomina, hay que cruzar Decidim con
**datos objetivos de carencia**: vulnerabilidad oficial, espacios verdes por
habitante, equipamientos municipales, longitud de carril bici, zonas
acústicamente saturadas, etc. Eso es lo que hace este Atlas.

\pagebreak

## 2. Metodología

### 2.1 Fuentes de datos

Toda la información proviene del **Portal de Datos Abiertos del Ayuntamiento de
València** (`opendata.vlci.valencia.es`). El proyecto consume **17 datasets**:

| Dataset | Rol en el análisis |
|---|---|
| `apoyo-propuestas-decidimvlc` | Fuente principal — 5.795 propuestas con apoyos, edición, ámbito, presupuesto y selección. |
| `districtes-distritos` | 19 distritos administrativos (polígonos). Unidad de análisis. |
| `barris-barrios` | 88 barrios (sub-vista). |
| `vulnerabilidad-por-barrios` | Índices oficiales 2021 de vulnerabilidad equipamental, demográfica, económica y global. |
| `equipamients-municipals` | 2.915 equipamientos municipales con ubicación. |
| `espais-verds` | 807 jardines, parques y zonas verdes (m²). |
| `itinerarios-ciclistas` | Red de carriles bici (longitud por tramo). |
| `aparcaments-bicicletes` | 4.297 plazas de aparcamiento para bicis. |
| `parkings` | Parkings públicos (plazas). |
| `centros-educativos` | 534 colegios e institutos. |
| `mayores`, `joventut` | Recursos para personas mayores y juventud. |
| `estacions-de-soroll`, `zones-zas` | Mediciones de ruido y zonas saturadas. |
| `falles-fallas` | 351 fallas (intensidad cultural). |

Adicionalmente se incorpora la **población por distrito** según el padrón
municipal 2022 (807.396 habitantes totales).

### 2.2 Pipeline

El análisis se construye en diez scripts Python autocontenidos. La cadena
completa va desde la descarga reproducible hasta los JSON estáticos que sirven
la web:

```
01_download.py            → bajada de los 17 datasets (≈70 MB)
02_load_and_normalize.py  → 19 distritos (dissolve sobre 22 polígonos),
                            resolución de 5.795 → 4.553 propuestas en
                            distrito + 1.195 globales (99,2% asignado)
03_topic_modeling.py      → embeddings multilingües (5.285 títulos
                            limpios) + UMAP + HDBSCAN → 50 clusters
04_label_and_merge_topics → mapeo manual → 38 temas legibles
05_matriz_demanda.py      → Matriz Demanda (19 × 38), apoyos
                            por 1.000 hab.
06_matriz_realidad.py     → 29 indicadores por distrito (verde m²/hab,
                            carril bici km/1.000 hab, vulnerabilidad
                            oficial, equipamientos, etc.)
07_indice_discrepancia.py → z-score(demanda) - z-score(carencia)
                            → 4 cuadrantes
08_evolucion.py           → análisis longitudinal de 7 ediciones,
                            propuestas zombi, temas emergentes
09_export_to_web.py       → JSON estáticos (<260 KB total)
10_hallazgos.py           → 13 cifras verificables para el informe
```

Todo el código es libre (licencia MIT) y reproducible:

```
git clone https://github.com/santiago-medina/atlas-voz-ciudadana-valencia
cd atlas-voz-ciudadana-valencia
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python etl/01_download.py
python etl/02_load_and_normalize.py
# … hasta 10_hallazgos.py
```

### 2.3 Concepto: los cuatro cuadrantes

Para cada par (distrito × tema) calculamos:

- **Demanda Z**: z-score del nº de apoyos por 1.000 habitantes en ese tema
  dentro de ese distrito, comparado con la media de los 19 distritos.
- **Carencia Z**: z-score del indicador de realidad correspondiente al tema,
  invirtiendo el signo cuando "más es mejor" (ej. más m² de verde = menos
  carencia).

La combinación genera cuatro cuadrantes:

| | **Poca carencia** | **Mucha carencia** |
|---|---|---|
| **Mucha demanda** | **Sobre-demandante** | **Demanda legítima** |
| **Poca demanda** | **Cómodo** | **Silencioso vulnerable** |

El cuadrante interesante es **Silencioso vulnerable**: los distritos donde un
problema existe pero no se nombra en Decidim. Son los que requieren acción
proactiva — no llegará por sí sola desde el proceso participativo.

\pagebreak

## 3. Hallazgos

Los 13 hallazgos siguientes se han generado automáticamente con
`etl/10_hallazgos.py`. Cada cifra es trazable hasta el dataset original.

{HALLAZGOS}

\pagebreak

## 4. Recomendaciones para la 8ª edición de DecidimVLC

Estos hallazgos no son una crítica al proceso participativo; al contrario,
demuestran que **DecidimVLC funciona como herramienta de expresión**. Pero
revelan tres dinámicas que la 8ª edición (2025-2026, en curso) puede corregir:

### R1 · Activar la voz silenciosa donde más se necesita

Los **51 pares (distrito × tema) con vulnerabilidad alta y demanda baja**
identificados por este Atlas dibujan un mapa de prioridades para campañas
focalizadas: salas en centros culturales de Campanar, presencia en mercados de
Algirós y Rascanya, conexión con asociaciones vecinales de l'Olivereta. La voz
silenciosa no nace sola, hay que ir a buscarla.

### R2 · Acortar el embudo de las "demandas zombi"

28 combinaciones de distrito × tema con cuatro o más ediciones de demanda y
cero ejecuciones constituyen un problema reputacional. Sin entrar en por qué
no se ejecutaron (puede haber razones técnicas o presupuestarias legítimas),
**la ciudadanía merece una respuesta razonada y pública sobre cada caso**.
Sin esa respuesta, el sistema acumula frustración.

### R3 · Reducir el peso de "Toda la ciudad"

El 20,6% de las propuestas históricas se etiquetaron como "Toda la ciudad",
lo que las hace invisibles al mecanismo de reequilibrio territorial de la 8ª
edición. Forzar a quien propone a asignar un distrito —o crear una categoría
"propuestas transversales" con cuotas explícitas— ayudaría a que el
reequilibrio funcione realmente.

\pagebreak

## 5. Próximos pasos

Este Atlas es una pieza viva. Las próximas mejoras previstas (post-concurso):

- **Incorporar la 8ª edición** cuando se publique en el portal abierto
  (previsiblemente 2027), para evaluar si las recomendaciones se cumplieron.
- **Cruzar con sección censal** (no solo distrito) para detectar bolsas de
  silencio dentro de distritos heterogéneos como Quatre Carreres o
  l'Eixample.
- **Validación cualitativa**: entrevistas en los 5 distritos con más silencio
  vulnerable para entender las razones (¿desconocimiento, desconfianza,
  brecha digital?).

El código y los datos están abiertos para que cualquier persona o entidad
pueda extenderlos.

\pagebreak

## Anexo · Datasets y licencias

Todos los datos provienen del Portal de Datos Abiertos del Ayuntamiento de
València (`opendata.vlci.valencia.es`), publicados bajo licencia compatible
con la reutilización con atribución. La población por distrito se obtuvo del
Padrón Municipal 2022 publicado por el propio Ayuntamiento.

El código del Atlas se publica bajo licencia MIT en:
**`github.com/santiago-medina/atlas-voz-ciudadana-valencia`**

La web interactiva está disponible permanentemente en:
**`santiago-medina.github.io/atlas-voz-ciudadana-valencia`**

---

*Atlas de la Voz Ciudadana de València · Mayo 2026 · Santiago Medina.*
