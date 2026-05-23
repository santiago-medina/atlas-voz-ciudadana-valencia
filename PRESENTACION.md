# Presentación al concurso

## Materiales a entregar en la Sede Electrónica

Trámite: **AD.TR.15** · Premios para proyectos de datos abiertos y periodismo
de datos del Ayuntamiento de València, edición 2026.

Plazo: **2026-05-08 → 2026-06-08**.

### Documentos obligatorios

1. **Solicitud normalizada** (Anexo I del trámite) — rellenar y firmar
   electrónicamente.
2. **Declaración responsable** (Anexo II) — rellenar y firmar.
3. **Autorizaciones para el acceso a datos personales** (Anexo III) —
   solo si aplica.
4. **Memoria resumen del proyecto** — `informe/MEMORIA_RESUMEN.pdf`
   (este repo).
5. **El proyecto en sí** — los siguientes elementos:
   - **URL del proyecto desplegado**:
     `https://santiago-medina.github.io/atlas-voz-ciudadana-valencia/`
   - **Repositorio de código y datos**:
     `https://github.com/santiago-medina/atlas-voz-ciudadana-valencia`
   - **Informe técnico completo**: `informe/informe.pdf`

### Cómo subirlo

1. Acceder a `https://sede.valencia.es/sede/registro/procedimiento/AD.TR.15`
2. Identificarse con certificado digital o Cl@ve.
3. Iniciar el trámite "Solicitud premios para proyectos de datos abiertos y
   periodismo de datos".
4. Adjuntar los PDF/documentos del paso anterior.
5. Firmar y registrar. Guardar el justificante de registro.

## Materiales del proyecto generados en este repo

| Archivo | Tamaño | Descripción |
|---|---|---|
| `informe/MEMORIA_RESUMEN.pdf` | ~60 KB | Memoria resumen (3-4 págs) |
| `informe/informe.pdf` | ~85 KB | Informe técnico completo (15+ págs) |
| `web/public/data/` | ~260 KB | Datasets procesados (JSON) |
| `data/processed/` | ~3 MB | Outputs intermedios del análisis |

## Para regenerar todo

```bash
# 1. Crear entorno y dependencias
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Pipeline ETL (descarga + análisis)
python etl/01_download.py
python etl/02_load_and_normalize.py
python etl/repaginate_truncated.py     # bypass ArcGIS 2000-cap
python etl/02_load_and_normalize.py    # rerun con datos completos
python etl/03_topic_modeling.py
python etl/04_label_and_merge_topics.py
python etl/05_matriz_demanda.py
python etl/06_matriz_realidad.py
python etl/07_indice_discrepancia.py
python etl/08_evolucion.py
python etl/09_export_to_web.py
python etl/10_hallazgos.py

# 3. Informes PDF
python informe/build_informe.py

# 4. Build de la web (opcional, GitHub Actions lo hace automático)
cd web && npm install && npm run build
```

Tiempo total del pipeline: ~4 minutos en una máquina estándar.
