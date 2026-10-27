# Importem les llibreries que necessitem per al programa
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

# ==============================================================================
# 1. Càrrega i neteja de dades
# ==============================================================================
# Definim el nom del fitxer CSV que conté les dades sismològiques
arxiu = "earthquakes.csv"

# Llegim el fitxer CSV amb pandas i el guardem en una taula (DataFrame)
print(f"1. Llegint dades sismològiques de: {arxiu}")
df = pd.read_csv(arxiu)

# Indiquem quines són les 4 característiques que utilitzarem de cada sisme
features = ["mag", "depth", "latitude", "longitude"]

# Eliminem les files que tinguin valors buits en aquestes 4 columnes
df = df.dropna(subset=features).reset_index(drop=True)

# Mostrem quants terratrèmols s'han carregat correctament
print(f"S'han carregat correctament {len(df)} esdeveniments sísmics.")

# ==============================================================================
# 2. Normalització Z-Score
# ==============================================================================
# Seleccionem només les 4 columnes numèriques per treballar-hi
X = df[features]

# Apliquem el Z-score: restem la mitjana i dividim per la desviació estàndard
X_scaled = (X - X.mean()) / X.std()

# ==============================================================================
# 3. Clustering K-Means
# ==============================================================================
print("\n2. Classificant terratrèmols segons la seva naturalesa física...")

# Definim el nombre de grups (clústers) que volem trobar
K = 3

# Creem el model K-Means (random_state fa que el resultat sigui sempre el mateix)
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)

# Entrenem el model i guardem el grup assignat a cada sisme dins del DataFrame
df["cluster"] = kmeans.fit_predict(X_scaled)

# Agrupem per clúster i calculem el nombre de sismes, magnitud i profunditat mitjanes
resum = df.groupby("cluster").agg(
    Nombre_sismes=("mag", "count"),
    Magnitud_mitjana=("mag", "mean"),
    Profunditat_mitjana=("depth", "mean"),
)

# Mostrem la taula resum arrodonida a 2 decimals
print("\n--- CLUSTERS DE SISMES TROBATS ---")
print(resum.round(2))

# ==============================================================================
# 4. Detecció d'anomalies (distància als veïns més propers)
# ==============================================================================
print("\n3. Identificant esdeveniments sísmics anòmals (extrems)...")

# Definim quants veïns mirem i quantes anomalies volem mostrar
k_veins = 5
n_anomalies = 5

# Creem el model de veïns; demanem un veí de més perquè el primer és el propi sisme
veins = NearestNeighbors(n_neighbors=k_veins + 1)

# Ensenyem al model els punts normalitzats
veins.fit(X_scaled)

# Calculem les distàncies de cada sisme als seus veïns més propers
distancies, _ = veins.kneighbors(X_scaled)

# Calculem la distància mitjana als 5 veïns (ignorem la columna 0, que és ell mateix)
df["dist_veins"] = distancies[:, 1:].mean(axis=1)

# Agafem els 5 sismes amb la distància mitjana més gran: són els més anòmals
top_anomalies = df.nlargest(n_anomalies, "dist_veins")

# Mostrem per pantalla el rànquing de les anomalies
print("\n--- TOP 5 SISMES MÉS ANÒMALS / EXCEPCIONALS ---")
rank = 1
for i, fila in top_anomalies.iterrows():
    print(f"{rank}. {fila['place']}")
    print(
        f"    Magnitud: {fila['mag']} | Profunditat: {fila['depth']} km | "
        f"Coordenades: ({fila['latitude']:.2f}, {fila['longitude']:.2f})"
    )
    rank = rank + 1

# ==============================================================================
# 5. Gràfic
# ==============================================================================
# Creem la figura amb una mida adequada
plt.figure(figsize=(10, 6))

# Dibuixem tots els terratrèmols, pintats segons el clúster al qual pertanyen
plt.scatter(
    df["mag"], df["depth"], c=df["cluster"], cmap="viridis", alpha=0.5, s=20,
    label="Terratrèmols",
)

# Marquem les 5 anomalies amb un quadrat vermell
plt.scatter(
    top_anomalies["mag"], top_anomalies["depth"], color="red", marker="s",
    s=90, edgecolor="black", label="Anomalies",
)

# Afegim els textos dels eixos i el títol
plt.xlabel("Magnitud")
plt.ylabel("Profunditat (km)")
plt.title("Clustering i Anomalies de Terratrèmols")

# Afegim la llegenda
plt.legend()

# Invertim l'eix Y perquè la profunditat va cap avall
plt.gca().invert_yaxis()

# Mostrem el gràfic per pantalla
plt.show()