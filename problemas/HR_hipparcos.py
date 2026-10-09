from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Leer el catálogo Hipparcos (paralaje mejor del 10 %): B-V y magnitud absoluta V
DATOS = Path(__file__).resolve().parent.parent / 'datos'
df = pd.read_csv(DATOS / 'hr_hipparcos.csv')

# 2. Color B-V -> temperatura efectiva (Ballesteros 2012, EPL 97, 34008)
bv = df['B-V']
df['T'] = 4600 * (1 / (0.92 * bv + 1.7) + 1 / (0.92 * bv + 0.62))

# 3. Magnitud absoluta V -> luminosidad bolométrica
#    M_bol = M_V + BC(T); BC de Flower (1996) con los coeficientes corregidos de Torres (2010, AJ 140, 1158)
def correccion_bolometrica(T):
    logT = np.log10(T)
    frio = [-0.190537291496456e5, 0.155144866764412e5, -0.421278819301717e4, 0.381476328422343e3]
    medio = [-0.370510203809015e5, 0.385672629965804e5, -0.150651486316025e5,
             0.261724637119416e4, -0.170623810323864e3]
    caliente = [-0.118115450538963e6, 0.137145973583929e6, -0.636233812100225e5,
                0.147412923562646e5, -0.170587278406872e4, 0.788731721804990e2]
    poly = lambda c: sum(ci * logT**i for i, ci in enumerate(c))
    return np.where(logT < 3.70, poly(frio), np.where(logT < 3.90, poly(medio), poly(caliente)))

M_BOL_SOL = 4.74
df['L'] = 10 ** (-0.4 * (df['abs_v_mag'] + correccion_bolometrica(df['T']) - M_BOL_SOL))

# 4. Diagrama HR en L, T
plt.figure(figsize=(9, 6))
plt.scatter(df['T'], df['L'], s=2, alpha=0.4, color='tab:blue', label=f'Estrellas Hipparcos ({len(df)})')

plt.xscale('log')
plt.yscale('log')
plt.gca().invert_xaxis()  # convención HR: temperaturas altas a la izquierda

plt.title('Diagrama de Hertzsprung-Russell (Hipparcos)')
plt.xlabel('Temperatura efectiva (K)')
plt.ylabel(r'Luminosidad ($L/L_\odot$)')
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.legend(markerscale=5)

plt.tight_layout()
plt.show()
