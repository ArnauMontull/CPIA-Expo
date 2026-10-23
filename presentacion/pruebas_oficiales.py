"""Eventos que el USGS tiene como `earthquake` dentro del polígono de pruebas de Nevada y que coinciden con una prueba
nuclear de la lista oficial DOE/NV-209 Rev. 16 (NNSA Nevada, 2015; https://www.osti.gov/biblio/1351809).
Los índices son filas del mismo DataFrame que usa el dashboard (dropna + mag >= 4.5 sobre sismos_usgs_M45_1951_2025.csv).
Escribe presentacion/datos_pruebas.json.   Ejecutar desde CPIA_Expo/: .venv/Scripts/python.exe presentacion/pruebas_oficiales.py"""
import json
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
# (inicio de la hora USGS, prueba oficial, hora oficial UTC, confianza del cruce, nota)
PRUEBAS = [
    ("1975-02-28T15:15:00", "Cementback", "15:15:00.09", "media", "Misma hora y lugar; la fecha de la fila del PDF está desplazada."),
    ("1981-11-11T20:00:00", "Tilci", "no legible en el PDF", "baja", "Misma fecha y misma longitud; la hora oficial no se pudo leer."),
    ("1982-07-29T20:05:00", "Monterey", "20:05:00.08", "media", "Hora y coordenadas coinciden; el PDF mezcla columnas."),
    ("1983-03-26T20:20:00", "Cabra", "no legible en el PDF", "baja", "Misma fecha y zona (Pahute Mesa); la hora oficial no se pudo leer."),
    ("1985-04-02T20:00:00", "Hermosa", "20:00:00.09", "alta", "Fecha, hora (al centésimo) y lugar coinciden."),
    ("1986-06-25T20:27:45", "Pozo U20aq", "20:27:45.09", "alta", "Fecha, hora y lugar coinciden. El nombre no se leyó en el PDF."),
    ("1988-10-13T16:18:07", "Dalhart", "14:00:00.08", "baja", "Mismo lugar y día, pero 2 h 18 min después de la hora oficial."),
    ("1988-12-10T20:30:00", "Misty Echo", "20:30:00.06", "alta", "Fecha, hora (al centésimo) y lugar coinciden."),
    ("1989-02-10T20:06:00", "Pozo U7ca", "20:06:00.06", "media", "Hora y lugar coinciden; el PDF da la fecha como 24/02, el USGS 10/02."),
    ("1990-03-10T16:00:00", "Metropolis", "16:00:00.08", "alta", "Fecha, hora (al centésimo) y lugar coinciden."),
]
d = pd.read_csv(RAIZ / "datos" / "sismos_usgs_M45_1951_2025.csv").dropna(subset=["latitude", "longitude", "depth", "mag"])
d = d[d["mag"] >= 4.5].reset_index(drop=True)
out = []
for t0, nombre, hora, conf, nota in PRUEBAS:
    m = d[(d["tipo"] == "earthquake") & d["time"].str.startswith(t0) & d["latitude"].between(36, 38.2) & d["longitude"].between(-117.5, -115)]
    assert len(m) == 1, (t0, len(m))
    i = int(m.index[0])
    out.append(dict(i=i, nombre=nombre, hora=hora, conf=conf, nota=nota))
(RAIZ / "presentacion" / "datos_pruebas.json").write_text(json.dumps(dict(n=len(d), pruebas=out), ensure_ascii=False), encoding="utf-8")
print("ok", len(d), [o["i"] for o in out])
