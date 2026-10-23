"""Prepara los datos del dashboard del globo (presentacion/sismos_nucleares.html).

No toca el script de Arnau: lo ejecuta tal cual (problemas/2_Nuclear/data_extract.py), recoge su DataFrame
`df` (DBSCAN 50 km, min_samples=3) sobre el catálogo completo datos/sismos_usgs_M45_1951_2025.csv (M>=4.5, 1951-2025, sin filtrar tipo en la consulta) y calcula aparte: la rejilla eps x min_samples, la comparación con
Isolation Forest y los clusters sospechosos. Escribe presentacion/datos_globo.json.
Ejecutar desde CPIA_Expo/:  .venv/Scripts/python.exe presentacion/generar_datos_globo.py
"""
import contextlib, io, json, runpy, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ.parent.parent.parent / "scripts"))
try:
    from progreso import marcar, terminar
except Exception:  # sin ventana de progreso
    marcar = lambda *a, **k: None
    terminar = lambda *a, **k: None

# El script de Arnau lee 'datos/sismos_usgs.csv' (ruta relativa). Se ejecuta en una carpeta temporal donde ese
# archivo es el catálogo unido (1951-2025), sin modificar ni el script ni el CSV original.
import os, shutil, tempfile
UNIDO = RAIZ / "datos" / "sismos_usgs_M45_1951_2025.csv"
with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "datos").mkdir()
    shutil.copy(UNIDO if UNIDO.exists() else RAIZ / "datos" / "sismos_usgs.csv", Path(tmp) / "datos" / "sismos_usgs.csv")
    cwd = os.getcwd(); os.chdir(tmp)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            g = runpy.run_path(str(RAIZ / "problemas" / "2_Nuclear" / "data_extract.py"))
    finally:
        os.chdir(cwd)
df, coords = g["df"], g["coords_rad"]
real = (df["tipo"] == "nuclear explosion").to_numpy()
R = 6371

def evaluar(labels, umbral=5.0, minimo=-1e9):
    sub = df.assign(cl=labels)
    med = sub[sub.cl >= 0].groupby("cl")["depth"].median()
    sosp = med[(med >= minimo) & (med < umbral)].index
    det = sub.cl.isin(sosp).to_numpy()
    tp, fp = int((det & real).sum()), int((det & ~real).sum())
    return dict(prec=tp / max(tp + fp, 1), rec=tp / real.sum(), tp=tp, fp=fp, fn=int(real.sum()) - tp,
                n=int(labels.max() + 1), sosp=len(sosp))

# 1) rejilla eps x min_samples
EPS, MS = [10, 25, 50, 100, 200], [3, 5, 10]   # el dashboard abre con eps=10, 3 vecinos y profundidad < 1 km
grid, k = [], 0
for e in EPS:
    for m in MS:
        marcar("globo", k, len(EPS) * len(MS) + 1, f"DBSCAN eps={e} km, min_samples={m}")
        lb = DBSCAN(eps=e / R, min_samples=m, metric="haversine").fit_predict(coords)
        r, r5 = evaluar(lb, 1.0, -0.1), evaluar(lb, 5.0, -0.1)   # rango de la mediana: [-0,1, 1) km y [-0,1, 5) km
        grid.append(dict(eps=e, ms=m, prec=round(r["prec"], 4), rec=round(r["rec"], 4), tp=r["tp"], fp=r["fp"], n=r["n"],
                         prec5=round(r5["prec"], 4), rec5=round(r5["rec"], 4), tp5=r5["tp"], fp5=r5["fp"]))
        k += 1

# 2) clusters del script de Arnau (50 km, 3)
lab = df["cluster"].to_numpy()
base = evaluar(lab)
med = df[df.cluster >= 0].groupby("cluster")["depth"].median()
sosp = set(med[med < 5.0].index)
clase = np.where(lab < 0, 0, np.where(np.isin(lab, list(sosp)), 2, 1)).astype(int)   # 0 ruido, 1 normal, 2 sospechoso
tabla = []
for c in sosp:
    s = df[df.cluster == c]
    tabla.append(dict(id=int(c), lugar=str(s["place"].mode().iat[0]), expl=int((s.tipo == "nuclear explosion").sum()),
                      terr=int((s.tipo != "nuclear explosion").sum()), prof=round(float(s["depth"].median()), 1)))
tabla.sort(key=lambda t: -(t["expl"] + t["terr"]))

# 3) Isolation Forest con las mismas variables (posición 3D, profundidad, magnitud)
marcar("globo", k, len(EPS) * len(MS) + 1, "Isolation Forest")
la, lo = coords[:, 0], coords[:, 1]
X = StandardScaler().fit_transform(np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la), df.depth, df.mag])
an = IsolationForest(n_estimators=200, contamination=real.mean(), random_state=0).fit_predict(X) == -1
iso_tp = int((an & real).sum())
iso = dict(prec=iso_tp / an.sum(), rec=iso_tp / real.sum())

# 4) histograma de profundidad
BINS = [-1e9, 1, 5, 10, 20, 35, 70, 150, 1e9]
h = lambda m: (np.histogram(df.depth[m], bins=BINS)[0] / m.sum()).round(4).tolist()

out = dict(
    lat=(df.latitude * 100).round().astype(int).tolist(), lon=(df.longitude * 100).round().astype(int).tolist(),
    dep=df.depth.round(1).tolist(), mag=df.mag.round(1).tolist(),
    nuc=real.astype(int).tolist(), cl=clase.tolist(), cid=lab.tolist(),
    day=(pd.to_datetime(df.time, utc=True) - pd.Timestamp('1970-01-01', tz='UTC')).dt.days.tolist(),
    base=dict(eps=g["radio_km"], ms=g["min_samples"], **{x: round(base[x], 4) for x in ("prec", "rec")},
              tp=base["tp"], fp=base["fp"], fn=base["fn"], n=base["n"], sosp=base["sosp"], ruido=int((lab < 0).sum())),
    grid=grid, tabla=tabla, iso={x: round(v, 4) for x, v in iso.items()},
    hist=dict(terr=h(~real), expl=h(real)), n_expl=int(real.sum()), n_terr=int((~real).sum()),
)
(RAIZ / "presentacion" / "datos_globo.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
terminar("globo")
print("ok", len(df), "puntos;", "base", out["base"], "iso", out["iso"])
for r in grid: print(r)
