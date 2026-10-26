from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN

# Catalogo: 'grande' (1951-2025, 614 explosiones) o 'pequeno' (sismos_usgs.csv, 554 explosiones)
CATALOGO = 'grande'

CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA.parent.parent / 'datos'
archivos = {'grande': DATOS / 'sismos_usgs_M45_1951_2025.csv',
            'pequeno': DATOS / 'sismos_usgs.csv'}

# Parametros optimos de nuke_optimizar.py para cada catalogo
optimos = {'grande': dict(eps_km=25, vmin=1, dmin=0, dmax=0.1),
           'pequeno': dict(eps_km=10, vmin=1, dmin=-4, dmax=0.1)}

# --- Datos ---
df = pd.read_csv(archivos[CATALOGO])
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])
df = df[df['mag'] >= 4.5].reset_index(drop=True)


# --- Funcion: marca los sismos sospechosos de ser explosiones ---
def nukeDBSCAN(df, eps_km, vmin, dmin, dmax):
    coordenadas = np.radians(df[['latitude', 'longitude']])
    dbscan = DBSCAN(eps=eps_km / 6371, min_samples=vmin, metric='haversine')
    cluster = pd.Series(dbscan.fit_predict(coordenadas), index=df.index)

    # Sospechoso: cluster (no ruido, -1) con profundidad mediana entre dmin y dmax
    mediana = df['depth'].groupby(cluster[cluster != -1]).median()
    sospechosos = mediana[(mediana >= dmin) & (mediana < dmax)].index
    return cluster.isin(sospechosos)


# --- Falsos positivos y falsos negativos ---
def errores(df, detectado):
    es_explosion = df['tipo'] == 'nuclear explosion'
    falsos_positivos = (detectado & ~es_explosion).sum()   # terremoto/volcán/nuke_no_etiquetada marcado como explosion
    falsos_negativos = (~detectado & es_explosion).sum()   # explosion no detectada
    return falsos_positivos, falsos_negativos


# --- Barrido de eps con un 10% de los sismos al azar ---
p = optimos[CATALOGO]
eps_vec = np.linspace(1, 201, 50)
fp_vec, fn_vec = [], []

for i, eps in enumerate(eps_vec):
    muestra = df.sample(frac=0.1, random_state=i)
    detectado = nukeDBSCAN(muestra, eps, p['vmin'], p['dmin'], p['dmax'])
    fp, fn = errores(muestra, detectado)
    fp_vec.append(fp)
    fn_vec.append(fn)
    print(f'eps={eps:.1f} km: FP={fp}, FN={fn}')

plt.plot(eps_vec, fp_vec, 'o-', color='orange', label='Falsos positivos')
plt.plot(eps_vec, fn_vec, 'o-', color='gray', label='Falsos negativos')
plt.title('Errores de DBSCAN con un 10% de los datos')
plt.xlabel('Radio eps (km)')
plt.ylabel('Numero de sismos')
plt.legend()
plt.grid(True)
plt.show()

# --- Run con los parametros optimos ---
detectado = nukeDBSCAN(df, **p)
fp, fn = errores(df, detectado)
print(f'\nOptimos {p}: FP={fp}, FN={fn}')

# --- Globo (globo.html) ---
es_explosion = df['tipo'] == 'nuclear explosion'
vistas = {
    'Todos los eventos': [(df[~es_explosion].sample(4000, random_state=0), 'Terremotos (muestra)', 'lightgray'),
                          (df[es_explosion], 'Explosiones nucleares', 'red')],
    'Sospechosos': [(df[detectado], 'Sospechosos', 'purple')],
    'Reales': [(df[es_explosion], 'Explosiones nucleares', 'red')],
    'Aciertos y errores': [(df[detectado & es_explosion], 'Acierto', 'green'),
                           (df[detectado & ~es_explosion], 'Falso positivo', 'orange'),
                           (df[~detectado & es_explosion], 'Falso negativo', 'gray')],
}

fig = go.Figure()
for vista, capas in vistas.items():
    for sismos, nombre, color in capas:
        fig.add_trace(go.Scattergeo(lat=sismos['latitude'], lon=sismos['longitude'], mode='markers',
                                    marker=dict(color=color, size=5), name=f'{nombre} ({len(sismos)})',
                                    hoverinfo='skip', meta=vista, visible=(vista == 'Todos los eventos')))

botones = [dict(label=vista, method='update', args=[{'visible': [capa.meta == vista for capa in fig.data]}])
           for vista in vistas]
fig.update_layout(updatemenus=[dict(buttons=botones, x=0.01, y=0.99)],
                  legend=dict(x=0.01, y=0.1), margin=dict(l=0, r=0, t=0, b=0))
fig.update_geos(projection_type='natural earth', showland=True, landcolor='whitesmoke', showcountries=True)

# Plotly incluido en el HTML (include_plotlyjs=True): funciona sin internet
fig.write_html(CARPETA / 'globo.html', include_plotlyjs=True)
fig.show()
