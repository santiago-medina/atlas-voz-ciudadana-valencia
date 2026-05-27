# Hallazgos del Atlas de la Voz Ciudadana de València

*Versión derivada automáticamente desde `etl/10_hallazgos.py`. Cada cifra es reproducible ejecutando el pipeline ETL.*


## H01 · La participación ha crecido un 153 % en una década

**+948**

En la 1ª edición (2015-2016) se presentaron 619 propuestas; en la 7ª (2022-2023) fueron 1.567, un crecimiento del 153 %. Los apoyos ciudadanos (registrados a partir de la 2ª edición) pasaron de 15.728 a 35.481. DecidimVLC ha consolidado un canal real de expresión ciudadana.


*Fuente: decidim raw · agregación por Edicion (incluye propuestas sin título legible)*


## H02 · Más propuestas, mayor distancia con la capacidad presupuestaria

**17,6 % → 9,3 %**

En la 1ª edición se seleccionó el 17,6 % de las propuestas; en la 7ª solo el 9,3 %. La tasa de selección cae al crecer la participación, lo que aumenta la distancia entre expectativa ciudadana y capacidad presupuestaria municipal. No es necesariamente una pérdida de capacidad, sino una mayor competencia entre propuestas por un presupuesto limitado.


*Fuente: evolucion.json · tasa_seleccion por edición (raw, dataset completo)*


## H03 · Campanar: alta vulnerabilidad y baja demanda relativa

**3,77 / 6**

Campanar registra el índice de vulnerabilidad más alto de los 19 distritos (3,77, escala 0-10) según el dataset municipal de 2021. En el cruce con Decidim aparece en el cuadrante 'silencioso vulnerable' en 6 de los 23 temas con indicador municipal específico, entre ellos: aparcamiento para vehículos, equipamientos culturales, equipamientos específicos, instalaciones deportivas y otros. La velocidad media de sus calles (38,3 km/h) es la segunda más alta de la ciudad y sin embargo el distrito no figura en el top de demanda en el tema 'pacificación del tráfico'.


*Fuente: matriz_realidad.csv + indice_discrepancia.csv*


## H04 · Carril bici: demanda emergente con brecha de selección

**+103 propuestas / 0 ejecuciones en repetidas**

Los carriles bici son el tema con mayor crecimiento entre 2015 y 2023: de 11 propuestas en la 1ª edición a 114 en la 7ª (+103). En paralelo, 2 pares (distrito, tema) acumulan demanda en 4+ ediciones consecutivas sin que ninguna haya sido seleccionada (1.340 apoyos en total). El caso de mayor volumen: Extramurs, con 29 propuestas y 1.098 apoyos sin selección en 4 ediciones. La demanda emergente y la baja tasa de selección abren una brecha que conviene comunicar de forma explícita a la ciudadanía.


*Fuente: evolucion.json · emergentes_top10 + demandas_zombi*


## H05 · Pobles del Nord: el efecto de escala en los distritos pequeños

**456 apoyos/1.000 hab**

Con solo 6.730 habitantes, Pobles del Nord acumula 3.069 apoyos en propuestas, equivalentes a 456 apoyos por 1.000 habitantes, 3,1 veces la media de la ciudad (145). Esta cifra alta por habitante no significa necesariamente que el distrito participe más en términos absolutos: con tan pocos vecinos, un grupo relativamente pequeño basta para destacar mucho per cápita. La normalización por habitante mejora la comparabilidad entre distritos pero amplifica los territorios poco poblados, por lo que el mecanismo de reequilibrio territorial de la 8ª edición conviene complementar con este tipo de comparación.


*Fuente: decidim_tagged.csv + poblacion_distritos.csv*


## H06 · Una de cada cinco propuestas no se ata a ningún barrio

**22,6%**

1.195 propuestas (22,6 % del total) se presentaron bajo la etiqueta 'Toda la ciudad'. Es un volumen enorme que dificulta el reequilibrio territorial: las propuestas globales no se pueden asignar a un distrito concreto para medir si están atendiendo a un barrio vulnerable o reforzando privilegios. La nueva edición 2025-2026 podría revisar este criterio.


*Fuente: decidim_tagged.csv · count(id_distrito == 0)*


## H07 · Verde: el distrito mejor servido tiene 5 veces más m² por habitante que el peor

**15,6 vs 3,0 m²/hab**

Campanar lidera con 15,6 m² de zona verde por habitante. En el extremo opuesto, Benimaclet ofrece 3,0 m²/hab, unas 5 veces menos. La mediana de la ciudad se sitúa en 6,8 m²/hab, con 9 de los 19 distritos por debajo de esa cifra. Ninguno de los distritos con menos verde por habitante figura en el top de demanda del tema 'Zonas verdes' dentro de Decidim, lo que sugiere que la carencia medida no se traduce automáticamente en demanda expresada.


*Fuente: matriz_realidad.csv · m2_verde_per_hab (comparación interna a la ciudad, sin umbral externo)*


## H08 · El silencio sobre carencia observable es la situación más frecuente

**175 de 437 pares (40 %)**

Cruzando los 23 temas que tienen un indicador municipal específico con los 19 distritos obtenemos 437 pares analizables. En 175 (40 %) detectamos un patrón de 'silencio sobre carencia observable': el distrito tiene una carencia observable por encima de la media de la ciudad pero su demanda en Decidim queda por debajo. Es el cuadrante más numeroso, por delante de 'cómodo' (110), 'demanda legítima' (85) y 'sobre-demandante' (67).


*Fuente: indice_discrepancia.csv · value_counts(cuadrante)*


## H09 · 28 demandas persistentes no han sido seleccionadas en 4 o más ediciones

**28 pares · 8.121 apoyos**

28 combinaciones de distrito y tema han sido objeto de propuestas en al menos 4 de las 7 ediciones sin que ninguna haya sido seleccionada. Acumulan 8.121 apoyos ciudadanos. Las tres con más apoyos acumulados son: Extramurs (carriles bici y movilidad ciclista), Poblats Marítims (litoral y puerto), Quatre Carreres (aceras y movilidad peatonal). Cada caso representa una propuesta vecinal que se repite edición tras edición sin que el proceso participativo dé una respuesta clara, y conviene que el Ayuntamiento publique el estado de cada una.


*Fuente: evolucion.json · demandas_zombi*


## H10 · 38 temas detectados, 23 con indicador municipal para cruzar

**38 temas / 23 con indicador**

Para agrupar las 4.229 propuestas con título legible, convertimos cada título en un vector numérico que captura su significado (usando un modelo de inteligencia artificial entrenado en castellano y valenciano), agrupamos las propuestas que dicen cosas parecidas, y revisamos a mano cada grupo para ponerle un nombre legible. Aparecen 38 temas. Los tres con más apoyos: Carriles bici y movilidad ciclista (20.799 apoyos), Parques y plazas (10.473 apoyos), Instalaciones deportivas (9.878 apoyos). De estos 38 temas, 23 cuentan con un indicador municipal específico que mide su carencia (m² de zona verde por habitante para parques, metros de carril bici para movilidad ciclista, etc.). Los otros 15 temas (aceras, iluminación pública, seguridad, asfaltado…) se mantienen en la matriz de demanda y en las fichas de distrito, pero no entran en el índice de discrepancia porque el portal no publica un dato objetivo que mida directamente esa carencia. Preferimos dejarlos fuera antes que compararlos contra un indicador genérico que no encaja con cada tema.


*Fuente: decidim_tagged.csv + topics.csv + indice_discrepancia.csv*


## H11 · Por cada euro ejecutado, la ciudadanía ha pedido cuatro

**233,6 M€ vs 58,4 M€**

El conjunto de propuestas de las 7 ediciones suma 233,6 millones de euros en inversión solicitada. De ese volumen, 58,4 M€ pertenecen a propuestas finalmente seleccionadas, un 25 %. El embudo presupuestario es severo, y debería comunicarse de forma explícita a la ciudadanía como criterio de gestión.


*Fuente: decidim.csv · Presupuesto_euros agregado*


## H12 · Pobles de l'Oest, ejemplo de demanda alineada con la carencia

**9 temas con demanda legítima**

En Pobles de l'Oest, varias demandas ciudadanas coinciden con carencias objetivas medibles: centros cívicos y huertos urbanos, mobiliario urbano deportivo, equipamientos culturales. Es un caso donde el proceso participativo funciona como cabe esperar: los vecinos identifican y priorizan exactamente los temas en los que su distrito está peor que la media.


*Fuente: indice_discrepancia.csv · cuadrante='Demanda legítima'*


## H13 · El envejecimiento se queda fuera del debate participativo

**146 centros · pocas propuestas**

Valencia cuenta con 146 recursos para personas mayores según el portal municipal. Sin embargo, ninguno de los temas detectados en Decidim se centra específicamente en mayores. Las propuestas relacionadas se reparten entre instalaciones deportivas, accesibilidad y equipamientos culturales, pero no aparece como tal una voz que represente las necesidades de las personas mayores. La 8ª edición podría plantear cómo facilitar su participación.


*Fuente: matriz_realidad.csv · n_recursos_mayores*
