---
title: "Atlas de la Voz Ciudadana de València"
subtitle: "Análisis cruzado entre las propuestas de Decidim VLC y los datasets municipales ({{EDICIONES_PERIODO}})"
author: "Santiago Medina"
date: "Mayo de 2026"
lang: es
geometry: margin=2.4cm
fontsize: 11pt
linkcolor: "{HTML}{B03A2E}"
---

\pagebreak

## Resumen ejecutivo

Entre 2015 y 2023, vecinas y vecinos de València generaron **{{N_PROPUESTAS_BRUTAS|int}}
propuestas brutas** ({{N_PROPUESTAS_LEGIBLES|int}} con título legible,
{{N_PROPUESTAS_DISTRITO|int}} asignadas a un distrito concreto,
{{N_PROPUESTAS_GLOBAL|int}} bajo "Toda la ciudad") y **{{N_APOYOS_TOTAL|int}}
apoyos** en las siete ediciones de los presupuestos participativos DecidimVLC.
Ese caudal de información ha sido publicado por el Ayuntamiento de València
como dataset abierto, pero hasta hoy no se había cruzado con el resto del
portal para contestar a una pregunta sencilla y políticamente relevante:

> **¿La voz ciudadana refleja las carencias observables en los datos
> municipales para cada distrito?**

Este Atlas responde con un cruce sistemático entre Decidim y **{{N_DATASETS_REALIDAD|raw}} datasets
de realidad urbana**. Cada uno de los {{N_TEMAS_DETECTADOS|raw}} temas detectados se intenta cruzar
con un indicador municipal específico (carril bici per cápita, velocidad media de
calles, contenedores per cápita, m² verde/hab, paradas EMT, etc.). Cuando no
existe un indicador directo, el tema se mantiene en la matriz de demanda pero
**no entra en el índice de discrepancia**: preferimos cobertura honesta a una
proxy genérica repetida {{N_TEMAS_SIN_INDICADOR|raw}} veces. Resultado:
**{{N_TEMAS_CON_INDICADOR|raw}} de los {{N_TEMAS_DETECTADOS|raw}} temas** tienen un cuadrante medible,
**{{N_PARES_TOTAL|raw}} pares (distrito × tema) analizables**.

Principales conclusiones:

1. La participación ha crecido un **{{PCT_CRECIMIENTO_PROPUESTAS|pct0}}** entre la
   1ª edición ({{N_PROPUESTAS_ED1|raw}} propuestas) y la 7ª ({{N_PROPUESTAS_ED7|int}}
   propuestas), mientras la **tasa de selección global** queda en el
   **{{PCT_TASA_SELECCION|pct}}**. Más voz, mayor brecha de ejecución.

2. **El {{PCT_SILENCIO|pct0}} de los pares (distrito × tema) con cruce honesto
   muestra un patrón de "silencio sobre carencia observable"**:
   {{N_PARES_SILENCIO|raw}} de {{N_PARES_TOTAL|raw}} pares. El distrito presenta una
   carencia observable por encima de la media de la ciudad pero su demanda
   en Decidim queda por debajo. Es la situación más frecuente.

3. **{{N_DEMANDAS_ZOMBI|raw}} pares (distrito × tema) repiten propuestas en 4 o más
   ediciones consecutivas sin que ninguna haya sido seleccionada**, acumulando
   {{APOYOS_ZOMBI|int}} apoyos. Top por apoyos acumulados: Extramurs en carriles
   bici ({{EXTRAMURS_BICI_APOYOS|raw}} apoyos en {{EXTRAMURS_BICI_EDICIONES|raw}} ediciones,
   0 ejecuciones).

4. Los **carriles bici** son la demanda con mayor crecimiento entre 2015 y
   2023 (+{{BICI_CRECIMIENTO|raw}} propuestas, de {{BICI_ED1|raw}} a {{BICI_ED7|raw}}) y
   la categoría con más casos de demanda persistente sin selección.

5. **{{DISTRITO_VUL_MAX}} registra el índice de vulnerabilidad más alto
   de los {{N_DISTRITOS|raw}} distritos** ({{N_VUL_MAX|float2}} sobre 10) y aparece como
   "silencioso vulnerable" en **{{N_CAMPANAR_SILENCIOS|raw}} de los
   {{N_TEMAS_CON_INDICADOR|raw}} temas con indicador específico**, entre ellos:
   pacificación del tráfico (velocidad media de sus calles
   {{VEL_CAMPANAR|float}} km/h, la #{{CAMPANAR_VEL_RANK|raw}} más alta de la
   ciudad), recogida de residuos, equipamientos culturales, instalaciones
   deportivas, aparcamiento y equipamientos específicos.

6. La **8ª edición de DecidimVLC**, abierta en mayo de 2026 con un mecanismo
   nuevo de reequilibrio territorial, puede beneficiarse de estos hallazgos
   para corregir patrones acumulados desde hace casi una década.

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
València** (`opendata.vlci.valencia.es`). El pipeline consume en total una
fuente principal (Decidim), dos de geometría territorial (distritos y barrios),
un complemento demográfico (padrón 2022) y **{{N_DATASETS_REALIDAD|raw}} datasets de "realidad urbana"**
que alimentan los indicadores específicos del cruce con la demanda ciudadana:

| Tipo | Dataset | Rol en el análisis |
|---|---|---|
| Principal | `apoyo-propuestas-decidimvlc` | {{N_PROPUESTAS_BRUTAS|int}} propuestas con apoyos, edición, ámbito, presupuesto y selección. |
| Geometría | `districtes-distritos` | {{N_DISTRITOS|raw}} distritos administrativos. Unidad de análisis. |
| Geometría | `barris-barrios` | 88 barrios (sub-vista). |
| Demografía | Padrón municipal 2022 | {{POBLACION_TOTAL|int}} habitantes para normalizar per cápita. |
| Realidad | `vulnerabilidad-por-barrios` | Índices oficiales 2021 (equipamental, demográfico, económico, global). |
| Realidad | `equipamients-municipals` | {{N_EQUIPAMIENTOS|int}} equipamientos municipales con ubicación. |
| Realidad | `espais-verds` | {{N_ESPACIOS_VERDES|int}} jardines, parques y zonas verdes (m²). |
| Realidad | `itinerarios-ciclistas` | Red de carriles bici (longitud por tramo). |
| Realidad | `aparcaments-bicicletes` | {{N_APARCABICIS_PLAZAS|int}} plazas de aparcamiento para bicis. |
| Realidad | `parkings` | Parkings públicos ({{N_PARKING_PLAZAS|int}} plazas). |
| Realidad | `centros-educativos` | {{N_CENTROS_EDUCATIVOS|int}} colegios e institutos. |
| Realidad | `majors-mayores`, `joventut-juventud` | Recursos para personas mayores y juventud. |
| Realidad | `estacions-de-soroll` + `zones-zas` | Mediciones de ruido y zonas acústicamente saturadas. |
| Realidad | `falles-fallas` | {{N_FALLAS|int}} fallas (intensidad cultural). |
| Realidad | `velocitat-carrers` | Velocidad oficial en {{N_TRAMOS_CALLES|int}} tramos de calle. |
| Realidad | `contenidors-residus-solids` | {{N_CONTENEDORES|int}} contenedores de residuos. |
| Realidad | `catalogo-urbano` | {{N_BIC|int}} BIC/BRL/CH (patrimonio protegido). |
| Realidad | `emt` | {{N_PARADAS_EMT|int}} paradas de bus EMT. |
| Realidad | `fonts-daigua-publica` | {{N_FUENTES_AGUA|int}} fuentes de agua pública. |
| Realidad | `pipicans` | {{N_PIPICANS|int}} zonas caninas. |
| Realidad | `zones-jocs-infantils` | {{N_JUEGOS_INFANTILES|int}} zonas de juego infantil. |
| Realidad | `panells-informatius` + `mupis-ocoval` | {{N_PANELES|int}} paneles y mupis en vía pública. |
| Realidad | `zones-dactivitats` | Zonas de actividades (espacios públicos para uso vecinal). |

### 2.2 Pipeline

El análisis se construye en once scripts Python autocontenidos. La cadena
completa va desde la descarga reproducible hasta los JSON estáticos que sirven
la web:

```
01_download.py            → bajada de los {{N_DATASETS_TOTALES|raw}} datasets del manifiesto
02_load_and_normalize.py  → {{N_DISTRITOS|raw}} distritos (dissolve), resolución de
                            {{N_PROPUESTAS_BRUTAS|raw}} → {{N_PROPUESTAS_DISTRITO|raw}}
                            propuestas en distrito + {{N_PROPUESTAS_GLOBAL|raw}} globales
03_topic_modeling.py      → embeddings multilingües sobre {{N_PROPUESTAS_LEGIBLES|raw}}
                            títulos limpios + UMAP + HDBSCAN → 50 clusters
04_label_and_merge_topics → mapeo manual → {{N_TEMAS_DETECTADOS|raw}} temas legibles
05_matriz_demanda.py      → Matriz Demanda (distrito × tema), apoyos por
                            1.000 habitantes
06_matriz_realidad.py     → indicadores por distrito desde {{N_DATASETS_REALIDAD|raw}} datasets
07_indice_discrepancia.py → z-score(demanda) - z-score(carencia)
                            → 4 cuadrantes en {{N_TEMAS_CON_INDICADOR|raw}} temas
08_evolucion.py           → análisis longitudinal de 7 ediciones,
                            propuestas zombi, temas emergentes
09_export_to_web.py       → JSON estáticos (<260 KB total)
10_hallazgos.py           → 13 hallazgos verificables
11_numeros.py             → 80+ números clave a numeros.json
                            (single source of truth para informe/web)
```

Todo el código es libre (licencia MIT) y reproducible desde el repositorio
público.

### 2.3 Concepto: los cuatro cuadrantes

Para cada par (distrito × tema) calculamos:

- **Demanda Z**: z-score del nº de apoyos por 1.000 habitantes en ese tema
  dentro de ese distrito, comparado con la media de los {{N_DISTRITOS|raw}} distritos.
- **Carencia Z**: z-score del indicador de realidad correspondiente al tema,
  invirtiendo el signo cuando "más es mejor" (ej. más m² de verde = menos
  carencia).

La combinación genera cuatro cuadrantes:

| | **Poca carencia** | **Mucha carencia** |
|---|---|---|
| **Mucha demanda** | **Sobre-demandante** | **Demanda legítima** |
| **Poca demanda** | **Cómodo** | **Silencioso vulnerable** |

El cuadrante interesante es **Silencioso vulnerable**: los distritos donde
existe una carencia observable por encima de la media pero no aparece en
Decidim. Son los candidatos a acción proactiva del Ayuntamiento porque no
llegarán por sí solos a través del proceso participativo.

### 2.4 Indicadores de carencia por tema

De los {{N_TEMAS_DETECTADOS|raw}} temas detectados, **{{N_TEMAS_CON_INDICADOR|raw}} cuentan
con un indicador municipal directo** que permite calcular el cuadrante de
discrepancia. Cada tema se mapea contra una variable concreta del portal:

| Tema | Indicador específico |
|---|---|
| Carriles bici y movilidad ciclista | `m_carril_bici_per_1000hab` |
| Aparcamiento para vehículos | `plazas_parking_per_1000hab` |
| Pacificación del tráfico / Reducción de velocidad | `velocidad_media_kmh` ({{N_TRAMOS_CALLES|int}} tramos) |
| Transporte público (EMT) | `paradas_emt_per_1000hab` |
| Parques y plazas, Jardines, Zonas verdes | `m2_verde_per_hab` |
| Parques infantiles | `juegos_infantiles_per_1000hab` |
| Pipicanes y zonas caninas | `pipicans_per_1000hab` |
| Centros educativos | `centros_educativos_per_1000hab` |
| Centros de salud | `ind_equip` (vulnerabilidad equipamental) |
| Bibliotecas, equipamientos culturales, instalaciones deportivas, mobiliario, fuentes/aseos, equipamientos específicos | `equipamientos_per_1000hab` |
| Fuentes y aseos públicos | `fuentes_agua_per_1000hab` |
| Recogida de residuos | `contenedores_residuos_per_1000hab` ({{N_CONTENEDORES|int}} contenedores) |
| Paneles informativos | `paneles_total_per_1000hab` |
| Rehabilitación del patrimonio | `bic_per_1000hab` ({{N_BIC|int}} BIC/BRL/CH) |
| Reducción del ruido | `n_zonas_zas` (zonas acústicamente saturadas) |

**Los {{N_TEMAS_SIN_INDICADOR|raw}} temas restantes quedan fuera del índice de
discrepancia.** Son temas como aceras y movilidad peatonal, iluminación
pública, seguridad ciudadana, reurbanización de calles o rehabilitación de
mercados, para los que el portal no publica un indicador objetivo de carencia.
En una versión anterior del Atlas estos temas se cruzaban contra el índice de
vulnerabilidad global, pero esa proxy aplicada {{N_TEMAS_SIN_INDICADOR|raw}} veces
producía cuadrantes artificialmente repetidos (el mismo z-score atribuido a
temas muy distintos). Eliminarlos gana rigor sin perder cobertura: estos temas
siguen apareciendo en las fichas de distrito y en la matriz de demanda,
simplemente no se les asigna cuadrante de discrepancia.

Esta elección está documentada en `etl/07_indice_discrepancia.py` y es
auditable: cualquiera puede ampliar o sustituir el mapeo y recalcular los
cuadrantes.

La **tabla completa de trazabilidad** (qué dataset alimenta qué indicador y
qué tema usa ese indicador) está en `docs/DATASETS_USO.md` del repositorio,
generada automáticamente por `etl/12_trazabilidad.py`. Este script verifica
en cada ejecución que no haya desajustes entre lo declarado en MANIFEST,
lo documentado y el código real, y falla con error explícito si los
encuentra.

### 2.5 Limitaciones metodológicas

El proyecto se publica con sus límites explícitos:

- **El Atlas no mide la necesidad urbana en su totalidad.** Mide la
  discrepancia entre la demanda expresada en Decidim y un conjunto concreto de
  indicadores municipales abiertos. Carencias en salud, atención a mayores,
  seguridad subjetiva o bienestar emocional están parcial o totalmente fuera
  del alcance de los datasets disponibles.
- **Decidim no es una muestra representativa de la población.** Quien
  participa lo hace voluntariamente y tiende a estar más organizado y
  conectado. Por tanto, "demanda baja" no equivale necesariamente a "ausencia
  de necesidad".
- **Algunos temas usan vulnerabilidad equipamental como proxy.** Para "centros
  de salud" no existe un dataset de cobertura sanitaria por distrito, por lo
  que se usa el subíndice `ind_equip` de vulnerabilidad equipamental. Es una
  aproximación razonable, pero no equivalente a una métrica sanitaria directa.
- **La unidad de análisis es el distrito ({{N_DISTRITOS|raw}} unidades).** Distritos
  heterogéneos como Quatre Carreres o l'Eixample pueden tener bolsas de
  silencio internas que el agregado distrital esconde. La próxima iteración
  prevista cruzará a nivel sección censal.
- **El padrón municipal usado es de 2022.** Las cifras per cápita pueden
  variar ligeramente para ediciones de 2015-2019. El efecto sobre los
  cuadrantes es marginal.

Estas limitaciones no invalidan los hallazgos: los más fuertes —Campanar,
demandas persistentes sin selección, peso de "Toda la ciudad"— son robustos a
cambios razonables de metodología. Pero conviene tenerlas presentes al usar
el Atlas para diseño de política.

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

Los {{N_PARES_SILENCIO|raw}} pares (distrito × tema) con vulnerabilidad alta y demanda
baja identificados por este Atlas dibujan un mapa de prioridades para campañas
focalizadas: salas en centros culturales de Campanar, presencia en mercados de
Algirós y Rascanya, conexión con asociaciones vecinales de l'Olivereta. La voz
silenciosa no nace sola, hay que ir a buscarla.

### R2 · Acortar el embudo de las "demandas zombi"

{{N_DEMANDAS_ZOMBI|raw}} combinaciones de distrito × tema con cuatro o más ediciones
de demanda y cero ejecuciones constituyen un problema reputacional. Sin entrar
en por qué no se ejecutaron (puede haber razones técnicas o presupuestarias
legítimas), **la ciudadanía merece una respuesta razonada y pública sobre cada
caso**. Sin esa respuesta, el sistema acumula frustración.

### R3 · Reducir el peso de "Toda la ciudad"

El {{PCT_PROPUESTAS_GLOBAL|pct}} de las propuestas históricas se etiquetaron como
"Toda la ciudad" ({{N_PROPUESTAS_GLOBAL|int}} de {{N_PROPUESTAS_BRUTAS|int}}), lo que
las hace invisibles al mecanismo de reequilibrio territorial de la 8ª edición.
Forzar a quien propone a asignar un distrito —o crear una categoría
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
