import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN

# ---------------------------------------------------------------
# PASO 1: Cargar los datos
# ---------------------------------------------------------------
# Leemos el catalogo de sismos y nos quedamos solo con los grandes (magnitud >= 4.5)
df = pd.read_csv('datos/sismos_usgs.csv')
df = df.dropna(subset=['latitude', 'longitude', 'depth', 'mag'])
df = df[df['mag'] >= 4.5]
df = df.reset_index(drop=True)

# ---------------------------------------------------------------
# PASO 2: Agrupar sismos cercanos con DBSCAN
# ---------------------------------------------------------------
# DBSCAN junta sismos que estan a menos de 50 km unos de otros.
# Un grupo necesita al menos 3 sismos. Los que quedan solos reciben el grupo -1.
radio_km = 50
radio_tierra_km = 6371
minimo_sismos = 3

# Con la distancia 'haversine' (distancia sobre la esfera) hay que dar
# las coordenadas en radianes y el radio como fraccion del radio de la Tierra
coordenadas = np.radians(df[['latitude', 'longitude']])

dbscan = DBSCAN(eps=radio_km / radio_tierra_km,
                min_samples=minimo_sismos,
                metric='haversine')
df['cluster'] = dbscan.fit_predict(coordenadas)

# ---------------------------------------------------------------
# PASO 3: Decidir que grupos son sospechosos
# ---------------------------------------------------------------
# Una explosion nuclear ocurre casi en la superficie.
# Por eso un grupo es sospechoso si la profundidad mediana de sus sismos es < 5 km.
profundidad_maxima_km = 5

sin_ruido = df[df['cluster'] != -1]
profundidad_mediana = sin_ruido.groupby('cluster')['depth'].median()
grupos_sospechosos = profundidad_mediana[profundidad_mediana < profundidad_maxima_km].index

# detectado = True si el sismo pertenece a un grupo sospechoso
df['detectado'] = df['cluster'].isin(grupos_sospechosos)

# ---------------------------------------------------------------
# PASO 4: Comprobar si acertamos
# ---------------------------------------------------------------
# La columna 'tipo' dice la verdad: sabemos cuales son explosiones de verdad.
es_explosion = df['tipo'] == 'nuclear explosion'

acierto = df['detectado'] & es_explosion              # explosion y la detectamos
falso_positivo = df['detectado'] & ~es_explosion      # terremoto que marcamos como explosion
falso_negativo = ~df['detectado'] & es_explosion      # explosion que no detectamos

n_aciertos = acierto.sum()
n_falsos_positivos = falso_positivo.sum()
n_falsos_negativos = falso_negativo.sum()

# Precision: de lo que marcamos, que parte era explosion de verdad
precision = n_aciertos / (n_aciertos + n_falsos_positivos)
# Recall: de todas las explosiones, que parte detectamos
recall = n_aciertos / (n_aciertos + n_falsos_negativos)

print('Aciertos:', n_aciertos)
print('Falsos positivos:', n_falsos_positivos)
print('Falsos negativos:', n_falsos_negativos)
print('Precision:', precision)
print('Recall:', recall)

# ---------------------------------------------------------------
# PASO 5: Dibujar el mapa
# ---------------------------------------------------------------
# El mapa tiene 4 vistas que se cambian con un menu desplegable.
# Hay ~100.000 terremotos normales, asi que dibujamos solo 4000 al azar
# para que el archivo HTML pese poco.
terremotos_normales = df[~es_explosion].sample(4000, random_state=0)

fig = go.Figure()


def anadir_capa(sismos, nombre, color, vista):
    """Anade un grupo de puntos al mapa. 'vista' dice en que vista se ve."""
    fig.add_trace(go.Scattergeo(
        lat=sismos['latitude'],
        lon=sismos['longitude'],
        mode='markers',
        marker=dict(color=color, size=5),
        name=f'{nombre} ({len(sismos)})',
        hoverinfo='skip',
        meta=vista,
        visible=(vista == 'Todos los eventos'),   # al abrir se ve la primera vista
    ))


# Vista 1: todos los eventos
anadir_capa(terremotos_normales, 'Terremotos (muestra)', 'lightgray', 'Todos los eventos')
anadir_capa(df[es_explosion], 'Explosiones nucleares', 'red', 'Todos los eventos')

# Vista 2: los sospechosos que ha encontrado DBSCAN
anadir_capa(df[df['detectado']], 'Sospechosos', 'purple', 'Sospechosos')

# Vista 3: las explosiones reales
anadir_capa(df[es_explosion], 'Explosiones nucleares', 'red', 'Reales')

# Vista 4: aciertos y errores
anadir_capa(df[acierto], 'Acierto', 'green', 'Aciertos y errores')
anadir_capa(df[falso_positivo], 'Falso positivo', 'orange', 'Aciertos y errores')
anadir_capa(df[falso_negativo], 'Falso negativo', 'gray', 'Aciertos y errores')

# Un boton por vista: muestra las capas de esa vista y oculta las demas
nombres_vistas = ['Todos los eventos', 'Sospechosos', 'Reales', 'Aciertos y errores']
botones = []
for vista in nombres_vistas:
    visibles = [capa.meta == vista for capa in fig.data]
    botones.append(dict(label=vista, method='update', args=[{'visible': visibles}]))

fig.update_layout(
    updatemenus=[dict(buttons=botones, x=0.01, y=0.99)],
    legend=dict(x=0.01, y=0.1),
    margin=dict(l=0, r=0, t=0, b=0),
)
fig.update_geos(projection_type='natural earth',
                showland=True, landcolor='whitesmoke', showcountries=True)

# Guardamos el mapa junto a este script y lo abrimos en el navegador
carpeta = os.path.dirname(os.path.abspath(__file__))
fig.write_html(os.path.jo   in(carpeta, 'globo.html'), include_plotlyjs='cdn')
fig.show()
