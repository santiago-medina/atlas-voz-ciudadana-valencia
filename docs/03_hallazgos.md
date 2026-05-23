# Hallazgos del Atlas de la Voz Ciudadana de València

*Versión derivada automáticamente desde `etl/10_hallazgos.py`. Cada cifra es reproducible ejecutando el pipeline ETL.*


## H01 · La participación se ha duplicado en una década

**+1.160**

En la 1ª edición (2015-2016) se presentaron 86 propuestas; en la 7ª (2022-2023) fueron 1.246. un crecimiento del 1349%. Los apoyos ciudadanos (registrados a partir de la 2ª edición) pasaron de 13.162 a 28.467. DecidimVLC ha consolidado un canal real de expresión ciudadana.


*Fuente: decidim_tagged.csv · agregación por Edicion*


## H02 · Más propuestas, menos ejecución

**9.6%**

En la 1ª edición se seleccionó el 100.0% de las propuestas; en la 7ª solo el 9.6%. El proceso ha ganado masa crítica pero ha perdido capacidad de convertir demanda en proyecto ejecutado, lo que genera frustración acumulada.


*Fuente: evolucion.json · tasa_seleccion por edición*


## H03 · Campanar: máxima vulnerabilidad, mínima voz

**3.77 / 19**

Campanar registra el índice de vulnerabilidad más alto de la ciudad (3.77, escala 0-10) según el dataset municipal de 2021. Pese a ello, aparece como 'silencioso vulnerable' en 19 temas distintos: aceras y movilidad peatonal, recogida de residuos, pacificación del tráfico, rehabilitación de mercados, reurbanización de calles, seguridad ciudadana, iluminación pública, repavimentación, puentes peatonales y litoral. Pide muy poco para la situación que vive.


*Fuente: matriz_realidad.csv + indice_discrepancia.csv*


## H04 · El carril bici: la demanda que más crece y más se ignora

**+103 / 0 ejecuciones**

Los carriles bici son la demanda que más ha crecido entre 2015 y 2023: de 11 propuestas en la 1ª edición a 114 en la 7ª (+103). Sin embargo. 2 pares (distrito. edición) piden carril bici de forma persistente (1.340 apoyos acumulados) sin que se haya seleccionado ninguno. El caso más sangrante: Extramurs. con 29 propuestas y 1.098 apoyos en 4 ediciones consecutivas.


*Fuente: evolucion.json · emergentes_top10 + demandas_zombi*


## H05 · Pobles del Nord: la voz desproporcionada de los pequeños

**503 apoyos/1.000 hab**

Con solo 6.104 habitantes. Pobles del Nord ha generado 3.069 apoyos en propuestas: 503 apoyos por 1.000 habitantes. casi el doble que la media de Valencia (115). En distritos pequeños. una minoría organizada puede dominar el proceso participativo en términos relativos.


*Fuente: decidim_tagged.csv + poblacion_distritos.csv*


## H06 · Una de cada cinco propuestas no se ata a ningún barrio

**22.6%**

1.195 propuestas (22.6% del total) se presentaron bajo la etiqueta 'Toda la ciudad'. Es un volumen enorme que dificulta el reequilibrio territorial: las propuestas globales no se pueden asignar a un distrito concreto para medir si están atendiendo a un barrio vulnerable o reforzando privilegios. La nueva edición 2025-2026 podría revisar este criterio.


*Fuente: decidim_tagged.csv · count(id_distrito == 0)*


## H07 · Verde: 6 veces más en el extremo alto que en el bajo

**17.5 vs 2.7 m²/hab**

Campanar lidera con 17.5 m² de zona verde por habitante. En el extremo opuesto, Benimaclet ofrece 2.7 m²/hab. La OMS recomienda 9 m²/hab como mínimo: 5 distritos están por debajo. Sin embargo, ninguno de esos 5 distritos está en el top de demanda en el tema 'Zonas verdes' en Decidim.


*Fuente: matriz_realidad.csv · m2_verde_per_hab*


## H08 · El silencio vulnerable es la situación más frecuente

**280 de 722 pares (39%)**

Cruzando los 38 temas con los 19 distritos obtenemos 722 pares posibles. En 280 (39%) detectamos un patrón de 'silencio vulnerable': el distrito tiene una carencia objetiva por encima de la media de la ciudad pero su demanda en Decidim está por debajo. Es el cuadrante más numeroso. por delante del 'cómodo' (256). 'demanda legítima' (104) y 'sobre-demandante' (82).


*Fuente: indice_discrepancia.csv · value_counts(cuadrante)*


## H09 · 28 demandas se repiten desde hace 4+ ediciones sin ser ejecutadas

**28 · 8.121 apoyos**

28 pares (distrito. tema) han sido objeto de propuestas en al menos 4 de las 7 ediciones sin que se seleccionara ninguna. Acumulan 8.121 apoyos. El top: Extramurs (carriles bici y movilidad ciclista), Poblats Marítims (litoral y puerto), Quatre Carreres (aceras y movilidad peatonal). Cada propuesta zombi es un voto ciudadano que el sistema ignora durante años.


*Fuente: evolucion.json · demandas_zombi*


## H10 · Las prioridades de Valencia caben en 38 categorías

**38 temas detectados**

Aplicando topic modeling sobre los 4.229 títulos legibles surgen 38 agrupaciones temáticas. El top 3 por apoyos: Carriles bici y movilidad ciclista (20.799 apoyos), Parques y plazas (10.473 apoyos), Instalaciones deportivas (9.878 apoyos). Identificar estas categorías hace posible analizar la demanda al margen del ruido lingüístico (castellano/valenciano, abreviaturas, faltas).


*Fuente: decidim_tagged.csv + topics.csv*


## H11 · Por cada euro ejecutado, la ciudadanía ha pedido 4

**233.6 M€ vs 58.4 M€**

El conjunto de propuestas de las 7 ediciones suma 233.6 millones de euros en inversión solicitada. De ese volumen, 58.4 M€ pertenecen a propuestas finalmente seleccionadas, un 25%. El embudo presupuestario es severo, y debería usarse como criterio explícito al comunicar resultados a la ciudadanía.


*Fuente: decidim.csv · Presupuesto_euros agregado*


## H12 · Pobles de l'Oest, ejemplo de demanda alineada con la carencia

**7 temas con demanda legítima**

En Pobles de l'Oest, varias demandas ciudadanas coinciden con carencias objetivas medibles: centros cívicos y huertos urbanos, mobiliario urbano deportivo, equipamientos culturales. Es un caso donde el proceso participativo funciona como cabe esperar: los vecinos identifican y priorizan exactamente los temas en los que su distrito está peor que la media.


*Fuente: indice_discrepancia.csv · cuadrante='Demanda legítima'*


## H13 · El envejecimiento se queda fuera del debate participativo

**146 centros · pocas propuestas**

Valencia cuenta con 146 recursos para personas mayores según el portal municipal. Sin embargo, no aparece ningún tema específicamente centrado en mayores en el ranking de demanda. Las propuestas relacionadas se dispersan entre instalaciones deportivas, accesibilidad y equipamientos culturales, pero ninguna 'voz mayor' se articula explícitamente en Decidim. La 8ª edición podría incorporar incentivos a la participación senior.


*Fuente: matriz_realidad.csv · n_recursos_mayores*
