# Genera las figuras del documento (docs/figuras/*.png) con el catalogo grande y los parametros fijos
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
P = dict(eps_km=25, vmin=1, dmin=0, dmax=2.5)

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
terremoto = df['tipo'] == 'earthquake'
otros_tipos = [('volcanic eruption', 'Erupciones volcánicas', 'darkorange', '^'),
               ('explosion', 'Explosiones (otras)', 'blue', 's'),
               ('mine collapse', 'Colapsos de mina', 'saddlebrown', 'D'),
               ('rock burst', 'Estallidos de roca', 'magenta', 'P'),
               ('landslide', 'Deslizamientos', 'green', 'v'),
               ('quarry blast', 'Voladura de cantera', 'cyan', 'X'),
               ('other event', 'Otro evento', 'black', '*')]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.scatter(df[terremoto].longitude, df[terremoto].latitude, s=1, c='lightgray', label=f'Terremotos ({terremoto.sum():,})')
for tipo, nombre, color, marcador in otros_tipos:
    sel = df['tipo'] == tipo
    ax.scatter(df[sel].longitude, df[sel].latitude, s=28, c=color, marker=marcador, edgecolors='white', linewidths=.3,
               label=f'{nombre} ({sel.sum()})')
ax.scatter(df[expl].longitude, df[expl].latitude, s=6, c='red', label=f'Explosiones nucleares ({expl.sum()})')
ax.set(xlabel='Longitud (°)', ylabel='Latitud (°)', xlim=(-180, 180), ylim=(-90, 90))
ax.legend(loc='lower left', markerscale=1.5, fontsize=7, ncol=2); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'catalogo.png', dpi=170); plt.close(fig)

# 2. Profundidad: la pista fisica
# Mismo ancho de bin (0.5 km) y mismo eje y en los dos paneles: fraccion de cada clase en cada bin
fig, ejes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
terremotos, explosiones = df[~expl].depth, df[expl].depth
for ax, (lo, hi, titulo) in zip(ejes, [(-5, 60, 'Todo el rango'), (-5, 15, 'Ampliado cerca de la superficie')]):
    bins = np.arange(lo, hi + 0.5, 0.5)
    ax.hist(terremotos, bins=bins, weights=np.ones(len(terremotos)) / len(terremotos), color='gray', alpha=.7, label='Terremotos')
    ax.hist(explosiones, bins=bins, weights=np.ones(len(explosiones)) / len(explosiones), color='red', alpha=.7, label='Explosiones')
    ax.axvline(P['dmin'], color='purple', lw=1.5, label=f"Ventana [{P['dmin']}; {P['dmax']}) km")
    ax.axvline(P['dmax'], color='purple', lw=1.5)
    ax.set(xlabel='Profundidad (km)', title=titulo, yscale='log', xlim=(lo, hi))
    ax.legend(loc='upper right', fontsize=8)
ejes[0].set_ylabel('Fraccion de la clase por bin de 0,5 km')
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
