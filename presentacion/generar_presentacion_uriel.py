"""generar_presentacion_uriel.py

Sincronitza la presentació d'Uriel (presentacion_materiales_uriel.pptx) a totes les rutes del projecte:
- problemas/5_Materials_Uriel/presentacion_materiales_uriel.pptx
- presentacion/presentacion_materiales_uriel.pptx
- CPIA/presentacion_materiales_uriel.pptx
"""

from pathlib import Path
import shutil

AQUI = Path(__file__).resolve().parent
REPO_ROOT = AQUI.parent
PPTX_PRESENTACION = AQUI / "presentacion_materiales_uriel.pptx"
PPTX_PROBLEMAS = REPO_ROOT / "problemas" / "5_Materials_Uriel" / "presentacion_materiales_uriel.pptx"
PPTX_ROOT = REPO_ROOT.parent / "presentacion_materiales_uriel.pptx"
PPTX_DOWNLOADS = Path.home() / "Downloads" / "presentacion_materiales_uriel.pptx"

def sincronitzar_presentacions():
    origen = None
    if PPTX_PRESENTACION.exists():
        origen = PPTX_PRESENTACION
    elif PPTX_PROBLEMAS.exists():
        origen = PPTX_PROBLEMAS
    elif PPTX_ROOT.exists():
        origen = PPTX_ROOT
    
    if origen is None:
        print("No s'ha trobat cap fitxer presentacion_materiales_uriel.pptx per sincronitzar.")
        return

    destinacions = [PPTX_PRESENTACION, PPTX_PROBLEMAS, PPTX_ROOT, PPTX_DOWNLOADS]
    for dst in destinacions:
        if dst != origen:
            try:
                shutil.copy2(origen, dst)
                print(f"Sincronitzat a: {dst}")
            except Exception as e:
                print(f"Avís en copiar a {dst}: {e}")

if __name__ == "__main__":
    sincronitzar_presentacions()
