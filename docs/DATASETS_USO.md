# Trazabilidad de datasets: cómo usa el Atlas cada uno

> **Documento generado automáticamente por `etl/12_trazabilidad.py`.**
> Refleja el estado real del pipeline. Para regenerarlo: `python etl/12_trazabilidad.py`.
> El script falla si encuentra un desajuste entre lo documentado, el MANIFEST y el código real.

## Resumen

- **26 datasets documentados** del Portal de Datos Abiertos del Ayuntamiento de València.
- **1 dataset principal** (Decidim) que alimenta la Matriz de Demanda.
- **2 datasets de geometría base** (distritos, barrios) como unidades de análisis.
- **16 datasets alimentan un indicador específico en el índice de discrepancia.**
- **9 datasets se usan como contexto** en fichas de distrito (no entran en cuadrantes).

Categorías de uso definidas:

1. **Cruce honesto**: el dataset genera una columna que se usa como indicador en `TEMA_TO_INDICADORES` de `etl/07_indice_discrepancia.py` para clasificar al menos un tema en los cuatro cuadrantes (silencio sobre carencia observable, demanda alineada, demanda por encima del indicador, sin carencia ni demanda destacadas).
2. **Contexto**: el dataset se carga, se cuentan sus features por distrito y los conteos aparecen en las fichas de distrito como información complementaria. NO se usa para clasificar cuadrantes.
3. **Geometría base**: distritos y barrios, usados como unidades de análisis.

## Tabla completa de uso por dataset

| Dataset (id en portal) | Categoría | Columnas que genera | Indicador en cruce | Temas que usan ese indicador |
|---|---|---|---|---|
| **apoyo-propuestas-decidimvlc** | Fuente principal | `(propuestas, apoyos, seleccionadas, edicion, distrito, presupuesto)` | — | — |
| **districtes-distritos** | Geometría base | `id_distrito`<br>`nombre_distrito`<br>`geometry` | — | — |
| **barris-barrios** | Geometría base | `id_barrio`<br>`nombre_barrio`<br>`geometry` | — | — |
| **illa-de-cases-cadastrals-amb-dades-de-poblacio** | Descartado | — | — | — |
| **vulnerabilidad-por-barrios** | Cruce honesto | `ind_equip`<br>`ind_dem`<br>`ind_econom`<br>`ind_global` | `ind_equip` | Centros de salud |
| **espais-verds-espacios-verdes** | Cruce honesto | `m2_espacios_verdes`<br>`n_jardines`<br>`m2_verde_per_hab` | `m2_verde_per_hab` | Jardines y arbolado<br>Parques y plazas<br>Zonas verdes |
| **equipamients-municipals-equipamientos-municipales** | Cruce honesto | `n_equipamientos`<br>`equipamientos_per_1000hab` | `equipamientos_per_1000hab` | Bibliotecas y ludotecas<br>Centros cívicos y huertos urbanos<br>Equipamientos culturales<br>Equipamientos específicos<br>Instalaciones deportivas<br>Mobiliario urbano deportivo |
| **centros-educativos-en-valencia** | Cruce honesto | `n_centros_educativos`<br>`centros_educativos_per_1000hab` | `centros_educativos_per_1000hab` | Centros educativos |
| **itinerarios-ciclistas-itineraris-ciclistes** | Cruce honesto | `m_carril_bici`<br>`m_carril_bici_per_1000hab` | `m_carril_bici_per_1000hab` | Carriles bici y movilidad ciclista |
| **parkings** | Cruce honesto | `n_plazas_parking`<br>`plazas_parking_per_1000hab` | `plazas_parking_per_1000hab` | Aparcamiento para vehículos |
| **velocitat-carrers** | Cruce honesto | `velocidad_media_kmh` | `velocidad_media_kmh` | Pacificación del tráfico<br>Reducción de velocidad y zonas 30 |
| **emt** | Cruce honesto | `n_paradas_emt`<br>`paradas_emt_per_1000hab` | `paradas_emt_per_1000hab` | Transporte público (EMT) |
| **contenidors-residus-solids** | Cruce honesto | `n_contenedores_residuos`<br>`contenedores_residuos_per_1000hab` | `contenedores_residuos_per_1000hab` | Recogida de residuos |
| **panells-informatius** | Cruce honesto | `n_paneles_total (suma con mupis)` | `paneles_total_per_1000hab` | Paneles informativos |
| **mupis-ocoval** | Cruce honesto | `n_paneles_total (suma con paneles_informativos)` | `paneles_total_per_1000hab` | Paneles informativos |
| **catalogo-urbano** | Cruce honesto | `n_bic`<br>`bic_per_1000hab` | `bic_per_1000hab` | Rehabilitación del patrimonio |
| **fonts-daigua-publica** | Cruce honesto | `n_fuentes_agua`<br>`fuentes_agua_per_1000hab` | `fuentes_agua_per_1000hab` | Fuentes y aseos públicos |
| **pipicans-zona-socialitzacio-canina** | Cruce honesto | `n_pipicans`<br>`pipicans_per_1000hab` | `pipicans_per_1000hab` | Pipicanes y zonas caninas |
| **zones-jocs-infantils** | Cruce honesto | `n_juegos_infantiles`<br>`juegos_infantiles_per_1000hab` | `juegos_infantiles_per_1000hab` | Parques infantiles |
| **zones-zas-zonas-zas** | Cruce honesto | `n_zonas_zas` | `n_zonas_zas` | Reducción del ruido |
| **estacions-de-soroll-estaciones-de-ruido** | Contexto | `n_estaciones_ruido` | — | — |
| **aparcaments-bicicletes-aparcamientos-bicicletas** | Contexto | `n_plazas_aparcabici`<br>`plazas_aparcabici_per_1000hab` | — | — |
| **majors-mayores** | Contexto | `n_recursos_mayores`<br>`recursos_mayores_per_1000hab` | — | — |
| **joventut-juventud** | Contexto | `n_recursos_juventud`<br>`recursos_juventud_per_1000hab` | — | — |
| **falles-fallas** | Contexto | `n_fallas`<br>`fallas_per_1000hab` | — | — |
| **zones-dactivitats** | Contexto | `n_zonas_actividades`<br>`zonas_actividades_per_1000hab` | — | — |

## Notas detalladas por dataset

### `apoyo-propuestas-decidimvlc`

- **Fichero**: `decidim.csv`
- **Rol declarado en MANIFEST**: `decidim`
- **URL del recurso**: https://opendata.vlci.valencia.es/dataset/4ccedafd-4055-4cef-aaed-91390b00a131/resource/87a0dbdf-bc65-469e-8552-c75d333e6372/download/apoyo-propuestas-decidimvlc.csv
- **Uso real en el pipeline**: Fuente principal — alimenta la Matriz de Demanda. No es un indicador de carencia.

### `districtes-distritos`

- **Fichero**: `distritos.geojson`
- **Rol declarado en MANIFEST**: `geometry-distritos`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/UrbanismoEInfraestructuras/MapServer/225/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Geometría base — 19 distritos como unidad de análisis (dissolve aplicado).

### `barris-barrios`

- **Fichero**: `barrios.geojson`
- **Rol declarado en MANIFEST**: `geometry-barrios`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/UrbanismoEInfraestructuras/MapServer/224/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Geometría auxiliar — 88 barrios para sub-vista futura.

### `illa-de-cases-cadastrals-amb-dades-de-poblacio`

- **Fichero**: `poblacion_manzanas.geojson`
- **Rol declarado en MANIFEST**: `demografia`
- **URL del recurso**: https://geoportal.valencia.es/apps/OpenData/UrbanismoEInfraestructuras/MANZANAS.json
- **Uso real en el pipeline**: Descargado pero descartado: el GeoJSON del portal no trae población. Se usa el Padrón 2022 transcrito como dataset derivado.

### `vulnerabilidad-por-barrios`

- **Fichero**: `vulnerabilidad.geojson`
- **Rol declarado en MANIFEST**: `realidad-vulnerabilidad`
- **URL del recurso**: https://opendata.vlci.valencia.es/dataset/ca18278b-d040-4274-b9c7-c1a9daae54b9/resource/fd2ca0dc-5344-4aad-8934-2077a0bb120d/download/vulnerabilidad-por-barrios.geojson
- **Uso real en el pipeline**: Cruce: ind_equip alimenta el tema 'Centros de salud' (no hay dataset municipal directo de cobertura sanitaria).

### `espais-verds-espacios-verdes`

- **Fichero**: `espacios_verdes.geojson`
- **Rol declarado en MANIFEST**: `realidad-verde`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/MedioAmbiente/MapServer/8/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: m2_verde_per_hab alimenta los temas 'Parques y plazas', 'Jardines y arbolado' y 'Zonas verdes'.

### `equipamients-municipals-equipamientos-municipales`

- **Fichero**: `equipamientos.geojson`
- **Rol declarado en MANIFEST**: `realidad-equipamientos`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/SociedadBienestar/MapServer/1/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: equipamientos_per_1000hab alimenta varios temas culturales/sociales (bibliotecas, equipamientos culturales, centros cívicos, instalaciones deportivas, mobiliario deportivo, equipamientos específicos).

### `centros-educativos-en-valencia`

- **Fichero**: `centros_educativos.geojson`
- **Rol declarado en MANIFEST**: `realidad-educacion`
- **URL del recurso**: https://opendata.vlci.valencia.es/dataset/11436f0c-082b-4e5b-9659-005f5b528bde/resource/938e34b7-bb7d-4b0c-8176-3602d47ebd6a/download/centros-educativos-en-valencia.geojson
- **Uso real en el pipeline**: Cruce: centros_educativos_per_1000hab alimenta el tema 'Centros educativos'.

### `itinerarios-ciclistas-itineraris-ciclistes`

- **Fichero**: `itinerarios_ciclistas.geojson`
- **Rol declarado en MANIFEST**: `realidad-bici`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/189/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: m_carril_bici_per_1000hab alimenta el tema 'Carriles bici y movilidad ciclista'.

### `parkings`

- **Fichero**: `parkings.geojson`
- **Rol declarado en MANIFEST**: `realidad-parking`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/194/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: plazas_parking_per_1000hab alimenta el tema 'Aparcamiento para vehículos'.

### `velocitat-carrers`

- **Fichero**: `velocidad_calles.geojson`
- **Rol declarado en MANIFEST**: `realidad-trafico`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/223/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: velocidad_media_kmh alimenta los temas 'Pacificación del tráfico' y 'Reducción de velocidad y zonas 30'.

### `emt`

- **Fichero**: `emt_paradas.geojson`
- **Rol declarado en MANIFEST**: `realidad-transporte`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/226/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: paradas_emt_per_1000hab alimenta el tema 'Transporte público (EMT)'.

### `contenidors-residus-solids`

- **Fichero**: `contenedores_residuos.geojson`
- **Rol declarado en MANIFEST**: `realidad-residuos`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/MedioAmbiente/MapServer/0/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: contenedores_residuos_per_1000hab alimenta el tema 'Recogida de residuos'.

### `panells-informatius`

- **Fichero**: `paneles_informativos.geojson`
- **Rol declarado en MANIFEST**: `realidad-informacion`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/187/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: combinado con mupis.geojson genera paneles_total_per_1000hab, indicador del tema 'Paneles informativos'.

### `mupis-ocoval`

- **Fichero**: `mupis.geojson`
- **Rol declarado en MANIFEST**: `realidad-informacion`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/UrbanismoEInfraestructuras/MapServer/3/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: combinado con paneles_informativos.geojson genera paneles_total_per_1000hab.

### `catalogo-urbano`

- **Fichero**: `patrimonio_urbano.geojson`
- **Rol declarado en MANIFEST**: `realidad-patrimonio`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/UrbanismoEInfraestructuras/MapServer/322/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: bic_per_1000hab alimenta el tema 'Rehabilitación del patrimonio'.

### `fonts-daigua-publica`

- **Fichero**: `fuentes_agua.geojson`
- **Rol declarado en MANIFEST**: `realidad-fuentes`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/MedioAmbiente/MapServer/158/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: fuentes_agua_per_1000hab alimenta el tema 'Fuentes y aseos públicos'.

### `pipicans-zona-socialitzacio-canina`

- **Fichero**: `pipicans.geojson`
- **Rol declarado en MANIFEST**: `realidad-canina`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/MedioAmbiente/MapServer/163/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: pipicans_per_1000hab alimenta el tema 'Pipicanes y zonas caninas'.

### `zones-jocs-infantils`

- **Fichero**: `juegos_infantiles.geojson`
- **Rol declarado en MANIFEST**: `realidad-juegos`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/MedioAmbiente/MapServer/166/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: juegos_infantiles_per_1000hab alimenta el tema 'Parques infantiles'.

### `zones-zas-zonas-zas`

- **Fichero**: `zones_zas.geojson`
- **Rol declarado en MANIFEST**: `realidad-ruido`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/SociedadBienestar/MapServer/5/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Cruce: n_zonas_zas alimenta el tema 'Reducción del ruido'.

### `estacions-de-soroll-estaciones-de-ruido`

- **Fichero**: `estaciones_ruido.geojson`
- **Rol declarado en MANIFEST**: `realidad-ruido`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/MedioAmbiente/MapServer/160/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Contexto: solo 4 estaciones físicas, demasiado pocas para indicador. Se cuenta en fichas de distrito.

### `aparcaments-bicicletes-aparcamientos-bicicletas`

- **Fichero**: `aparcabicis.geojson`
- **Rol declarado en MANIFEST**: `realidad-bici`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Trafico/MapServer/206/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Contexto: las plazas de aparcabicis aparecen como dato secundario en fichas de distrito. El tema relacionado ('Carriles bici') cruza con m_carril_bici_per_1000hab, indicador más relevante.

### `majors-mayores`

- **Fichero**: `mayores.geojson`
- **Rol declarado en MANIFEST**: `realidad-mayores`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/SociedadBienestar/MapServer/24/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Contexto: no existe tema Decidim específico de 'recursos para mayores'. Se cuenta en fichas como información complementaria.

### `joventut-juventud`

- **Fichero**: `juventud.geojson`
- **Rol declarado en MANIFEST**: `realidad-juventud`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/SociedadBienestar/MapServer/23/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Contexto: análogo a 'mayores'. Aparece en fichas de distrito.

### `falles-fallas`

- **Fichero**: `fallas.geojson`
- **Rol declarado en MANIFEST**: `realidad-cultura`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Turismo/MapServer/215/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Contexto: 351 fallas geolocalizadas. Información cultural complementaria en fichas de distrito.

### `zones-dactivitats`

- **Fichero**: `zonas_actividades.geojson`
- **Rol declarado en MANIFEST**: `realidad-actividades`
- **URL del recurso**: https://geoportal.valencia.es/server/rest/services/OPENDATA/Turismo/MapServer/206/query?where=1=1&outFields=*&f=geojson
- **Uso real en el pipeline**: Contexto: contado por distrito pero no se usa como indicador específico de carencia.

## Verificación de coherencia

El script `etl/12_trazabilidad.py` realiza tres comprobaciones automáticas y falla si
encuentra un desajuste:

1. **MANIFEST ↔ Documentación**: que cada dataset declarado en `data/raw/MANIFEST.json` esté documentado aquí.
2. **Documentación ↔ Código**: que cada indicador mencionado en este documento exista en el mapeo `TEMA_TO_INDICADORES` de `etl/07_indice_discrepancia.py`.
3. **Documentación ↔ MANIFEST**: que no haya datasets documentados que no se descarguen realmente.

Esta verificación corre cada vez que se regenera el pipeline, por lo que cualquier
drift entre lo declarado y lo implementado se detecta de inmediato.