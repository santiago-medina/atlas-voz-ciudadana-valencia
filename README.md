# Atlas de la Voz Ciudadana de València

> ¿La voz ciudadana refleja las carencias observables en los datos municipales
> de cada distrito?
>
> El Atlas cruza las **5.795 propuestas** vecinales registradas en
> Decidim VLC entre 2015 y 2023 (5.285 con título legible,
> 3.221 asignadas a distrito, 1.195 globales)
> con **22 datasets de realidad urbana** del Portal de Datos
> Abiertos para responder a esta pregunta.

**Proyecto presentado a los Premios de Proyectos de Datos Abiertos y Periodismo de Datos del Ayuntamiento de València · Edición 2026.**

- **Web interactiva**: https://santiago-medina.github.io/atlas-voz-ciudadana-valencia/
- **Repositorio**: este mismo
- **Licencia**: MIT (código) · datos sujetos a la licencia del Portal de Datos Abiertos del Ayuntamiento

> Todos los números de este README, de la web, del informe técnico y de la
> memoria resumen salen de un único archivo computado por el pipeline
> (`data/processed/numeros.json` generado por `etl/11_numeros.py`). Nada
> escrito a mano.

---

## La idea en una imagen

Cada par (distrito × tema) se sitúa en uno de cuatro cuadrantes:

| | **Poca carencia** | **Mucha carencia** |
|---|---|---|
| **Mucha demanda** | Sobre-demandante | **Demanda legítima** |
| **Poca demanda** | Cómodo | **Silencioso vulnerable** ← clave |

El cuadrante interesante es el de los **silenciosos vulnerables**: distritos
con carencia objetiva por encima de la media pero demanda en Decidim por
debajo. Es el cuadrante más numeroso (46% de los
437 pares analizados) y el que requiere acción proactiva: no
llegará por sí solo a través del proceso participativo.

## Tres hallazgos para abrir boca

1. **Campanar**, el distrito con mayor vulnerabilidad oficial
   (índice 3,77) → aparece como silencioso vulnerable en
   **6 de los 23 temas con
   indicador municipal específico**, incluido el más rotundo: su velocidad
   media en calles es 38,3 km/h (la #2
   más alta de la ciudad) y, sin embargo, no figura en el top de demanda de
   "pacificación del tráfico".
2. **28 pares (distrito × tema) repiten propuestas en
   4+ ediciones consecutivas sin ninguna selección**. Caso destacado:
   Extramurs, carriles bici, 1.098 apoyos acumulados,
   0 ejecuciones.
3. **El embudo presupuestario**: la ciudadanía solicitó
   234 M €; se seleccionaron
   58 M €. Por cada euro ejecutado se pidieron
   4,0 €, y el 75% de la inversión
   propuesta no se ha convertido en proyecto seleccionado.

Los **13 hallazgos** completos están en [`docs/03_hallazgos.md`](docs/03_hallazgos.md)
y en el [informe técnico](informe/informe.pdf).

## Datasets utilizados

Todos del [Portal de Datos Abiertos del Ayuntamiento de València](https://opendata.vlci.valencia.es/):

- `apoyo-propuestas-decidimvlc` (fuente principal, 5.795 propuestas)
- `districtes-distritos` + `barris-barrios` (geometrías)
- `vulnerabilidad-por-barrios` (índices oficiales 2021)
- `equipamients-municipals` (2.840), `espais-verds` (805),
  `itinerarios-ciclistas`, `aparcaments-bicicletes` (23.558 plazas),
  `parkings` (9.932 plazas)
- `velocitat-carrers` (12.872 tramos), `contenidors-residus-solids`
  (20.612 contenedores), `emt` (1.092 paradas)
- `catalogo-urbano` (929 BIC/BRL/CH), `fonts-daigua-publica`
  (826 fuentes), `pipicans` (433),
  `zones-jocs-infantils` (493), `panells-informatius` + `mupis-ocoval`
- `centros-educativos` (520), `majors-mayores`, `joventut-juventud`
- `estacions-de-soroll`, `zones-zas`
- `falles-fallas` (349)

Manifest completo en [`data/raw/MANIFEST.json`](data/raw/MANIFEST.json).
Adicionalmente se usa el **padrón municipal 2022** (807.396
habitantes) para normalizar todos los indicadores per cápita.

**Trazabilidad completa de cómo se usa cada dataset (qué columna genera, qué
indicador alimenta, qué temas se cruzan con él) en
[`docs/DATASETS_USO.md`](docs/DATASETS_USO.md).** El documento se genera
automáticamente con `python etl/12_trazabilidad.py` y verifica la coherencia
entre lo declarado en MANIFEST, lo documentado y el código real.

## Estructura del repo

```
atlas-voz-ciudadana-valencia/
├── data/
│   ├── raw/                # Datasets originales (gitignored, regenerables)
│   │   └── MANIFEST.json
│   └── processed/          # Outputs intermedios + JSON listos para la web
│       └── numeros.json    # ← single source of truth de todas las cifras
├── etl/                    # Pipeline Python (11 scripts numerados)
│   ├── 01_download.py
│   ├── 02_load_and_normalize.py
│   ├── 03_topic_modeling.py
│   ├── 04_label_and_merge_topics.py
│   ├── 05_matriz_demanda.py
│   ├── 06_matriz_realidad.py
│   ├── 07_indice_discrepancia.py
│   ├── 08_evolucion.py
│   ├── 09_export_to_web.py
│   ├── 10_hallazgos.py
│   └── 11_numeros.py
├── web/                    # Next.js (static export → GitHub Pages)
├── informe/
│   ├── informe.md/.pdf     # Informe técnico de 15+ págs (plantilla con placeholders)
│   ├── MEMORIA_RESUMEN.*   # Memoria oficial para el trámite AD.TR.15
│   ├── build_informe.py    # md (plantilla) → html → pdf con números reales
│   ├── guion_video.md      # Guion del vídeo demo de 90s
│   └── screenshots/        # Capturas estáticas de la web (Playwright)
├── README.template.md      # Plantilla del README con placeholders
└── docs/                   # Notas metodológicas
```

## Reproducir todo el pipeline

```bash
git clone https://github.com/santiago-medina/atlas-voz-ciudadana-valencia.git
cd atlas-voz-ciudadana-valencia

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Pipeline ETL (tarda ~4 minutos en una máquina estándar)
python etl/01_download.py
python etl/repaginate_truncated.py
python etl/02_load_and_normalize.py
python etl/03_topic_modeling.py
python etl/04_label_and_merge_topics.py
python etl/05_matriz_demanda.py
python etl/06_matriz_realidad.py
python etl/07_indice_discrepancia.py
python etl/08_evolucion.py
python etl/09_export_to_web.py
python etl/10_hallazgos.py
python etl/11_numeros.py        # ← genera numeros.json

# Informe técnico + memoria + README (todos desde plantilla + numeros.json)
python informe/build_informe.py

# Web (opcional, GitHub Actions la publica automáticamente)
cd web && npm install && npm run build
```

## Stack

- **Análisis**: Python · Pandas · GeoPandas · scikit-learn · sentence-transformers · UMAP · HDBSCAN
- **Geoespacial**: GeoPandas en EPSG:25830 para distancias/áreas (no requiere PostGIS)
- **Web**: Next.js 14 (static export) · Leaflet · tiles CartoDB
- **Hosting**: GitHub Pages · **coste recurrente: 0 €**

## Encaje con los criterios del jurado

| Criterio | Cómo lo cubre |
|---|---|
| **Innovación** | Cruce inédito Decidim + 22 datasets municipales · topic modeling automático · índice de discrepancia z-score con indicadores específicos por tema |
| **Impacto social** | Identifica los silenciosos vulnerables → recomendaciones directas para la 8ª edición en curso |
| **Viabilidad** | Producto desplegado en Pages · pipeline reproducible en <5 min · sin dependencias propietarias |
| **Colaboración** | Código y datos abiertos (MIT) · diseñado para que asociaciones, prensa o investigación puedan extenderlo |

## Próximos pasos previstos

- Re-ejecutar el pipeline cuando se publique la 8ª edición de DecidimVLC
  (previsiblemente 2027).
- Cruzar también a nivel sección censal para detectar bolsas de silencio
  dentro de distritos heterogéneos.
- Validación cualitativa: entrevistas en los distritos con más patrones de
  silencio vulnerable.

---

**Atlas de la Voz Ciudadana de València · Mayo 2026 · Santiago Medina**
