# Atlas de la Voz Ciudadana de València

> ¿La voz ciudadana refleja las carencias reales de cada distrito?
>
> El Atlas cruza las **5.285 propuestas** vecinales presentadas a Decidim VLC
> entre 2015 y 2023 con **once datasets municipales** del Portal de Datos
> Abiertos para responder a esta pregunta.

**Proyecto presentado a los Premios de Proyectos de Datos Abiertos y Periodismo de Datos del Ayuntamiento de València · Edición 2026.**

- **Web interactiva**: https://santiago-medina.github.io/atlas-voz-ciudadana-valencia/
- **Repositorio**: este mismo
- **Licencia**: MIT (código) · datos sujetos a la licencia del Portal de Datos Abiertos del Ayuntamiento

---

## La idea en una imagen

Cada par (distrito × tema) se sitúa en uno de cuatro cuadrantes:

| | **Poca carencia** | **Mucha carencia** |
|---|---|---|
| **Mucha demanda** | Sobre-demandante | **Demanda legítima** |
| **Poca demanda** | Cómodo | **Silencioso vulnerable** ← clave |

El cuadrante interesante es el de los **silenciosos vulnerables**: distritos
con carencia objetiva por encima de la media pero demanda en Decidim por
debajo. Es el cuadrante más numeroso (39% de los 722 pares analizados) y el
que requiere acción proactiva: no llegará por sí solo a través del proceso
participativo.

## Tres hallazgos para abrir boca

1. **Campanar**, máxima vulnerabilidad oficial (índice 3,77) → aparece como
   silencioso vulnerable en **10 temas distintos**.
2. **28 demandas zombi**: combinaciones (distrito × tema) que se repiten 4+
   ediciones sin que se haya seleccionado ninguna. El caso top: Extramurs,
   carriles bici, 1.098 apoyos acumulados, 0 ejecuciones.
3. **El embudo presupuestario**: por cada euro que el Ayuntamiento ejecutó,
   la ciudadanía pidió 4. Casi el 80 % de la inversión solicitada no se ha
   convertido en proyecto.

Los **13 hallazgos** completos están en [`docs/03_hallazgos.md`](docs/03_hallazgos.md)
y en el [informe técnico](informe/informe.pdf).

## Datasets utilizados

Todos del [Portal de Datos Abiertos del Ayuntamiento de València](https://opendata.vlci.valencia.es/):

- `apoyo-propuestas-decidimvlc` (fuente principal)
- `districtes-distritos` + `barris-barrios` (geometrías)
- `vulnerabilidad-por-barrios` (índices oficiales 2021)
- `equipamients-municipals`, `espais-verds`, `itinerarios-ciclistas`,
  `aparcaments-bicicletes`, `parkings`
- `centros-educativos`, `majors-mayores`, `joventut-juventud`
- `estacions-de-soroll`, `zones-zas`
- `falles-fallas`

Manifest completo en [`data/raw/MANIFEST.json`](data/raw/MANIFEST.json).
Adicionalmente se usa el **padrón municipal 2022** (807.396 habitantes) para
normalizar todos los indicadores per cápita.

## Estructura del repo

```
atlas-voz-ciudadana-valencia/
├── data/
│   ├── raw/                # Datasets originales (gitignored, regenerables)
│   │   └── MANIFEST.json
│   └── processed/          # Outputs intermedios + JSON listos para la web
├── etl/                    # Pipeline Python (10 scripts numerados)
│   ├── 01_download.py
│   ├── 02_load_and_normalize.py
│   ├── 03_topic_modeling.py
│   ├── 04_label_and_merge_topics.py
│   ├── 05_matriz_demanda.py
│   ├── 06_matriz_realidad.py
│   ├── 07_indice_discrepancia.py
│   ├── 08_evolucion.py
│   ├── 09_export_to_web.py
│   └── 10_hallazgos.py
├── web/                    # Next.js (static export → GitHub Pages)
├── informe/
│   ├── informe.md/.pdf     # Informe técnico de 15+ págs
│   ├── MEMORIA_RESUMEN.*   # Memoria oficial para el trámite AD.TR.15
│   ├── build_informe.py    # md → html → pdf con pandoc + wkhtmltopdf
│   ├── guion_video.md      # Guion del vídeo demo de 90s
│   └── screenshots/        # Capturas estáticas de la web (Playwright)
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

# Informe técnico + memoria
python informe/build_informe.py

# Web (opcional — GitHub Actions la publica automáticamente)
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
| **Innovación** | Cruce inédito Decidim + 11 datasets · topic modeling automático · índice de discrepancia z-score |
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
