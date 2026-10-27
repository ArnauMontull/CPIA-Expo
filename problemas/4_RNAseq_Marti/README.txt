CLUSTERING JERÀRQUIC I K-MEANS EN DADES D'EXPRESSIÓ GÈNICA (leucèmia ALL vs AML)

QUÈ FA
Agrupa 72 pacients i els seus gens SENSE usar el diagnòstic (ALL/AML). Al final
compara els grups trobats amb el diagnòstic real per veure si coincideixen i avaluar COM de
bons són els diferents models.

QUÈ CAL
- Python (crea un entorn propi) amb: numpy, pandas, scipy, scikit-learn, matplotlib, seaborn, pytest (veure requirements.txt)
- Internet la primera vegada (el codi descarrega el dataset de Golub d'OpenML; no cal cap fitxer de dades)

COM EXECUTAR-HO
1. Obre el terminal de Miniconda (Anaconda) i entra a la carpeta del projecte. Executa les següents comandes:
       conda create -n transcripto python=3.12 -y
       conda activate transcripto
       cd carpeta_del_projecte
2. Instal·la les llibreries (només un cop):
       pip install -r requirements.txt
3. Executa el programa:
       python clustering_marti.py (per seguir el codi s'han d'anar tancant les figures)

QUÈ S'OBTÉ
- A la consola: taules de resultats (ARI dels enllaços, K-Means, mòduls de gens).
- A la carpeta: 5 figures en PDF (hist_log, dendrograma_pacients_average,
  kmeans_pacients_colze_silhouette, heatmap_sense_clustering, clustermap_expressio).
- Les figures i els números de l'informe surten d'aquesta mateixa execució.
- Els paràmetres principals (retall, nombre de gens, llavor) es canvien a la part de dalt del codi.

PROVES AUTOMÀTIQUES (no necessiten Internet)
       python -m pytest -v
  Comproven amb dades inventades que les funcions funcionen i que fallen quan han de fallar.

RESULTATS ESPERATS (amb les dades reals de Golub)
  ARI (k=2):  single -0.0129 | complete 0.7868 | average 0.6900
  K-Means (k=2): silhouette 0.1352, ARI 0.8897
  Mòduls de gens: k = 2, mides [178, 322], silhouette 0.1812
