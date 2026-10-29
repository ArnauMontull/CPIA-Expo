# -*- coding: utf-8 -*-
"""compile_final_pdf.py
Reemplaza los placeholders de imágenes por Base64 y compila el HTML a PDF usando Edge headless.
"""
import os
import sys
import base64
import subprocess
import shutil

BASE_DIR = r"c:\Users\marti\Documents\CPIA\CPIA-Expo\problemas\5_Materials_Uriel"
DOCS_DIR = r"c:\Users\marti\Documents\CPIA\CPIA-Expo\docs"
HTML_PATH = os.path.join(BASE_DIR, "preguntas_tribunal_uriel.html")
PDF_PATH_1 = os.path.join(BASE_DIR, "preguntas_tribunal_uriel.pdf")
PDF_PATH_2 = r"c:\Users\marti\Documents\CPIA\preguntas_tribunal_uriel.pdf"
PDF_PATH_3 = r"c:\Users\marti\Downloads\preguntas_tribunal_uriel.pdf"
EDGE_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def get_base64_image(file_path):
    if os.path.exists(file_path):
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        mime = "image/png" if ext == "png" else "image/jpeg" if ext in ["jpg", "jpeg"] else "image/svg+xml"
        with open(file_path, "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode("utf-8")
    return ""

print("Leyendo imágenes y codificando en Base64...")
logo_upc = get_base64_image(os.path.join(DOCS_DIR, "Logo_UPC.svg.png"))
logo_ef = get_base64_image(os.path.join(DOCS_DIR, "logo-enginyeria-fisica.jpg"))
img_comp = get_base64_image(os.path.join(BASE_DIR, "comparativa_abans_despres_dbscan.png"))

print("Reemplazando placeholders en el HTML...")
with open(HTML_PATH, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("__LOGO_UPC__", logo_upc)
content = content.replace("__LOGO_EF__", logo_ef)
content = content.replace("__IMG_COMP__", img_comp)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"HTML final preparado ({os.path.getsize(HTML_PATH):,} bytes).")

print("\nCompilando PDF con Microsoft Edge headless...")
cmd = [
    EDGE_BIN,
    "--headless=new",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=10000",
    f"--print-to-pdf={PDF_PATH_1}",
    HTML_PATH
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Error al compilar PDF:", res.stderr)
    sys.exit(1)

print(f"PDF generado con éxito ({os.path.getsize(PDF_PATH_1):,} bytes) en:")
print(f"-> {PDF_PATH_1}")

shutil.copy(PDF_PATH_1, PDF_PATH_2)
print(f"-> Copiado a: {PDF_PATH_2}")

shutil.copy(PDF_PATH_1, PDF_PATH_3)
print(f"-> Copiado a: {PDF_PATH_3}")

try:
    import pypdf
    reader = pypdf.PdfReader(PDF_PATH_1)
    print(f"\n¡Éxito total! El documento PDF tiene {len(reader.pages)} páginas.")
    for i, p in enumerate(reader.pages):
        txt = p.extract_text()
        first_line = txt.split('\n')[0] if txt else 'Página vacía'
        print(f"  Página {i+1}: {first_line[:60]}")
except Exception as e:
    print("Error al verificar páginas con pypdf:", e)
