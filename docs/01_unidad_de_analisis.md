# Unidad de análisis: distritos (19), no barrios

## Hallazgo (día 1)

Decidim VLC asigna cada propuesta a un **ámbito**, no a un barrio. Esos ámbitos resultaron ser:

- **19 distritos administrativos** de la ciudad (Quatre Carreres, Patraix, Extramurs, l'Eixample, Ciutat Vella, Camins al Grau, Benicalap, l'Olivereta, Rascanya, Algirós, Jesús, Benimaclet, el Pla del Real, la Saïdia, Poblats Maritims, Campanar) + 3 distritos de pedanías (Pobles del Nord, Pobles del Sud, Pobles de l'Oest).
- **"Toda la ciudad"** (1.194 propuestas — el ámbito más usado, propuestas no asignadas a distrito).
- **Códigos numéricos 1-8** (538 propuestas — aparentemente codificación numérica de los distritos en ediciones tempranas; hay que verificar mapping).
- **"No consta"** y vacío (48 propuestas — descartar o agrupar en "Toda la ciudad").

Resultado: trabajaremos a **nivel distrito (19 unidades + categoría 'Ciudad global' para propuestas no localizadas)**. Esta decisión:

- Reduce ruido estadístico (más propuestas por unidad, mejor poder estadístico).
- Encaja con los datasets de realidad: `vulnerabilidad-por-barrios` tiene 70 barrios mapeables a distritos vía `coddistrit`, y los demás datasets son puntos/polígonos que agregamos por intersección espacial.
- Permite sub-vista a nivel barrio (88) cuando la pregunta lo pide.

## Implicaciones operativas

1. **Necesitamos mapear los códigos numéricos** 1-8 a distritos reales. Hipótesis: corresponden al orden alfabético o al `codigo_ambito_referencia` del dataset. Confirmar revisando propuestas concretas.
2. **`vulnerabilidad-por-barrios` (70 barrios)** se agrega por distrito usando `coddistrit` del barrio.
3. **`barrios.geojson` (88 barrios)** se mantiene para la sub-vista pero la columna principal de análisis es `coddistrit`.
4. **Datasets de puntos** (equipamientos, fallas, etc.) se asignan a distrito vía `ST_Contains(distritos.geom, punto)`.

## Convención de campo

A partir de aquí cualquier output del ETL usa el campo `id_distrito` (entero 1-19) y `nombre_distrito` (string). Los datos a nivel barrio llevan `id_barrio`/`nombre_barrio` + `id_distrito` para join up.
