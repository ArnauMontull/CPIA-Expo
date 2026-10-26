import csv
import math
import random
import matplotlib.pyplot as plt

# Primer carreguem les dades sismològiquesw
arxiu = "earthquakes.csv"

# Creem una llista buida on es guardaran els identificadors, ubicacions i hores dels sismes
earthquake_ids = []
# Creem una llista buida on es guardaran les 4 característiques dels terratrèmols (Magnitud, Profunditat, Latitud i Longitud)
data_raw = []  

# Obertura del fitxer i lectura i extracció de les dades necessàries:
print(f"1. Llegint dades sismològiques de: {arxiu}")
# Obrim el fitxer en mode lectura ("r") amb la codificació estàndard universal. Assignem el fitxer a la variable f
with open(arxiu, mode="r", encoding="utf-8") as f:
    # Llegim el CSV en forma de diccionari
    reader = csv.DictReader(f)

    
    for idx, row in enumerate(reader):
        try:
            # S'adapta automàticament a diferents nomenclatures de capçalera
            mag = float(row.get("magnitude", row.get("mag", row.get("Mag", 0))))
            depth = float(
                row.get("depth", row.get("Depth", row.get("depth_km", 10)))
            )
            lat = float(row.get("latitude", row.get("lat", row.get("Lat", 0))))
            lon = float(
                row.get("longitude", row.get("lon", row.get("Lon", 0)))
            )

            # Identificador o data del sisme
            eq_id = row.get(
                "place", row.get("id", row.get("time", f"Sisme #{idx+1}"))
                )  

            earthquake_ids.append(eq_id)
            data_raw.append([mag, depth, lat, lon])
        except (ValueError, KeyError):
            # Saltem files incompletes o amb valors nuls
            continue

n_samples = len(data_raw)
n_features = len(data_raw[0])
print(
    f"S'han carregat correctament {n_samples} esdeveniments sísmics des de l'ordinador."
)

# ==============================================================================
# 2. Normalització Z-Score (Matemàtica nàtiva)
# ==============================================================================
means = [
    sum(data_raw[i][j] for i in range(n_samples)) / n_samples
    for j in range(n_features)
]
stdevs = [
    math.sqrt(
        sum((data_raw[i][j] - means[j]) ** 2 for i in range(n_samples))
        / n_samples
    )
    for j in range(n_features)
]

# Evitem divisió per zero si una columna és constant
stdevs = [sd if sd != 0 else 1.0 for sd in stdevs]

data_scaled = [
    [(data_raw[i][j] - means[j]) / stdevs[j] for j in range(n_features)]
    for i in range(n_samples)
]


def distancia_euclidiana(p1, p2):
    return math.sqrt(sum((p1[j] - p2[j]) ** 2 for j in range(len(p1))))


# ==============================================================================
# 3. Clustering K-Means: Classificació Tectònica (Python Pur)
# ==============================================================================
print("\n2. Classificant terratrèmols segons la seva naturalesa física...")

K = 3  # Ex: 1. Superficials, 2. Intermedis, 3. Profunds / Subducció
random.seed(42)
centroids = random.sample(data_scaled, K)
clusters = [0] * n_samples

for iteracio in range(25):
    for i in range(n_samples):
        distancies = [
            distancia_euclidiana(data_scaled[i], c) for c in centroids
        ]
        clusters[i] = distancies.index(min(distancies))

    nous_centroides = []
    for k in range(K):
        punts = [data_scaled[i] for i in range(n_samples) if clusters[i] == k]
        if punts:
            nou_c = [
                sum(p[j] for p in punts) / len(punts) for j in range(n_features)
            ]
            nous_centroides.append(nou_c)
        else:
            nous_centroides.append(centroids[k])
    centroids = nous_centroides

print("\n--- CLUSTERS DE SISMES TROBATS ---")
for k in range(K):
    idx_grup = [i for i in range(n_samples) if clusters[i] == k]
    count = len(idx_grup)

    avg_mag = sum(data_raw[i][0] for i in idx_grup) / count
    avg_depth = sum(data_raw[i][1] for i in idx_grup) / count

    print(f"\nGrup {k+1}: {count} esdeveniments sísmics")
    print(f" -> Magnitud mitjana: {avg_mag:.2f} Mwd")
    print(f" -> Profunditat mitjana: {avg_depth:.1f} km")

# ==============================================================================
# 4. Detecció d'Anomalies: Megasismes i Sismes Excepcionals
# ==============================================================================
print("\n3. Identificant esdeveniments sísmics anòmals (extrems)...")

distancies_veins = []
for i in range(n_samples):
    dists = [
        distancia_euclidiana(data_scaled[i], data_scaled[j])
        for j in range(n_samples)
        if i != j
    ]
    dists.sort()
    # Mitjana de distància als 5 veïns més propers
    dist_mitjana = sum(dists[:5]) / 5
    distancies_veins.append((dist_mitjana, i))

distancies_veins.sort(reverse=True)

print("\n--- TOP 5 SISMES MÉS ANÒMALS / EXCEPCIONALS ---")
for rank in range(min(5, n_samples)):
    dist, idx = distancies_veins[rank]
    mag_orig = data_raw[idx][0]
    depth_orig = data_raw[idx][1]
    lat_orig = data_raw[idx][2]
    lon_orig = data_raw[idx][3]

    print(f"{rank+1}. {earthquake_ids[idx]}")
    print(
        f"    Magnitud: {mag_orig} | Profunditat: {depth_orig} km | Coordenades: ({lat_orig:.2f}, {lon_orig:.2f})"
    )

# 5. GRÀFIC (Només 6 línies de Matplotlib)
mags = [p[0] for p in data_raw]
depths = [p[1] for p in data_raw]

plt.figure(figsize=(8, 5))
plt.scatter(
    mags, depths, c=clusters, cmap="viridis", alpha=0.5, label="Terratrèmols"
)

# Marcar les 5 anomalies amb un quadrat vermell
ano_mags = [data_raw[i][0] for i in distancies_veins]
ano_deps = [data_raw[i][1] for i in distancies_veins]
plt.scatter(
    ano_mags,
    ano_deps,
    color="red",
    marker="s",
    s=60,
    label="Anomalies (Top 5)",
)

plt.xlabel("Magnitud")
plt.ylabel("Profunditat (km)")
plt.title("Clustering i Anomalies de Terratrèmols")
plt.legend()
plt.gca().invert_yaxis()  # Invertim eix Y perquè la profunditat va cap avall
plt.show()