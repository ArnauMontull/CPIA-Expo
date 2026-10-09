from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# 1. Leer el CSV (separado por comas, decimales con punto) desde datos/,
#    sin depender de la carpeta desde la que se ejecute el script
DATOS = Path(__file__).resolve().parent.parent / 'datos'
df = pd.read_csv(DATOS / 'star_dataset.csv')

# 2. Filtrar valores no positivos para poder aplicar escala logarítmica
df_clean = df[(df['Temperature (K)'] > 0) & (df['Luminosity (L/Lo)'] > 0)].copy()

# 3. Configurar el diagrama HR
plt.figure(figsize=(9, 6))

# Usar scatter en lugar de plot con línea continua
plt.scatter(
    df_clean['Temperature (K)'], 
    df_clean['Luminosity (L/Lo)'], 
    color='tab:blue', 
    alpha=0.7, 
    edgecolors='k',
    label='Estrellas'
)

plt.xscale('log')
plt.yscale('log')

# Convención del diagrama HR: temperaturas altas a la izquierda
plt.gca().invert_xaxis()

plt.title('Diagrama de Hertzsprung-Russell (HR)')
plt.xlabel('Temperatura efectiva (K)')
plt.ylabel(r'Luminosidad ($L/L_\odot$)')
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.legend()

plt.tight_layout()
plt.show()