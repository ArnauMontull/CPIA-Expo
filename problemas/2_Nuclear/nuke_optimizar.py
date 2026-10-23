# Archivo nuevo: busca los mejores eps_km, vmin, dmin y dmax para nuke_DBSCANfun.py
#
# Por que no Newton: el resultado (aciertos/fallos) salta a trompicones, no tiene derivada,
# y vmin es un numero entero. Lo que si se puede es ahorrar ejecuciones:
#   - DBSCAN (lo lento, ~2 s) solo depende de eps_km y vmin.
#   - dmin y dmax solo deciden que grupos se marcan como sospechosos, asi que se prueban
#     todas las combinaciones sobre los grupos ya calculados, sin repetir DBSCAN.
# Resultado: 11 x 7 = 77 ejecuciones de DBSCAN en vez de 77 x 21 x 20 = 32.340.
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

# 1. Cargar los datos (igual que en nuke_DBSCANfun.py)
df = pd.read_csv('datos/sismos_usgs.csv')
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])
df = df[df['mag'] >= 4.5]
df = df.reset_index(drop=True)

es_real = df['tipo'] == 'nuclear explosion'
total_explosiones = es_real.sum()
coordenadas = np.radians(df[['latitude', 'longitude']])

# 2. Valores a probar
eps_candidatos = np.arange(5, 30.1, 2.5)
vmin_candidatos = range(1, 8)
dmin_candidatos = np.arange(-40, 0.1, 2)
dmax_candidatos = np.arange(0.1, 10.1, 0.5)

# 3. Bucle de busqueda
mejor = {'f1': 0}
for eps_km in eps_candidatos:
    for vmin in vmin_candidatos:
        # DBSCAN una sola vez para este eps_km y vmin
        dbscan = DBSCAN(eps=eps_km / 6371, min_samples=vmin, metric='haversine')
        grupo = dbscan.fit_predict(coordenadas)

        # Por grupo: profundidad mediana, sismos totales y explosiones (sin el ruido, -1)
        tabla = pd.DataFrame({'grupo': grupo, 'depth': df['depth'], 'real': es_real})
        tabla = tabla[tabla['grupo'] != -1]
        tabla = tabla.groupby('grupo').agg(mediana=('depth', 'median'),
                                           total=('real', 'size'),
                                           explosiones=('real', 'sum'))

        # Probar todos los dmin y dmax sobre esos grupos
        for dmin in dmin_candidatos:
            for dmax in dmax_candidatos:
                marcado = (tabla['mediana'] >= dmin) & (tabla['mediana'] < dmax)
                aciertos = tabla.loc[marcado, 'explosiones'].sum()
                if aciertos == 0:
                    continue
                falsos_positivos = tabla.loc[marcado, 'total'].sum() - aciertos
                falsos_negativos = total_explosiones - aciertos

                # F1 = un solo numero que junta precision y recall (1 = perfecto)
                f1 = 2 * aciertos / (2 * aciertos + falsos_positivos + falsos_negativos)
                if f1 > mejor['f1']:
                    mejor = {'f1': round(f1, 4), 'eps_km': eps_km, 'vmin': vmin,
                             'dmin': dmin, 'dmax': dmax,
                             'FP': falsos_positivos, 'FN': falsos_negativos}
    print(f'eps={eps_km} km hecho. Mejor hasta ahora: {mejor}', flush=True)

print('\nParametros optimos:', mejor)
