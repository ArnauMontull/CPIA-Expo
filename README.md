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

## Estructura
- `problemas/`: un script por problema; cada uno descarga sus datos en `datos/`, que no se sube a git.
- `docs/`: enunciado, rúbrica y el documento de descripción.
- `presentacion/`: las diapositivas.
