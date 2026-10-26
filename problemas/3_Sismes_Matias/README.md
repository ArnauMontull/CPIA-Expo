# Anàlisi de Dades Sismològiques mitjançant Clustering K-Means i Detecció d'Anomalies

Aquest projecte implementa un sistema d'aprenentatge no supervisat per al processament, classificació i detecció d'anomalies en esdeveniments sísmics globals. Mitjançant l'aplicació de l'algorisme K-Means i tècniques de proximitat per k-Veïns Més Propers (k-NN), el sistema permet categoritzar terratrèmols segons la seva profunditat, magnitud i ubicació geogràfica.

---

## 1\. Objectiu i Abast del Projecte

El projecte aborda dues tasques analítiques principals:

* **Classificació Tectònica (K-Means):** Segmentació automàtica dels esdeveniments sísmics en 3 clústers principals segons les seves propietats físiques i espacials per identificar patrons de subducció i activitat en les vores de les plaques.  
* **Detecció d'Anomalies (k-NN):** Identificació d'esdeveniments d'alta magnitud o profunditat excepcional mitjançant el càlcul de distàncies en l'espai de característiques normalitzat.

---

## 2\. Estructura del Repositori

| Fitxer | Descripció i Funció |
| :---- | :---- |
| `earthquakes.csv` | Conjunt de dades sismològiques d'entrada (magnitud, profunditat, latitud, longitud). |
| `problema_matias.py` | Script principal d'execució: neteja de dades, clustering K-Means i generació de gràfiques. |
| `validacio.py` | Mòdul de validació matemàtica (Inèrcia, Silueta, ARI i generació del mapa geogràfic). |
| `requirements.txt` | Llista de dependències i versions de biblioteques necessàries. |
| `README.md` | Documentació tècnica del projecte. |

---

## 3\. Pipeline Metodològic

1. **Preprocessament de Dades:** Carrega de dades, reordenació de columnes i filtratge de registres incomplets o invàlids.  
2. **Normalització Z-Score:** Estandardització de les 4 variables (magnitud, profunditat, latitud i longitud) per tal que tinguin mitjana zero i desviació estàndard unitària.  
3. **Clustering K-Means:** Assignació dels sismes en k=3 clústers físics.  
4. **Detecció d'Anomalies:** Càlcul de la distància euclidiana mitjana als k=5 veïns més propers per identificar els punts més aïllats del conjunt.

---

## 4\. Instruccions d'Execució

### Instal·lació de dependències

```sh
pip install -r requirements.txt
```

### Execució de l'anàlisi principal

```sh
python problema_matias.py
```

### Execució de la validació del model

```sh
python validacio.py
```

---

## 5\. Mètrics de Validació i Avaluació

* **Mètode del Colze (WCSS):** Avaluació de la reducció de la variància intra-clúster per confirmar el nombre òptim de grups (K).  
* **Coeficient de Silueta (Silhouette Score):** Avaluació de la cohesió interna dels clústers i la seva separació respecte als grups veïns.  
* **Adjusted Rand Index (ARI):** Comprovació de l'estabilitat i consistència de l'algorisme davant diferents llavors d'inicialització.