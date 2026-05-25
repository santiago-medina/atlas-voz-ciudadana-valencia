# Hallazgos del Atlas de la Voz Ciudadana de València

*Versión derivada automáticamente desde `etl/10_hallazgos.py`. Cada cifra es reproducible ejecutando el pipeline ETL.*


## H01 · La participación ha crecido un 153 % en una década

**+948**

En la 1ª edición (2015-2016) se presentaron 619 propuestas; en la 7ª (2022-2023) fueron 1.567, un crecimiento del 153 %. Los apoyos ciudadanos (registrados a partir de la 2ª edición) pasaron de 15.728 a 35.481. DecidimVLC ha consolidado un canal real de expresión ciudadana.


*Fuente: decidim raw · agregación por Edicion (incluye propuestas sin título legible)*


## H02 · Más propuestas, mayor distancia con la capacidad presupuestaria

**17,6 % → 9,3 %**

En la 1ª edición se seleccionó el 17,6 % de las propuestas; en la 7ª solo el 9,3 %. La tasa de selección cae al crecer la participación, lo que aumenta la distancia entre expectativa ciudadana y capacidad presupuestaria municipal — no necesariamente una pérdida de capacidad, sino una mayor competencia entre propuestas por un presupuesto limitado.


*Fuente: evolucion.json · tasa_seleccion por edición (raw, dataset completo)*


## H03 · Campanar: alta vulnerabilidad y baja demanda relativa

**3,77 / 6**

Campanar registra el índice de vulnerabilidad más alto de los 19 distritos (3,77, escala 0-10) según el dataset municipal de 2021. En el cruce con Decidim aparece en el cuadrante 'silencioso vulnerable' en 6 de los 23 temas con indicador municipal específico, entre ellos: aparcamiento para vehículos, equipamientos culturales, equipamientos específicos, instalaciones deportivas y otros. La velocidad media de sus calles (38,3 km/h) es la segunda más alta de la ciudad y sin embargo el distrito no figura en el top de demanda en el tema 'pacificación del tráfico'.


*Fuente: matriz_realidad.csv + indice_discrepancia.csv*


## H04 · Carril bici: demanda emergente con brecha de selección

**+103 propuestas / 0 ejecuciones en repetidas**

Los carriles bici son el tema con mayor crecimiento entre 2015 y 2023: de 11 propuestas en la 1ª edición a 114 en la 7ª (+103). En paralelo, 2 pares (distrito, tema) acumulan demanda en 4+ ediciones consecutivas sin que ninguna haya sido seleccionada — 1.340 apoyos en total. El caso de mayor volumen: Extramurs, con 29 propuestas y 1.098 apoyos sin selección en 4 ediciones. La demanda emergente y la baja tasa de selección abren una brecha que conviene comunicar de forma explícita a la ciudadanía.


*Fuente: evolucion.json · emergentes_top10 + demandas_zombi*


## H05 · Pobles del Nord: el peso relativo de los distritos pequeños

**503 apoyos/1.000 hab**

Con solo 6.104 habitantes, Pobles del Nord acumula 3.069 apoyos en propuestas, equivalentes a 503 apoyos por 1.000 habitantes — 3,4 veces la media de la ciudad (147). En distritos pequeños, una organización vecinal activa puede amplificar el peso relativo del distrito en el proceso participativo, lo que conviene considerar al diseñar mecanismos de reequilibrio.


*Fuente: decidim_tagged.csv + poblacion_distritos.csv*


## H06 · Una de cada cinco propuestas no se ata a ningún barrio

**22,6%**

1.195 propuestas (22,6 % del total) se presentaron bajo la etiqueta 'Toda la ciudad'. Es un volumen enorme que dificulta el reequilibrio territorial: las propuestas globales no se pueden asignar a un distrito concreto para medir si están atendiendo a un barrio vulnerable o reforzando privilegios. La nueva edición 2025-2026 podría revisar este criterio.


*Fuente: decidim_tagged.csv · count(id_distrito == 0)*


## H07 · Verde: hasta 6 veces más en el extremo alto que en el bajo

**17,5 vs 2,7 m²/hab**

Campanar lidera con 17,5 m² de zona verde por habitante. En el extremo opuesto, Benimaclet ofrece 2,7 m²/hab. Tomando 9 m²/hab como umbral ampliamente citado en literatura urbana, 14 distritos quedan por debajo. Ninguno de ellos figura en el top de demanda en el tema 'Zonas verdes' dentro de Decidim, lo que sugiere que la carencia observable no se traduce automáticamente en demanda explícita.


*Fuente: matriz_realidad.csv · m2_verde_per_hab*


## H08 · El silencio sobre carencia observable es la situación más frecuente

**199 de 437 pares (46 %)**

Cruzando los 23 temas que tienen un indicador municipal específico con los 19 distritos obtenemos 437 pares analizables. En 199 (46 %) detectamos un patrón de 'silencio sobre carencia observable': el distrito tiene una carencia observable por encima de la media de la ciudad pero su demanda en Decidim queda por debajo. Es el cuadrante más numeroso, por delante de 'cómodo' (96), 'demanda legítima' (76) y 'sobre-demandante' (66).


*Fuente: indice_discrepancia.csv · value_counts(cuadrante)*


## H09 · 28 demandas persistentes no han sido seleccionadas en 4+ ediciones

**28 pares · 8.121 apoyos**

28 pares (distrito, tema) han sido objeto de propuestas en al menos 4 de las 7 ediciones sin que ninguna haya sido seleccionada. Acumulan 8.121 apoyos ciudadanos. Los tres pares con más apoyos acumulados son: Extramurs (carriles bici y movilidad ciclista), Poblats Marítims (litoral y puerto), Quatre Carreres (aceras y movilidad peatonal). Cada demanda persistente sin selección representa una desconexión entre expresión ciudadana y ejecución que conviene comunicar de forma explícita.


*Fuente: evolucion.json · demandas_zombi*


## H10 · 38 temas detectados, 23 con cruce honesto contra datos municipales

**38 temas / 23 cruzables**

Aplicando topic modeling sobre los 4.229 títulos legibles surgen 38 agrupaciones temáticas. El top 3 por apoyos: Carriles bici y movilidad ciclista (20.799 apoyos), Parques y plazas (10.473 apoyos), Instalaciones deportivas (9.878 apoyos). De los 38, 23 tienen un indicador municipal específico que permite calcular el cuadrante de discrepancia; el resto se muestra solo en la matriz de demanda. Esta separación honesta evita usar la vulnerabilidad global como proxy genérico repetido.


*Fuente: decidim_tagged.csv + topics.csv + indice_discrepancia.csv*


## H11 · Por cada euro ejecutado, la ciudadanía ha pedido cuatro

**233,6 M€ vs 58,4 M€**

El conjunto de propuestas de las 7 ediciones suma 233,6 millones de euros en inversión solicitada. De ese volumen, 58,4 M€ pertenecen a propuestas finalmente seleccionadas, un 25 %. El embudo presupuestario es severo, y debería comunicarse de forma explícita a la ciudadanía como criterio de gestión.


*Fuente: decidim.csv · Presupuesto_euros agregado*


## H12 · Pobles de l'Oest, ejemplo de demanda alineada con la carencia

**8 temas con demanda legítima**

En Pobles de l'Oest, varias demandas ciudadanas coinciden con carencias objetivas medibles: centros cívicos y huertos urbanos, mobiliario urbano deportivo, equipamientos culturales. Es un caso donde el proceso participativo funciona como cabe esperar: los vecinos identifican y priorizan exactamente los temas en los que su distrito está peor que la media.


*Fuente: indice_discrepancia.csv · cuadrante='Demanda legítima'*


## H13 · El envejecimiento se queda fuera del debate participativo

**146 centros · pocas propuestas**

Valencia cuenta con 146 recursos para personas mayores según el portal municipal. Sin embargo, no aparece ningún tema específicamente centrado en mayores en el ranking de demanda. Las propuestas relacionadas se dispersan entre instalaciones deportivas, accesibilidad y equipamientos culturales, pero ninguna 'voz mayor' se articula explícitamente en Decidim. La 8ª edición podría incorporar incentivos a la participación senior.


*Fuente: matriz_realidad.csv · n_recursos_mayores*
