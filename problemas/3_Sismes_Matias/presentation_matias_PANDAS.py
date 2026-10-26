"""
Mòdul principal per a l'anàlisi de dades sismològiques.
Realitza la càrrega, normalització, clustering K-Means i detecció d'anomalies (KNN).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def carregar_i_netejar_dades(ruta_csv: str) -> pd.DataFrame:
    """Carrega el fitxer CSV, gestiona diferents noms de columnes i elimina registres nuls.

    Args:
        ruta_csv (str): Ruta al fitxer CSV.

    Returns:
        pd.DataFrame: DataFrame amb les columnes standarditzades.
    """
    df = pd.read_csv(ruta_csv)

    # Mapeig de columnes per compatibilitat de capçaleres
    col_map = {
        "magnitude": "mag",
        "Mag": "mag",
        "Depth": "depth",
        "depth_km": "depth",
        "Latitude": "latitude",
        "Lat": "latitude",
        "lat": "latitude",
        "Longitude": "longitude",
        "Lon": "longitude",
        "lon": "longitude",
    }
    df.rename(columns=col_map, inplace=True)

    # Identificador de l'esdeveniment sísmic
    if "place" in df.columns:
        df["eq_id"] = df["place"]
    elif "id" in df.columns:
        df["eq_id"] = df["id"]
    elif "time" in df.columns:
        df["eq_id"] = df["time"]
    else:
        df["eq_id"] = [f"Sisme #{i+1}" for i in range(len(df))]

    # Selecció i filtratge de columnes rellevants
    cols_requerides = ["mag", "depth", "latitude", "longitude"]
    df = df.dropna(subset=cols_requerides).copy()

    # Conversió tipus de dades
    for col in cols_requerides:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=cols_requerides).reset_index(drop=True)
    return df


def normalitzar_zscore(df: pd.DataFrame, columnes: list) -> np.ndarray:
    """Aplica la normalització Z-score a les columnes seleccionades.

    Args:
        df (pd.DataFrame): DataFrame de dades.
        columnes (list): Llista de columnes a normalitzar.

    Returns:
        np.ndarray: Matriu de dades normalitzades.
    """
    X = df[columnes].to_numpy()
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    stds[stds == 0] = 1.0  # Evita divisió per zero
    return (X - means) / stds


def aplicar_kmeans(
    X_scaled: np.ndarray, n_clusters: int = 3, random_state: int = 42
) -> tuple:
    """Executa l'algorisme K-Means de scikit-learn.

    Args:
        X_scaled (np.ndarray): Dades normalitzades.
        n_clusters (int): Nombre de clústers.
        random_state (int): Llavor aleatòria per a reproductibilitat.

    Returns:
        tuple: (etiquetes dels clústers, centroides)
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    return labels, kmeans.cluster_centers_


def detectar_anomalies_knn(
    X_scaled: np.ndarray, n_top: int = 5, k_neighbors: int = 5, seed: int = 42
) -> np.ndarray:
    """Identifica els esdeveniments més anòmals basat en la distància mitjana als k veïns més propers.

    Args:
        X_scaled (np.ndarray): Dades normalitzades.
        n_top (int): Nombre d'anomalies a retornar.
        k_neighbors (int): Nombre de veïns més propers.
        seed (int): Llavor aleatòria per al subconjunt de mostra.

    Returns:
        np.ndarray: Índexs de les top n anomalies.
    """
    n_samples = len(X_scaled)
    rng = np.random.default_rng(seed)
    sample_size = min(2000, n_samples)
    sample_idx = rng.choice(n_samples, sample_size, replace=False)
    X_sample = X_scaled[sample_idx]

    scores = np.zeros(n_samples)

    # Processament per blocs per a major eficiència
    batch_size = 500
    for i in range(0, n_samples, batch_size):
        batch = X_scaled[i : i + batch_size]
        dists = np.linalg.norm(batch[:, np.newaxis, :] - X_sample[np.newaxis, :, :], axis=2)
        dists.sort(axis=1)

        # Si el punt està a la mostra, omitim la distància 0 a ell mateix
        has_self = dists[:, 0] < 1e-9
        k_dists = np.where(
            has_self[:, np.newaxis],
            dists[:, 1 : k_neighbors + 1],
            dists[:, :k_neighbors],
        )
        scores[i : i + batch_size] = k_dists.mean(axis=1)

    return np.argsort(-scores)[:n_top]


def visualitzar_resultats(
    df: pd.DataFrame, labels: np.ndarray, anomalies_idx: np.ndarray
):
    """Genera la representació gràfica del clustering i les anomalies."""
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        df["mag"],
        df["depth"],
        c=labels,
        cmap="viridis",
        alpha=0.5,
        s=20,
        label="Terratrèmols",
    )

    plt.scatter(
        df.loc[anomalies_idx, "mag"],
        df.loc[anomalies_idx, "depth"],
        color="red",
        marker="s",
        s=90,
        edgecolor="black",
        linewidth=1.5,
        label="Anomalies (Extrems)",
    )

    plt.colorbar(scatter, label="Clúster")
    plt.xlabel("Magnitud (Mwd)")
    plt.ylabel("Profunditat (km)")
    plt.title("Clustering K-Means i Detecció d'Anomalies en Terratrèmols")
    plt.legend()
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()


def main():
    arxiu = "earthquakes.csv"
    print(f"1. Càrrega i preparació de dades des de: {arxiu}")
    df = carregar_i_netejar_dades(arxiu)
    print(f"S'han carregat correctament {len(df)} registres sísmics.")

    # Normalització
    features = ["mag", "depth", "latitude", "longitude"]
    X_scaled = normalitzar_zscore(df, features)

    # Clustering
    print("\n2. Executant clustering K-Means...")
    labels, _ = aplicar_kmeans(X_scaled, n_clusters=3, random_state=42)
    df["cluster"] = labels

    print("\n--- RESUM DELS CLÚSTERS ---")
    resum = df.groupby("cluster").agg(
        Count=("mag", "count"),
        Mag_Mitjana=("mag", "mean"),
        Profunditat_Mitjana=("depth", "mean"),
    )
    print(resum.round(2))

    # Anomalies
    print("\n3. Detecció d'anomalies (KNN)...")
    top_anomalies_idx = detectar_anomalies_knn(X_scaled, n_top=5)

    print("\n--- TOP 5 SISMES ANÒMALS ---")
    for rank, idx in enumerate(top_anomalies_idx, start=1):
        row = df.iloc[idx]
        print(
            f"{rank}. {row['eq_id']} | Magnitud: {row['mag']} | Profunditat: {row['depth']} km | "
            f"Coordenades: ({row['latitude']:.2f}, {row['longitude']:.2f})"
        )

    # Visualització
    visualitzar_resultats(df, labels, top_anomalies_idx)


if __name__ == "__main__":
    main()