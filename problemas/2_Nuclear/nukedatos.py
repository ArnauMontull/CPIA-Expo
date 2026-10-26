"""
Descarga los dos catalogos del USGS que usa nukeDBSCAN_arnau.py y los deja en datos/:
  pequeno -> sismos_usgs.csv                  (terremotos M>=4.5 de 2010-2025 + todas las explosiones nucleares)
  grande  -> sismos_usgs_M45_1951_2025.csv    (todos los eventos M>=4.5 de 1951-2025; solo se guardan
                                               terremotos y explosiones)

Uso:  python nukedatos.py            (descarga lo que falte)
      python nukedatos.py --forzar   (vuelve a descargar todo)
"""
import sys
from pathlib import Path
import pandas as pd

DATOS = Path(__file__).resolve().parent.parent.parent / 'datos'
URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&orderby=time-asc'
COLUMNAS = ['time', 'latitude', 'longitude', 'depth', 'mag', 'magType', 'nst', 'gap', 'dmin', 'rms',
            'place', 'type', 'horizontalError', 'depthError', 'magError', 'magNst', 'status']


def descargar_anyo(anyo, filtro=''):
    """Eventos M>=4.5 de un anyo (la API limita cada consulta a 20 000 eventos). Reintenta si falla la red."""
    consulta = f'{URL}&minmagnitude=4.5{filtro}&starttime={anyo}-01-01&endtime={anyo + 1}-01-01'
    for intento in range(4):
        try:
            return pd.read_csv(consulta)
        except Exception as error:
            if intento == 3:
                raise
            print(f'  {anyo}: reintento ({type(error).__name__})')


def guardar(partes, destino):
    df = pd.concat(partes, ignore_index=True)
    df = df[COLUMNAS].rename(columns={'type': 'tipo'})
    df = df[df['tipo'].isin(['earthquake', 'nuclear explosion'])]
    df.to_csv(destino, index=False)
    print(f'{destino.name}: {len(df)} eventos, {(df["tipo"] == "nuclear explosion").sum()} explosiones')


def catalogo_pequeno(destino):
    # Todas las explosiones nucleares (sin limite de magnitud) + terremotos de 2010-2025
    partes = [pd.read_csv(f'{URL}&eventtype=nuclear%20explosion&starttime=1900-01-01')]
    for anyo in range(2010, 2026):
        partes.append(descargar_anyo(anyo, '&eventtype=earthquake'))
        print(f'  {anyo}: {len(partes[-1])} terremotos')
    guardar(partes, destino)


def catalogo_grande(destino):
    # Sin filtrar por tipo en la consulta: asi la API devuelve explosiones que de otro modo omite
    partes = []
    for anyo in range(1951, 2026):
        partes.append(descargar_anyo(anyo))
        print(f'  {anyo}: {len(partes[-1])} eventos')
    guardar(partes, destino)


if __name__ == '__main__':
    forzar = '--forzar' in sys.argv
    DATOS.mkdir(exist_ok=True)

    catalogos = [(catalogo_pequeno, DATOS / 'sismos_usgs.csv'),
                 (catalogo_grande, DATOS / 'sismos_usgs_M45_1951_2025.csv')]
    for funcion, destino in catalogos:
        if destino.exists() and not forzar:
            print(f'{destino.name}: ya esta')
        else:
            print(f'{destino.name}: descargando...')
            funcion(destino)
