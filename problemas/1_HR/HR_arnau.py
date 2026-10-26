from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# 1. Leer el catálogo Hipparcos (paralaje mejor del 10 %): B-V y magnitud absoluta V
#    (el script está en problemas/1)HR/, así que hay que subir tres carpetas hasta CPIA_Expo/)
CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA.parent.parent / 'datos'
df = pd.read_csv(DATOS / 'hr_hipparcos.csv')

# 2. Color B-V -> temperatura efectiva (Ballesteros 2012, EPL 97, 34008)
bv = df['B-V']
df['T'] = 4600 * (1 / (0.92 * bv + 1.7) + 1 / (0.92 * bv + 0.62))

# 3. Magnitud absoluta V -> luminosidad bolométrica
#    M_bol = M_V + BC(T); BC de Flower (1996) con los coeficientes corregidos de Torres (2010, AJ 140, 1158)
def correccion_bolometrica(T):
    logT = np.log10(T)
    frio = [-0.190537291496456e5, 0.155144866764412e5, -0.421278819301717e4, 0.381476328422343e3]
    medio = [-0.370510203809015e5, 0.385672629965804e5, -0.150651486316025e5,
             0.261724637119416e4, -0.170623810323864e3]
    caliente = [-0.118115450538963e6, 0.137145973583929e6, -0.636233812100225e5,
                0.147412923562646e5, -0.170587278406872e4, 0.788731721804990e2]
    poly = lambda c: sum(ci * logT**i for i, ci in enumerate(c))
    return np.where(logT < 3.70, poly(frio), np.where(logT < 3.90, poly(medio), poly(caliente)))

M_BOL_SOL = 4.74
df['L'] = 10 ** (-0.4 * (df['abs_v_mag'] + correccion_bolometrica(df['T']) - M_BOL_SOL))

# 4. Features: log T y log L (los ejes del HR), escaladas a media 0 y desviación 1
#    para que la distancia euclídea de K-Means no la domine la luminosidad
X = np.column_stack([np.log10(df['T']), np.log10(df['L'])])
escalador = StandardScaler()
X_esc = escalador.fit_transform(X)

# 5. K-Means con 4 clusters (10 inicializaciones; random_state fijo para que sea reproducible)
K = 4
km = KMeans(n_clusters=K, n_init=10, random_state=0)
etiquetas = km.fit_predict(X_esc)

# Centroides de vuelta a unidades físicas: deshacer el escalado y luego el log
centroides = 10 ** escalador.inverse_transform(km.cluster_centers_)

for k in range(K):
    T_c, L_c = centroides[k]
    print(f'Cluster {k}: {np.sum(etiquetas == k):5d} estrellas, centroide T = {T_c:6.0f} K, L = {L_c:8.3g} L_sol')

# 6. Diagrama HR coloreado por cluster
colores = plt.cm.tab10(np.arange(K))
plt.figure(figsize=(9, 6))
for k in range(K):
    sel = etiquetas == k
    plt.scatter(df['T'][sel], df['L'][sel], s=2, alpha=0.4, color=colores[k],
                label=f'Cluster {k} ({sel.sum()})')
plt.scatter(centroides[:, 0], centroides[:, 1], s=200, marker='X', color=colores,
            edgecolors='k', linewidths=1.5, label='Centroides')

plt.xscale('log')
plt.yscale('log')
plt.gca().invert_xaxis()  # convención HR: temperaturas altas a la izquierda

plt.title(f'K-Means (k = {K}) sobre el diagrama HR de Hipparcos ({len(df)} estrellas)')
plt.xlabel('Temperatura efectiva (K)')
plt.ylabel(r'Luminosidad ($L/L_\odot$)')
plt.grid(True, linestyle='--', alpha=0.5)
leyenda = plt.legend(markerscale=4, loc='lower left')
leyenda.legend_handles[-1].set_sizes([80])  # que la X de los centroides no salga gigante en la leyenda
plt.tight_layout()
plt.savefig(CARPETA / 'kmeans_hr.png', dpi=150)

# 7. ¿Es k = 4 una buena elección? Método del codo (inercia) y silhouette para k = 2..8
#    (silhouette es O(n^2): se calcula sobre una muestra de 5000 estrellas)
ks = range(2, 9)
inercias, siluetas = [], []
for k in ks:
    modelo = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X_esc)
    inercias.append(modelo.inertia_)
    siluetas.append(silhouette_score(X_esc, modelo.labels_, sample_size=5000, random_state=0))
    print(f'k = {k}: inercia = {modelo.inertia_:8.0f}, silhouette = {siluetas[-1]:.3f}')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
ax1.plot(ks, inercias, 'o-')
ax1.set_xlabel('Número de clusters k')
ax1.set_ylabel('Inercia (suma de distancias² al centroide)')
ax1.set_title('Método del codo')
ax2.plot(ks, siluetas, 'o-', color='tab:orange')
ax2.set_xlabel('Número de clusters k')
ax2.set_ylabel('Silhouette medio')
ax2.set_title('Silhouette')
for ax in (ax1, ax2):
    ax.axvline(K, color='gray', linestyle='--')
    ax.grid(True, linestyle='--', alpha=0.5)
fig.tight_layout()
fig.savefig(CARPETA / 'kmeans_codo_silhouette.png', dpi=150)

plt.show()
