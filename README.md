# CPIA · Exposición: Aprendizaje no supervisado y detección de anomalías

Equipo: **Matías, Martí, Uriel y Arnau** (enunciado: `docs/temas_exposicion.pdf`; rúbrica: `docs/rubrica.odt`).

## Objetivo
Entender cómo encontrar estructura y patrones en datos sin etiquetar mediante algoritmos de clustering y
detección de anomalías.

## Guion
- Algoritmos de clustering: K-Means (`sklearn.cluster.KMeans`), DBSCAN (`sklearn.cluster.DBSCAN`) y
  clustering jerárquico.
- Modelos de mezcla gaussiana: `sklearn.mixture.GaussianMixture`.
- Detección de anomalías: Isolation Forest (`sklearn.ensemble.IsolationForest`).
- Cómo evaluar un clustering sin etiquetas: silhouette score y método del codo.
- Cuatro problemas con aplicación física (uno por persona). Sugerencias del enunciado:
  - Fácil: agrupar estrellas por temperatura y luminosidad con K-Means y comparar con el diagrama HR.
  - Media: identificar cúmulos estelares en datos reales de Gaia con DBSCAN (`astroquery`).
  - Difícil: detectar tránsitos de exoplanetas como anomalías en curvas de luz de Kepler (`lightkurve`).

## Reparto
| Problema | Responsable | Fichero |
|---|---|---|
| (por decidir) | Matías | `problemas/<nemotecnico>_matias.py` |
| (por decidir) | Martí | `problemas/<nemotecnico>_marti.py` |
| (por decidir) | Uriel | `problemas/<nemotecnico>_uriel.py` |
| (por decidir) | Arnau | `problemas/<nemotecnico>_arnau.py` |

## Entregables
1. **Presentación** (`presentacion/`), preferiblemente `.pptx`, en catalán, castellano o inglés.
2. **Documento de descripción** de los problemas: nombres de todos los integrantes, quién ha implementado
   cada problema y una descripción detallada para reproducir cada experimento, sin omitir detalles. Se valora
   la originalidad.
3. **Código fuente**: un `.py` por problema, con el nombre `<nemotécnico del problema>_<estudiante>.py`.

## Rúbrica de la exposición
Contenido 20 % · organización 10 % · exposición (mantener el interés) 30 % · expresión oral 10 % ·
tiempo 5 % · trabajo en equipo 5 % (todos exponen y conocen la presentación entera) · respuesta a
preguntas 20 %.

## Entorno y datos
```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt        # Linux/Mac: .venv/bin/pip
.venv\Scripts\python descargar_datos.py              # solo si quieres regenerar datos/ (los CSV ya están en git)
```
| Dataset | Fichero | Para |
|---|---|---|
| Hipparcos (VizieR I/239), estrellas con paralaje mejor del 10 %: B−V y magnitud absoluta V | `datos/hr_hipparcos.csv` (~20 800 estrellas) | K-Means vs diagrama HR (fácil) |
| Gaia DR3, cono de 3° alrededor de las Pléyades (M45) con movimientos propios y paralaje | `datos/gaia_pleiades.csv` | DBSCAN para encontrar el cúmulo (media) |
| Kepler-10, curva de luz de cadencia larga (todos los trimestres) | `datos/kepler10_curva_luz.csv` (~52 000 puntos) | Tránsitos como anomalías con Isolation Forest (difícil) |

Comprobación: en la curva de Kepler-10, un BLS da el periodo de Kepler-10b (0,8375 d, ~160 ppm de profundidad).

## Estructura
- `problemas/`: un script por problema; leen los CSV de `datos/`.
- `docs/`: enunciado, rúbrica y el documento de descripción.
- `presentacion/`: las diapositivas.
