# Atlas de la Voz Ciudadana de València

> Análisis cruzado entre las **5.285 propuestas vecinales** presentadas a Decidim VLC (2015-2023) y los **datasets municipales** del Portal de Datos Abiertos del Ayuntamiento de València, para responder a una pregunta:
>
> **¿La voz ciudadana refleja las carencias reales de cada barrio?**

Proyecto presentado a los **Premios de Proyectos de Datos Abiertos y Periodismo de Datos del Ayuntamiento de València, edición 2026** (categoría Datos Abiertos).

## Idea

Cruzamos lo que cada barrio **pide** (propuestas a presupuestos participativos, ponderadas por apoyos ciudadanos) con lo que cada barrio **tiene** (ruido, espacios verdes, vulnerabilidad, equipamientos, accesibilidad…). El resultado es un mapa que clasifica cada barrio × tema en cuatro cuadrantes:

| | **Poca carencia** | **Mucha carencia** |
|---|---|---|
| **Mucha demanda** | Sobre-demandante | Demanda legítima |
| **Poca demanda** | Cómodo | **Silencioso vulnerable** |

El cuadrante interesante es el de los *silenciosos vulnerables*: barrios que no se hacen oír y sin embargo tienen las mayores carencias objetivas. Esa es la principal contribución del proyecto.

## Datasets

Todos los datos provienen del [Portal de Datos Abiertos del Ayuntamiento de València](https://opendata.vlci.valencia.es/). El manifiesto completo está en [`data/raw/MANIFEST.json`](data/raw/MANIFEST.json).

Para descargar todos los datasets en bruto:

```bash
python etl/01_download.py
```

## Estructura del repo

```
atlas-voz-ciudadana-valencia/
├── data/
│   ├── raw/          # Datasets originales (gitignored, regenerables)
│   └── processed/    # Outputs intermedios del análisis
├── etl/              # Scripts Python de ingesta y análisis
├── web/              # Next.js + Leaflet (publicado en GitHub Pages)
├── informe/          # Informe PDF tipo periodismo de datos
└── docs/             # Documentación de metodología
```

## Stack

- **Análisis**: Python + Pandas + GeoPandas + scikit-learn + PostgreSQL/PostGIS local.
- **Web**: Next.js (static export) + Leaflet + tiles CartoDB.
- **Hosting**: GitHub Pages. Coste recurrente: 0 €.

## Licencia

Código bajo [MIT](LICENSE). Los datos provienen del Portal de Datos Abiertos del Ayuntamiento de València y mantienen su licencia original.
