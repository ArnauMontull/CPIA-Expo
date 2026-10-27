# Figuras en catala para la presentacion (presentacion/figuras_cat/*.png): mismas figuras que docs/figuras_nuclear.py
# con las etiquetas traducidas, mas la figura de errores segun eps y el histograma de profundidad
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

RAIZ = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / 'figuras_cat'
OUT.mkdir(exist_ok=True)
P = dict(eps_km=25, vmin=2, dmin=0, dmax=2.5)

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
for ax, titulo, foco, color in [(ejes[0], 'Terratrèmol', prof_terremoto, 'black'),
                                (ejes[1], 'Explosió nuclear', 0.8, 'firebrick')]:
    ax.axhspan(0, 60, color='0.94', zorder=0)
    ax.axhline(0, color='black', lw=1)
    for xe in (-40, 40):
        ax.plot(xe, -1.6, marker='v', color='black', ms=7, clip_on=False)
    # frentes de onda P (continua) y, solo en el terremoto, S (discontinua, mas lenta)
    for r in (12, 24, 36):
        frente(ax, foco, r, color=color, lw=1)
    if titulo == 'Terratrèmol':
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
ejes[0].set_ylabel('profunditat (km)', fontsize=10)
ejes[0].plot([], [], color='black', lw=1, label='ona P (compressió)')
ejes[0].plot([], [], color='0.45', lw=1, ls='--', label='ona S (cisalla)')
ejes[0].plot([], [], 'kv', ms=6, ls='none', label='sismògraf')
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.legend(loc='lower center', ncol=3, fontsize=9.5, frameon=False)
fig.savefig(OUT / 'fuentes.png', dpi=200)
plt.close(fig)
plt.rcdefaults()
matplotlib.use('Agg')

# 1. Catalogo: terremotos vs explosiones
terremoto = df['tipo'] == 'earthquake'
otros_tipos = [('volcanic eruption', 'Erupcions volcàniques', 'darkorange', '^'),
               ('explosion', 'Explosions (altres)', 'blue', 's'),
               ('mine collapse', 'Esfondraments de mina', 'saddlebrown', 'D'),
               ('rock burst', 'Esclats de roca', 'magenta', 'P'),
               ('landslide', 'Esllavissades', 'green', 'v'),
               ('quarry blast', 'Voladura de pedrera', 'cyan', 'X'),
               ('other event', 'Altre esdeveniment', 'black', '*')]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.scatter(df[terremoto].longitude, df[terremoto].latitude, s=1, c='lightgray', label=f'Terratrèmols ({terremoto.sum():,})')
for tipo, nombre, color, marcador in otros_tipos:
    sel = df['tipo'] == tipo
    ax.scatter(df[sel].longitude, df[sel].latitude, s=28, c=color, marker=marcador, edgecolors='white', linewidths=.3,
               label=f'{nombre} ({sel.sum()})')
ax.scatter(df[expl].longitude, df[expl].latitude, s=6, c='red', label=f'Explosions nuclears ({expl.sum()})')
ax.set(xlabel='Longitud (°)', ylabel='Latitud (°)', xlim=(-180, 180), ylim=(-90, 90))
ax.legend(loc='lower left', markerscale=1.5, fontsize=7, ncol=2); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'catalogo.png', dpi=170); plt.close(fig)

# 3. Como se detecta: zoom en Nevada, clusters y mediana de profundidad
z = df[(df.latitude.between(35.5, 38.5)) & (df.longitude.between(-118.5, -114))]
cz = cl[z.index]
medz = z['depth'].groupby(cz).median()
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6), sharex=True, sharey=True)
ax[0].scatter(z.longitude, z.latitude, s=14, c='lightgray', edgecolors='k', linewidths=.3)
ax[0].set_title('1) Epicentres M ≥ 4,5 (sense etiquetes)')
sosp = det[z.index]
real = expl[z.index]
ax[1].scatter(z[~sosp].longitude, z[~sosp].latitude, s=24, c='steelblue', edgecolors='none', label='Clúster no sospitós')
ax[1].scatter(z[sosp].longitude, z[sosp].latitude, s=24, c='darkorange', edgecolors='none', label='Clúster sospitós (mediana < 2,5 km)')
ax[1].scatter(z[real].longitude, z[real].latitude, s=7, facecolors='none', edgecolors='black', linewidths=.5, label='Explosió real (etiqueta USGS)')
ax[1].set_title('2) DBSCAN amb eps = 25 km')
ax[1].legend(loc='upper right', fontsize=7.5, framealpha=.95)
for a in ax:
    a.set_xlabel('Longitud (°)'); a.grid(alpha=.3)
ax[0].set_ylabel('Latitud (°)')
fig.tight_layout(); fig.savefig(OUT / 'deteccion_nevada.png', dpi=170); plt.close(fig)

# 5. Resultado final: aciertos y errores
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.scatter(df[~expl & ~det].longitude, df[~expl & ~det].latitude, s=1, c='lightgray')
for m, c, n in [(det & expl, 'green', 'Encert'), (det & ~expl, 'orange', 'Fals positiu'), (~det & expl, 'black', 'Fals negatiu')]:
    ax.scatter(df[m].longitude, df[m].latitude, s=8, c=c, label=f'{n} ({m.sum()})')
ax.set(xlabel='Longitud (°)', ylabel='Latitud (°)', xlim=(-180, 180), ylim=(-90, 90))
ax.legend(loc='lower left', markerscale=2); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'resultado.png', dpi=170); plt.close(fig)

# 5b. Mapa de los poligonos de ensayo: cada cluster con explosiones, detectado o no
sitios = [  # numero, nombre, (lon min, lon max, lat min, lat max) del cluster, posicion del texto
    (1, 'Nevada', (-117.5, -115, 36, 38), (-150, 12)),
    (2, 'Fallon (Shoal, 1963)', (-118.6, -118.2, 39, 39.4), (-150, 62)),
    (3, 'Semipalatinsk', (77, 80, 49, 51), (62, 22)),
    (4, 'Astracan', (47.5, 49, 46, 48), (14, 24)),
    (5, 'Nova Zembla', (52, 56, 70, 75), (24, 79)),
    (6, 'Lop Nur', (88, 89.5, 41, 42), (96, 12)),
    (7, 'Punggye-ri', (128.5, 129.5, 41, 42), (132, 52)),
    (8, 'Mururoa', (-139.5, -138, -23, -21.5), (-100, -50)),
]
fig, ax = plt.subplots(figsize=(11, 5.4))
ax.scatter(df[~expl].longitude, df[~expl].latitude, s=1, c='lightgray', zorder=1)
ax.scatter(df[expl & det].longitude, df[expl & det].latitude, s=12, c='green', zorder=3, label=f'Explosió detectada ({(expl & det).sum()})')
ax.scatter(df[expl & ~det].longitude, df[expl & ~det].latitude, s=16, c='black', marker='X', zorder=4, label=f'Explosió no detectada ({(expl & ~det).sum()})')
for num, nombre, (x0, x1, y0, y1), (tx, ty) in sitios:
    m = expl & df.longitude.between(x0, x1) & df.latitude.between(y0, y1)
    cx, cy = df[m].longitude.mean(), df[m].latitude.mean()
    ax.scatter([cx], [cy], s=260, facecolors='none', edgecolors='darkorange', linewidths=1.6, zorder=5)
    ax.annotate(f'{num}. {nombre}', xy=(cx, cy), xytext=(tx, ty), fontsize=9, ha='center',
                arrowprops=dict(arrowstyle='-', color='darkorange', lw=.8), zorder=6,
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='darkorange', lw=.8))
ax.set(xlabel='Longitud (°)', ylabel='Latitud (°)', xlim=(-180, 180), ylim=(-90, 90))
ax.legend(loc='lower right', markerscale=1.5, fontsize=9); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'mapa_clusters.png', dpi=170); plt.close(fig)

tp, fp, fn = (det & expl).sum(), (det & ~expl).sum(), (~det & expl).sum()
print(f'TP={tp} FP={fp} FN={fn} precision={tp/(tp+fp):.3f} recall={tp/(tp+fn):.3f} F1={2*tp/(2*tp+fp+fn):.4f}')


# 6. Profundidad (un panel, cerca de la superficie) con la ventana sombreada
fig, ax = plt.subplots(figsize=(8, 4.2))
bins = np.arange(-5, 60.5, 0.5)
terremotos, explosiones = df[~expl].depth, df[expl].depth
ax.hist(terremotos, bins=bins, weights=np.ones(len(terremotos)) / len(terremotos), color='#6B7280', alpha=.75, label='Terratrèmols')
ax.hist(explosiones, bins=bins, weights=np.ones(len(explosiones)) / len(explosiones), color='#D64545', alpha=.85, label='Explosions nuclears')
ax.axvspan(P['dmin'], P['dmax'], color='#E8710A', alpha=.25, label='Finestra [0; 2,5) km')
ax.set(xlabel='Profunditat (km)', ylabel='Fracció de la classe', yscale='log', xlim=(-5, 60))
ax.legend(loc='upper right', frameon=False)
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'profunditat.png', dpi=200); plt.close(fig)

# 7. Errores segun eps (valores de nukeval.py, eps de 5 en 5 km)
eps = list(range(5, 101, 5))
fp = [266, 126, 89, 66, 57, 99, 100, 88, 86, 453, 130, 129, 136, 137, 137, 137, 139, 136, 139, 136]
fn = [77, 56, 66, 64, 63, 63, 63, 62, 61, 57, 289, 289, 288, 288, 288, 288, 286, 292, 291, 293]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(eps, fp, 'o-', color='#E8710A', label='Falsos positius')
ax.plot(eps, fn, 'o-', color='#1B2430', label='Falsos negatius')
ax.axvline(25, color='#6B7280', linestyle=':')
ax.annotate('eps = 25 km\n57 FP', xy=(25, 57), xytext=(31, 190), fontsize=11, arrowprops=dict(arrowstyle='->', color='#6B7280'))
ax.set(xlabel='eps (km)', ylabel='Nombre d\'esdeveniments', yscale='log')
ax.legend(loc='upper left', frameon=False)
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'errors_eps.png', dpi=200); plt.close(fig)

# 8. Mapa simple (portada y diapositiva de dades): terratremols en gris y explosions nuclears en vermell
fig, ax = plt.subplots(figsize=(10, 5.4))
ax.scatter(df[~expl].longitude, df[~expl].latitude, s=1.2, c='#C5CAD1')
ax.scatter(df[expl].longitude, df[expl].latitude, s=14, c='#D64545', label=f'Explosions nuclears ({expl.sum()})')
ax.scatter([], [], s=30, c='#C5CAD1', label=f'Altres esdeveniments ({(~expl).sum():,})'.replace(',', ' '))
ax.set(xlabel='Longitud (°)', ylabel='Latitud (°)', xlim=(-180, 180), ylim=(-90, 90))
ax.legend(loc='lower left', fontsize=13, frameon=True)
ax.tick_params(labelsize=12)
ax.xaxis.label.set_size(13); ax.yaxis.label.set_size(13)
ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(OUT / 'mapa_simple.png', dpi=200); plt.close(fig)
