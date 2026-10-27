# Genera presentacion/expo_cpia.pptx: parte de Arnau y Uriel completas y diapositivas con hueco para los demas
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
    'Parámetros fijos: eps = 25 km, vmin = 1, profundidad mediana en [0; 2,5) km (criterio físico)',
    'eps = 25 km da el mínimo de falsos positivos (115) entre 5 y 100 km; es la única elección que mira la etiqueta',
    'La silueta no elige eps (es negativa y baja con eps); el codo de distancias k no marca un valor claro',
    'Con eps ≥ 50 km los grupos se funden con terremotos profundos: FP 483 (50 km) y FN 261 (75 km)',
    'Estabilidad (ARI, muestra del 50 %): 0,54-0,65',
    'nuke_optimizar.py se probó y se descartó: su ventana [0; 0,1) mide la convención del USGS'], 'nukeval_eps.png', 7.2)

diapo('Resultado', [
    '586 aciertos, 115 FP, 28 FN',
    'Precisión 83,6 %  ·  recall 95,4 %  ·  F1 = 0,891',
    'Globo interactivo: problemas/2_Nuclear/globo.html (4 vistas, sin internet)'], 'resultado.png', 7.2)

diapo('Limitaciones (preguntas probables)', [
    'vmin = 1: no hay ruido; la selección real la hace la profundidad. Con vmin = 3, F1 baja a 0,899',
    'Sin conjunto de prueba separado: se ajusta y se evalúa en el mismo catálogo',
    'El 85 % de las explosiones figura con profundidad 0,0 km en el USGS: una ventana [0; 0,1) daría F1 0,931, pero mediría esa convención',
    '115 FP: 24 son otros eventos no sísmicos (explosiones, minas); sin ellos serían 91 y F1 0,908',
    'Algunas pruebas oficiales figuran como earthquake (error de la etiqueta)',
    'No usamos año ni número de estaciones: delatarían la época, no la física'])

# --- Huecos para Matías y Martí ---
for nombre in ('Matías', 'Martí'):
    diapo(f'Problema de {nombre}', pendiente='título, datos, método, resultado, figuras')

# --- Part d\'Uriel: Classificació de Materials Elèctrics amb DBSCAN ---
diapo('Problema: 3 famílies i signatures tèrmiques', [
    'Conducció segons l\'estructura quàntica de bandes',
    'Variació tèrmica: ρ(T) = ρ₀ · [1 + α·(T - T₀)]',
    'Coeficient tèrmic: α = (1 / ρ₀) · (dρ / dT)₃₀₀K',
    'Metalls (α > 0) · Semiconductors (α < 0) · Aïllants (α ≈ 0)'],
    'esquema_bandas_materiales.png', 7.2,
    notas='Estructura de bandes i variació tèrmica: el signe i la magnitud d\'alfa delaten la física microscòpica.')

diapo('Dataset i espai (log₁₀ρ, α)', [
    '57 materials reals recopilats experimentalment',
    '30 ordres de magnitud en resistivitat (10⁻⁸ a 10²² Ω·m)',
    'Escala lineal col·lapsa a l\'origen; log₁₀(ρ) separa les fases',
    'Clustering no supervisat: descobrir les classes sense etiquetes'],
    'materiales_antes_clustering.png', 7.2,
    notas='Comparativa d\'escala: la compressió logarítmica és imprescindible perquè metalls i aïllants coexisteixin.')

diapo('Per què DBSCAN enfront de K-Means?', [
    '✖ K-Means: assumeix esfericitat, fractura aïllants i no aïlla soroll',
    '✔ DBSCAN: connecta per densitat local i tolera densitats desiguals',
    'Metalls hiperdensos vs aïllants estesos en 12 ordres',
    'DBSCAN detecta anomalies de manera nativa (etiqueta -1)'],
    'comparativa_kmeans_dbscan.png', 7.2,
    notas='K-Means assumeix variàncies similars i falla; DBSCAN connecta per densitat i respecta la dispersió natural.')

diapo('Metodologia: Fórmules i paràmetres', [
    'Estandardització manual Z-Score amb NumPy: Z = (X - μ) / σ',
    'Veïnat: N_ε(p) = { q | d(p, q) ≤ ε }',
    'Nucli (Core Point): |N_ε(p)| ≥ min_samples',
    'Paràmetres fixats: ε = 0,65 (colze k-NN) i min_samples = 3 (d = 2)'])

diapo('Resultat: DBSCAN en 57 materials', [
    '3 clústers purs descoberts per densitat: 0 soroll',
    'Clúster 0 (ambre): 35 metalls conductors (Cu, Ag, Au...)',
    'Clúster 1 (blau): 10 aïllants dielèctrics (vidre, tefló...)',
    'Clúster 2 (verd): 10 semiconductors (Si, Ge, GaAs...)',
    'Frontera α = 0: fonons vs activació tèrmica'],
    'comparativa_abans_despres_dbscan.png', 7.2,
    notas='Resultat gràfic: el pla 2D mostra la separació nítida de les tres classes.')

diapo('Validació física: Matriu de contingència', [
    'Conductors: 35 de 35 (100 % puresa al Clúster 0)',
    'Aïllants: 10 de 10 (100 % puresa al Clúster 1)',
    'Semiconductors: 10 de 12 (83,3 % puresa al Clúster 2; 2 semimetalls al clúster 0)',
    'Silhouette Score complementari: 0,7858 (alta cohesió interna)'])

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
