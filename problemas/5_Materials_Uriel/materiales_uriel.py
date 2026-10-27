"""problemas/5_Materials_Uriel/materiales_uriel.py

Clasificación no supervisada de materiales eléctricos (Conductores, Semiconductores y Aislantes)
mediante DBSCAN de scikit-learn (Density-Based Spatial Clustering of Applications with Noise).

Parámetros fijados:
- Epsilon (radio de vecindad): eps = 0.65
- Min samples (mínimo de muestras por núcleo): min_samples = 3

Autor: Uriel
Asignatura: CPIA · Aprendizaje No Supervisado
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

# ==============================================================================
# 1. Cargar el dataset descargado en datos/
# ==============================================================================
DATOS_DIR = Path(__file__).resolve().parents[2] / "datos"
CSV_PATH = DATOS_DIR / "materiales_electricos.csv"

if not CSV_PATH.exists():
    raise FileNotFoundError(f"No se encontró el archivo de datos en: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)
print(f"Dataset cargado con éxito ({len(df)} materiales).")

# ==============================================================================
# 2. Selección de características y estandarización manual (Z-Score)
# ==============================================================================
# x1: log10(resistividad a 300 K) -> comprime más de 30 órdenes de magnitud
# x2: coeficiente térmico alpha -> firma cuántica del material
features = ["log_rho_300K", "alpha_coef"]
X_raw = df[features].values

# Estandarización manual: Z = (X - μ) / σ
# Garantiza media = 0 y desviación típica = 1 en cada dimensión
media = np.mean(X_raw, axis=0)
desv = np.std(X_raw, axis=0)
X_scaled = (X_raw - media) / desv

# ==============================================================================
# 3. Aplicación de DBSCAN (scikit-learn)
# ==============================================================================
EPS = 0.65
MIN_SAMPLES = 3

dbscan = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES)
df["cluster"] = dbscan.fit_predict(X_scaled)

# ==============================================================================
# 4. Cálculo del Silhouette Score (scikit-learn)
# ==============================================================================
mask_validos = df["cluster"] != -1
if len(set(df["cluster"][mask_validos])) > 1:
    score_sil = silhouette_score(X_scaled[mask_validos], df["cluster"][mask_validos])
else:
    score_sil = None

# ==============================================================================
# 5. Métricas y análisis de resultados
# ==============================================================================
clusters_encontrados = sorted(set(df["cluster"]) - {-1})
n_clusters = len(clusters_encontrados)
n_ruido = int(np.sum(df["cluster"] == -1))

print("\n" + "=" * 65)
print(f"RESULTADOS DE DBSCAN (eps={EPS}, min_samples={MIN_SAMPLES})")
print("=" * 65)
print(f"Clusters descubiertos por densidad : {n_clusters}")
print(f"Puntos clasificados como ruido (-1): {n_ruido} de {len(df)}")
if score_sil is not None:
    print(f"Silhouette Score (núcleos densos) : {score_sil:.4f}")

print("\nMatriz de contingencia (Clase real vs. Cluster DBSCAN):")
print(pd.crosstab(df["clase_real"], df["cluster"], margins=True))

if n_ruido > 0:
    ruido_df = df[df["cluster"] == -1][["material", "log_rho_300K", "alpha_coef", "clase_real"]]
    print("\nMateriales clasificados como ruido/anomalía (cluster = -1):")
    for _, r in ruido_df.iterrows():
        print(f" - {r['material']:<30} | log10(ρ)={r['log_rho_300K']:>6.2f} | α={r['alpha_coef']:>8.5f} | Tipo: {r['clase_real']}")

# ==============================================================================
# 6. Visualización científica en 2D con Matplotlib
# ==============================================================================
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

plt.figure(figsize=(10, 6.5))

paleta_colores = {
    0: ("#d97706", "Clúster 0 (Conductors)"),
    1: ("#2563eb", "Clúster 1 (Aïllants)"),
    2: ("#059669", "Clúster 2 (Semiconductors)"),
}

for cl in clusters_encontrados:
    sub = df[df["cluster"] == cl]
    color, nombre_cl = paleta_colores.get(cl, ("#6b7280", f"Clúster {cl}"))
    plt.scatter(
        sub["log_rho_300K"],
        sub["alpha_coef"],
        c=color,
        s=70,
        alpha=0.85,
        edgecolors="black",
        linewidth=0.8,
        label=f"{nombre_cl} (n={len(sub)})"
    )

# Puntos de ruido si existieran
sub_ruido = df[df["cluster"] == -1]
if len(sub_ruido) > 0:
    plt.scatter(
        sub_ruido["log_rho_300K"],
        sub_ruido["alpha_coef"],
        c="#dc2626",
        marker="x",
        s=80,
        linewidth=2,
        label=f"Soroll / Anomalies (n={len(sub_ruido)})",
        zorder=5
    )

# Línea de referencia física para α = 0
plt.axhline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label=r"Frontera física $\alpha = 0$")

# Etiquetas de texto para materiales clave representativos
materiales_destacados = ["copper", "silver", "silicon", "germanium", "gaas", "glass", "ptfe", "quartz", "graphite"]
for _, r in df.iterrows():
    mat = r["material"]
    if any(k in mat.lower() for k in materiales_destacados):
        plt.annotate(
            mat.split("(")[0].strip(),
            (r["log_rho_300K"], r["alpha_coef"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=8.5,
            fontweight="semibold",
            color="#1e293b",
            alpha=0.9
        )

plt.title(f"Classificació de Materials amb DBSCAN ($\\varepsilon = {EPS}$, $min\\_samples = {MIN_SAMPLES}$)", fontsize=13, fontweight="bold")
plt.xlabel(r"$\log_{10}(\rho_{300\mathrm{K}})$ [$\rho$ en $\Omega\cdot\mathrm{m}$]", fontsize=11)
plt.ylabel(r"Coeficient tèrmic $\alpha$ [$\mathrm{K}^{-1}$]", fontsize=11)
plt.grid(True, linestyle=":", alpha=0.6)
plt.legend(loc="upper right", framealpha=0.9)
plt.tight_layout()

# Guardar figura en la carpeta del problema
FIGURA_PATH = Path(__file__).resolve().parent / "clusters_materiales_dbscan.png"
plt.savefig(FIGURA_PATH, dpi=300)
print(f"\nGráfico guardado en: {FIGURA_PATH}")

try:
    plt.show()
except Exception:
    pass
