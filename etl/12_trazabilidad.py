"""
12_trazabilidad.py — Tabla única de uso de datasets.

Documenta de forma trazable cómo se usa cada dataset del MANIFEST. Genera:
  - docs/DATASETS_USO.md   (humano)
  - data/processed/datasets_uso.json   (máquina)

El mapeo dataset → columna(s) generadas y dataset → indicador final está
declarado explícitamente abajo en DATASET_TO_OUTPUT. Esto es preferible
a un parser AST automático: más mantenible y auditable.

El script VERIFICA dos cosas:
  1. Que cada filename declarado en DATASET_TO_OUTPUT está en el MANIFEST.
  2. Que cada indicador declarado figura en TEMA_TO_INDICADORES de
     07_indice_discrepancia.py (o se marca explícitamente como contexto).
Si algo no encaja, el script falla y avisa.
"""

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
DOCS = ROOT / "docs"


# Relación declarada explícitamente entre cada dataset y lo que produce.
# Formato:
#   filename → {
#     "columnas":    columnas de matriz_realidad.csv que origina este dataset,
#     "indicador":   nombre del indicador final (en TEMA_TO_INDICADORES); None si
#                    el dataset es solo de contexto y no entra al índice.
#   }
DATASET_TO_OUTPUT: dict[str, dict] = {
    # Decidim
    "decidim.csv": {
        "columnas": ["(propuestas, apoyos, seleccionadas, edicion, distrito, presupuesto)"],
        "indicador": None,
        "uso": "Fuente principal — alimenta la Matriz de Demanda. No es un indicador de carencia.",
    },

    # Geometría
    "distritos.geojson": {
        "columnas": ["id_distrito", "nombre_distrito", "geometry"],
        "indicador": None,
        "uso": "Geometría base — 19 distritos como unidad de análisis (dissolve aplicado).",
    },
    "barrios.geojson": {
        "columnas": ["id_barrio", "nombre_barrio", "geometry"],
        "indicador": None,
        "uso": "Geometría auxiliar — 88 barrios para sub-vista futura.",
    },
    "poblacion_manzanas.geojson": {
        "columnas": [],
        "indicador": None,
        "uso": "Descargado pero descartado: el GeoJSON del portal no trae población. Se usa el Padrón 2022 transcrito como dataset derivado.",
    },

    # Datasets de realidad — con indicador en cruce
    "vulnerabilidad.geojson": {
        "columnas": ["ind_equip", "ind_dem", "ind_econom", "ind_global"],
        "indicador": "ind_equip",
        "uso": "Cruce: ind_equip alimenta el tema 'Centros de salud' (no hay dataset municipal directo de cobertura sanitaria).",
    },
    "espacios_verdes.geojson": {
        "columnas": ["m2_espacios_verdes", "n_jardines", "m2_verde_per_hab"],
        "indicador": "m2_verde_per_hab",
        "uso": "Cruce: m2_verde_per_hab alimenta los temas 'Parques y plazas', 'Jardines y arbolado' y 'Zonas verdes'.",
    },
    "equipamientos.geojson": {
        "columnas": ["n_equipamientos", "equipamientos_per_1000hab"],
        "indicador": "equipamientos_per_1000hab",
        "uso": "Cruce: equipamientos_per_1000hab alimenta varios temas culturales/sociales (bibliotecas, equipamientos culturales, centros cívicos, instalaciones deportivas, mobiliario deportivo, equipamientos específicos).",
    },
    "centros_educativos.geojson": {
        "columnas": ["n_centros_educativos", "centros_educativos_per_1000hab"],
        "indicador": "centros_educativos_per_1000hab",
        "uso": "Cruce: centros_educativos_per_1000hab alimenta el tema 'Centros educativos'.",
    },
    "itinerarios_ciclistas.geojson": {
        "columnas": ["m_carril_bici", "m_carril_bici_per_1000hab"],
        "indicador": "m_carril_bici_per_1000hab",
        "uso": "Cruce: m_carril_bici_per_1000hab alimenta el tema 'Carriles bici y movilidad ciclista'.",
    },
    "parkings.geojson": {
        "columnas": ["n_plazas_parking", "plazas_parking_per_1000hab"],
        "indicador": "plazas_parking_per_1000hab",
        "uso": "Cruce: plazas_parking_per_1000hab alimenta el tema 'Aparcamiento para vehículos'.",
    },
    "velocidad_calles.geojson": {
        "columnas": ["velocidad_media_kmh"],
        "indicador": "velocidad_media_kmh",
        "uso": "Cruce: velocidad_media_kmh alimenta los temas 'Pacificación del tráfico' y 'Reducción de velocidad y zonas 30'.",
    },
    "emt_paradas.geojson": {
        "columnas": ["n_paradas_emt", "paradas_emt_per_1000hab"],
        "indicador": "paradas_emt_per_1000hab",
        "uso": "Cruce: paradas_emt_per_1000hab alimenta el tema 'Transporte público (EMT)'.",
    },
    "contenedores_residuos.geojson": {
        "columnas": ["n_contenedores_residuos", "contenedores_residuos_per_1000hab"],
        "indicador": "contenedores_residuos_per_1000hab",
        "uso": "Cruce: contenedores_residuos_per_1000hab alimenta el tema 'Recogida de residuos'.",
    },
    "paneles_informativos.geojson": {
        "columnas": ["n_paneles_total (suma con mupis)"],
        "indicador": "paneles_total_per_1000hab",
        "uso": "Cruce: combinado con mupis.geojson genera paneles_total_per_1000hab, indicador del tema 'Paneles informativos'.",
    },
    "mupis.geojson": {
        "columnas": ["n_paneles_total (suma con paneles_informativos)"],
        "indicador": "paneles_total_per_1000hab",
        "uso": "Cruce: combinado con paneles_informativos.geojson genera paneles_total_per_1000hab.",
    },
    "patrimonio_urbano.geojson": {
        "columnas": ["n_bic", "bic_per_1000hab"],
        "indicador": "bic_per_1000hab",
        "uso": "Cruce: bic_per_1000hab alimenta el tema 'Rehabilitación del patrimonio'.",
    },
    "fuentes_agua.geojson": {
        "columnas": ["n_fuentes_agua", "fuentes_agua_per_1000hab"],
        "indicador": "fuentes_agua_per_1000hab",
        "uso": "Cruce: fuentes_agua_per_1000hab alimenta el tema 'Fuentes y aseos públicos'.",
    },
    "pipicans.geojson": {
        "columnas": ["n_pipicans", "pipicans_per_1000hab"],
        "indicador": "pipicans_per_1000hab",
        "uso": "Cruce: pipicans_per_1000hab alimenta el tema 'Pipicanes y zonas caninas'.",
    },
    "juegos_infantiles.geojson": {
        "columnas": ["n_juegos_infantiles", "juegos_infantiles_per_1000hab"],
        "indicador": "juegos_infantiles_per_1000hab",
        "uso": "Cruce: juegos_infantiles_per_1000hab alimenta el tema 'Parques infantiles'.",
    },
    "zones_zas.geojson": {
        "columnas": ["n_zonas_zas"],
        "indicador": "n_zonas_zas",
        "uso": "Cruce: n_zonas_zas alimenta el tema 'Reducción del ruido'.",
    },

    # Datasets de contexto — sin indicador en cruce
    "estaciones_ruido.geojson": {
        "columnas": ["n_estaciones_ruido"],
        "indicador": None,
        "uso": "Contexto: solo 4 estaciones físicas, demasiado pocas para indicador. Se cuenta en fichas de distrito.",
    },
    "aparcabicis.geojson": {
        "columnas": ["n_plazas_aparcabici", "plazas_aparcabici_per_1000hab"],
        "indicador": None,
        "uso": "Contexto: las plazas de aparcabicis aparecen como dato secundario en fichas de distrito. El tema relacionado ('Carriles bici') cruza con m_carril_bici_per_1000hab, indicador más relevante.",
    },
    "mayores.geojson": {
        "columnas": ["n_recursos_mayores", "recursos_mayores_per_1000hab"],
        "indicador": None,
        "uso": "Contexto: no existe tema Decidim específico de 'recursos para mayores'. Se cuenta en fichas como información complementaria.",
    },
    "juventud.geojson": {
        "columnas": ["n_recursos_juventud", "recursos_juventud_per_1000hab"],
        "indicador": None,
        "uso": "Contexto: análogo a 'mayores'. Aparece en fichas de distrito.",
    },
    "fallas.geojson": {
        "columnas": ["n_fallas", "fallas_per_1000hab"],
        "indicador": None,
        "uso": "Contexto: 351 fallas geolocalizadas. Información cultural complementaria en fichas de distrito.",
    },
    "zonas_actividades.geojson": {
        "columnas": ["n_zonas_actividades", "zonas_actividades_per_1000hab"],
        "indicador": None,
        "uso": "Contexto: contado por distrito pero no se usa como indicador específico de carencia.",
    },
}


def parse_indicador_to_tema() -> dict[str, list[str]]:
    """Extrae { indicador → [temas] } desde TEMA_TO_INDICADORES en
    07_indice_discrepancia.py mediante AST. Soporta tanto Assign como AnnAssign
    (asignación con anotación de tipo)."""
    code = (ROOT / "etl" / "07_indice_discrepancia.py").read_text(encoding="utf-8")
    tree = ast.parse(code)
    out: dict[str, list[str]] = {}

    def process_dict(value_node: ast.AST) -> None:
        if not isinstance(value_node, ast.Dict):
            return
        for k, v in zip(value_node.keys, value_node.values):
            if isinstance(k, ast.Constant) and isinstance(v, ast.Dict):
                tema = k.value
                col = next(
                    (vv.value for kk, vv in zip(v.keys, v.values)
                     if isinstance(kk, ast.Constant) and kk.value == "col"
                     and isinstance(vv, ast.Constant)),
                    None,
                )
                if col:
                    out.setdefault(col, []).append(tema)

    for node in ast.walk(tree):
        # Assign (sin anotación): TEMA_TO_INDICADORES = {...}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TEMA_TO_INDICADORES":
                    process_dict(node.value)
        # AnnAssign (con anotación): TEMA_TO_INDICADORES: dict[...] = {...}
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "TEMA_TO_INDICADORES":
                if node.value is not None:
                    process_dict(node.value)
    return {k: sorted(set(v)) for k, v in out.items()}


def main() -> None:
    manifest = json.loads((RAW / "MANIFEST.json").read_text(encoding="utf-8"))
    indicador_a_temas = parse_indicador_to_tema()

    # Validaciones cruzadas
    declared_filenames = {d["filename"] for d in manifest["datasets"]}
    documented = set(DATASET_TO_OUTPUT.keys())

    # 1. ¿Algún dataset del MANIFEST sin documentar?
    sin_documentar = declared_filenames - documented
    # Eliminamos los que no se descargan (decidim viene de RAW directo, distritos.geojson es procesado, etc.)
    sin_documentar = {f for f in sin_documentar if f not in {"decidim.csv"}}

    # 2. ¿Algún documentado que no esté en MANIFEST?
    fantasma = documented - declared_filenames - {"decidim.csv", "distritos.geojson", "barrios.geojson", "poblacion_manzanas.geojson"}

    # 3. ¿Indicador declarado que no exista en TEMA_TO_INDICADORES?
    indicadores_documentados = {v["indicador"] for v in DATASET_TO_OUTPUT.values() if v["indicador"]}
    indicadores_codigo = set(indicador_a_temas.keys())
    indicadores_fantasma = indicadores_documentados - indicadores_codigo

    if sin_documentar or fantasma or indicadores_fantasma:
        print("✗ DESAJUSTES detectados:")
        if sin_documentar:
            print(f"  Datasets en MANIFEST sin documentar en DATASET_TO_OUTPUT: {sin_documentar}")
        if fantasma:
            print(f"  Documentados pero NO en MANIFEST: {fantasma}")
        if indicadores_fantasma:
            print(f"  Indicadores documentados pero NO en TEMA_TO_INDICADORES: {indicadores_fantasma}")
        raise SystemExit(1)

    print(f"✓ Coherencia verificada: {len(DATASET_TO_OUTPUT)} datasets documentados")
    print(f"  → {sum(1 for d in DATASET_TO_OUTPUT.values() if d['indicador'])} alimentan un indicador en cruce")
    print(f"  → {sum(1 for d in DATASET_TO_OUTPUT.values() if not d['indicador'] and d.get('columnas'))} son contexto (columnas pero sin cruce)")

    # Generar tablas
    rows = []
    for fname, info in DATASET_TO_OUTPUT.items():
        # Encontrar metadatos del MANIFEST si aplica
        m = next((d for d in manifest["datasets"] if d["filename"] == fname), None)
        ds_id = m["id"] if m else fname.replace(".geojson", "").replace(".csv", "")
        titulo = m["title"] if m else fname
        url = m["url"] if m else ""
        role = m["role"] if m else "interno"

        ind = info["indicador"]
        temas = indicador_a_temas.get(ind, []) if ind else []

        rows.append({
            "filename": fname,
            "id": ds_id,
            "titulo": titulo,
            "role": role,
            "url": url,
            "columnas_generadas": info["columnas"],
            "indicador_en_cruce": ind,
            "temas_que_usan_ese_indicador": temas,
            "uso": info["uso"],
        })

    (PROC / "datasets_uso.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Estadísticas
    n_cruce = sum(1 for r in rows if r["indicador_en_cruce"])
    n_contexto = sum(1 for r in rows if not r["indicador_en_cruce"] and r["columnas_generadas"])
    n_geom = sum(1 for r in rows if r["role"].startswith("geometry"))
    n_principal = sum(1 for r in rows if r["filename"] == "decidim.csv")

    md = [
        "# Trazabilidad de datasets: cómo usa el Atlas cada uno",
        "",
        "> **Documento generado automáticamente por `etl/12_trazabilidad.py`.**",
        "> Refleja el estado real del pipeline. Para regenerarlo: `python etl/12_trazabilidad.py`.",
        "> El script falla si encuentra un desajuste entre lo documentado, el MANIFEST y el código real.",
        "",
        "## Resumen",
        "",
        f"- **{len(rows)} datasets documentados** del Portal de Datos Abiertos del Ayuntamiento de València.",
        f"- **{n_principal} dataset principal** (Decidim) que alimenta la Matriz de Demanda.",
        f"- **{n_geom} datasets de geometría base** (distritos, barrios) como unidades de análisis.",
        f"- **{n_cruce} datasets alimentan un indicador específico en el índice de discrepancia.**",
        f"- **{n_contexto} datasets se usan como contexto** en fichas de distrito (no entran en cuadrantes).",
        "",
        "Categorías de uso definidas:",
        "",
        "1. **Cruce honesto**: el dataset genera una columna que se usa como indicador en "
        "`TEMA_TO_INDICADORES` de `etl/07_indice_discrepancia.py` para clasificar al menos un "
        "tema en los cuatro cuadrantes (silencio sobre carencia observable, demanda alineada, "
        "demanda por encima del indicador, sin carencia ni demanda destacadas).",
        "2. **Contexto**: el dataset se carga, se cuentan sus features por distrito y los "
        "conteos aparecen en las fichas de distrito como información complementaria. NO se "
        "usa para clasificar cuadrantes.",
        "3. **Geometría base**: distritos y barrios, usados como unidades de análisis.",
        "",
        "## Tabla completa de uso por dataset",
        "",
        "| Dataset (id en portal) | Categoría | Columnas que genera | Indicador en cruce | Temas que usan ese indicador |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        categoria = (
            "Cruce honesto" if r["indicador_en_cruce"]
            else "Geometría base" if r["role"].startswith("geometry")
            else "Fuente principal" if r["filename"] == "decidim.csv"
            else "Contexto" if r["columnas_generadas"]
            else "Descartado"
        )
        cols_str = "<br>".join(f"`{c}`" for c in r["columnas_generadas"]) or "—"
        ind_str = f"`{r['indicador_en_cruce']}`" if r["indicador_en_cruce"] else "—"
        temas_str = "<br>".join(r["temas_que_usan_ese_indicador"]) or "—"
        md.append(
            f"| **{r['id']}** | {categoria} | {cols_str} | {ind_str} | {temas_str} |"
        )

    md += [
        "",
        "## Notas detalladas por dataset",
        "",
    ]
    for r in rows:
        md.append(f"### `{r['id']}`")
        md.append("")
        md.append(f"- **Fichero**: `{r['filename']}`")
        md.append(f"- **Rol declarado en MANIFEST**: `{r['role']}`")
        if r["url"]:
            md.append(f"- **URL del recurso**: {r['url']}")
        md.append(f"- **Uso real en el pipeline**: {r['uso']}")
        md.append("")

    md += [
        "## Verificación de coherencia",
        "",
        "El script `etl/12_trazabilidad.py` realiza tres comprobaciones automáticas y falla si",
        "encuentra un desajuste:",
        "",
        "1. **MANIFEST ↔ Documentación**: que cada dataset declarado en `data/raw/MANIFEST.json` "
        "esté documentado aquí.",
        "2. **Documentación ↔ Código**: que cada indicador mencionado en este documento exista "
        "en el mapeo `TEMA_TO_INDICADORES` de `etl/07_indice_discrepancia.py`.",
        "3. **Documentación ↔ MANIFEST**: que no haya datasets documentados que no se "
        "descarguen realmente.",
        "",
        "Esta verificación corre cada vez que se regenera el pipeline, por lo que cualquier",
        "drift entre lo declarado y lo implementado se detecta de inmediato.",
    ]

    (DOCS / "DATASETS_USO.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nGenerados:")
    print(f"  - docs/DATASETS_USO.md ({(DOCS / 'DATASETS_USO.md').stat().st_size / 1024:.1f} KB)")
    print(f"  - data/processed/datasets_uso.json ({(PROC / 'datasets_uso.json').stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
