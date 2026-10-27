"""Script per descarregar i processar la taula oficial de resistivitats i coeficients
tèrmics (CRC Handbook / Viquipèdia) a datos/materiales_electricos.csv.
"""
import sys
import re
import json
import urllib.request
from pathlib import Path
import math

# ==============================================================================
# CODI FET AMB GEMINI
# ==============================================================================

# Assegurar codificació UTF-8 a Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATOS_DIR = Path(__file__).resolve().parents[2] / "datos"
DATOS_DIR.mkdir(exist_ok=True)
CSV_DESTINO = DATOS_DIR / "materiales_electricos.csv"

URL = "https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity"

print(f"Descarregant dades des de: {URL} ...")
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
html = urllib.request.urlopen(req).read().decode("utf-8")

# Localitzar la taula principal de resistivitat
tables = re.findall(r'<table[^>]*wikitable[^>]*>(.*?)</table>', html, re.DOTALL)
tabla = None
for t in tables:
    if "Material" in t and ("Resistivity" in t or "Conductivity" in t) and "Silver" in t:
        tabla = t
        break

if not tabla:
    raise RuntimeError("No s'ha pogut localitzar la taula de resistivitat a l'HTML descarregat.")

rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tabla, re.DOTALL)

def extract_number(cell_html):
    # 1. Intentar parsejar data-mw JSON de la plantilla val
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

    # 2. Parseig mitjançant expressions regulars
    clean = re.sub(r'<[^>]+>', ' ', cell_html)
    clean = re.sub(r'\[.*?\]', '', clean)
    clean = clean.replace('×', 'e').replace('&times;', 'e').replace('−', '-').replace('–', '-').strip()
    
    # Gestionar notació científica com 1.59e-8 o 1.59 e 10^-8
    m2 = re.search(r'([0-9.]+)\s*(?:e|x|X|\*)\s*10\^?\s*(-?[0-9]+)', clean)
    if m2:
        return float(m2.group(1)) * (10.0 ** float(m2.group(2)))
    
    # Gestionar ordres de magnitud directes com 10^12 o 10 12
    m3 = re.search(r'10\s*\^?\s*([0-9]+)', clean)
    if m3:
        return 10.0 ** float(m3.group(1))
    
    # Gestionar número decimal estàndard
    m4 = re.search(r'^-?[0-9]+(?:\.[0-9]+)?', clean)
    if m4:
        return float(m4.group(0))
    
    return None

# Valors de referència CRC per a metalls/materials on la taula wiki no tabula alpha explícitament
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

# Materials no sòlids (líquids o biològics) que descartem per centrar-nos en estat sòlid
EXCLUIR = ["sea water", "swimming pool water", "drinking water", "bone", "wood (damp)", "deionised water", "ultrapure water"]

# Semiconductors tecnològics addicionals estàndard (CRC Handbook / Sze 'Physics of Semiconductor Devices')
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
    
    # Nom net del material
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
    
    # Ajust d'alpha segons la física del material
    nombre_lower = nombre.lower()
    if alpha is None:
        # Si és un aïllant (rho >= 1e6), el coeficient tèrmic a temperatura ambient és pràcticament nul
        if rho >= 1e6:
            alpha = 0.0
        else:
            # Cercar en els fallbacks del CRC Handbook
            for k, val in CRC_ALPHA_FALLBACK.items():
                if k in nombre_lower:
                    alpha = val
                    break
            if alpha is None:
                # Si és un metall amb rho baixa, assignar alpha metàl·lic estàndard (~0.0038)
                if rho < 1e-4:
                    alpha = 0.0038
                else:
                    alpha = 0.0

    # Classificació física real (Ground truth per a avaluació)
    if rho < 1e-5:
        clase = "Conductor"
    elif 1e-5 <= rho <= 1e5:
        clase = "Semiconductor"
    else:
        clase = "Aislante"
        # Per a aïllants, fixar alpha estrictament a 0.0
        alpha = 0.0
        
    log_rho = math.log10(rho)
    
    datos_materiales.append({
        "material": nombre,
        "resistividad_ohm_m": rho,
        "log_rho_300K": round(log_rho, 4),
        "alpha_coef": round(alpha, 6),
        "clase_real": clase
    })

# Afegir semiconductors tecnològics tabulats
datos_materiales.extend(SEMICONDUCTORES_EXTRA)

# Guardar a CSV
with open(CSV_DESTINO, "w", encoding="utf-8") as f:
    f.write("material,resistividad_ohm_m,log_rho_300K,alpha_coef,clase_real\n")
    for d in datos_materiales:
        f.write(f'"{d["material"]}",{d["resistividad_ohm_m"]},{d["log_rho_300K"]},{d["alpha_coef"]},"{d["clase_real"]}"\n')

print(f"\nÈxit! Dataset generat amb {len(datos_materiales)} materials a:")
print(f"-> {CSV_DESTINO}")
print("\nResum per classe real:")
clases = {}
for d in datos_materiales:
    clases[d["clase_real"]] = clases.get(d["clase_real"], 0) + 1
for k, v in clases.items():
    print(f" - {k}: {v} materials")
