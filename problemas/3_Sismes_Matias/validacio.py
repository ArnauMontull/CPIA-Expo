"""Validacio complementaria del clustering K-Means i de la deteccio d'anomalies.

Reutilitza les mateixes dades i la mateixa normalitzacio z-score que
presentation_matias.py, pero amb NumPy per poder calcular metriques costoses.
"""
import csv
import time
import numpy as np


def carrega(path="earthquakes.csv"):
    """Retorna matriu (n,4) [mag, prof, lat, lon] i llista de noms; salta files invalides."""
    X, noms = [], []
    with open(path, encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f)):
            try:
                X.append([float(r["mag"]), float(r["depth"]),
                          float(r["latitude"]), float(r["longitude"])])
                noms.append(r["place"] or f"Sisme #{i+1}")
            except (ValueError, KeyError, TypeError):
                continue
    return np.array(X), noms


def zscore(X):
    """Estandarditza cada columna (sigma poblacional, com el script original)."""
    sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    return (X - X.mean(axis=0)) / sd


def kmeans(Z, K, seed=42, iters=25):
    """K-Means de Lloyd amb inicialitzacio aleatoria; retorna etiquetes i inercia."""
    rng = np.random.default_rng(seed)
    C = Z[rng.choice(len(Z), K, replace=False)]
    for _ in range(iters):
        D = ((Z[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
        lab = D.argmin(axis=1)
        C = np.array([Z[lab == k].mean(axis=0) if (lab == k).any() else C[k]
                      for k in range(K)])
    D = ((Z[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
    return D.argmin(axis=1), D.min(axis=1).sum()


def silhouette(Z, lab, n=2000, seed=0):
    """Coeficient de silueta mitja sobre una mostra aleatoria de n punts."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(Z), min(n, len(Z)), replace=False)
    S = []
    for i in idx:
        d = np.sqrt(((Z - Z[i]) ** 2).sum(axis=1))
        a = d[lab == lab[i]].sum() / max((lab == lab[i]).sum() - 1, 1)
        b = min(d[lab == k].mean() for k in set(lab) if k != lab[i])
        S.append((b - a) / max(a, b))
    return float(np.mean(S))


def top_anomalies(Z, m=5, sample=2000, k=5, seed=42):
    """Index dels m punts amb major distancia mitjana als k veins de la mostra."""
    rng = np.random.default_rng(seed)
    M = Z[rng.choice(len(Z), sample, replace=False)]
    sc = np.empty(len(Z))
    for s in range(0, len(Z), 500):
        d = np.sqrt(((Z[s:s+500, None, :] - M[None]) ** 2).sum(axis=2))
        d.sort(axis=1)
        d = np.where(d[:, :1] < 1e-9, d[:, 1:k+1], d[:, :k])
        sc[s:s+500] = d.mean(axis=1)
    return np.argsort(-sc)[:m]


def rand_index(a, b, n=3000, seed=0):
    """Rand index (concordancia de parelles) sobre una mostra, per mesurar estabilitat."""
    rng = np.random.default_rng(seed)
    i = rng.choice(len(a), n, replace=False)
    a, b = a[i], b[i]
    sa = a[:, None] == a[None]; sb = b[:, None] == b[None]
    iu = np.triu_indices(n, 1)
    return float((sa[iu] == sb[iu]).mean())


if __name__ == "__main__":
    X, noms = carrega()
    Z = zscore(X)
    print("N =", len(X))
    print("K, inercia, silueta")
    for K in range(2, 9):
        lab, J = kmeans(Z, K)
        print(K, round(J, 1), round(silhouette(Z, lab), 3))
    base, _ = kmeans(Z, 3, seed=42)
    print("Estabilitat K=3 (Rand vs seed 42):")
    for s in (1, 2, 3, 4, 5):
        l, J = kmeans(Z, 3, seed=s)
        print(s, round(J, 1), round(rand_index(base, l), 3), np.bincount(l))
    print("Anomalies amb 5 mostres diferents:")
    ref = set(top_anomalies(Z, 5, seed=42))
    for s in (1, 2, 3, 4, 5, 6):
        t = top_anomalies(Z, 5, seed=s)
        print(s, [noms[i] for i in t], len(ref & set(t)))
    print("Perfil clusters K=3 (mag, prof, lat, lon mitjanes; mag min-max; prof min-max)")
    for k in range(3):
        g = X[base == k]
        print(k, len(g), g.mean(axis=0).round(2), g[:, 0].min(), g[:, 0].max(), g[:, 1].min(), g[:, 1].max())
    print("Correlacio mag-prof:", np.corrcoef(X[:, 0], X[:, 1])[0, 1].round(3))


def figura_mapa(X, lab, sortida="fig_mapa.png"):
    """Dibuixa longitud/latitud acolorit per cluster (figura de l'informe)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(9, 4.2))
    plt.scatter(X[:, 3], X[:, 2], c=lab, cmap="viridis", s=6, alpha=0.5)
    plt.xlabel("Longitud (°)"); plt.ylabel("Latitud (°)")
    plt.title("Distribució geogràfica dels clústers")
    plt.tight_layout(); plt.savefig(sortida, dpi=200)
