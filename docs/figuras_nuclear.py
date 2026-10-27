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

# 0. Fuentes: corte vertical de un terremoto y de una explosion (esquema estatico, estilo LaTeX)
from matplotlib.patches import Arc


def frente(ax, foco, r, **kw):
    # Frente de onda de radio r, solo la parte bajo el suelo (profundidad >= 0)
    if r <= foco:
        ax.add_patch(Arc((0, foco), 2 * r, 2 * r, **kw))
    else:
        a = np.degrees(np.arcsin(foco / r))
        ax.add_patch(Arc((0, foco), 2 * r, 2 * r, theta1=-a, theta2=180 + a, **kw))



plt.rcParams.update({'font.family': 'serif', 'font.serif': ['STIXGeneral'], 'mathtext.fontset': 'stix'})
prof_terremoto = df.loc[df['tipo'] == 'earthquake', 'depth'].median()
fig, ejes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for ax, titulo, foco, color in [(ejes[0], 'Terremoto', prof_terremoto, 'black'),
                                (ejes[1], 'Explosión nuclear', 0.8, 'firebrick')]:
    ax.axhspan(0, 60, color='0.94', zorder=0)
    ax.axhline(0, color='black', lw=1)
    for xe in (-40, 40):
        ax.plot(xe, -1.6, marker='v', color='black', ms=7, clip_on=False)
    # frentes de onda P (continua) y, solo en el terremoto, S (discontinua, mas lenta)
    for r in (12, 24, 36):
        frente(ax, foco, r, color=color, lw=1)
    if titulo == 'Terremoto':
        for r in (7, 14, 21):
            frente(ax, foco, r, color='0.45', lw=1, ls='--')
        ax.plot([-9, 9], [foco + 9, foco - 9], color='black', lw=2)          # falla
        ax.annotate('', (-5, foco + 2.5), (1, foco - 3.5), arrowprops=dict(arrowstyle='->', lw=.8))
        ax.annotate('', (5, foco - 2.5), (-1, foco + 3.5), arrowprops=dict(arrowstyle='->', lw=.8))
        ax.text(10, foco - 10, 'falla', fontsize=10)
    else:
        for ang in np.radians(np.arange(200, 341, 35)):
            ax.annotate('', (7 * np.cos(ang), foco - 7 * np.sin(ang)), (2 * np.cos(ang), foco - 2 * np.sin(ang)),
                        arrowprops=dict(arrowstyle='->', lw=.8, color=color))
    ax.plot(0, foco, marker='*', color=color, ms=13, zorder=5)
    ax.annotate('', (-47, foco), (-47, 0), arrowprops=dict(arrowstyle='<->', lw=.7))
    ax.text(-45.5, foco / 2 if foco > 3 else 4, f'{foco:.0f} km' if foco > 3 else '< 1 km', fontsize=10, va='center')
    ax.set_title(titulo, fontsize=12)
    ax.set(xlim=(-50, 50), ylim=(55, -6), xticks=[], aspect='equal')
    for lado in ('top', 'right', 'bottom'):
        ax.spines[lado].set_visible(False)
ejes[0].set_ylabel('profundidad (km)', fontsize=10)
ejes[0].plot([], [], color='black', lw=1, label='onda P (compresión)')
ejes[0].plot([], [], color='0.45', lw=1, ls='--', label='onda S (cizalla)')
ejes[0].plot([], [], 'kv', ms=6, ls='none', label='sismógrafo')
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.legend(loc='lower center', ncol=3, fontsize=9.5, frameon=False)
fig.savefig(OUT / 'fuentes.png', dpi=200)
plt.close(fig)
plt.rcdefaults()
matplotlib.use('Agg')

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
ax[0].scatter(z.longitude, z.latitude, s=14, c='lightgray', edgecolors='k', linewidths=.3)
ax[0].set_title('1) Epicentros M ≥ 4,5 (sin etiquetas)')
sosp = det[z.index]
real = expl[z.index]
ax[1].scatter(z[~sosp].longitude, z[~sosp].latitude, s=24, c='steelblue', edgecolors='none', label='Cluster no sospechoso')
ax[1].scatter(z[sosp].longitude, z[sosp].latitude, s=24, c='darkorange', edgecolors='none', label='Cluster sospechoso (mediana < 2,5 km)')
ax[1].scatter(z[real].longitude, z[real].latitude, s=7, facecolors='none', edgecolors='black', linewidths=.5, label='Explosión real (etiqueta USGS)')
ax[1].set_title('2) DBSCAN con eps = 25 km')
ax[1].legend(loc='upper right', fontsize=7.5, framealpha=.95)
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
