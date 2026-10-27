# Genera presentacion/expo_cpia.pptx: parte de Arnau y Uriel completas y diapositivas con hueco para los demas
from pathlib import Path
import shutil
import copy
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml

AQUI = Path(__file__).resolve().parent
FIG = AQUI.parent / 'docs' / 'figuras'
PPTX_URIEL = AQUI / 'presentacion_materiales_uriel.pptx'

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
vacia = prs.slide_layouts[6]
ROJO = RGBColor(0xB0, 0x30, 0x30)
GRIS = RGBColor(0x55, 0x55, 0x55)


def texto(slide, x, y, w, h, lineas, tam=20, color=None, negrita=False):
    caja = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    caja.word_wrap = True
    for i, linea in enumerate(lineas):
        p = caja.paragraphs[0] if i == 0 else caja.add_paragraph()
        p.text = linea
        p.font.name = 'Arial'
        p.font.size, p.font.bold = Pt(tam), negrita
        if color:
            p.font.color.rgb = color
        p.space_after = Pt(8)


def diapo(titulo, lineas=(), figura=None, ancho_fig=7.2, pendiente=None, notas=None):
    s = prs.slides.add_slide(vacia)
    texto(s, 0.6, 0.35, 12, 1, [titulo], 32, negrita=True)
    ancho_texto = 12 if figura is None else 5.2
    texto(s, 0.6, 1.5, ancho_texto, 5, [f'• {l}' for l in lineas], 20)
    if figura:
        s.shapes.add_picture(str(FIG / figura), Inches(5.9), Inches(1.5), width=Inches(ancho_fig))
    if pendiente:
        texto(s, 0.6, 6.4, 12, 0.8, [f'[PENDIENTE: {pendiente}]'], 18, ROJO, True)
    if notas:
        s.notes_slide.notes_text_frame.text = notas
    return s


def clonar_slides_uriel(prs_dst, ruta_pptx):
    """Clona exactament les diapositives de la presentació d'Uriel."""
    prs_src = Presentation(ruta_pptx)
    blank_layout = prs_dst.slide_layouts[6]
    for src_slide in prs_src.slides:
        dst_slide = prs_dst.slides.add_slide(blank_layout)
        rId_map = {}
        for rel_id, rel in src_slide.part.rels.items():
            if "image" in rel.reltype:
                image_blob = rel.target_part.blob
                image_file = io.BytesIO(image_blob)
                image_part, new_rel_id = dst_slide.part.get_or_add_image_part(image_file)
                rId_map[rel_id] = new_rel_id

        for shape in src_slide.shapes:
            new_el = copy.deepcopy(shape.element)
            xml_str = new_el.xml
            for old_rid, new_rid in rId_map.items():
                xml_str = xml_str.replace(f'r:embed="{old_rid}"', f'r:embed="{new_rid}"')
            new_el = parse_xml(xml_str)
            dst_slide.shapes._spTree.append(new_el)


# Portada
s = prs.slides.add_slide(vacia)
texto(s, 0.8, 2.2, 11.5, 2, ['Aprendizaje no supervisado y detección de anomalías'], 40, negrita=True)
texto(s, 0.8, 3.9, 11.5, 1, ['CPIA · Grado en Ingeniería Física · UPC'], 22, GRIS)
texto(s, 0.8, 4.6, 11.5, 1, ['Matías · Martí · Uriel · Arnau Montull'], 22)

diapo('Qué vamos a ver', [
    'Clustering: K-Means, DBSCAN, jerárquico',
    'Mezclas gaussianas (GaussianMixture) e Isolation Forest',
    'Evaluar sin etiquetas: silhouette y método del codo',
    'Cuatro problemas con aplicación física, uno por persona'],
    pendiente='el equipo reparte quién explica la teoría de cada algoritmo')

diapo('Teoría común', pendiente='diapositivas de K-Means, DBSCAN, jerárquico, GMM, Isolation Forest, silhouette y codo')

# --- Parte de Arnau ---
diapo('Problema: ¿terremoto o explosión nuclear?', [
    'Sismógrafos: mismos registros para terremotos y explosiones',
    'Sin usar la etiqueta, ¿puede un clustering señalarlas?',
    'Pista 1: las pruebas se repiten en los mismos polígonos',
    'Pista 2: ocurren casi en la superficie (mediana 0 km frente a 33 km)'], 'catalogo.png')

diapo('Datos', [
    'Catálogo USGS, M ≥ 4,5, 1951-2025, todos los tipos de evento',
    '298 127 eventos; 614 etiquetados «nuclear explosion»',
    'La etiqueta solo se usa para evaluar, nunca para entrenar'], 'profundidad.png', 7.2)

diapo('Cómo se detecta', [
    '1. DBSCAN con distancia haversine (esfera)',
    '2. Mediana de profundidad de cada cluster',
    '3. Sospechoso si mediana en [dmin, dmax)',
    '4. Comparar con la etiqueta: aciertos, falsos positivos (FP) y falsos negativos (FN)'], 'deteccion_nevada.png', 7.2,
    notas='Zoom en Nevada: a la izquierda los epicentros, a la derecha los clusters; en naranja los sospechosos y con un círculo negro las explosiones reales.')

diapo('Elegir y validar los parámetros', [
    'Parámetros fijos: eps = 25 km, vmin = 2, profundidad mediana en [0; 2,5) km (criterio físico)',
    'eps = 25 km da el mínimo de falsos positivos (57) entre 5 y 100 km; es la única elección que mira la etiqueta',
    'La silueta no elige eps (es negativa y baja con eps); el codo de distancias k no marca un valor claro',
    'Con eps ≥ 50 km los grupos se funden con terremotos profundos: FP 453 (50 km) y FN 288 (75 km)',
    'Estabilidad (ARI, muestra del 50 %): 0,54-0,64',
    'nuke_optimizar.py se probó y se descartó: su ventana [0; 0,1) mide la convención del USGS'], 'nukeval_eps.png', 7.2)

diapo('Resultado', [
    '551 aciertos, 57 FP, 63 FN',
    'Precisión 90,6 %  ·  recall 89,7 %  ·  F1 = 0,902',
    'Globo interactivo: problemas/2_Nuclear/globo.html (4 vistas, sin internet)'], 'resultado.png', 7.2)

diapo('Limitaciones (preguntas probables)', [
    'vmin = 2: los sismos aislados son ruido. Con vmin = 1 hay 28 FN pero 115 FP (F1 0,891): compromiso precisión-recall',
    'Sin conjunto de prueba separado: se ajusta y se evalúa en el mismo catálogo',
    'El 85 % de las explosiones figura con profundidad 0,0 km en el USGS: una ventana [0; 0,1) daría F1 0,922, pero mediría esa convención',
    '57 FP: 14 son otros eventos no sísmicos (explosiones, minas); sin ellos serían 43 y F1 0,912. 40 de los 63 FN son explosiones aisladas (ruido)',
    'Algunas pruebas oficiales figuran como earthquake (error de la etiqueta)',
    'No usamos año ni número de estaciones: delatarían la época, no la física'])

# --- Huecos para Matías y Martí ---
for nombre in ('Matías', 'Martí'):
    diapo(f'Problema de {nombre}', pendiente='título, datos, método, resultado, figuras')

# --- Part d'Uriel: Classificació de Materials Elèctrics mitjançant DBSCAN ---
if PPTX_URIEL.exists():
    clonar_slides_uriel(prs, PPTX_URIEL)

diapo('Conclusiones', pendiente='comparativa del equipo: qué algoritmo funcionó mejor y por qué')
diapo('Preguntas', ['Código y documento de descripción entregados en Atenea'])

def aplicar_fuente_arial(presentation):
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    paragraph.font.name = "Arial"
                    for run in paragraph.runs:
                        run.font.name = "Arial"

aplicar_fuente_arial(prs)

prs.save(AQUI / 'expo_cpia.pptx')
print('guardado', AQUI / 'expo_cpia.pptx')

# Sincronitzar amb arrel de CPIA i Descàrregues si és possible
for dest in [AQUI.parent.parent / 'expo_cpia.pptx', Path.home() / 'Downloads' / 'expo_cpia.pptx']:
    try:
        shutil.copy2(AQUI / 'expo_cpia.pptx', dest)
        print(f"Copia actualitzada a: {dest}")
    except Exception as e:
        print(f"Avís en copiar a {dest}: {e}")
