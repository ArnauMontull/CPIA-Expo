from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN

# --- Catalogo y parametros ---
# 'grande': 1951-2025, 614 explosiones. 'pequeno': sismos_usgs.csv, 554 explosiones.
CATALOGO = 'grande'

CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA.parent.parent / 'datos'
archivos = {'grande': DATOS / 'sismos_usgs_M45_1951_2025.csv',
            'pequeno': DATOS / 'sismos_usgs.csv'}

# Parametros fijos (iguales para los dos catalogos)
#   eps_km: radio de DBSCAN. vmin: sismos minimos por cluster.
#   dmin, dmax: una explosion es casi superficial, asi que un cluster es sospechoso
#   si la mediana de su profundidad esta entre 0 y 2.5 km.
parametros = dict(eps_km=25, vmin=1, dmin=0, dmax=2.5)

# --- Datos ---
df = pd.read_csv(archivos[CATALOGO])
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])
df = df[df['mag'] >= 4.5]
df = df.reset_index(drop=True)


# --- Agrupar los sismos cercanos con DBSCAN ---
def agrupar(df, eps_km, vmin):
    radio_tierra_km = 6371
    coordenadas = np.radians(df[['latitude', 'longitude']])
    eps_rad = eps_km / radio_tierra_km

    dbscan = DBSCAN(eps=eps_rad, min_samples=vmin, metric='haversine')
    cluster = dbscan.fit_predict(coordenadas)
    return pd.Series(cluster, index=df.index)


# --- Marcar los sismos sospechosos de ser explosiones ---
def nukeDBSCAN(df, eps_km, vmin, dmin, dmax):
    cluster = agrupar(df, eps_km, vmin)

    # Profundidad mediana de cada cluster (el ruido, -1, no cuenta)
    sin_ruido = cluster != -1
    mediana = df['depth'].groupby(cluster[sin_ruido]).median()

    # Sospechoso: cluster casi en la superficie, con la mediana entre dmin y dmax
    es_superficial = (mediana >= dmin) & (mediana < dmax)
    clusters_sospechosos = mediana[es_superficial].index

    return cluster.isin(clusters_sospechosos)


# --- Falsos positivos y falsos negativos ---
def errores(df, detectado):
    es_explosion = df['tipo'] == 'nuclear explosion'

    # Falso positivo: detectado, pero no es una explosion
    falsos_positivos = (detectado & ~es_explosion).sum()
    # Falso negativo: es una explosion, pero no se detecta
    falsos_negativos = (~detectado & es_explosion).sum()
    return falsos_positivos, falsos_negativos


if __name__ == '__main__':
    # --- Run con los parametros fijos ---
    detectado = nukeDBSCAN(df, **parametros)
    fp, fn = errores(df, detectado)
    print(f'{parametros}: FP={fp}, FN={fn}')

    # --- Grupos de sismos para el globo ---
    es_explosion = df['tipo'] == 'nuclear explosion'
    terremotos_muestra = df[~es_explosion].sample(4000, random_state=0)
    explosiones = df[es_explosion]
    sospechosos = df[detectado]
    aciertos = df[detectado & es_explosion]
    falsos_positivos = df[detectado & ~es_explosion]
    falsos_negativos = df[~detectado & es_explosion]

    # Cada vista del globo es una lista de (sismos, nombre, color)
    vistas = {
        'Todos los eventos': [(terremotos_muestra, 'Terremotos (muestra)', 'lightgray'),
                              (explosiones, 'Explosiones nucleares', 'red')],
        'Sospechosos': [(sospechosos, 'Sospechosos', 'purple')],
        'Reales': [(explosiones, 'Explosiones nucleares', 'red')],
        'Aciertos y errores': [(aciertos, 'Acierto', 'green'),
                               (falsos_positivos, 'Falso positivo', 'orange'),
                               (falsos_negativos, 'Falso negativo', 'gray')],
    }

    # --- Globo (globo.html) ---
    fig = go.Figure()
    for vista, capas in vistas.items():
        for sismos, nombre, color in capas:
            fig.add_trace(go.Scattergeo(
                lat=sismos['latitude'],
                lon=sismos['longitude'],
                mode='markers',
                marker=dict(color=color, size=5),
                name=f'{nombre} ({len(sismos)})',
                hoverinfo='skip',
                meta=vista,
                visible=(vista == 'Todos los eventos'),
            ))

    # Un boton por vista: muestra las capas de esa vista y oculta las demas
    botones = []
    for vista in vistas:
        visibles = [capa.meta == vista for capa in fig.data]
        botones.append(dict(label=vista, method='update', args=[{'visible': visibles}]))

    fig.update_layout(updatemenus=[dict(buttons=botones, x=0.01, y=0.99)],
                      legend=dict(x=0.01, y=0.1),
                      margin=dict(l=0, r=0, t=0, b=0))
    fig.update_geos(projection_type='natural earth',
                    showland=True, landcolor='whitesmoke', showcountries=True)

    # Plotly va incluido en el HTML: funciona sin internet
    fig.write_html(CARPETA / 'globo.html', include_plotlyjs=True)
    fig.show()
