# Classificació No Supervisada de Materials Elèctrics mitjançant DBSCAN

**Autor:** Uriel Martínez Rosa  
**Titulació:** Grau en Enginyeria Física  
**Assignatura:** Computer Programming and Its Applications (CPIA)  
**Institució:** Escola Tècnica Superior d'Enginyeria de Telecomunicació de Barcelona (ETSETB), Universitat Politècnica de Catalunya (UPC)  
**Equip CPIA:** Arnau Montull Bainad, Matías Stein Niell, Martí Canut Sumarroca i Uriel Martínez Rosa  
**Data:** Curs Acadèmic 2026–2027  

---

## 1. Descripció del Problema Físic

Aquest mòdul aborda la **classificació no supervisada** (*unsupervised clustering*) de les tres grans fases de conducció de la matèria condensada:
1. **Conductors (Metalls):** Mar de Fermi lliure ($E_g = 0$), resistivitat ultrabaixa ($\log_{10}\rho \approx -8$ a $-6$) i coeficient tèrmic estrictament positiu ($\alpha > 0$) per dispersió creixent electró-fonó.
2. **Semiconductors:** Banda prohibida moderada ($E_g \approx 0.2$ a $2.0\text{ eV}$), resistivitat intermèdia ($\log_{10}\rho \approx -2$ a $+4$) i coeficient fortament negatiu ($\alpha < 0$) per excitació tèrmica exponencial de portadors.
3. **Aïllants (Dielèctrics):** Bandgap colossal ($E_g > 5\text{ eV}$), conducció pràcticament nul·la ($\log_{10}\rho \ge 11$) i coeficient tèrmic nul ($\alpha \approx 0\text{ K}^{-1}$).

Mitjançant l'algorisme espacial basat en densitat **DBSCAN** sobre l'espai bidimensional estandarditzat $(\log_{10}\rho_{300\mathrm{K}}, \alpha)$, el sistema descobreix de forma autònoma les tres fases quàntiques sense cap etiqueta prèvia durant el modelatge.

---

## 2. Estructura de Fitxers

```
CPIA - Uriel/
├── README.md                           # Instruccions completes de reproducció i context científic
├── requirements.txt                    # Dependències de Python amb versions fitades
├── descargar_materiales.py             # Script de descàrrega i compilació del dataset de 57 materials reals
├── materiales_uriel.py                 # Pipeline principal: càrrega, Z-score, DBSCAN i generació de figures
├── test_materiales.py                  # Bateria d'11 proves automàtiques (casos normals, límit i d'error)
├── informe_materiales_uriel.pdf        # Informe complet del treball en format PDF
├── informe_materiales_uriel.tex        # Codi font LaTeX complet de l'informe per a Overleaf
├── presentacion_materiales_uriel.pptx  # Presentació oficial de diapositives de l'exposició
├── datos/
│   └── materiales_electricos.csv       # Dataset oficial amb 57 materials experimentals contrastats
└── figuras/
    ├── materiales_antes_clustering.png        # Distribució inicial en brut a l'espai físic (Fig. 1)
    ├── clusters_materiales_dbscan.png         # Clústers descoberts per connectivitat de densitat (Fig. 3)
    ├── comparativa_abans_despres_dbscan.png   # Panell comparatiu Abans vs. Després (Fig. 2)
    └── esquema_bandas_materiales.png          # Esquema quàntic de bandes electròniques
```

---

## 3. Instal·lació de l'Entorn

Es recomana utilitzar Python 3.10 o superior (verificat en Python 3.12).

1. **Crear l'entorn virtual:**
   ```bash
   python -m venv .venv
   ```

2. **Activar l'entorn virtual:**
   - A Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - A Linux / macOS (Bash):
     ```bash
     source .venv/bin/activate
     ```

3. **Instal·lar les dependències:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 4. Guia Pas a Pas d'Execució

### Pas 1: Generació del Dataset
Si es desitja re-descarregar i compilar les dades empíriques de referència (*CRC Handbook of Chemistry and Physics*, Kittel, Ashcroft & Mermin):
```bash
python descargar_materiales.py
```
*Nota:* El paquet ja inclou el fitxer `datos/materiales_electricos.csv`, de manera que aquest pas és opcional i no requereix connexió a Internet per a les fases posteriors.

### Pas 2: Execució del Model de Clustering i Figures
Executa el pipeline de preprocessament Z-Score, DBSCAN ($\varepsilon = 0.65$, $\text{min\_samples} = 3$), anàlisi de matriu de contingència i generació de les tres figures d'alta resolució (300 dpi):
```bash
python materiales_uriel.py
```

### Pas 3: Execució de les Proves Automàtiques
Per verificar el funcionament del codi davant de casos normals, situacions límit (columnes constants, $\varepsilon$ extrem) i gestió d'errors:
```bash
python test_materiales.py
```
o bé amb el mòdul estàndard:
```bash
python -m unittest -v test_materiales.py
```
Les 11 proves s'executen en $\approx 0.04\text{ s}$ i han de passar totes satisfactòriament (`OK`).

---

## 5. Resultats Experimentals Principals

- **Clústers descoberts autònomament per DBSCAN:** 3 clústers (sense imposar $K$ a priori).
- **Punts de soroll:** 0 de 57 materials.
- **Puresa de la classificació:**
  - **Conductors:** $100\,\%$ (35 de 35 metalls purs i aliatges al Clúster 0).
  - **Aïllants:** $100\,\%$ (10 de 10 dielèctrics al Clúster 1).
  - **Semiconductors:** $10$ de $12$ al Clúster 2. Els dos restants (grafit pirolític i antimoni) cauen al Clúster 0 pel seu caràcter semimetàl·lic documentat a $300\text{ K}$ ($\rho \sim 10^{-5}\ \Omega\cdot\text{m}$).

---

## 6. Referències Bibliogràfiques

1. **Ester, M., et al. (1996).** *A density-based algorithm for discovering clusters in large spatial databases with noise.* KDD-96, 226–231.
2. **Haynes, W. M. (Ed.). (2016).** *CRC Handbook of Chemistry and Physics* (97th ed.). CRC Press.
3. **Kittel, C. (2005).** *Introduction to Solid State Physics* (8th ed.). John Wiley & Sons.
4. **Schubert, E., et al. (2017).** *DBSCAN revisited, revisited: why and how you should (still) use DBSCAN.* ACM TODS, 42(3), 1–21.
5. **Pedregosa, F., et al. (2011).** *Scikit-learn: Machine Learning in Python.* JMLR, 12, 2825–2830.
