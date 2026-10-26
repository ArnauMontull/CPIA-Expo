"""problemas/5_Materials_Uriel/materiales_uriel.py

Clasificación no supervisada de materiales eléctricos (Conductores, Semiconductores y Aislantes)
mediante DBSCAN (Density-Based Spatial Clustering of Applications with Noise).

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
# 2. Selección de características y estandarización (Z-Score)
# ==============================================================================
# x1: log10(resistividad a 300 K) -> comprime más de 30 órdenes de magnitud
# x2: coeficiente térmico alpha -> firma cuántica del material
features = ["log_rho_300K", "alpha_coef"]
X_raw = df[features].values

# Estandarización obligatoria: Z = (X - μ) / σ
media = np.mean(X_raw, axis=0)
desv = np.std(X_raw, axis=0)
X_scaled = (X_raw - media) / desv

# ==============================================================================
# 3. Aplicación de DBSCAN con eps = 0.65 y min_samples = 3
# ==============================================================================
EPS = 0.65
MIN_SAMPLES = 3

def ejecutar_dbscan(X, eps=0.65, min_samples=3):
    """Algoritmo canónico de DBSCAN implementado desde cero con NumPy."""
    N = len(X)
    etiquetas = np.full(N, -1, dtype=int)
    visitados = np.zeros(N, dtype=bool)
    cluster_actual = 0
    
    # Matriz de distancias euclídeas
    D = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=-1)
    
    for i in range(N):
        if visitados[i]:
            continue
        visitados[i] = True
        
        vecinos = np.where(D[i] <= eps)[0]
        if len(vecinos) < min_samples:
            etiquetas[i] = -1  # Ruido inicial
        else:
            etiquetas[i] = cluster_actual
            cola = list(vecinos[vecinos != i])
            while cola:
                j = cola.pop(0)
                if not visitados[j]:
                    visitados[j] = True
                    j_vecinos = np.where(D[j] <= eps)[0]
                    if len(j_vecinos) >= min_samples:
                        for v in j_vecinos:
                            if v not in cola and etiquetas[v] == -1:
                                cola.append(v)
                if etiquetas[j] == -1:
                    etiquetas[j] = cluster_actual
            cluster_actual += 1
    return etiquetas

df["cluster"] = ejecutar_dbscan(X_scaled, eps=EPS, min_samples=MIN_SAMPLES)

# ==============================================================================
# 4. Cálculo del Silhouette Score
# ==============================================================================
def calcular_silhouette(X, labels):
    """Calcula el Silhouette Score sobre los puntos asignados a clusters válidos."""
    mask = labels != -1
    if len(set(labels[mask])) <= 1:
        return None
    D = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=-1)
    sils = []
    for i in range(len(X)):
        if labels[i] == -1:
            continue
        c_i = labels[i]
        same_c = np.where((labels == c_i) & (np.arange(len(X)) != i))[0]
        a_i = np.mean(D[i, same_c]) if len(same_c) > 0 else 0
        other_clusters = set(labels) - {-1, c_i}
        b_i = min(np.mean(D[i, labels == c_o]) for c_o in other_clusters)
        sils.append((b_i - a_i) / max(a_i, b_i))
    return float(np.mean(sils))

score_sil = calcular_silhouette(X_scaled, df["cluster"].values)

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
# 6. Visualización científica en 2D
# ==============================================================================
plt.figure(figsize=(10, 6.5))

paleta_colores = {
    0: ("#d97706", "Cluster 0 (Conductores)"),
    1: ("#2563eb", "Cluster 1 (Aislantes)"),
    2: ("#059669", "Cluster 2 (Semiconductores)"),
}

for cl in clusters_encontrados:
    sub = df[df["cluster"] == cl]
    color, nombre_cl = paleta_colores.get(cl, ("#6b7280", f"Cluster {cl}"))
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

# Puntos de ruido (si los hubiera)
sub_ruido = df[df["cluster"] == -1]
if len(sub_ruido) > 0:
    plt.scatter(
        sub_ruido["log_rho_300K"],
        sub_ruido["alpha_coef"],
        c="#dc2626",
        marker="x",
        s=80,
        linewidth=2,
        label=f"Ruido / Anomalías (n={len(sub_ruido)})",
        zorder=5
    )

# Línea de referencia física para α = 0
plt.axhline(0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label=r"Frontera $\alpha = 0$")

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

plt.title(f"Clasificación de Materiales con DBSCAN ($\\varepsilon = {EPS}$, $min\\_samples = {MIN_SAMPLES}$)", fontsize=13, fontweight="bold")
plt.xlabel(r"$\log_{10}(\rho_{300\mathrm{K}})$ [$\rho$ en $\Omega\cdot\mathrm{m}$]", fontsize=11)
plt.ylabel(r"Coeficiente térmico $\alpha$ [$\mathrm{K}^{-1}$]", fontsize=11)
plt.grid(True, linestyle=":", alpha=0.6)
plt.legend(loc="upper right", framealpha=0.9)
plt.tight_layout()

# Guardar figura en disco
FIGURA_PATH = Path(__file__).resolve().parent / "clusters_materiales_dbscan.png"
plt.savefig(FIGURA_PATH, dpi=300)
print(f"\nGráfico guardado en: {FIGURA_PATH}")

try:
    plt.show()
except Exception:
    pass
