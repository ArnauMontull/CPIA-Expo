import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

# 1. Cargar los datos: sismos con magnitud >= 4.5
df = pd.read_csv('datos/sismos_usgs.csv')
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])
df = df[df['mag'] >= 4.5]
df = df.reset_index(drop=True)


# 2. Funcion que agrupa los sismos cercanos con DBSCAN
def nukeDBSCAN(df, eps_km, vmin):
    """
    Agrupa los sismos cercanos con DBSCAN

    Args:
        df: tabla de sismos
        eps_km: radio en km
        vmin: sismos minimos por cluster

    Returns:
        Numero de cluster de cada sismo (-1 = sismo aislado)
    """
    radio_tierra_km = 6371

    # La distancia 'haversine' (sobre la esfera) pide las coordenadas en radianes
    # y el radio como fraccion del radio de la Tierra
    coordenadas = np.radians(df[['latitude', 'longitude']])

    eps_rad=eps_km / radio_tierra_km
    dbscan = DBSCAN(eps=eps_rad,
                    min_samples=vmin,
                    metric='haversine')
    return dbscan.fit_predict(coordenadas)


# 3. Probar varios radios, cada vez con un 10% de los sismos al azar
eps_vec = np.linspace(1, 201, 50)
falsos_positivos = []
falsos_negativos = []

# Un cluster es sospechoso si la profundidad mediana de sus sismos esta entre dmin y dmax (km),
# porque una explosion nuclear ocurre casi en la superficie
dmin = -4
dmax = 0.1

for i, eps in enumerate(eps_vec):
    # Muestra distinta en cada vuelta; random_state=i la hace reproducible
    muestra = df.sample(frac=0.1, random_state=i).copy()
    muestra['cluster'] = nukeDBSCAN(muestra, eps_km=eps, vmin=3)

    # Clusters sospechosos (sin contar el ruido, -1)
    sin_ruido = muestra[muestra['cluster'] != -1]
    profundidad_mediana = sin_ruido.groupby('cluster')['depth'].median()
    es_sospechoso = (profundidad_mediana >= dmin) & (profundidad_mediana < dmax)
    clusters_sospechosos = profundidad_mediana[es_sospechoso].index

    # detectado: el sismo esta en un cluster sospechoso
    detectado = muestra['cluster'].isin(clusters_sospechosos)
    es_explosion = muestra['tipo'] == 'nuclear explosion'

    # Falso positivo: terremoto marcado como explosion
    # Falso negativo: explosion que no se detecta
    falsos_positivos.append((detectado & ~es_explosion).sum())
    falsos_negativos.append((~detectado & es_explosion).sum())
    print(f'eps={eps:.1f} km: FP={falsos_positivos[-1]}, FN={falsos_negativos[-1]}')

# 4. Grafica de los errores segun el radio
plt.plot(eps_vec, falsos_positivos, 'o-', color='orange', label='Falsos positivos')
plt.plot(eps_vec, falsos_negativos, 'o-', color='gray', label='Falsos negativos')
plt.title('Errores de DBSCAN con un 10% de los datos')
plt.xlabel('Radio eps (km)')
plt.ylabel('Numero de sismos')
plt.legend()
plt.grid(True)
plt.show()
