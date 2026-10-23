import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

# 1. Cargar los datos
# Leemos el catalogo de sismos
df = pd.read_csv('datos/sismos_usgs.csv')
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])
#  Nos quedamos solo con los grandes (magnitud >= 4.5)
df = df[df['mag'] >= 4.5]
df = df.reset_index(drop=True)


# funcion DBSCAN
def nukeDBSCAN(df, eps_km, vmin, dmin, dmax):
    """
    Detecta los clusters y los filtra con DBSCAN

    Args:
        df: tabla de sismos
        eps_km: radio km
        vmin: vecinos mínimos del cluster
        dmin: profundidad mediana mínima (km) de un cluster sospechoso
        dmax: profundidad mediana máxima (km) de un cluster sospechoso

    Returns:
        Serie True/False: el sismo cae en un cluster sospechoso
    """

    # ---------------------------------------------------------------
    # PASO 2: Agrupar sismos cercanos con DBSCAN
    # ---------------------------------------------------------------
    # DBSCAN junta sismos que estan a menos de eps_km unos de otros.
    # Un grupo necesita al menos vmin sismos. Los que quedan solos reciben el grupo -1.
    radio_tierra_km = 6371

    # Con la distancia 'haversine' (distancia sobre la esfera) hay que dar
    # las coordenadas en radianes y el radio como fraccion del radio de la Tierra
    coordenadas = np.radians(df[['latitude', 'longitude']])

    dbscan = DBSCAN(eps=eps_km / radio_tierra_km,
                    min_samples=vmin,
                    metric='haversine')
    df = df.copy()
    df['cluster'] = dbscan.fit_predict(coordenadas)

    # ---------------------------------------------------------------
    # PASO 3: Decidir que grupos son sospechosos
    # ---------------------------------------------------------------
    # Una explosion nuclear ocurre casi en la superficie.
    # Por eso un grupo es sospechoso si la profundidad mediana de sus sismos esta entre dmin y dmax.
    sin_ruido = df[df['cluster'] != -1]
    profundidad_mediana = sin_ruido.groupby('cluster')['depth'].median()
    es_sospechoso = (profundidad_mediana >= dmin) & (profundidad_mediana < dmax)
    grupos_sospechosos = profundidad_mediana[es_sospechoso].index

    # detectado = True si el sismo pertenece a un grupo sospechoso
    return df['cluster'].isin(grupos_sospechosos)


# PASO 4: Probar varios radios, cada vez con un 10% de los sismos al azar
vec = np.linspace(1, 101, 100)
falsos_positivos = []
falsos_negativos = []

for i, eps in enumerate(vec):
    # # Muestra nueva del 20% en cada vuelta (el random_state = eps la hace reproducible)
    muestra = df.sample(frac=0.1, random_state=i)

    # Antes se guardaba en df[f'detectado_{eps}']; ahora se aplica a la muestra
    detectado = nukeDBSCAN(muestra, eps_km=10, vmin=vec, dmin=-10, dmax=5)
    es_explosion = muestra['tipo'] == 'nuclear explosion'

    # Contamos los dos tipos de error de esta vuelta
    falsos_positivos.append((detectado & ~es_explosion).sum())   # terremoto marcado como explosion
    falsos_negativos.append((~detectado & es_explosion).sum())   # explosion que no detectamos
    print(f'eps={eps} km: FP={falsos_positivos[-1]}, FN={falsos_negativos[-1]}')

# PASO 5: Grafica con matplotlib (antes era plotly y se guardaba en HTML)
plt.plot(eps_vec, falsos_positivos, 'o-', color='orange', label='Falsos positivos')
plt.plot(eps_vec, falsos_negativos, 'o-', color='gray', label='Falsos negativos')
plt.title('Errores de DBSCAN con un 10% de los datos')
plt.xlabel('Radio eps (km)')
plt.ylabel('Numero de sismos')
plt.legend()
plt.grid(True)
plt.show()
