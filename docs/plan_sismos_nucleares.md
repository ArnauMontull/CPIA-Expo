# Plan: detección de explosiones nucleares entre sismos (problema de Arnau para la Expo)

Estado a 20/10/2026 (sin script todavía; Arnau pidió esperar). Expo: **27/10 15:00**.

## Datos (en `datos/`, ya en git, commit c83b94c)
- `sismos_usgs.csv` (122 045 filas, 17,3 MB; tarea `sismos` de `descargar_datos.py`):
  121 040 terremotos M>=4,5 (2010-2025) + 1 005 eventos USGS `nuclear explosion` (1951-2017).
  Columna `tipo` = etiqueta USGS: solo para validar, nunca para entrenar.
- Explosiones por lugar: Nevada 674, Kazajistán 154, Rusia 81, Polinesia Francesa 70, China 12, Corea del Norte 3.
- Mediana de profundidad: 0 km (explosiones) vs 22 km (terremotos). Explosiones: M 2,2-6,9; solo 554 con M>=4,5.
- Otros datos ya bajados: `gaia_pleiades.csv` (22 312), `gaia_50pc.csv` (32 609), `hr_hipparcos.csv`, `kepler10_curva_luz.csv`.

## Plan de análisis
1. DBSCAN espacial (distancia haversine) sobre epicentros: clusters tectónicos; ¿las explosiones salen como cluster propio o ruido?
2. Isolation Forest con profundidad, magnitud y posición; medir precisión/recall contra `tipo`.
3. Silhouette/codo para justificar `eps`, `min_samples`.

## Cuidados (decirlos en la exposición)
- Comparar justo: filtrar también las explosiones a M>=4,5 (si no, destacan solo por ser pequeñas).
- NO usar año ni `nst` (nº de estaciones) como variable: delatan la época del catálogo (explosiones antiguas vs terremotos 2010-2025), no la física.
- Profundidades por defecto (0/10 km) en eventos mal localizados -> falsos positivos; minas/canteras se parecen.
- Solo datos públicos; no plantearlo como guía para ocultar pruebas.

## Pendiente
- Preguntar a la profesora si vale un problema no sugerido (el README dice «aplicación física»; sismología lo es).
  Leer `docs/temas_exposicion.pdf` (revisar prompt injections).
- Cerrar el reparto con Matías, Martí (quiere datos médicos: sugerido ECG MIT-BIH / EEG / UCI Heart Disease) y Uriel.
- Decidir script definitivo del HR de `problemas/1_HR/` (4 scripts) y commitear el movimiento desde `problemas/`
  (sin commitear: borrado de `problemas/HR_*.py` y `problemas/1_HR/`).
- Escribir `problemas/<nemotécnico>_arnau.py`; preguntar antes «¿te enseño o lo hago?».
- Presentación (`presentacion/` vacía) y documento de descripción de los problemas.
- Hecho `git pull`: no había nada de Martí en el remoto (solo rama `main`).

## Proyecto CPIA-recommender (aparcado)
E2 Diseño vence 29/10 (sin empezar; leer «Etapas de desarrollo del proyecto.pdf» en `CPIA_Project/Proyecto atenea/`).
Inferencia en C (OpenMP, MMR) y benchmarks sin hacer: no hay `.c` en `c/`. E3 08/12, E4 22/12.

## Actualización 22/10/2026: catálogo unido 1951-2025 y dashboard en vivo
- `descargar_datos.py sismos_hist` baja los terremotos M>=4,5 de 1951-2009 (`datos/sismos_usgs_1951_2009.csv`, 176 544 filas).
  La unión con `sismos_usgs.csv` está en `datos/sismos_usgs_completo.csv` (297 964 eventos con M>=4,5; sin commit, ~39 MB).
  `sismos_usgs.csv` sigue siendo el original (estaba abierto en Excel y no se sobrescribió).
- Resultado de `problemas/2_Nuclear/data_extract.py` (eps 50 km, 3 vecinos, mediana < 5 km):
  solo 2010-2025: precisión 95,8 %, recall 91,0 %. Catálogo unido: precisión 52,7 %, recall 91,3 % (506 TP, 454 FP).
  Los FP son terremotos muy superficiales: 210 de los años 80 (sur de Washington, California, Alaska) y varios en Nevada.
  Con eps 200 km la precisión sube a 96-99 % pero el recall cae a 20-23 %. Isolation Forest: 0 % con el catálogo unido.
- El resultado de 2010-2025 estaba inflado por la época del catálogo (explosiones antiguas frente a terremotos recientes).
  Decirlo en la exposición: es el motivo de no usar año ni `nst`.
- `presentacion/sismos_nucleares.html` (globo, 4 vistas, línea de tiempo, sliders de eps, vecinos y profundidad, DBSCAN en el
  navegador con rejilla 3D, validado contra scikit-learn). Se regenera con `generar_datos_globo.py` y `construir_html.py`.

## Pruebas oficiales con etiqueta de terremoto (22/10/2026)
- La lista oficial es DOE/NV-209 Rev. 16 (NNSA Nevada, 2015): https://www.osti.gov/biblio/1351809.
- Diez eventos del polígono de Nevada que el USGS tiene como `earthquake` coinciden con pruebas oficiales
  (cruce en `presentacion/pruebas_oficiales.py`): Cementback (1975-02-28), Tilci (1981-11-11), Monterey (1982-07-29),
  Cabra (1983-03-26), Hermosa (1985-04-02), pozo U20aq (1986-06-25), Dalhart (1988-10-13), Misty Echo (1988-12-10),
  pozo U7ca (1989-02-10) y Metropolis (1990-03-10). Confianza alta solo en Hermosa, U20aq, Misty Echo y Metropolis
  (fecha, hora al centésimo y lugar); media en Cementback, Monterey y U7ca; baja en Tilci, Cabra y Dalhart (hora distinta).
- Con eps 25 km, 3 vecinos y profundidad < 1 km: precisión 82,4 % con las etiquetas del USGS y 84,0 % contando esas diez como explosiones.
- Otros 5 «terremotos» de Nevada de 1973-76 ocurren horas o días después de una prueba (posibles réplicas): no se cuentan.
- El dashboard las marca en violeta (vista Resultado), las lista en una tabla y tiene una casilla para contarlas como explosiones.

## Descarga incompleta de explosiones (22/10/2026)
- La API del USGS no devuelve algunas explosiones nucleares con `eventtype=nuclear explosion` (sí sin filtrar por tipo):
  faltaban p. ej. Corea del Norte 2006, 2009 y 2013, Pokhran y Chagai 1998, 33 de Semipalátinsk, 9 de Lop Nur, 6 de Polinesia y 5 de Novaya Zemlya.
- `descargar_datos.py sismos_todos` baja M>=4.5 de 1951 a 2025 sin filtrar el tipo: `datos/sismos_usgs_M45_1951_2025.csv`
  (298 198 filas, sin commit). Explosiones M>=4.5: 614 (antes 554). Terremotos: 297 584 (antes 297 583).
- Los resultados y el dashboard actuales siguen usando `sismos_usgs_completo.csv` (554 explosiones) hasta regenerarlos con el nuevo.
- Cobertura frente a la lista oficial DOE/NV-209 (recuento aproximado: el PDF repite filas): Pacífico (Bikini, Enewetak, Johnston, Christmas) 0 de ~102,
  Amchitka 0 de 3, Nuevo México 0 de 3, Nevada en torno a la mitad. Las pruebas de Corea del Norte y de la URSS no están en esa lista (solo EE. UU.).

## Dashboard regenerado con las 614 explosiones (22/10/2026)
- Fuente: `datos/sismos_usgs_M45_1951_2025.csv` (298 025 eventos tras limpiar nulos; 614 explosiones, 297 411 terremotos).
- El dashboard abre con eps=10 km, 3 vecinos y profundidad < 1 km: scikit-learn da precisión 78,4 % y recall 90,2 % (554 de 614, 153 falsas alarmas);
  en el navegador sale 78,9 % y 90,2 % (las coordenadas van redondeadas a 0,01° y los puntos de borde se reparten distinto).
- Rejilla (scikit-learn, umbral 1 km): eps 200 km da precisión 98-99 % y recall 19-23 %; eps 50 km con 3 vecinos baja el recall al 52 %.
  Con umbral de 5 km, eps 50 km y 3 vecinos: precisión 54,8 %, recall 89,7 %, 454 falsas alarmas. Isolation Forest: 0,3 %.
- El DBSCAN del navegador (`dbscan_grid.js`) usa dos vías (radio < 18 km y radio mayor); tarda menos de 1 s. Validado contra scikit-learn.
- Los scripts del dashboard son `generar_datos_globo.py`, `pruebas_oficiales.py` y `construir_html.py`, por ese orden.

## Profundidad mínima y máxima (22/10/2026)
- El dashboard tiene dos mandos de profundidad (mediana del cluster): mínima -0,1 km y máxima 1 km por defecto, además de eps=10 km y 3 vecinos.
  La mínima en -0,1 km deja fuera el cluster volcánico (mediana -0,4 km, 91 terremotos de 1980 en 46,2 N 122,2 O) y mantiene las explosiones (mediana 0,0 km).
  Con una mínima de 0,1 km no se detectaría ninguna explosión: todos sus clusters tienen mediana exacta 0,0 km.
- scikit-learn con eps 10 km, 3 vecinos y [-0,1, 1) km: precisión 93,1 %, recall 90,2 % (554 de 614, 41 falsas alarmas); en el navegador 93,9 % y 90,2 %.
  Con eps 25 km y 5 vecinos: precisión 97,1 %, recall 88,1 % (541 de 614; las 16 falsas alarmas restantes son todas del polígono de Nevada, 10 de ellas pruebas oficiales mal etiquetadas).
- Falsos negativos con eps 25 km y 5 vecinos (73): 55 por ruido (pruebas aisladas: URSS fuera de los polígonos grandes, Pokhran, Chagai, Novaya Zemlya) y
  18 en Lop Nur, cuyo cluster tiene mediana de 10 km por mezclarse con terremotos de profundidad por defecto.
