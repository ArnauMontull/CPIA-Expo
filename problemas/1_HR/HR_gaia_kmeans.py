from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# 1. Leer Gaia DR3 a menos de 50 pc (paralaje > 20 mas, error < 10 %, RUWE < 1.4)
#    generado con: .venv\Scripts\python descargar_datos.py cercanas
CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA.parent.parent / 'datos'
df = pd.read_csv(DATOS / 'gaia_50pc.csv')

# 2. Features: HR observacional, color BP-RP (~ temperatura) y magnitud absoluta G (~ luminosidad).
#    Las dos ya son logarítmicas (magnitudes), así que no hace falta tomar log; sí escalar.
X = df[['bp_rp', 'abs_g_mag']].to_numpy()
escalador = StandardScaler()
X_esc = escalador.fit_transform(X)

# 3. K-Means con 4 clusters
K = 4
km = KMeans(n_clusters=K, n_init=10, random_state=0)
etiquetas = km.fit_predict(X_esc)
centroides = escalador.inverse_transform(km.cluster_centers_)

for k in range(K):
    c, M = centroides[k]
    print(f'Cluster {k}: {np.sum(etiquetas == k):6d} estrellas, centroide BP-RP = {c:5.2f}, M_G = {M:5.2f}')

# 4. Diagrama HR coloreado por cluster
colores = plt.cm.tab10(np.arange(K))
plt.figure(figsize=(9, 7))
for k in range(K):
    sel = etiquetas == k
    plt.scatter(df['bp_rp'][sel], df['abs_g_mag'][sel], s=1, alpha=0.4, color=colores[k],
                label=f'Cluster {k} ({sel.sum()})')
plt.scatter(centroides[:, 0], centroides[:, 1], s=200, marker='X', color=colores,
            edgecolors='k', linewidths=1.5, label='Centroides')

plt.gca().invert_yaxis()  # magnitud: más brillante arriba
plt.title(f'K-Means (k = {K}) sobre el HR de Gaia DR3 a < 50 pc ({len(df)} estrellas)')
plt.xlabel(r'Color $G_{BP} - G_{RP}$ (mag)  →  más fría')
plt.ylabel(r'Magnitud absoluta $M_G$')
plt.grid(True, linestyle='--', alpha=0.5)
leyenda = plt.legend(markerscale=6, loc='upper right')
leyenda.legend_handles[-1].set_sizes([80])
plt.tight_layout()
plt.savefig(CARPETA / 'kmeans_hr_gaia.png', dpi=150)

# 5. Codo y silhouette para k = 2..8 (silhouette sobre una muestra de 5000)
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
fig.savefig(CARPETA / 'kmeans_codo_silhouette_gaia.png', dpi=150)

plt.show()
