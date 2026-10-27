import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score

# ==========================================
# PAS 1: Càrrega i neteja inicial de les dades
# ==========================================

# Llegim el fitxer CSV que conté les dades dels terratrèmols
df = pd.read_csv("earthquakes.csv")

# Seleccionem només les columnes numèriques que necessitem per a l'anàlisi
columnes_interes = ["mag", "depth", "latitude", "longitude"]
df = df[columnes_interes]

# Eliminem les files que tinguin valors buits o nuls (NaN) per evitar errors
df = df.dropna()

# ==========================================
# PAS 2: Normalització de les dades (Z-score)
# ==========================================

# Perquè el model no doni més importància a una variable que a una altra,
# restem la mitjana i dividim per la desviació estàndard a cada columna.
df_normalitzat = (df[columnes_interes] - df[columnes_interes].mean()) / df[columnes_interes].std()

# Convertim les dades normalitzades en un array de NumPy per utilitzar-lo a scikit-learn
X_scaled = df_normalitzat.to_numpy()

# ==========================================
# PAS 3: Avaluació del nombre òptim de clústers (K)
# ==========================================

print("\n--- AVALUACIÓ DEL NOMBRE ÒPTIM DE CLÚSTERS (K) ---")
print(f"{'K':<5}{'Inèrcia':<15}{'Silhouette Score':<15}")
print("-" * 35)

# Fem un bucle per provar diferents valors de K (des de 2 fins a 8 clústers)
for k in range(2, 9):
    # Creem i entrenem el model K-Means per a K clústers
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    etiquetes = kmeans.fit_predict(X_scaled)
    
    # Obtenim la inèrcia (suma de distàncies al quadrat dins dels clústers)
    inercia = kmeans.inertia_

    # Calculem la puntuació de silueta (mesura com de ben separats estan els clústers)
    # Utilitzem una mostra de 2000 punts per fer el càlcul més ràpid
    puntuacio_silueta = silhouette_score(
        X_scaled, etiquetes, sample_size=min(2000, len(X_scaled)), random_state=42
    )
    
    # Imprimim els resultats en format de taula
    print(f"{k:<5}{inercia:<15.2f}{puntuacio_silueta:<15.4f}")

# ==========================================
# PAS 4: Avaluació de l'estabilitat del model
# ==========================================

# Fixem K=3 per comprovar si el model és estable canviant la llavor d'inicialització (seed)
k_triat = 3
print(f"\n--- AVALUACIÓ D'ESTABILITAT (K={k_triat}) ---")

# Entrenem un model base amb la llavor 42
kmeans_base = KMeans(n_clusters=k_triat, random_state=42, n_init=10)
etiquetes_base = kmeans_base.fit_predict(X_scaled)

# Provem diferents llavors per veure si els resultats canvien molt
llavors = [1, 2, 3, 4, 5]
for s in llavors:
    kmeans_test = KMeans(n_clusters=k_triat, random_state=s, n_init=10)
    etiquetes_test = kmeans_test.fit_predict(X_scaled)
    
    # Calculem l'Adjusted Rand Index (ARI) per comparar amb les etiquetes base (1.0 = idèntic)
    ari = adjusted_rand_score(etiquetes_base, etiquetes_test)
    print(f"Llavor: {s} | Inèrcia: {kmeans_test.inertia_:.2f} | ARI (vs base seed 42): {ari:.4f}")

# ==========================================
# PAS 5: Entrenament final amb K=3 i generació del mapa
# ==========================================

# Entrenem el model final amb K=3
kmeans_final = KMeans(n_clusters=3, random_state=42, n_init=10)
etiquetes_finals = kmeans_final.fit_predict(X_scaled)

# Creem la figura per al mapa geogràfic
plt.figure(figsize=(10, 5))

# Dibuixem els punts utilitzant la longitud i la latitud de les dades originals
grafic = plt.scatter(
    df["longitude"],
    df["latitude"],
    c=etiquetes_finals,
    cmap="viridis",
    s=8,
    alpha=0.6,
)

# Afegim la barra de colors, títols i etiquetes dels eixos
plt.colorbar(grafic, label="Clúster")
plt.xlabel("Longitud (°)")
plt.ylabel("Latitud (°)")
plt.title("Distribució geogràfica dels 3 clústers")
plt.grid(True, linestyle="--", alpha=0.5)

# Ajustem el disseny i meprem la imatge a disc
plt.tight_layout()
ruta_sortida = "fig_mapa.png"
plt.savefig(ruta_sortida, dpi=200)

print(f"\nFigura geogràfica desada a: {ruta_sortida}")
