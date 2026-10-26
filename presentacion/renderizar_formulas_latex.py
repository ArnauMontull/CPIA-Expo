"""renderizar_formulas_latex.py

Genera imagenes PNG transparentes en alta resolucion (300 DPI)
con tipografia LaTeX Computer Modern autentica para incrustar en las diapositivas.
"""

from pathlib import Path
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "figuras" / "latex"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['font.family'] = 'serif'

formulas = {
    # Slide 2: Variacion termica y coeficiente termico
    "formula_transporte.png": (
        r"$\rho(T) = \rho_0 [1 + \alpha(T - T_0)] \qquad\quad \alpha = \frac{1}{\rho_0} \left(\frac{d\rho}{dT}\right)_{300\mathrm{K}}$",
        18,
        (8.5, 1.2)
    ),
    # Slide 3: Coordenadas del espacio
    "formula_coordenadas.png": (
        r"$x_1 = \log_{10}(\rho_{300\mathrm{K}}) \qquad\quad x_2 = \alpha = \frac{1}{\rho_0} \frac{d\rho}{dT}$",
        17,
        (6.5, 1.0)
    ),
    # Slide 5 - Caja 1: Z-Score manual
    "formula_zscore.png": (
        r"$Z = \frac{X - \mu}{\sigma} \qquad \mu = \frac{1}{N}\sum_{i=1}^N X_i \qquad \sigma = \sqrt{\frac{1}{N}\sum_{i=1}^N (X_i - \mu)^2}$",
        17,
        (7.5, 1.2)
    ),
    # Slide 5 - Caja 2: Criterio de Vecindad y Nucleo
    "formula_nucleo.png": (
        r"$N_\varepsilon(p) = \{q \in D \mid d(p, q) \leq \varepsilon\} \qquad |N_\varepsilon(p)| \geq \mathrm{min\_samples}$",
        17,
        (7.5, 1.2)
    ),
    # Slide 5 - Caja 3: Parametros
    "formula_parametros.png": (
        r"$\varepsilon = 0.65 \quad (\mathrm{codo}\ k\mathrm{-NN}) \qquad\quad \mathrm{min\_samples} = 3 \quad (k \geq d + 1)$",
        17,
        (7.5, 1.2)
    ),
    # Slide 7: Silhouette Score
    "formula_silhouette.png": (
        r"$s(i) = \frac{b(i) - a(i)}{\max\{a(i), b(i)\}} \qquad\Longrightarrow\qquad S = 0.7858$",
        17,
        (7.5, 1.1)
    )
}

for fname, (latex_code, fontsize, figsize) in formulas.items():
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    fig.patch.set_facecolor("#ffffff")
    fig.patch.set_alpha(0.0) # Transparente
    ax.axis("off")
    ax.text(0.5, 0.5, latex_code, fontsize=fontsize, ha="center", va="center", color="#000000")
    
    out_file = OUTPUT_DIR / fname
    plt.savefig(out_file, bbox_inches="tight", transparent=True, pad_inches=0.08)
    plt.close()
    print(f"Generada formula LaTeX: {out_file}")

print("Todas las formulas LaTeX han sido renderizadas con exito.")
