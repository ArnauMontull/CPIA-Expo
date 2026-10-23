"""Une plantilla_globo.html + datos_globo.json + dbscan_grid.js en un solo archivo: sismos_nucleares.html.
Los clusters del globo se calculan en el navegador (dbscan_grid.js), así que se descartan los de Python."""
import json
from pathlib import Path
aqui = Path(__file__).resolve().parent
datos = json.loads((aqui / "datos_globo.json").read_text(encoding="utf-8"))
for k in ("cl", "cid", "tabla"):
    datos.pop(k, None)
pr = json.loads((aqui / "datos_pruebas.json").read_text(encoding="utf-8"))
assert pr["n"] == len(datos["lat"]), "datos_pruebas.json no encaja con datos_globo.json: ejecuta pruebas_oficiales.py"
datos["pruebas"] = pr["pruebas"]
grid = (aqui / "dbscan_grid.js").read_text(encoding="utf-8").split("if(typeof module")[0]
html = (aqui / "plantilla_globo.html").read_text(encoding="utf-8")
html = html.replace("__GRID__", grid).replace("__DATA__", json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
(aqui / "sismos_nucleares.html").write_text(html, encoding="utf-8")
print("ok", len(html) // 1024, "KB")
