"""
Mòdul de validació complementària per al model de clustering i anomalies.
Calcula inèrcies, coeficients de silueta, Rand Index i genera el mapa geogràfic.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from presentation_matias import carregar_i_netejar_dades, normalitzar_zscore, detectar_anomalies_knn


def avaluar_nombre_clusters(X_scaled: np.ndarray, max_k: int = 8):
    """Calcula inèrcia i coeficient de silueta per a diferents valors de K."""
    print("\n--- AVALUACIÓ DEL NOMBRE ÒPTIM DE CLÚSTERS (K) ---")
    print(f"{'K':<5}{'Inèrcia':<15}{'Silhouette Score':<15}")
    print("-" * 35)

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        inertia = kmeans.inertia_

        # Mostra aleatòria per accelerar la silueta en grans volums de dades
        score = silhouette_score(
            X_scaled, labels, sample_size=min(2000, len(X_scaled)), random_state=42
        )
        print(f"{k:<5}{inertia:<15.2f}{score:<15.4f}")


def avaluar_estabilitat(X_scaled: np.ndarray, k: int = 3, seeds: list = [1, 2, 3, 4, 5]):
    """Mesura l'estabilitat del model mitjançant l'Adjusted Rand Index (ARI)."""
    print(f"\n--- AVALUACIÓ D'ESTABILITAT (K={k}) ---")
    base_kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    base_labels = base_kmeans.fit_predict(X_scaled)

    for s in seeds:
        kmeans = KMeans(n_clusters=k, random_state=s, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        ari = adjusted_rand_score(base_labels, labels)
        print(f"Seed: {s} | Inèrcia: {kmeans.inertia_:.2f} | ARI (vs base seed 42): {ari:.4f}")


def generar_figura_mapa(df: pd.DataFrame, labels: np.ndarray, output_path: str = "fig_mapa.png"):
    """Dibuixa la distribució geogràfica dels clústers."""
    plt.figure(figsize=(10, 5))
    scatter = plt.scatter(
        df["longitude"],
        df["latitude"],
        c=labels,
        cmap="viridis",
        s=8,
        alpha=0.6,
    )
    plt.colorbar(scatter, label="Clúster")
    plt.xlabel("Longitud (°)")
    plt.ylabel("Latitud (°)")
    plt.title("Distribució Geogràfica dels Clústers Sísmics")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(f"\nFigura geogràfica desada a: {output_path}")


def main():
    df = carregar_i_netejar_dades("earthquakes.csv")
    X_scaled = normalitzar_zscore(df, ["mag", "depth", "latitude", "longitude"])

    avaluar_nombre_clusters(X_scaled)
    avaluar_estabilitat(X_scaled)

    labels = KMeans(n_clusters=3, random_state=42, n_init=10).fit_predict(X_scaled)
    generar_figura_mapa(df, labels)


if __name__ == "__main__":
    main()