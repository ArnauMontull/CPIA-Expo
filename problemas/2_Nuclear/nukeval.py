"""
Validacion de nukeDBSCAN_arnau.py: elegir eps sin etiquetas (clusters y silueta), medir la estabilidad
con el Adjusted Rand Index (ARI) y dibujar el mapa de aciertos y errores.
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.neighbors import NearestNeighbors

from nukeDBSCAN_arnau import CATALOGO, optimos, df, agrupar, nukeDBSCAN, errores

CARPETA = Path(__file__).resolve().parent
RADIO_TIERRA_KM = 6371


def silueta(df, cluster, n=2000):
    """Silueta (distancia haversine) sobre una muestra de n sismos; nan si la muestra no tiene 2+ grupos."""
    coordenadas = np.radians(df[['latitude', 'longitude']])
    try:
        return silhouette_score(coordenadas, cluster, metric='haversine', sample_size=n, random_state=42)
    except ValueError:
        return np.nan


def evaluar_eps(df, vmin, dmin, dmax, eps_vec=(5, 10, 15, 20, 25, 30, 40, 50, 75, 100)):
    """Para cada eps: numero de clusters y silueta (sin etiquetas), y FP/FN (con etiquetas)."""
    print('\n--- ELECCION DE EPS ---')
    print(f"{'eps (km)':<10}{'clusters':<10}{'silueta':<10}{'FP':<8}{'FN':<8}")
    print('-' * 46)
    n_clusters, siluetas = [], []
    for eps in eps_vec:
        cluster = agrupar(df, eps, vmin)
        detectado = nukeDBSCAN(df, eps, vmin, dmin, dmax)
        fp, fn = errores(df, detectado)
        n_clusters.append(cluster.nunique())
        siluetas.append(silueta(df, cluster))
        print(f'{eps:<10}{n_clusters[-1]:<10}{siluetas[-1]:<10.3f}{fp:<8}{fn:<8}')
    return list(eps_vec), n_clusters, siluetas


def distancias_k(df, k=4):
    """Distancia (km) de cada sismo a su k-esimo vecino, ordenada: el 'codo' clasico para elegir eps en DBSCAN."""
    coordenadas = np.radians(df[['latitude', 'longitude']])
    vecinos = NearestNeighbors(n_neighbors=k, metric='haversine').fit(coordenadas)
    distancias, _ = vecinos.kneighbors(coordenadas)
    return np.sort(distancias[:, -1] * RADIO_TIERRA_KM)[::-1]


def evaluar_estabilidad(df, eps_km, vmin, semillas=(1, 2, 3, 4, 5), frac=0.5):
    """ARI entre los clusters de todo el catalogo y los de una muestra aleatoria (mismos sismos)."""
    print(f'\n--- ESTABILIDAD (eps={eps_km} km, muestra del {frac:.0%}) ---')
    base = agrupar(df, eps_km, vmin)
    for semilla in semillas:
        muestra = df.sample(frac=frac, random_state=semilla)
        cluster = agrupar(muestra, eps_km, vmin)
        ari = adjusted_rand_score(base[muestra.index], cluster)
        print(f'Semilla: {semilla} | clusters: {cluster.nunique()} | ARI (vs catalogo completo): {ari:.4f}')


def generar_figuras(df, eps_vec, n_clusters, siluetas, k_distancias, detectado, salida=CARPETA):
    """Figura 1: clusters y silueta frente a eps, y distancias k. Figura 2: mapa de aciertos y errores."""
    fig, ejes = plt.subplots(1, 3, figsize=(14, 3.8))
    ejes[0].plot(eps_vec, n_clusters, 'o-')
    ejes[0].set(xlabel='eps (km)', ylabel='Numero de clusters', title='Clusters segun eps')
    ejes[1].plot(eps_vec, siluetas, 'o-', color='green')
    ejes[1].set(xlabel='eps (km)', ylabel='Silueta', title='Silueta segun eps')
    ejes[2].plot(k_distancias)
    ejes[2].set(xlabel='Sismos ordenados', ylabel='Distancia al 4.o vecino (km)', yscale='log',
                title='Distancias k (codo)')
    for eje in ejes:
        eje.grid(True, linestyle='--', alpha=0.5)
    fig.tight_layout()
    fig.savefig(salida / 'nukeval_eps.png', dpi=200)

    es_explosion = df['tipo'] == 'nuclear explosion'
    plt.figure(figsize=(10, 5))
    plt.scatter(df[~detectado & ~es_explosion]['longitude'], df[~detectado & ~es_explosion]['latitude'],
                s=1, c='lightgray')
    for mascara, color, nombre in [(detectado & es_explosion, 'green', 'Acierto'),
                                   (detectado & ~es_explosion, 'orange', 'Falso positivo'),
                                   (~detectado & es_explosion, 'black', 'Falso negativo')]:
        plt.scatter(df[mascara]['longitude'], df[mascara]['latitude'], s=8, c=color,
                    label=f'{nombre} ({mascara.sum()})')
    plt.xlabel('Longitud (°)')
    plt.ylabel('Latitud (°)')
    plt.title('Aciertos y errores con los parametros optimos')
    plt.legend(loc='lower left', markerscale=2)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(salida / 'nukeval_mapa.png', dpi=200)
    print(f'\nFiguras guardadas en: {salida}')


def main():
    p = optimos[CATALOGO]
    print(f'Catalogo: {CATALOGO} ({len(df)} sismos), parametros {p}')

    eps_vec, n_clusters, siluetas = evaluar_eps(df, p['vmin'], p['dmin'], p['dmax'])
    evaluar_estabilidad(df, p['eps_km'], p['vmin'])

    detectado = nukeDBSCAN(df, **p)
    fp, fn = errores(df, detectado)
    print(f'\nRun optimo: FP={fp}, FN={fn}')
    generar_figuras(df, eps_vec, n_clusters, siluetas, distancias_k(df), detectado)


if __name__ == '__main__':
    main()
