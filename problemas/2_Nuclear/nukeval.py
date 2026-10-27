"""
Validacion de nukeDBSCAN_arnau.py: silueta y distancias k para mirar eps,
estabilidad con el Adjusted Rand Index (ARI) y mapa de aciertos y errores.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.neighbors import NearestNeighbors

from nukeDBSCAN_arnau import parametros, df, agrupar, nukeDBSCAN, errores

CARPETA = Path(__file__).resolve().parent
RADIO_TIERRA_KM = 6371
EPS_PROBADOS = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]


# --- Silueta de unos clusters (sobre una muestra de 2000 sismos) ---
def silueta(df, cluster):
    coordenadas = np.radians(df[['latitude', 'longitude']])
    try:
        return silhouette_score(coordenadas, cluster, metric='haversine',
                                sample_size=2000, random_state=42)
    except ValueError:
        # La muestra no tiene al menos 2 clusters
        return np.nan


# --- Para cada eps: numero de clusters, silueta, FP y FN ---
def evaluar_eps(df, vmin, dmin, dmax):
    print('\n--- ELECCION DE EPS ---')
    print(f"{'eps (km)':<10}{'clusters':<10}{'silueta':<10}{'FP':<8}{'FN':<8}")
    print('-' * 46)

    n_clusters = []
    siluetas = []
    for eps in EPS_PROBADOS:
        cluster = agrupar(df, eps, vmin)
        detectado = nukeDBSCAN(df, eps, vmin, dmin, dmax)
        fp, fn = errores(df, detectado)

        n_clusters.append(cluster.nunique())
        siluetas.append(silueta(df, cluster))
        print(f'{eps:<10}{n_clusters[-1]:<10}{siluetas[-1]:<10.3f}{fp:<8}{fn:<8}')

    return n_clusters, siluetas


# --- Distancia de cada sismo a su 4.o vecino, de mayor a menor (el "codo" de DBSCAN) ---
def distancias_k(df, k=4):
    coordenadas = np.radians(df[['latitude', 'longitude']])
    vecinos = NearestNeighbors(n_neighbors=k, metric='haversine').fit(coordenadas)
    distancias, _ = vecinos.kneighbors(coordenadas)

    distancia_k = distancias[:, -1] * RADIO_TIERRA_KM
    return np.sort(distancia_k)[::-1]


# --- Estabilidad: ARI entre los clusters del catalogo y los de una muestra del 50% ---
def evaluar_estabilidad(df, eps_km, vmin):
    print(f'\n--- ESTABILIDAD (eps={eps_km} km, muestra del 50%) ---')
    cluster_completo = agrupar(df, eps_km, vmin)

    for semilla in [1, 2, 3, 4, 5]:
        muestra = df.sample(frac=0.5, random_state=semilla)
        cluster_muestra = agrupar(muestra, eps_km, vmin)

        ari = adjusted_rand_score(cluster_completo[muestra.index], cluster_muestra)
        print(f'Semilla {semilla}: clusters={cluster_muestra.nunique()}, ARI={ari:.4f}')


# --- Figura 1: clusters, silueta y distancias k ---
def figura_eps(n_clusters, siluetas, distancia_k):
    fig, ejes = plt.subplots(1, 3, figsize=(14, 3.8))

    ejes[0].plot(EPS_PROBADOS, n_clusters, 'o-')
    ejes[0].set(xlabel='eps (km)', ylabel='Numero de clusters', title='Clusters segun eps')

    ejes[1].plot(EPS_PROBADOS, siluetas, 'o-', color='green')
    ejes[1].set(xlabel='eps (km)', ylabel='Silueta', title='Silueta segun eps')

    ejes[2].plot(distancia_k)
    ejes[2].set(xlabel='Sismos ordenados', ylabel='Distancia al 4.o vecino (km)',
                yscale='log', title='Distancias k (codo)')

    for eje in ejes:
        eje.grid(True, linestyle='--', alpha=0.5)

    fig.tight_layout()
    fig.savefig(CARPETA / 'nukeval_eps.png', dpi=200)


# --- Figura 2: mapa de aciertos y errores ---
def figura_mapa(df, detectado):
    es_explosion = df['tipo'] == 'nuclear explosion'
    otros = df[~detectado & ~es_explosion]

    fig, eje = plt.subplots(figsize=(10, 5))
    eje.scatter(otros['longitude'], otros['latitude'], s=1, c='lightgray')

    grupos = [(detectado & es_explosion, 'green', 'Acierto'),
              (detectado & ~es_explosion, 'orange', 'Falso positivo'),
              (~detectado & es_explosion, 'black', 'Falso negativo')]
    for mascara, color, nombre in grupos:
        sismos = df[mascara]
        eje.scatter(sismos['longitude'], sismos['latitude'], s=8, c=color,
                    label=f'{nombre} ({len(sismos)})')

    eje.set(xlabel='Longitud (°)', ylabel='Latitud (°)',
            title='Aciertos y errores con los parametros fijos')
    eje.legend(loc='lower left', markerscale=2)
    eje.grid(True, linestyle='--', alpha=0.5)

    fig.tight_layout()
    fig.savefig(CARPETA / 'nukeval_mapa.png', dpi=200)


if __name__ == '__main__':
    print(f'Catalogo: {len(df)} eventos, parametros {parametros}')

    n_clusters, siluetas = evaluar_eps(df, parametros['vmin'], parametros['dmin'], parametros['dmax'])
    evaluar_estabilidad(df, parametros['eps_km'], parametros['vmin'])

    detectado = nukeDBSCAN(df, **parametros)
    fp, fn = errores(df, detectado)
    print(f'\nRun con los parametros fijos: FP={fp}, FN={fn}')

    figura_eps(n_clusters, siluetas, distancias_k(df))
    figura_mapa(df, detectado)
    print(f'Figuras guardadas en: {CARPETA}')
