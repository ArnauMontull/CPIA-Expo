# Genera las figuras del documento (docs/figuras/*.png) con el catalogo grande y sus parametros optimos
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

RAIZ = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / 'figuras'
OUT.mkdir(exist_ok=True)
P = dict(eps_km=25, vmin=1, dmin=0, dmax=0.1)

df = pd.read_csv(RAIZ / 'datos' / 'sismos_usgs_M45_1951_2025.csv')
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])
df = df[df['mag'] >= 4.5].reset_index(drop=True)
expl = df['tipo'] == 'nuclear explosion'


def clusters(d, eps_km, vmin):
    c = DBSCAN(eps=eps_km / 6371, min_samples=vmin, metric='haversine').fit_predict(np.radians(d[['latitude', 'longitude']]))
    return pd.Series(c, index=d.index)


def sospechosos(d, c, dmin, dmax):
    med = d['depth'].groupby(c[c != -1]).median()
    return c.isin(med[(med >= dmin) & (med < dmax)].index)


cl = clusters(df, P['eps_km'], P['vmin'])
det = sospechosos(df, cl, P['dmin'], P['dmax'])

# 1. Catalogo: terremotos vs explosiones
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.scatter(df[~expl].longitude, df[~expl].latitude, s=1, c='lightgray', label=f'Terremotos ({(~expl).sum():,})')
ax.scatter(df[expl].longitude, df[expl].latitude, s=6, c='red', label=f'Explosiones nucleares ({expl.sum()})')
ax.set(xlabel='Longitud (°)', ylabel='Latitud (°)', xlim=(-180, 180), ylim=(-90, 90))
ax.legend(loc='lower left', markerscale=4); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'catalogo.png', dpi=170); plt.close(fig)

# 2. Profundidad: la pista fisica
fig, ax = plt.subplots(figsize=(7, 3.8))
bins = np.linspace(-2, 60, 63)
ax.hist(df[~expl].depth.clip(-2, 60), bins=bins, color='gray', alpha=.7, density=True, label='Terremotos')
ax.hist(df[expl].depth.clip(-2, 60), bins=bins, color='red', alpha=.7, density=True, label='Explosiones')
ax.axvspan(P['dmin'], P['dmax'], color='purple', alpha=.25, label='Ventana [dmin, dmax)')
ax.set(xlabel='Profundidad (km)', ylabel='Densidad'); ax.set_yscale('log'); ax.legend()
fig.tight_layout(); fig.savefig(OUT / 'profundidad.png', dpi=170); plt.close(fig)

# 3. Como se detecta: zoom en Nevada, clusters y mediana de profundidad
z = df[(df.latitude.between(35.5, 38.5)) & (df.longitude.between(-118.5, -114))]
cz = cl[z.index]
medz = z['depth'].groupby(cz).median()
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True, sharey=True)
ax[0].scatter(z.longitude, z.latitude, s=8, c='lightgray', edgecolors='k', linewidths=.2)
ax[0].set_title('1) Epicentros M ≥ 4,5 (sin etiquetas)')
col = np.where(det[z.index], 'purple', 'steelblue')
ax[1].scatter(z.longitude, z.latitude, s=8, c=col, edgecolors='none')
ax[1].scatter(z[expl[z.index]].longitude, z[expl[z.index]].latitude, s=40, facecolors='none', edgecolors='red', linewidths=.8)
ax[1].set_title('2) DBSCAN eps=25 km (morado: sospechoso)')
for a in ax:
    a.set_xlabel('Longitud (°)'); a.grid(alpha=.3)
ax[0].set_ylabel('Latitud (°)')
fig.tight_layout(); fig.savefig(OUT / 'deteccion_nevada.png', dpi=170); plt.close(fig)

# 4. Barrido de eps con el 10 % de los datos
eps_vec = np.linspace(1, 201, 50)
fp_v, fn_v = [], []
for i, eps in enumerate(eps_vec):
    m = df.sample(frac=0.1, random_state=i)
    d = sospechosos(m, clusters(m, eps, P['vmin']), P['dmin'], P['dmax'])
    e = m['tipo'] == 'nuclear explosion'
    fp_v.append((d & ~e).sum()); fn_v.append((~d & e).sum())
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.plot(eps_vec, fp_v, 'o-', color='orange', ms=3, label='Falsos positivos')
ax.plot(eps_vec, fn_v, 'o-', color='gray', ms=3, label='Falsos negativos')
ax.set(xlabel='Radio eps (km)', ylabel='Número de sismos', title='Errores con un 10 % aleatorio de los datos')
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'barrido_eps.png', dpi=170); plt.close(fig)

# 5. Resultado final: aciertos y errores
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.scatter(df[~expl & ~det].longitude, df[~expl & ~det].latitude, s=1, c='lightgray')
for m, c, n in [(det & expl, 'green', 'Acierto'), (det & ~expl, 'orange', 'Falso positivo'), (~det & expl, 'black', 'Falso negativo')]:
    ax.scatter(df[m].longitude, df[m].latitude, s=8, c=c, label=f'{n} ({m.sum()})')
ax.set(xlabel='Longitud (°)', ylabel='Latitud (°)', xlim=(-180, 180), ylim=(-90, 90))
ax.legend(loc='lower left', markerscale=2); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'resultado.png', dpi=170); plt.close(fig)

tp, fp, fn = (det & expl).sum(), (det & ~expl).sum(), (~det & expl).sum()
print(f'TP={tp} FP={fp} FN={fn} precision={tp/(tp+fp):.3f} recall={tp/(tp+fn):.3f} F1={2*tp/(2*tp+fp+fn):.4f}')
