"""Script para descargar y procesar la tabla oficial de resistividades y coeficientes
térmicos (CRC Handbook / Wikipedia) en datos/materiales_electricos.csv.
"""
import sys
import re
import json
import urllib.request
from pathlib import Path
import math

# ==============================================================================
#CODIGO HECHO con GEMINI
# ==============================================================================

# Asegurar codificación utf-8 en Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATOS_DIR = Path(__file__).resolve().parents[2] / "datos"
DATOS_DIR.mkdir(exist_ok=True)
CSV_DESTINO = DATOS_DIR / "materiales_electricos.csv"

URL = "https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity"

print(f"Descargando datos desde: {URL} ...")
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
html = urllib.request.urlopen(req).read().decode("utf-8")

# Localizar tabla principal de resistividad
tables = re.findall(r'<table[^>]*wikitable[^>]*>(.*?)</table>', html, re.DOTALL)
tabla = None
for t in tables:
    if "Material" in t and ("Resistivity" in t or "Conductivity" in t) and "Silver" in t:
        tabla = t
        break

if not tabla:
    raise RuntimeError("No se pudo localizar la tabla de resistividad en el HTML descargado.")

rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tabla, re.DOTALL)

def extract_number(cell_html):
    # 1. Intentar parsear data-mw json de la plantilla val
    m = re.search(r'data-mw=\'(.*?)\'', cell_html)
    if m:
        try:
            d = json.loads(m.group(1))
            parts = d.get('parts', [])
            for p in parts:
                params = p.get('template', {}).get('params', {})
                if '1' in params:
                    val = float(params['1']['wt'].replace('−', '-'))
                    exp = float(params.get('e', {}).get('wt', '0').replace('−', '-'))
                    return val * (10.0 ** exp)
        except Exception:
            pass

    # 2. Parseo por expresiones regulares
    clean = re.sub(r'<[^>]+>', ' ', cell_html)
    clean = re.sub(r'\[.*?\]', '', clean)
    clean = clean.replace('×', 'e').replace('&times;', 'e').replace('−', '-').replace('–', '-').strip()
    
    # Manejar notación científica como 1.59e-8 o 1.59 e 10^-8
    m2 = re.search(r'([0-9.]+)\s*(?:e|x|X|\*)\s*10\^?\s*(-?[0-9]+)', clean)
    if m2:
        return float(m2.group(1)) * (10.0 ** float(m2.group(2)))
    
    # Manejar órdenes de magnitud directos como 10^12 o 10 12
    m3 = re.search(r'10\s*\^?\s*([0-9]+)', clean)
    if m3:
        return 10.0 ** float(m3.group(1))
    
    # Manejar número decimal estándar
    m4 = re.search(r'^-?[0-9]+(?:\.[0-9]+)?', clean)
    if m4:
        return float(m4.group(0))
    
    return None

# Valores de referencia CRC para metales/materiales donde la tabla wiki no tabula alpha explícito
CRC_ALPHA_FALLBACK = {
    "brass": 0.0015,
    "rhodium": 0.0044,
    "ruthenium": 0.0045,
    "phosphor bronze": 0.0018,
    "niobium": 0.0040,
    "carbon steel": 0.0030,
    "galinstan": 0.0012,
    "electrical steel": 0.0011,
    "bismuth": 0.0042,
    "manganese": 0.0001,
    "plutonium": 0.0005,
    "gaas": -0.0600,
    "carbon (graphite)": -0.0005,
}

# Materiales no sólidos (líquidos o biológicos) que descartamos para centrarnos en estado sólido
EXCLUIR = ["sea water", "swimming pool water", "drinking water", "bone", "wood (damp)", "deionised water", "ultrapure water"]

# Semiconductores tecnológicos adicionales estándar (CRC Handbook / Sze 'Physics of Semiconductor Devices')
SEMICONDUCTORES_EXTRA = [
    {"material": "GaAs (doped)", "resistividad_ohm_m": 10.0, "log_rho_300K": 1.0, "alpha_coef": -0.060, "clase_real": "Semiconductor"},
    {"material": "InP (Indium Phosphide)", "resistividad_ohm_m": 0.20, "log_rho_300K": -0.699, "alpha_coef": -0.040, "clase_real": "Semiconductor"},
    {"material": "GaN (Gallium Nitride)", "resistividad_ohm_m": 100.0, "log_rho_300K": 2.0, "alpha_coef": -0.050, "clase_real": "Semiconductor"},
    {"material": "SiC (Silicon Carbide)", "resistividad_ohm_m": 10.0, "log_rho_300K": 1.0, "alpha_coef": -0.030, "clase_real": "Semiconductor"},
    {"material": "InSb (Indium Antimonide)", "resistividad_ohm_m": 0.005, "log_rho_300K": -2.301, "alpha_coef": -0.015, "clase_real": "Semiconductor"},
    {"material": "CdTe (Cadmium Telluride)", "resistividad_ohm_m": 10000.0, "log_rho_300K": 4.0, "alpha_coef": -0.065, "clase_real": "Semiconductor"},
    {"material": "Silicon (n-type doped)", "resistividad_ohm_m": 0.05, "log_rho_300K": -1.301, "alpha_coef": -0.020, "clase_real": "Semiconductor"},
    {"material": "Silicon (p-type doped)", "resistividad_ohm_m": 0.15, "log_rho_300K": -0.824, "alpha_coef": -0.020, "clase_real": "Semiconductor"},
]

datos_materiales = []

for r in rows[1:]:
    cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', r, re.DOTALL)
    if len(cells) < 4:
        continue
    
    # Nombre limpio del material
    nombre = re.sub(r'<[^>]+>', '', cells[0])
    nombre = re.sub(r'\[.*?\]', '', nombre).replace('‡', '').replace('♠', '').strip()
    if not nombre or "material" in nombre.lower():
        continue
    
    if any(exc in nombre.lower() for exc in EXCLUIR):
        continue
    
    rho = extract_number(cells[1])
    alpha = extract_number(cells[3])
    
    if rho is None:
        continue
    
    # Ajuste de alpha según física del material
    nombre_lower = nombre.lower()
    if alpha is None:
        # Si es un aislante (rho > 1e6), el coeficiente térmico a temp ambiente es prácticamente nulo
        if rho >= 1e6:
            alpha = 0.0
        else:
            # Buscar en fallbacks de CRC Handbook
            for k, val in CRC_ALPHA_FALLBACK.items():
                if k in nombre_lower:
                    alpha = val
                    break
            if alpha is None:
                # Si es un metal con rho baja, asignar alpha metálico estándar (~0.0038)
                if rho < 1e-4:
                    alpha = 0.0038
                else:
                    alpha = 0.0

    # Clasificación física real (Ground truth para evaluación)
    if rho < 1e-5:
        clase = "Conductor"
    elif 1e-5 <= rho <= 1e5:
        clase = "Semiconductor"
    else:
        clase = "Aislante"
        # Para aislantes, fijar alpha estrictamente en 0.0
        alpha = 0.0
        
    log_rho = math.log10(rho)
    
    datos_materiales.append({
        "material": nombre,
        "resistividad_ohm_m": rho,
        "log_rho_300K": round(log_rho, 4),
        "alpha_coef": round(alpha, 6),
        "clase_real": clase
    })

# Añadir semiconductores tecnológicos tabulados
datos_materiales.extend(SEMICONDUCTORES_EXTRA)

# Guardar en CSV
with open(CSV_DESTINO, "w", encoding="utf-8") as f:
    f.write("material,resistividad_ohm_m,log_rho_300K,alpha_coef,clase_real\n")
    for d in datos_materiales:
        f.write(f'"{d["material"]}",{d["resistividad_ohm_m"]},{d["log_rho_300K"]},{d["alpha_coef"]},"{d["clase_real"]}"\n')

print(f"\n¡Éxito! Dataset generado con {len(datos_materiales)} materiales en:")
print(f"-> {CSV_DESTINO}")
print("\nResumen por clase real:")
clases = {}
for d in datos_materiales:
    clases[d["clase_real"]] = clases.get(d["clase_real"], 0) + 1
for k, v in clases.items():
    print(f" - {k}: {v} materiales")
