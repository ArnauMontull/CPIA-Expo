# -*- coding: utf-8 -*-
"""Created on Sun Oct 25 11:36:18 2026.

@author: mcanu
"""

# importem llibreries:

import warnings
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_openml
from sklearn.metrics import adjusted_rand_score, silhouette_score

# Amaga un avís inofensiu de K-Means a Windows (no afecta els resultats)
warnings.filterwarnings("ignore", message="KMeans is known to have a memory leak")

# Paràmetres de l'anàlisi
TERRA, SOSTRE = 100, 16000   # retall de rang de l'expressió
N_GENES = 500                # nombre de gens més variables que es conserven
SEED = 42                    # llavor: resultats reproduïbles

# %% FUNCIONS

def load_data():

    """
    Aquesta funció carrega el dataset objectiu, l'analitza i el modifica a gust
    propi pel tractament que en farem:
      1. Descarrega el dataset d'OpenML, si no es fa, notifica l'error
      2. Observem i comprovem dades originals: files, columnes, etiquetes i recomptes
      3. Si les etiquetes no són ALL i AML, dona error d'assert
      4. Transposem. gens en files i pacients en columnes. Ho passem a dades NumPy
      5. Modifiquem les etiquetes: ALL passa a ser 0 i AML, 1.

    --- No té paràmetres --

    --- Retorna:
      X : np.ndarray
          Matriu de dimensions (gens x mostres).
      y : np.ndarray
          Etiquetes per mostra (0 = ALL, 1 = AML).
    """

    # descarreguem el dataset d'OpenML indicant ID i en format taula (DataFrame)
    try:
        print("Iniciant descàrrega del dataset...")
        dataset = fetch_openml(data_id=1104, as_frame=True)
        print("Descàrrega completada amb èxit.")
    except Exception:
        print("Error crític: No s'ha pogut descarregar el dataset.")
        raise

    # ara comprovem com són les dades carregades:
    df_original = dataset.data
    print("\nObservem i analitzem el dataset importat: \n")
    print(f"Dimensions originals (files, columnes): {df_original.shape}")
    print(f"Mostra de columnes: {df_original.columns[:4].tolist()}...")
    print(f"Mostra de files: {df_original.index[:4].tolist()}...")
    print("\nPrimeres files i columnes de la matriu tal com arriba:")
    print(df_original.iloc[:3, :4])  # mostrem una submatriu petita de 3x4

    # inspecció de les etiquetes originals i comprovació
    y_raw = dataset.target
    etiquetes_uniques, recomptes = np.unique(y_raw, return_counts=True)
    print(f"\nEtiquetes originals trobades a dataset.target: {etiquetes_uniques}")
    assert set(etiquetes_uniques) == {"ALL", "AML"}, f"Etiquetes inesperades: {etiquetes_uniques}"
    print(f"Distribució de classes original: {dict(zip(etiquetes_uniques, recomptes.tolist()))}")

    # gens en files i pacients en columnes, transposem i convertim a NumPy array
    # assignem les etiquetes ALL i AML a 0 i 1 respectivament
    X = dataset.data.T.to_numpy(dtype=float)
    y = np.where(dataset.target == "ALL", 0, 1)
    return X, y

def estad_matriu(A):

    """
    Aquesta funció analitza les estadístiques d'una matriu on tenim les dades
    de gens i mostres. L'objectiu és respondre a les següents preguntes:
    - Hi ha valors NaN, 0 o negatius?
    - Com de separats estan els valors? Hi ha asimetria?

    --- Paràmetres:
        A : np.ndarray
            Matriu de dimensions (gens x mostres)

    --- Retorna: només amb print les estadístiques.

    """
    num_nans = np.isnan(A).sum()    # nombre de NaN que hi ha
    val_min = np.min(A)             # valor mínim de la matriu
    val_max = np.max(A)             # valor màxim de la matriu
    val_mean = np.mean(A)           # mitjana dels valors
    val_median = np.median(A)       # mediana dels valors

    print("-" * 80)
    print("INSPECCIÓ ESTADÍSTICA DE LA MATRIU:")
    print(f"Nombre de valors NaN: {num_nans}")
    print(f"Valor mínim: {val_min:.2f} | Valor màxim: {val_max:.2f}")
    print(f"Hi ha valors negatius o zero?: {'Sí' if val_min <= 0 else 'No'}")
    print(f"Mitjana: {val_mean:.2f} | Mediana: {val_median:.2f}")

    # l'asimetria es pot identificar amb la diferència entre mitjana i mediana:
    print(f"Diferència (Mitjana - Mediana): {val_mean - val_median:.2f}")
    print("-" * 80)

def preprocess_log(X, terra=TERRA, sostre=SOSTRE):
    """
    Aplica un terra i sostre per eliminar valors negatius (biològicament no
    perdem info, és un tractament habitual) i transforma la matriu d'expressió
    mitjançant log2(X + 1).

    --- Paràmetres:
        X : np.ndarray
            Matriu de dimensions (gens x mostres).
        terra, sostre : int
            Valors mínim i màxim d'expressió permesos (retall de rang).

    --- Retorna:
        X_log : np.ndarray
            Matriu transformada amb la mateixa dimensió que l'entrada.
    """
    # 1. Apliquem el retall amb terra i sostre evitar NaN, errors al logaritme
    # 2. Transformació log2(X + 1)
    X_trunc = np.clip(X, terra, sostre)
    X_log = np.log2(X_trunc + 1)

    return X_log

def plot_histograms(X, X_log):

    """
    Genera dos histogrames comparatius de la distribució de valors abans i
    després d'aplicar la transformació logarítmica log2(X + 1).

    --- Paràmetres:
        X : np.ndarray
            Matriu de dades original.

        X_log : np.ndarray
                Matriu de dades transformada.
    """

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histograma 1: Dades originals
    axes[0].hist(X.ravel(), bins=100, color="steelblue", edgecolor="black", alpha=0.8)
    axes[0].set_yscale("log")  # Permet veure la cua dreta tot i el pic gegant al centre
    axes[0].set_title("Distribució original de valors (X) [Eix Y logarítmic]")
    axes[0].set_xlabel("Nivell d'expressió")
    axes[0].set_ylabel("Freqüència (escala log)")

    # Histograma 2: Dades després del logaritme
    axes[1].hist(X_log.ravel(), bins=100, color="forestgreen", edgecolor="black", alpha=0.8)
    axes[1].set_yscale("log")  # Permet apreciar tant el zero com tota la campana
    axes[1].set_title("Distribució després de log2(X + 1) [Eix Y logarítmic]")
    axes[1].set_xlabel("log2(expressió + 1)")
    axes[1].set_ylabel("Freqüència (escala log)")

    plt.tight_layout()
    plt.savefig("hist_log.pdf", bbox_inches="tight")
    plt.show()

def filtre_i_estandar(X_log, n_genes=N_GENES):

    """
    Filtra els n_genes amb major variància i estandarditza cada fila mitjançant
    la transformació Z-score.

    --- Paràmetres:
        X_log : np.ndarray
                Matriu de dimensions (gens x mostres) transformada logarítmicament.

        n_genes : int
                Nombre de gens a seleccionar segons la seva variància.

    --- Retorna:
        X_clean : np.ndarray
                  Matriu de dimensions (n_genes x mostres) estandarditzada (mitjana=0,std=1).

        top_gene_indices : np.ndarray
                           Índexs originals dels gens seleccionats.
    """

    # càlcul de la variància de cada gen (al llarg de les mostres, axis=1)
    variances = np.var(X_log, axis=1)

    # selecció dels n_genes amb més variància
    # np.argsort ordena de menor a major; agafem els últims n_genes
    top_gene_indices = np.argsort(variances)[-n_genes:]

    # actualitzem la matriu i ens quedem amb els gens amb més variància
    X_top = X_log[top_gene_indices, :]

    # apliquem la trasnformació Z-score per a cada gen
    mean = np.mean(X_top, axis=1, keepdims=True)
    std = np.std(X_top, axis=1, keepdims=True)
    X_clean = (X_top - mean) / std

    # comprovacions formals (asserts) internes per garantir la qualitat del resultat
    assert X_clean.shape == (n_genes, X_log.shape[1]), f"Error a les dimensions: {X_clean.shape} != ({n_genes}, {X_log.shape[1]})"
    assert np.allclose(X_clean.mean(axis=1), 0, atol=1e-7), "La mitjana dels gens no és propera a 0."
    assert np.allclose(X_clean.std(axis=1), 1, atol=1e-7), "La desviació estàndard dels gens no és propera a 1."
    assert not np.isnan(X_clean).any(), "S'han trobat valors NaN a X_clean."

    return X_clean, top_gene_indices

def jerarquic_pacients(X_clean, y, metodes=("single", "complete", "average"), k=2):

    """
    Clustering jeràrquic dels pacients amb distància de correlació (1 - r) i
    diversos criteris d'enllaç. Talla cada arbre en k grups i calcula l'ARI contra
    el diagnòstic real (només per validar, no per triar).

    --- Paràmetres:
        X_clean : np.ndarray
                  Matriu (gens x mostres) estandarditzada.
        y : np.ndarray
            Etiquetes reals (0 = ALL, 1 = AML).
        metodes : tuple
                  Criteris d'enllaç a comparar.
        k : int
            Nombre de grups en què es talla cada arbre.

    --- Retorna:
        Zs : dict
             Diccionari {mètode: matriu d'enllaç Z}.
        aris : dict
               Diccionari {mètode: ARI}.
    """
    dist = pdist(X_clean.T, metric="correlation")  # 72 pacients -> 2556 parells
    Zs, aris = {}, {}

    print("\n" + "=" * 50)
    print(f"{'Mètode':<10} | {'Mides dels grups':<18} | {'ARI (vs ALL/AML)':<10}")
    print("-" * 50)
    for m in metodes:
        Zs[m] = linkage(dist, method=m)
        assert Zs[m].shape == (X_clean.shape[1] - 1, 4), f"Forma incorrecta de Z ({m}): {Zs[m].shape}"
        labels = fcluster(Zs[m], t=k, criterion="maxclust")
        aris[m] = adjusted_rand_score(y, labels)
        print(f"{m:<10} | {str(np.bincount(labels)[1:].tolist()):<18} | {aris[m]:.4f}")
    print("=" * 50)
    return Zs, aris

def plot_dendrograma_pacients(Z, y, method="average"):

    """
    Dibuixa i exporta el dendrograma dels pacients amb etiquetes ALL/AML.

    --- Paràmetres:
        Z : np.ndarray
            Matriu d'enllaç obtinguda amb linkage.
        y : np.ndarray
            Etiquetes binàries de pacients (0 = ALL, 1 = AML).
        method : str
                 Nom del mètode utilitzat per al títol de la figura.
    """
    etiquetes = [f"{'ALL' if v == 0 else 'AML'}_{i}" for i, v in enumerate(y)]
    cut = (Z[-1, 2] + Z[-2, 2]) / 2  # altura que dona exactament 2 clústers

    fig, ax = plt.subplots(figsize=(14, 6))
    dendrogram(Z, labels=etiquetes, leaf_rotation=90, leaf_font_size=9,
               color_threshold=cut, ax=ax)
    ax.axhline(cut, color="gray", linestyle="--", label="Tall per k=2")
    for lbl in ax.get_xmajorticklabels():  # ALL = blau, AML = vermell
        lbl.set_color("dodgerblue" if lbl.get_text().startswith("ALL") else "crimson")

    ax.set_title(f"Dendrograma de Pacients - Enllaç {method.capitalize()} (k=2)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Pacients (Mostres)", fontsize=11)
    ax.set_ylabel("Distància d'unió", fontsize=11)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"dendrograma_pacients_{method}.pdf", bbox_inches="tight")
    plt.show()

def plot_corba_k(ax, ks, valors, ylabel, titol, best_k=None, color="navy", marker="o"):
    """
    Dibuixa una corba mètrica-vs-k i, si es dona, marca el k òptim.

    --- Paràmetres:
        ax : matplotlib.axes.Axes
        ks : list. Valors de k.
        valors : list. Valor de la mètrica per a cada k.
        ylabel, titol : str. Textos del gràfic.
        best_k : int o None. Si es dona, es marca amb una línia vertical.
        color, marker : estil de la línia.
    """
    ax.plot(ks, valors, marker=marker, color=color, linewidth=2)
    if best_k is not None:
        ax.axvline(best_k, color="firebrick", linestyle="--", label=f"Òptim (k={best_k})")
        ax.legend()
    ax.set_title(titol, fontsize=11, fontweight="bold")
    ax.set(xlabel="Nombre de clústers (k)", ylabel=ylabel)
    ax.grid(True, linestyle="--", alpha=0.6)

def kmeans_pacients(X_clean, y, k_range=range(2, 9)):

    """
    Ajusta K-Means per a diferents valors de k sobre les mostres de pacients (X_clean.T),
    calcula la inèrcia i el coeficient de silueta, i avalua l'ARI per a k=2.

    --- Paràmetres:
        X_clean : np.ndarray
                  Matriu de dimensions (gens x mostres) estandarditzada.
        y : np.ndarray
            Etiquetes reals dels pacients (0 = ALL, 1 = AML).
        k_range : range o list
                  Rang de valors de k a avaluar.

    --- Retorna:
        ari_k2 : float
                 Adjusted Rand Index per a k=2 contra les classes reals.
        best_k : int
                 Valor de k que maximitza el coeficient de silueta.
    """
    dades = X_clean.T  # 72 pacients x 500 gens
    k_values = list(k_range)
    assert 2 in k_values, "k_range ha d'incloure k=2 (per calcular l'ARI)"
    inercies, silhouettes, labels_per_k = [], [], {}
    for k in k_values:
        km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(dades)
        labels_per_k[k] = km.labels_
        inercies.append(km.inertia_)
        silhouettes.append(silhouette_score(dades, km.labels_))
    ari_k2 = adjusted_rand_score(y, labels_per_k[2])
    best_k = k_values[int(np.argmax(silhouettes))]
    assert -1.0 <= ari_k2 <= 1.0, f"ARI fora de rang: {ari_k2}"

    print("\n" + "=" * 55)
    print(f"{'k':<5} | {'Inèrcia':<15} | {'Silhouette':<15}")
    print("-" * 55)
    for k, ine, sil in zip(k_values, inercies, silhouettes):
        print(f"{k:<5} | {ine:<15.2f} | {sil:<15.4f}")
    print("-" * 55)
    print(f"K-Means (k=2) -> ARI contra ALL/AML: {ari_k2:.4f}")
    print("=" * 55)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    plot_corba_k(axes[0], k_values, inercies, "Inèrcia (WCSS)",
                 "Mètode del Colze (Inèrcia)", color="steelblue")
    plot_corba_k(axes[1], k_values, silhouettes, "Coeficient de Silhouette",
                 "Avaluació Silhouette", best_k, "darkorange", "s")
    plt.tight_layout()
    plt.savefig("kmeans_pacients_colze_silhouette.pdf", bbox_inches="tight")
    plt.show()
    return ari_k2, best_k

def moduls_gens(X_clean, k_range=range(2, 11)):

    """
    Calcula els mòduls de gens co-expressats mitjançant clustering jeràrquic
    amb enllaç average i distància de correlació, triant el k òptim amb Silhouette.

    --- Paràmetres:
        X_clean : np.ndarray
                  Matriu de dimensions (gens x mostres) estandarditzada (500 x 72).
        k_range : range o list
                  Rang de mòduls (k) a testejar.

    --- Retorna:
        Z_gens : np.ndarray
                 Matriu d'enllaç dels 500 gens (499 x 4).
        best_k_gens : int
                      Nombre de mòduls de gens òptim segons Silhouette.
        gene_labels : np.ndarray
                      Etiqueta de mòdul per a cadascun dels 500 gens.
    """
    dist_corr = pdist(X_clean, metric="correlation")
    Z_gens = linkage(dist_corr, method="average")
    assert Z_gens.shape == (X_clean.shape[0] - 1, 4), f"Forma incorrecta de Z_gens: {Z_gens.shape}"
    dist_mat = squareform(dist_corr)  # converteix el vector 1D en matriu quadrada
    k_values = list(k_range)
    silhouettes = []

    print("\n" + "=" * 60)
    print(f"{'Mòduls (k)':<12} | {'Silhouette':<12} | Mides dels mòduls")
    print("-" * 60)
    for k in k_values:
        labels = fcluster(Z_gens, t=k, criterion="maxclust")
        silhouettes.append(silhouette_score(dist_mat, labels, metric="precomputed"))
        print(f"{k:<12} | {silhouettes[-1]:<12.4f} | {np.bincount(labels)[1:].tolist()}")

    best_k_gens = k_values[int(np.argmax(silhouettes))]
    gene_labels = fcluster(Z_gens, t=best_k_gens, criterion="maxclust")
    print("-" * 60)
    print(f"Nombre òptim de mòduls gènics: k = {best_k_gens} (Silhouette = {max(silhouettes):.4f})")
    print("=" * 60)

    return Z_gens, best_k_gens, gene_labels

def plot_clustermap(X_clean, y, Z_gens, Z_pacients, gene_labels):
    """
    Genera i exporta dos mapes de calor de la mateixa matriu X_clean:
      1. SENSE clustering: gens i pacients en l'ordre original (mapa de calor brut).
      2. AMB clustering: files i columnes reordenades pels dendrogrames.
    Les dues figures porten una barra de colors amb el diagnòstic (ALL/AML) i una
    altra amb el mòdul de cada gen, per veure com el clustering agrupa els colors.

    --- Paràmetres:
        X_clean : np.ndarray
                  Matriu (gens x mostres) estandarditzada.
        y : np.ndarray
            Etiquetes de pacients (0 = ALL, 1 = AML).
        Z_gens : np.ndarray
                 Dendrograma calculat per als gens.
        Z_pacients : np.ndarray
                     Dendrograma calculat per als pacients.
        gene_labels : np.ndarray
                      Mòdul assignat a cadascun dels gens.
    """
    df_expr = pd.DataFrame(X_clean)
    cols_pac = pd.Series(np.where(y == 0, "dodgerblue", "crimson"), name="Subtipus")
    paleta = sns.color_palette("Set2", gene_labels.max())
    cols_gens = pd.Series([paleta[l - 1] for l in gene_labels], name="Mòdul")
    handles = [mpatches.Patch(color="dodgerblue", label="ALL"),
               mpatches.Patch(color="crimson", label="AML")]
    handles += [mpatches.Patch(color=paleta[i], label=f"Mòdul {i + 1}")
                for i in range(gene_labels.max())]

    # (títol, fitxer, opcions de clustering): la resta de paràmetres és comuna
    figures = [
        ("Mapa de calor SENSE clustering (ordre original)", "heatmap_sense_clustering.pdf",
         dict(row_cluster=False, col_cluster=False)),
        ("Clustermap AMB clustering jeràrquic (ordenat pels dendrogrames)", "clustermap_expressio.pdf",
         dict(row_linkage=Z_gens, col_linkage=Z_pacients)),
    ]
    for titol, fitxer, opcions in figures:
        g = sns.clustermap(
            df_expr, **opcions,
            row_colors=cols_gens, col_colors=cols_pac,
            cmap="vlag", center=0, vmin=-3, vmax=3,
            figsize=(11, 10), dendrogram_ratio=(0.12, 0.12), colors_ratio=0.025,
            cbar_pos=(0.02, 0.90, 0.10, 0.015),
            cbar_kws={"orientation": "horizontal", "label": "Z-score"},
            xticklabels=False, yticklabels=False,
        )
        g.ax_heatmap.set_xlabel("Pacients")
        g.ax_heatmap.set_ylabel("500 gens més variables")
        g.ax_heatmap.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1.0),
                            frameon=False, fontsize=9)
        g.figure.suptitle(titol, fontsize=12, fontweight="bold", y=1.0)
        g.savefig(fitxer, bbox_inches="tight")
        plt.show()
# %% MAIN

if __name__ == "__main__":

    # 1. Càrrega i preparació de les dades
    X, y = load_data()

    # 2. Inspecció ràpida de control i estadístiques de la matriu
    print("\nDimensions de X (gens, mostres):", X.shape)
    etiquetes, recomptes = np.unique(y, return_counts=True)
    print("Etiquetes trobades:", etiquetes)
    print("Quantitat de cadascuna:", recomptes.tolist())
    estad_matriu(X)

    # 3. Preprocessament logarítmic (retall + log2(x+1)) i % de valors retallats
    X_log = preprocess_log(X)
    print(f"Valors retallats: {(X < TERRA).mean():.1%} al terra, {(X > SOSTRE).mean():.1%} al sostre")

    # 4. Histogrames abans/després del log (Figura 1 de l'informe)
    plot_histograms(X, X_log)

    # 5. Els gens més variables + z-score per gen
    X_clean, top_gene_indices = filtre_i_estandar(X_log, n_genes=N_GENES)
    print(f"\nMatriu X_clean generada correctament amb dimensions: {X_clean.shape}")
    print(f"Variància mínima dels gens conservats: {np.var(X_log, axis=1)[top_gene_indices].min():.2f}")

    # 6. Clustering jeràrquic dels pacients (distància de correlació) i ARI (Taula 1)
    Zs, aris = jerarquic_pacients(X_clean, y)

    # 7. Dendrograma amb enllaç average (opció estàndard en expressió gènica, Eisen 1998) (Figura 2)
    plot_dendrograma_pacients(Zs["average"], y, method="average")

    # 8. K-Means: colze + silhouette + ARI (Figura 3)
    ari_kmeans, best_k_kmeans = kmeans_pacients(X_clean, y, k_range=range(2, 9))

    # 9. Mòduls de gens co-expressats (Taula 2)
    Z_gens, best_k_gens, gene_labels = moduls_gens(X_clean, k_range=range(2, 11))

    # 10. Mapes de calor: brut i ordenat pels dendrogrames (Figura 4)
    plot_clustermap(X_clean, y, Z_gens, Zs["average"], gene_labels)

# %% POTENCIAL CONTINUACIÓ DEL PROJECTE (no implementat)
# - Detecció de pacients atípics amb Isolation Forest (sobre components PCA dels pacients).
# - Comparació amb DBSCAN i Gaussian Mixture Models (GMM)
# - Anàlisi de sensibilitat: repetir el pipeline amb n_genes = 100, 500, 1000.
# - Interpretació biològica dels mòduls de gens (anotació dels gens de cada mòdul).
