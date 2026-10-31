"""Construye presentacion/animacion_bombas.html: globo 3D animado con las explosiones nucleares del USGS (1951-2025).

Lee datos/sismos_usgs.csv (filas con tipo == 'nuclear explosion' y magnitud), los contornos de países de
presentacion/vendor/countries-50m.json (world-atlas 2.0.2, Natural Earth) y mete en un único HTML (funciona sin
internet) three.js r128 + el bloom de sus ejemplos, los datos y plantilla_animacion_bombas.html.
Ejecutar desde CPIA_Expo/:  .venv/Scripts/python.exe presentacion/construir_animacion_bombas.py
"""
import json
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
VENDOR = AQUI / "vendor"
LIBS = ["three.min.js", "CopyShader.js", "LuminosityHighPassShader.js", "EffectComposer.js", "RenderPass.js",
        "ShaderPass.js", "UnrealBloomPass.js"]

PAISES = ["EE. UU.", "URSS", "Francia", "China", "India", "Corea del Norte"]


def clasificar(fila):
    """(país, lugar de pruebas) a partir del texto 'place' del USGS y las coordenadas."""
    p, lat, lon = fila.place, fila.latitude, fila.longitude
    if "Nevada" in p or p.endswith(", NV"):
        return 0, "Nevada"
    if "Colorado" in p:
        return 0, "Rio Blanco (Colorado)"
    if "Kazakhstan" in p:
        return 1, "Semipalatinsk" if 49 < lat < 51.5 and 77 < lon < 80 else "Kazajistán"
    if "Russia" in p:
        return 1, "Nueva Zembla" if lat > 70 else "Rusia"
    if "French Polynesia" in p:
        return 2, "Mururoa / Fangataufa"
    if "China" in p:
        return 3, "Lop Nur"
    if "India" in p:
        return 4, "Pokhran"
    if "North Korea" in p:
        return 5, "Punggye-ri"
    raise ValueError(f"lugar sin clasificar: {p}")


def eventos():
    d = pd.read_csv(RAIZ / "datos" / "sismos_usgs.csv",
                    usecols=["time", "latitude", "longitude", "depth", "mag", "magType", "place", "tipo"])
    e = d[(d.tipo == "nuclear explosion") & d.mag.notna()].copy()
    t = pd.to_datetime(e.time, utc=True)
    e["t"] = t.dt.year + (t.dt.dayofyear - 1 + t.dt.hour / 24) / (365 + t.dt.is_leap_year)
    e["fecha"] = t.dt.strftime("%Y-%m-%d")
    e[["pais", "sitio"]] = e.apply(lambda f: pd.Series(clasificar(f)), axis=1)
    e = e.sort_values("t")
    sitios = sorted(e.sitio.unique())
    return e, sitios, dict(
        t=[round(v, 5) for v in e.t], lat=[round(v, 3) for v in e.latitude], lon=[round(v, 3) for v in e.longitude],
        mag=[round(v, 2) for v in e.mag], mt=list(e.magType.fillna("")), prof=[round(v, 1) for v in e.depth.fillna(0)],
        pais=[int(v) for v in e.pais], sitio=[sitios.index(s) for s in e.sitio], fecha=list(e.fecha))


def etiquetas(e):
    """Una etiqueta por polígono de pruebas principal, en la mediana de sus epicentros."""
    out = []
    for s, g in e.groupby("sitio"):
        if s in ("Rusia", "Kazajistán", "Rio Blanco (Colorado)"):   # sueltos o pegados a Nevada
            continue
        out.append(dict(nombre=s, lat=round(g.latitude.median(), 2), lon=round(g.longitude.median(), 2),
                        pais=int(g.pais.iloc[0]), n=len(g)))
    return out


def contornos():
    """Decodifica el TopoJSON: arcos (lon/lat simplificados), polígonos como índices de arco, y si cada arco es costa."""
    topo = json.loads((VENDOR / "countries-50m.json").read_text(encoding="utf-8"))
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcos = []
    for arco in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arco:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        simp = [pts[0]]
        for p in pts[1:-1]:
            if abs(p[0] - simp[-1][0]) + abs(p[1] - simp[-1][1]) > 0.06:
                simp.append(p)
        if len(pts) > 1:
            simp.append(pts[-1])
        arcos.append([round(c, 2) for p in simp for c in p])
    usos = [0] * len(arcos)
    poligonos = []
    for g in topo["objects"]["countries"]["geometries"]:
        polys = g.get("arcs", [])
        if g["type"] == "Polygon":
            polys = [polys]
        for poly in polys:
            poligonos.append(poly)
            for anillo in poly:
                for a in anillo:
                    usos[a if a >= 0 else ~a] += 1
    return dict(arcos=arcos, poligonos=poligonos, costa=[1 if u == 1 else 0 for u in usos])


def main():
    e, sitios, ev = eventos()
    datos = dict(ev=ev, sitios=sitios, paises=PAISES, etiquetas=etiquetas(e), mundo=contornos())
    libs = "\n".join(f"<script>\n{(VENDOR / n).read_text(encoding='utf-8')}\n</script>" for n in LIBS)
    html = (AQUI / "plantilla_animacion_bombas.html").read_text(encoding="utf-8")
    html = html.replace("<!--LIBS-->", libs).replace("/*DATOS*/null", json.dumps(datos, separators=(",", ":"), ensure_ascii=False))
    salida = AQUI / "animacion_bombas.html"
    salida.write_text(html, encoding="utf-8")
    print(f"{len(e)} explosiones, {e.t.min():.1f}-{e.t.max():.1f}; {salida} ({salida.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
