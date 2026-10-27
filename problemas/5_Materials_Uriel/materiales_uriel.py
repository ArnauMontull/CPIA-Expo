"""problemas/5_Materials_Uriel/materiales_uriel.py

Classificació no supervisada de materials elèctrics (Conductors, Semiconductors i Aïllants)
mitjançant DBSCAN de scikit-learn (Density-Based Spatial Clustering of Applications with Noise).

Genera:
1. materiales_antes_clustering.png -> Visualització de l'espai físic abans de l'agrupament.
2. clusters_materiales_dbscan.png -> Clústers descoberts per densitat amb DBSCAN.
3. comparativa_abans_despres_dbscan.png -> Panell comparatiu (Abans vs Després).

Paràmetres fixats:
- Epsilon (radi de veïnat): eps = 0.65
- Min samples (mínim de mostres per nucli): min_samples = 3

"""
from pathlib import Path
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

# 1. Carregar el dataset descarregat a datos/

AQUI = Path(__file__).resolve().parent
REPO_ROOT = AQUI.parents[1] if len(AQUI.parents) >= 2 else AQUI

# Trobar el fitxer de dades (sigui al repositori complet o a la carpeta standalone)
candidats_csv = [
    AQUI / "datos" / "materiales_electricos.csv",
    AQUI / "materiales_electricos.csv",
    REPO_ROOT / "datos" / "materiales_electricos.csv",
]
CSV_PATH = next((p for p in candidats_csv if p.exists() and p.is_file()), None)

if CSV_PATH is None:
    raise FileNotFoundError(f"No s'ha trobat l'arxiu de dades a cap d'aquestes rutes: {candidats_csv}")

FIGURAS_DOCS = REPO_ROOT / "docs" / "figuras" if (REPO_ROOT / "docs" / "figuras").exists() else None
FIGURAS_LOCAL = AQUI / "figuras"
FIGURAS_LOCAL.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_PATH)
print(f"Dataset carregat amb èxit ({len(df)} materials).")

# 2. Selecció de característiques i estandardització manual (Z-Score)

# x1: log10(resistivitat a 300 K) -> comprimeix més de 30 ordres de magnitud
# x2: coeficient tèrmic alpha -> signatura quàntica del material, mirem el signe
features = ["log_rho_300K", "alpha_coef"]
X_raw = df[features].values

# Estandardització manual: Z = (X - μ) / σ
# --> Garanteix mitjana = 0 i desviació típica = 1 a cada dimensió (millora la distància euclidiana)
media = np.mean(X_raw, axis=0)
desv = np.std(X_raw, axis=0)
X_scaled = (X_raw - media) / desv

# Configuració tipogràfica per a Matplotlib
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

materiales_destacados = ["copper", "silver", "silicon", "germanium", "gaas", "glass", "ptfe", "quartz", "graphite"]

# 3. IMATGE 1: Pla (log10 rho, alpha) abans de l'agrupament (Dades en Brut)

fig_abans, ax_abans = plt.subplots(figsize=(10, 6.5))

ax_abans.scatter(
    df["log_rho_300K"],
    df["alpha_coef"],
    c="#334155",
    s=75,
    alpha=0.85,
    edgecolors="black",
    linewidth=0.8,
    label=f"Materials experimentals sense etiquetar (n={len(df)})"
)

# Línia de referència física per a alpha = 0
ax_abans.axhline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label=r"Frontera física $\alpha = 0$")

# Etiquetes de materials representatius
for _, r in df.iterrows():
    mat = r["material"]
    if any(k in mat.lower() for k in materiales_destacados):
        ax_abans.annotate(
            mat.split("(")[0].strip(),
            (r["log_rho_300K"], r["alpha_coef"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=8.5,
            fontweight="bold",
            color="#1e293b",
            alpha=0.9
        )

ax_abans.set_title(r"Pla $(\log_{10}\rho_{300\mathrm{K}}, \alpha)$ abans del Clustering (Dades en Brut)", fontsize=13, fontweight="bold")
ax_abans.set_xlabel(r"$\log_{10}(\rho_{300\mathrm{K}})$ [$\rho$ en $\Omega\cdot\mathrm{m}$]", fontsize=11)
ax_abans.set_ylabel(r"Coeficient tèrmic $\alpha$ [$\mathrm{K}^{-1}$]", fontsize=11)
ax_abans.grid(True, linestyle=":", alpha=0.6)
ax_abans.legend(loc="lower right", framealpha=0.9)
plt.tight_layout()

RUTA_ABANS = AQUI / "materiales_antes_clustering.png"
fig_abans.savefig(RUTA_ABANS, dpi=300)
plt.close(fig_abans)
print(f"Gràfic d'abans de l'agrupament guardat a: {RUTA_ABANS}")

if FIGURAS_LOCAL.exists():
    shutil.copy(RUTA_ABANS, FIGURAS_LOCAL / "materiales_antes_clustering.png")
if FIGURAS_DOCS is not None and FIGURAS_DOCS.exists():
    shutil.copy(RUTA_ABANS, FIGURAS_DOCS / "materiales_antes_clustering.png")


# 4. Aplicació de DBSCAN (funció de la llibreria scikit-learn)

EPS = 0.65 
MIN_SAMPLES = 3

dbscan = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES)
df["cluster"] = dbscan.fit_predict(X_scaled)

# ==============================================================================
# 5. Resultats de DBSCAN
# ==============================================================================
clusters_encontrados = sorted(set(df["cluster"]) - {-1})
n_clusters = len(clusters_encontrados)
n_ruido = int(np.sum(df["cluster"] == -1))

print("\n" + "=" * 65)
print(f"RESULTATS DE DBSCAN (eps={EPS}, min_samples={MIN_SAMPLES})")
print("=" * 65)
print(f"Clústers descoberts per densitat    : {n_clusters}")
print(f"Punts classificats com a soroll (-1): {n_ruido} de {len(df)}")

print("\nMatriu de contingència (Classe real vs. Clúster DBSCAN):")
print(pd.crosstab(df["clase_real"], df["cluster"], margins=True))

if n_ruido > 0:
    ruido_df = df[df["cluster"] == -1][["material", "log_rho_300K", "alpha_coef", "clase_real"]]
    print("\nMaterials classificats com a soroll/anomalia (cluster = -1):")
    for _, r in ruido_df.iterrows():
        print(f" - {r['material']:<30} | log10(ρ)={r['log_rho_300K']:>6.2f} | α={r['alpha_coef']:>8.5f} | Tipus: {r['clase_real']}")

# 6. IMATGE 2: Pla DESPRÉS de l'agrupament amb DBSCAN

paleta_colores = {
    0: ("#d97706", "Clúster 0 (Conductors)"),
    1: ("#2563eb", "Clúster 1 (Aïllants)"),
    2: ("#059669", "Clúster 2 (Semiconductors)"),
}

fig_despres, ax_despres = plt.subplots(figsize=(10, 6.5))

for cl in clusters_encontrados:
    sub = df[df["cluster"] == cl]
    color, nombre_cl = paleta_colores.get(cl, ("#6b7280", f"Clúster {cl}"))
    ax_despres.scatter(
        sub["log_rho_300K"],
        sub["alpha_coef"],
        c=color,
        s=75,
        alpha=0.85,
        edgecolors="black",
        linewidth=0.8,
        label=f"{nombre_cl} (n={len(sub)})"
    )

sub_ruido = df[df["cluster"] == -1]
if len(sub_ruido) > 0:
    ax_despres.scatter(
        sub_ruido["log_rho_300K"],
        sub_ruido["alpha_coef"],
        c="#dc2626",
        marker="x",
        s=85,
        linewidth=2,
        label=f"Soroll / Anomalies (n={len(sub_ruido)})",
        zorder=5
    )

ax_despres.axhline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label=r"Frontera física $\alpha = 0$")

for _, r in df.iterrows():
    mat = r["material"]
    if any(k in mat.lower() for k in materiales_destacados):
        ax_despres.annotate(
            mat.split("(")[0].strip(),
            (r["log_rho_300K"], r["alpha_coef"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=8.5,
            fontweight="bold",
            color="#1e293b",
            alpha=0.9
        )

ax_despres.set_title(f"Classificació de Materials amb DBSCAN ($\\varepsilon = {EPS}$, $min\\_samples = {MIN_SAMPLES}$)", fontsize=13, fontweight="bold")
ax_despres.set_xlabel(r"$\log_{10}(\rho_{300\mathrm{K}})$ [$\rho$ en $\Omega\cdot\mathrm{m}$]", fontsize=11)
ax_despres.set_ylabel(r"Coeficient tèrmic $\alpha$ [$\mathrm{K}^{-1}$]", fontsize=11)
ax_despres.grid(True, linestyle=":", alpha=0.6)
ax_despres.legend(loc="lower right", framealpha=0.9)
plt.tight_layout()

RUTA_DESPRES = AQUI / "clusters_materiales_dbscan.png"
fig_despres.savefig(RUTA_DESPRES, dpi=300)
plt.close(fig_despres)
print(f"Gràfic de clústers DBSCAN guardat a: {RUTA_DESPRES}")

if FIGURAS_LOCAL.exists():
    shutil.copy(RUTA_DESPRES, FIGURAS_LOCAL / "clusters_materiales_dbscan.png")
if FIGURAS_DOCS is not None and FIGURAS_DOCS.exists():
    shutil.copy(RUTA_DESPRES, FIGURAS_DOCS / "clusters_materiales_dbscan.png")

# 7. IMATGE 3: Comparativa ABANS i DESPRÉS (Panell 1x2)

fig_comp, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.2), sharey=True)

# Panell Esquerre: Abans
ax1.scatter(
    df["log_rho_300K"],
    df["alpha_coef"],
    c="#334155",
    s=70,
    alpha=0.85,
    edgecolors="black",
    linewidth=0.8,
    label=f"Materials en brut (n={len(df)})"
)
ax1.axhline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label=r"Frontera física $\alpha = 0$")
for _, r in df.iterrows():
    mat = r["material"]
    if any(k in mat.lower() for k in materiales_destacados):
        ax1.annotate(
            mat.split("(")[0].strip(),
            (r["log_rho_300K"], r["alpha_coef"]),
            xytext=(6, 4), textcoords="offset points",
            fontsize=8, fontweight="bold", color="#1e293b", alpha=0.9
        )
ax1.set_title(r"1. Abans: Dades Experimentals en Brut (Sense Etiquetes)", fontsize=12, fontweight="bold")
ax1.set_xlabel(r"$\log_{10}(\rho_{300\mathrm{K}})$ [$\rho$ en $\Omega\cdot\mathrm{m}$]", fontsize=10.5)
ax1.set_ylabel(r"Coeficient tèrmic $\alpha$ [$\mathrm{K}^{-1}$]", fontsize=10.5)
ax1.grid(True, linestyle=":", alpha=0.6)
ax1.legend(loc="lower right", framealpha=0.9, fontsize=9)

# Panell Dret: Després
for cl in clusters_encontrados:
    sub = df[df["cluster"] == cl]
    color, nombre_cl = paleta_colores.get(cl, ("#6b7280", f"Clúster {cl}"))
    ax2.scatter(
        sub["log_rho_300K"],
        sub["alpha_coef"],
        c=color,
        s=70,
        alpha=0.85,
        edgecolors="black",
        linewidth=0.8,
        label=f"{nombre_cl} (n={len(sub)})"
    )
if len(sub_ruido) > 0:
    ax2.scatter(
        sub_ruido["log_rho_300K"],
        sub_ruido["alpha_coef"],
        c="#dc2626",
        marker="x",
        s=85,
        linewidth=2,
        label=f"Soroll (-1)",
        zorder=5
    )
ax2.axhline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label=r"Frontera física $\alpha = 0$")
for _, r in df.iterrows():
    mat = r["material"]
    if any(k in mat.lower() for k in materiales_destacados):
        ax2.annotate(
            mat.split("(")[0].strip(),
            (r["log_rho_300K"], r["alpha_coef"]),
            xytext=(6, 4), textcoords="offset points",
            fontsize=8, fontweight="bold", color="#1e293b", alpha=0.9
        )
ax2.set_title(f"2. Després: 3 Clústers Descoberts amb DBSCAN ($\\varepsilon={EPS}$)", fontsize=12, fontweight="bold")
ax2.set_xlabel(r"$\log_{10}(\rho_{300\mathrm{K}})$ [$\rho$ en $\Omega\cdot\mathrm{m}$]", fontsize=10.5)
ax2.grid(True, linestyle=":", alpha=0.6)
ax2.legend(loc="lower right", framealpha=0.9, fontsize=9)

plt.tight_layout()
RUTA_COMP = AQUI / "comparativa_abans_despres_dbscan.png"
fig_comp.savefig(RUTA_COMP, dpi=300)
plt.close(fig_comp)
print(f"Gràfic comparatiu Abans vs Després guardat a: {RUTA_COMP}")

if FIGURAS_LOCAL.exists():
    shutil.copy(RUTA_COMP, FIGURAS_LOCAL / "comparativa_abans_despres_dbscan.png")
if FIGURAS_DOCS is not None and FIGURAS_DOCS.exists():
    shutil.copy(RUTA_COMP, FIGURAS_DOCS / "comparativa_abans_despres_dbscan.png")

print("\nTotes les figures s'han generat i guardat correctament.")
