# Genera presentacion/expo_cpia.pptx: parte de Arnau completa y diapositivas con hueco para los demas
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

AQUI = Path(__file__).resolve().parent
FIG = AQUI.parent / 'docs' / 'figuras'

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
    'Pista 2: ocurren casi en la superficie (mediana 0 km frente a 22 km)'], 'catalogo.png')

diapo('Datos', [
    'Catálogo USGS, M ≥ 4,5, 1951-2025',
    '298 025 eventos; 614 etiquetados «nuclear explosion»',
    'La etiqueta solo se usa para evaluar, nunca para entrenar'], 'profundidad.png', 6.8)

diapo('Cómo se detecta', [
    '1. DBSCAN con distancia haversine (esfera)',
    '2. Mediana de profundidad de cada cluster',
    '3. Sospechoso si mediana en [dmin, dmax)',
    '4. Comparar con la etiqueta: aciertos, falsos positivos (FP) y falsos negativos (FN)'], 'deteccion_nevada.png', 7.2,
    notas='Zoom en Nevada: a la izquierda los epicentros, a la derecha los clusters; en morado los sospechosos.')

diapo('Elegir y validar los parámetros', [
    'Optimizador por F1 (con etiquetas): DBSCAN una vez por (eps, vmin) y todas las ventanas de profundidad',
    'Óptimo: eps = 25 km, vmin = 1, profundidad [0; 0,1) km',
    'La silueta no elige eps (es negativa y baja con eps); el codo de distancias k no marca un valor claro',
    'Con eps ≥ 50 km los FN se disparan (261): los grupos se funden con terremotos profundos',
    'Estabilidad (ARI, muestra del 50 %): 0,52-0,62'], 'nukeval_eps.png', 7.2)

diapo('Resultado', [
    '585 aciertos, 36 FP, 29 FN',
    'Precisión 94,2 %  ·  recall 95,3 %  ·  F1 = 0,947',
    'Globo interactivo: problemas/2_Nuclear/globo.html (4 vistas, sin internet)'], 'resultado.png', 7.2)

diapo('Limitaciones (preguntas probables)', [
    'vmin = 1: no hay ruido; la selección real la hace la profundidad. Con vmin = 3, F1 baja a 0,928',
    'Sobreajuste: parámetros elegidos y evaluados con los mismos datos. Cruzado entre catálogos: F1 0,855 (pequeño→grande) y 0,977 (grande→pequeño)',
    'FP: terremotos muy superficiales y explosiones de minas; algunas pruebas oficiales figuran como earthquake',
    'No usamos año ni número de estaciones: delatarían la época, no la física'])

# --- Huecos para los demas ---
for nombre in ('Matías', 'Martí', 'Uriel'):
    diapo(f'Problema de {nombre}', pendiente='título, datos, método, resultado, figuras')

diapo('Conclusiones', pendiente='comparativa del equipo: qué algoritmo funcionó mejor y por qué')
diapo('Preguntas', ['Código y documento de descripción entregados en Atenea'])

prs.save(AQUI / 'expo_cpia.pptx')
print('guardado', AQUI / 'expo_cpia.pptx')
