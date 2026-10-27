"""
Descarga el catalogo del USGS (todos los eventos M>=4.5 de 1951 a 2025, de cualquier tipo)
y lo guarda en datos/sismos_usgs_M45_1951_2025.csv.
"""
from pathlib import Path
import pandas as pd

DATOS = Path(__file__).resolve().parent.parent.parent / 'datos'
DESTINO = DATOS / 'sismos_usgs_M45_1951_2025.csv'
URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&orderby=time-asc&minmagnitude=4.5'


def descargar_year(year):
    # La API limita cada consulta a 20 000 eventos, asi que se pide un año cada vez
    consulta = f'{URL}&starttime={year}-01-01&endtime={year + 1}-01-01'

    for intento in range(4):
        try:
            return pd.read_csv(consulta)
        except Exception:
            print(f'  {year}: reintento')

    raise RuntimeError(f'No se pudo descargar {year}')


if __name__ == '__main__':
    if DESTINO.exists():
        print(f'{DESTINO.name}: ya esta')
    else:
        DATOS.mkdir(exist_ok=True)

        years = []
        for year in range(1951, 2026):
            eventos = descargar_year(year)
            years.append(eventos)
            print(f'{year}: {len(eventos)} eventos')

        df = pd.concat(years, ignore_index=True)
        df = df.rename(columns={'type': 'tipo'})
        df.to_csv(DESTINO, index=False)

        explosiones = (df['tipo'] == 'nuclear explosion').sum()
        print(f'{DESTINO.name}: {len(df)} eventos, {explosiones} explosiones')
