"""generar_figuras_diapositivas.py

Genera figures gràfiques d'alta qualitat en català per a les diapositives d'Uriel:
1. docs/figuras/esquema_bandas_materiales.png (Estructura de bandes i fórmules de rho i alpha)
2. docs/figuras/comparativa_kmeans_dbscan.png (Comparativa visual entre K-Means i DBSCAN)
3. docs/figuras/distribucion_escala_rho.png (Distribució lineal vs logarítmica)
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

# ------------------------------------------------------------------------------
# FIGURA 1: Esquema de Bandes Quàntiques i Fórmules
# ------------------------------------------------------------------------------
def crear_figura_bandas():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2), dpi=300)
    fig.patch.set_facecolor("#ffffff")

    materiales = [
        {
            "tipo": "Conductors (Metalls)",
            "color": "#d97706",
            "bc_y": 0.7,
            "bc_h": 0.6,
            "gap": 0.0,
            "anotacion_gap": "Solapades ($E_g = 0$)",
            "alpha": r"$\mathbf{\alpha > 0}$ (+0.004 K$^{-1}$)",
            "rho": r"$\rho \sim 10^{-8}\ \Omega\cdot\mathrm{m}$",
            "mecanismo": "Mar d'electrons lliures\nXocs amb fonons en escalfar",
        },
        {
            "tipo": "Semiconductors",
            "color": "#059669",
            "bc_y": 1.4,
            "bc_h": 0.6,
            "gap": 0.7,
            "anotacion_gap": r"$E_g \sim 1.1\ \mathrm{eV}$",
            "alpha": r"$\mathbf{\alpha < 0}$ (-0.05 K$^{-1}$)",
            "rho": r"$\rho \sim 10^{-2}\text{--}10^3\ \Omega\cdot\mathrm{m}$",
            "mecanismo": "Activació tèrmica (Boltzmann)\n$n \propto e^{-E_g / 2k_B T}$",
        },
        {
            "tipo": "Aïllants",
            "color": "#2563eb",
            "bc_y": 2.05,
            "bc_h": 0.6,
            "gap": 1.35,
            "anotacion_gap": r"$E_g > 5\ \mathrm{eV}$",
            "alpha": r"$\mathbf{\alpha \approx 0}\ \mathrm{K}^{-1}$",
            "rho": r"$\rho > 10^{12}\ \Omega\cdot\mathrm{m}$",
            "mecanismo": r"$k_B T \ll E_g$ a 300 K" + "\nSense portadors en conducció",
        }
    ]

    for ax, mat in zip(axes, materiales):
        ax.set_facecolor("#f8fafc")
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.75, 3.4)
        ax.axis("off")

        # Titol superior
        ax.text(0.5, 3.1, mat["tipo"], ha="center", va="center", fontsize=13, fontweight="bold", color=mat["color"])

        # 1. Banda de Valencia (y = 0.18 a 0.70)
        bv = plt.Rectangle((0.15, 0.18), 0.7, 0.52, color="#94a3b8", alpha=0.85, ec="#334155", lw=1.5)
        ax.add_patch(bv)
        ax.text(0.5, 0.44, "Banda de\nValència", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#0f172a")

        # 2. Banda de Conduccio
        bc = plt.Rectangle((0.15, mat["bc_y"]), 0.7, mat["bc_h"], color=mat["color"], alpha=0.35, ec=mat["color"], lw=1.5)
        ax.add_patch(bc)
        ax.text(0.5, mat["bc_y"] + mat["bc_h"]/2, "Banda de\nConducció", ha="center", va="center", fontsize=9.5, fontweight="bold", color=mat["color"])

        # 3. Gap i fletxes indicadores
        if mat["gap"] > 0:
            ax.annotate("", xy=(0.88, mat["bc_y"]), xytext=(0.88, 0.70),
                        arrowprops=dict(arrowstyle="<->", color="#ef4444", lw=1.8))
            ax.text(0.92, (0.70 + mat["bc_y"])/2, mat["anotacion_gap"], ha="left", va="center", fontsize=9.5, fontweight="bold", color="#ef4444")
        else:
            ax.text(0.5, 1.45, "SOLAPADES ($E_g = 0$)", ha="center", va="center", fontsize=9, fontweight="bold", color="#d97706")

        # 4. Textos fisics inferiors
        info_text = (
            f"{mat['alpha']}\n"
            f"{mat['rho']}\n"
            f"{mat['mecanismo']}"
        )
        ax.text(0.5, -0.08, info_text, ha="center", va="top", fontsize=8.5, color="#1e293b", linespacing=1.35)

    plt.tight_layout()
    out_path = OUTPUT_DIR / "esquema_bandas_materiales.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura 1 (català) guardada a: {out_path}")


# ------------------------------------------------------------------------------
# FIGURA 2: Comparativa Visual K-Means vs DBSCAN
# ------------------------------------------------------------------------------
def crear_figura_comparativa():
    np.random.seed(42)
    c_denso = np.random.normal(loc=[-2.5, 1.0], scale=[0.3, 0.25], size=(35, 2))
    c_inter = np.random.normal(loc=[0.0, -1.8], scale=[0.5, 0.4], size=(12, 2))
    c_disp = np.random.normal(loc=[3.0, 0.0], scale=[1.1, 0.4], size=(15, 2))
    ruido = np.array([[1.5, 2.2], [-1.0, 2.0]])

    X = np.vstack([c_denso, c_inter, c_disp, ruido])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=250)
    fig.patch.set_facecolor("#ffffff")

    # K-Means
    ax1.set_facecolor("#f8fafc")
    ax1.set_title("K-Means (Falla amb densitats dispars)", fontsize=11, fontweight="bold", color="#dc2626")
    
    km_labels = []
    for p in X:
        if p[0] < -1.2:
            km_labels.append("#d97706")
        elif p[1] < -0.8 or p[0] < 1.0:
            km_labels.append("#2563eb")
        else:
            km_labels.append("#059669")
    
    ax1.scatter(X[:, 0], X[:, 1], c=km_labels, s=45, alpha=0.85, ec="black", lw=0.5)
    centroides = np.array([[-2.5, 1.0], [0.2, -0.9], [2.8, 0.3]])
    ax1.scatter(centroides[:, 0], centroides[:, 1], c="red", marker="X", s=130, ec="black", label=r"Centroides $\mu_k$")
    ax1.text(0.05, 0.06, "• Assumeix variàncies esfèriques iguals\n• Fractura el grup dispers d'aïllants\n• No detecta soroll (atípics)",
             transform=ax1.transAxes, fontsize=8.5, color="#7f1d1d",
             bbox=dict(boxstyle="round,pad=0.4", fc="#fef2f2", ec="#fca5a5"))
    ax1.legend(loc="upper left", fontsize=8.5)
    ax1.axis("off")

    # DBSCAN
    ax2.set_facecolor("#f8fafc")
    ax2.set_title("DBSCAN (Respecta densitats i aïlla soroll)", fontsize=11, fontweight="bold", color="#059669")
    
    db_colors = []
    for i, p in enumerate(X):
        if i >= len(X) - 2:
            db_colors.append("#ef4444")
        elif i < 35:
            db_colors.append("#d97706")
        elif i < 35 + 12:
            db_colors.append("#059669")
        else:
            db_colors.append("#2563eb")

    ax2.scatter(X[:-2, 0], X[:-2, 1], c=db_colors[:-2], s=45, alpha=0.85, ec="black", lw=0.5)
    ax2.scatter(X[-2:, 0], X[-2:, 1], c="#ef4444", marker="x", s=90, lw=2.2, label="Soroll (-1)")
    
    circle1 = plt.Circle((-2.5, 1.0), 0.65, color="#d97706", fill=False, lw=1.5, ls="--", label=r"Radi $\varepsilon$")
    ax2.add_patch(circle1)
    ax2.text(0.05, 0.06, "• Connecta punts per densitat local\n• Permet grups densos i grups laxos\n• Filtra anomalies automàticament",
             transform=ax2.transAxes, fontsize=8.5, color="#064e3b",
             bbox=dict(boxstyle="round,pad=0.4", fc="#ecfdf5", ec="#a7f3d0"))
    ax2.legend(loc="upper left", fontsize=8.5)
    ax2.axis("off")

    plt.tight_layout()
    out_path = OUTPUT_DIR / "comparativa_kmeans_dbscan.png"
    plt.savefig(out_path, dpi=250, bbox_inches="tight")
    plt.close()
    print(f"Figura 2 (català) guardada a: {out_path}")


# ------------------------------------------------------------------------------
# FIGURA 3: Distribució del Dataset (Histograma de 30 ordres de magnitud)
# ------------------------------------------------------------------------------
def crear_figura_dataset():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8), dpi=250)
    fig.patch.set_facecolor("#ffffff")

    np.random.seed(42)
    rho_cond = 10**np.random.normal(-7.8, 0.4, 35)
    rho_semi = 10**np.random.normal(1.5, 1.8, 12)
    rho_aisl = 10**np.random.normal(15.0, 2.5, 10)
    rho_all = np.concatenate([rho_cond, rho_semi, rho_aisl])

    # Escala lineal
    ax1.set_facecolor("#f8fafc")
    ax1.hist(rho_all, bins=15, color="#dc2626", alpha=0.75, ec="black")
    ax1.set_title(r"Escala Lineal ($\Omega\cdot\mathrm{m}$): Col·lapse a l'origen", fontsize=10.5, fontweight="bold", color="#dc2626")
    ax1.set_xlabel(r"Resistivitat $\rho$ [$\Omega\cdot\mathrm{m}$]", fontsize=9.5)
    ax1.set_ylabel("Nre. de materials", fontsize=9.5)
    ax1.text(0.4, 0.7, "99% de materials\ncol·lapsen a [0, 0.01]", transform=ax1.transAxes,
             fontsize=9, color="#7f1d1d", bbox=dict(boxstyle="round,pad=0.3", fc="#fef2f2", ec="#fca5a5"))
    ax1.grid(True, ls=":", alpha=0.5)

    # Escala logaritmica
    ax2.set_facecolor("#f8fafc")
    log_rho = np.log10(rho_all)
    n, bins, patches = ax2.hist(log_rho, bins=18, color="#059669", alpha=0.75, ec="black")
    ax2.set_title(r"Escala Logarítmica $\log_{10}(\rho)$: Separació de Fases", fontsize=10.5, fontweight="bold", color="#059669")
    ax2.set_xlabel(r"$\log_{10}(\rho_{300\mathrm{K}})$ [$\Omega\cdot\mathrm{m}$]", fontsize=9.5)
    ax2.set_ylabel("Nre. de materials", fontsize=9.5)
    ax2.text(0.08, 0.75, "Metalls\n(~ -8)", transform=ax2.transAxes, fontsize=8.5, fontweight="bold", color="#d97706")
    ax2.text(0.42, 0.75, "Semiconductors\n(~ 1)", transform=ax2.transAxes, fontsize=8.5, fontweight="bold", color="#059669")
    ax2.text(0.72, 0.75, "Aïllants\n(> 12)", transform=ax2.transAxes, fontsize=8.5, fontweight="bold", color="#2563eb")
    ax2.grid(True, ls=":", alpha=0.5)

    plt.tight_layout()
    out_path = OUTPUT_DIR / "distribucion_escala_rho.png"
    plt.savefig(out_path, dpi=250, bbox_inches="tight")
    plt.close()
    print(f"Figura 3 (català) guardada a: {out_path}")

if __name__ == "__main__":
    crear_figura_bandas()
    crear_figura_comparativa()
    crear_figura_dataset()
