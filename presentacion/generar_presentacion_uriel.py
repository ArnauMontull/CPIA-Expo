"""generar_presentacion_uriel.py

Genera una presentacion PowerPoint (.pptx) profesional y minimalista para Uriel:
- Todos los recuadros redondeados con borde NEGRO solido.
- Sin barras/rayas debajo de los titulos.
- Todo el texto unificado en un solo color (NEGRO puro).
- Todas las formulas matematicas en estilo LaTeX Computer Modern incrustadas como imagenes.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = Path(__file__).resolve().parents[1]
FIG_DIR = BASE_DIR / "docs" / "figuras"
LATEX_DIR = FIG_DIR / "latex"

FIG_CLUSTERS = BASE_DIR / "problemas" / "5_Materials_Uriel" / "clusters_materiales_dbscan.png"
FIG_BANDAS = FIG_DIR / "esquema_bandas_materiales.png"
FIG_COMPARATIVA = FIG_DIR / "comparativa_kmeans_dbscan.png"
FIG_DATASET = FIG_DIR / "distribucion_escala_rho.png"

# Fórmulas LaTeX
LATEX_TRANSPORTE = LATEX_DIR / "formula_transporte.png"
LATEX_COORDENADAS = LATEX_DIR / "formula_coordenadas.png"
LATEX_ZSCORE = LATEX_DIR / "formula_zscore.png"
LATEX_NUCLEO = LATEX_DIR / "formula_nucleo.png"
LATEX_PARAMETROS = LATEX_DIR / "formula_parametros.png"
LATEX_SILHOUETTE = LATEX_DIR / "formula_silhouette.png"

OUTPUT_DIR_1 = BASE_DIR / "problemas" / "5_Materials_Uriel" / "presentacion_materiales_uriel.pptx"
OUTPUT_DIR_2 = BASE_DIR / "presentacion" / "presentacion_materiales_uriel.pptx"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Paleta unificada: Todo el texto y bordes en NEGRO
COLOR_NEGRO = RGBColor(0x00, 0x00, 0x00)
COLOR_BG_CARD = RGBColor(0xFF, 0xFF, 0xFF)      # Blanco puro para maximo contraste
COLOR_BORDER_BLACK = RGBColor(0x00, 0x00, 0x00) # Borde NEGRO en todos los recuadros

def add_header(slide, title_text, category="CPIA · APRENDIZAJE NO SUPERVISADO"):
    """Cabecera limpia: categoria y titulo en negro, sin ninguna raya/barra debajo."""
    # Categoria
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_cat = cat_box.text_frame
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_NEGRO
    
    # Titulo principal
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.7))
    tf_t = t_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(23)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NEGRO
    # No se añade ninguna barra o raya debajo

def add_card(slide, x, y, w, h, bg_color=COLOR_BG_CARD):
    """Crea un recuadro de esquinas redondeadas con borde NEGRO estricto."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = COLOR_BORDER_BLACK
    card.line.width = Pt(1.5)
    return card

def set_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes_text

# ==============================================================================
# SLIDE 1: PORTADA
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
add_card(s1, 0.8, 0.8, 11.733, 5.9)

b_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(0.5))
p = b_box.text_frame.paragraphs[0]
p.text = "CPIA · APRENDIZAJE NO SUPERVISADO"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

t_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.7), Inches(1.8))
tf = t_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Clasificación de Materiales Eléctricos mediante DBSCAN"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

sub_box = s1.shapes.add_textbox(Inches(1.3), Inches(3.6), Inches(10.7), Inches(1.0))
tf_sub = sub_box.text_frame
p = tf_sub.paragraphs[0]
p.text = "Descubrimiento No Supervisado de Fases Cuánticas (Conductores, Semiconductores y Aislantes)"
p.font.size = Pt(17)
p.font.color.rgb = COLOR_NEGRO

meta_box = s1.shapes.add_textbox(Inches(1.3), Inches(4.7), Inches(10.7), Inches(1.5))
tf_m = meta_box.text_frame
p1 = tf_m.paragraphs[0]
p1.text = "Uriel · Grado en Ingeniería Física (UPC)"
p1.font.size = Pt(16)
p1.font.bold = True
p1.font.color.rgb = COLOR_NEGRO

p2 = tf_m.add_paragraph()
p2.text = "Equipo: Matías · Martí · Uriel · Arnau Montull"
p2.font.size = Pt(14)
p2.font.color.rgb = COLOR_NEGRO

set_speaker_notes(s1,
    "Buenos días tribunal y compañeros. Soy Uriel y presento la clasificación no supervisada de materiales eléctricos con DBSCAN."
)

# ==============================================================================
# SLIDE 2: DEFINICIÓN DEL PROBLEMA Y LAS 3 FASES (BANDAS + FÓRMULAS LATEX)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "El Problema Físico: Estructura de Bandas y Firmas Térmicas")

# Recuadro superior con borde negro para las fórmulas LaTeX (compacto y centrado)
add_card(s2, 0.8, 1.45, 11.733, 1.25)

# Titulo de formulas en negro
tit_f = s2.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(0.3))
p = tit_f.text_frame.paragraphs[0]
p.text = "Ecuaciones Macroscópicas de Transporte Eléctrico:"
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

# Incrustar formula LaTeX de transporte centrada
if LATEX_TRANSPORTE.exists():
    s2.shapes.add_picture(str(LATEX_TRANSPORTE), Inches(2.4), Inches(1.82), width=Inches(8.5))

# Imagen de estructura de bandas de los 3 materiales abajo (bien separada)
if FIG_BANDAS.exists():
    s2.shapes.add_picture(str(FIG_BANDAS), Inches(0.8), Inches(2.85), width=Inches(11.733))

set_speaker_notes(s2,
    "GUION SLIDE 2:\n"
    "Definimos el problema físico a partir de las ecuaciones de transporte en LaTeX:\n"
    "- La variación térmica de la resistividad rho(T) y su derivada térmica alfa.\n"
    "- Metales: bandas solapadas, electrones libres, alfa positivo por choques con fonones de la red.\n"
    "- Semiconductores: bandgap moderado, alfa negativo por activación térmica exponencial según Boltzmann.\n"
    "- Aislantes: bandgap colosal (> 5 eV), sin portadores libres a 300 K, alfa nulo y resistividad gigantesca."
)

# ==============================================================================
# SLIDE 3: DATASET Y CLASIFICACIÓN SIN ETIQUETAS (30 ÓRDENES DE MAGNITUD)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Dataset Experimental y Espacio de Trabajo (log₁₀ρ, α)")

# Tarjeta izquierda con borde negro
add_card(s3, 0.8, 1.6, 4.6, 5.3)
b_data = s3.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(4.2), Inches(5.0))
tf_d = b_data.text_frame
tf_d.word_wrap = True

p = tf_d.paragraphs[0]
p.text = "¿Cómo clasificar sin etiquetas?"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

# Incrustar formula LaTeX de coordenadas
if LATEX_COORDENADAS.exists():
    s3.shapes.add_picture(str(LATEX_COORDENADAS), Inches(1.0), Inches(2.3), width=Inches(4.1))

# Texto en negro debajo de la formula
b_data2 = s3.shapes.add_textbox(Inches(1.0), Inches(3.1), Inches(4.2), Inches(3.7))
tf_d2 = b_data2.text_frame
tf_d2.word_wrap = True

d_items = [
    ("57 Materiales reales:", " Metales puros, aleaciones, semiconductores y dieléctricos."),
    ("30 órdenes de magnitud:", " De conductores (~10⁻⁸ Ω·m) a teflón (> 10²² Ω·m)."),
    ("Compresión logarítmica:", " Evita el colapso numérico en el origen."),
    ("Firma cuántica:", " α delata el origen microscópico del transporte."),
    ("Objetivo no supervisado:", " Descubrir las clases automáticamente por densidad.")
]
for i, (tit, desc) in enumerate(d_items):
    p = tf_d2.paragraphs[0] if i == 0 else tf_d2.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(7)

# Imagen derecha: Grafico comparativo de escala lineal vs logaritmica
if FIG_DATASET.exists():
    s3.shapes.add_picture(str(FIG_DATASET), Inches(5.6), Inches(1.9), width=Inches(6.9))

set_speaker_notes(s3,
    "GUION SLIDE 3:\n"
    "Disponemos de 57 materiales reales en el dataset.\n"
    "Como se aprecia en el gráfico comparativo: en escala lineal, el 99% de los materiales se aplasta en el cero. "
    "El logaritmo de resistividad es imprescindible para desplegar el espacio, y combinado con alfa crea un plano perfecto para el clustering."
)

# ==============================================================================
# SLIDE 4: ¿POR QUÉ DBSCAN Y NO K-MEANS? (LISTA VENTAJAS/DESVENTAJAS + FIGURA)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "¿Por qué DBSCAN y no K-Means?")

# Tarjeta izquierda con borde negro
add_card(s4, 0.8, 1.6, 4.8, 5.3)
b_vs = s4.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(4.4), Inches(5.0))
tf_vs = b_vs.text_frame
tf_vs.word_wrap = True

# K-Means Desventajas (texto en negro)
p = tf_vs.paragraphs[0]
p.text = "K-Means (Inadecuado en este dominio)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

km_list = [
    "Asume grupos esféricos e isodensos (igual varianza).",
    "Fractura el grupo disperso de aislantes.",
    "Exige prefijar 'k' a priori de forma arbitraria.",
    "No detecta ruido: fuerza anomalías a tener cluster."
]
for l in km_list:
    p = tf_vs.add_paragraph()
    p.text = f"✖  {l}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(4)

# DBSCAN Ventajas (texto en negro)
p_db = tf_vs.add_paragraph()
p_db.text = "\nDBSCAN (Elección Óptima)"
p_db.font.size = Pt(15)
p_db.font.bold = True
p_db.font.color.rgb = COLOR_NEGRO

db_list = [
    "Conecta por densidad local de cualquier forma.",
    "Tolera metales hiperdensos y aislantes laxos.",
    "Descubre el número de clusters sin prefijar k.",
    "Etiqueta ruido y anomalías de forma nativa (-1)."
]
for l in db_list:
    p = tf_vs.add_paragraph()
    p.text = f"✔  {l}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(4)

# Imagen derecha: Comparativa grafica
if FIG_COMPARATIVA.exists():
    s4.shapes.add_picture(str(FIG_COMPARATIVA), Inches(5.8), Inches(1.8), width=Inches(6.7))

set_speaker_notes(s4,
    "GUION SLIDE 4:\n"
    "Pregunta clave: ¿por qué DBSCAN y no K-Means?\n"
    "En el gráfico de la derecha se ve claro: K-Means impone fronteras esféricas forzadas. "
    "Al tener metales ultra concentrados y aislantes dispersos, K-Means falla. "
    "DBSCAN sigue los caminos de densidad natural y aísla puntos atípicos como ruido."
)

# ==============================================================================
# SLIDE 5: METODOLOGÍA Y PARÁMETROS (SOLO FÓRMULAS LATEX)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Metodología Matemática: Fórmulas y Parámetros")

w_box = 3.65
h_box = 5.2
y_s5 = 1.6

# 1. Estandarización Z-Score (Recuadro con borde negro)
add_card(s5, 0.8, y_s5, w_box, h_box)
b_f1 = s5.shapes.add_textbox(Inches(1.0), Inches(y_s5 + 0.15), Inches(w_box - 0.4), Inches(1.0))
p = b_f1.text_frame.paragraphs[0]
p.text = "1. Estandarización Z-Score\n(Implementada con NumPy)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

# Incrustar formula LaTeX Z-Score
if LATEX_ZSCORE.exists():
    s5.shapes.add_picture(str(LATEX_ZSCORE), Inches(0.95), Inches(y_s5 + 0.95), width=Inches(3.35))

b_f1_desc = s5.shapes.add_textbox(Inches(1.0), Inches(y_s5 + 2.45), Inches(w_box - 0.4), Inches(2.7))
tf_1_desc = b_f1_desc.text_frame
tf_1_desc.word_wrap = True

f1_sub = [
    "μ = Media muestral por columna",
    "σ = Desviación estándar típica",
    "Resultado: Media = 0, Varianza = 1",
    "Imprescindible: equipara el rango de log₁₀ρ (~31) con el de α (~0.08) para la distancia euclídea."
]
for i, item in enumerate(f1_sub):
    p = tf_1_desc.paragraphs[0] if i == 0 else tf_1_desc.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(5)

# 2. Criterio de Vecindad DBSCAN (Recuadro con borde negro)
add_card(s5, 4.85, y_s5, w_box, h_box)
b_f2 = s5.shapes.add_textbox(Inches(5.05), Inches(y_s5 + 0.15), Inches(w_box - 0.4), Inches(1.0))
p = b_f2.text_frame.paragraphs[0]
p.text = "2. Criterio de Núcleo\n(DBSCAN Espacial)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

# Incrustar formula LaTeX Nucleo
if LATEX_NUCLEO.exists():
    s5.shapes.add_picture(str(LATEX_NUCLEO), Inches(5.0), Inches(y_s5 + 0.95), width=Inches(3.35))

b_f2_desc = s5.shapes.add_textbox(Inches(5.05), Inches(y_s5 + 2.45), Inches(w_box - 0.4), Inches(2.7))
tf_2_desc = b_f2_desc.text_frame
tf_2_desc.word_wrap = True

f2_sub = [
    "d(p, q) = Distancia Euclídea en 2D",
    "Punto Núcleo (Core Point):",
    "   |N_ε(p)| ≥ min_samples",
    "Punto Frontera (Border):",
    "   Alcanzable desde un núcleo",
    "Ruido (Noise):",
    "   No alcanzable (|N_ε| < min_samples)"
]
for i, item in enumerate(f2_sub):
    p = tf_2_desc.paragraphs[0] if i == 0 else tf_2_desc.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(4)

# 3. Parámetros fijados (Recuadro con borde negro)
add_card(s5, 8.9, y_s5, w_box, h_box)
b_f3 = s5.shapes.add_textbox(Inches(9.1), Inches(y_s5 + 0.15), Inches(w_box - 0.4), Inches(1.0))
p = b_f3.text_frame.paragraphs[0]
p.text = "3. Parámetros Fijados\n(Criterio Objetivo)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

# Incrustar formula LaTeX Parametros
if LATEX_PARAMETROS.exists():
    s5.shapes.add_picture(str(LATEX_PARAMETROS), Inches(9.05), Inches(y_s5 + 0.95), width=Inches(3.35))

b_f3_desc = s5.shapes.add_textbox(Inches(9.1), Inches(y_s5 + 2.45), Inches(w_box - 0.4), Inches(2.7))
tf_3_desc = b_f3_desc.text_frame
tf_3_desc.word_wrap = True

f3_sub = [
    "min_samples = 3:",
    "   Regla canónica k ≥ d + 1 (dimensión d = 2).",
    "ε = 0.65:",
    "   Determinado mediante gráfico k-NN (codo).",
    "   Ventana óptima que aísla aislantes sin fusionar metales.",
    "Ejecución: scikit-learn DBSCAN"
]
for i, item in enumerate(f3_sub):
    p = tf_3_desc.paragraphs[0] if i == 0 else tf_3_desc.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(5)

set_speaker_notes(s5,
    "GUION SLIDE 5:\n"
    "En metodología: fórmulas en LaTeX claras y limpias.\n"
    "1. Escalado Z-Score manual con NumPy para igualar varianzas.\n"
    "2. Criterio de núcleo de DBSCAN: puntos con al menos min_samples vecinos en radio épsilon.\n"
    "3. Hiperparámetros fijados rigurosamente: min_samples=3 (dimensión + 1) y épsilon=0.65 obtenido por el codo k-NN."
)

# ==============================================================================
# SLIDE 6: CLUSTERS EN GRANDE (SOLO LA IMAGEN)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)

# Cabecera minima en negro, sin lineas
t_box = s6.shapes.add_textbox(Inches(0.8), Inches(0.25), Inches(11.7), Inches(0.6))
p = t_box.text_frame.paragraphs[0]
p.text = "Resultado DBSCAN: Clasificación 2D de Materiales Eléctricos"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

sub_t = t_box.text_frame.add_paragraph()
sub_t.text = "ε = 0.65 · min_samples = 3  |  3 Clusters descubiertos  |  0 Ruido"
sub_t.font.size = Pt(13)
sub_t.font.color.rgb = COLOR_NEGRO

# Imagen grande ocupando la diapositiva completa
if FIG_CLUSTERS.exists():
    s6.shapes.add_picture(str(FIG_CLUSTERS), Inches(1.1), Inches(1.15), width=Inches(11.1))

set_speaker_notes(s6,
    "GUION SLIDE 6:\n"
    "Este es el resultado gráfico final en pantalla grande:\n"
    "- Cluster 0 (ámbar): Metales conductores (Cu, Ag, Au, Al) concentrados arriba a la izquierda con alfa > 0.\n"
    "- Cluster 1 (azul): Aislantes dieléctricos (Vidrio, Cuarzo, Teflón) a la derecha con alfa centrado en cero.\n"
    "- Cluster 2 (verde): Semiconductores (Silicio, Germanio, GaAs) abajo, claramente separados por alfa fuertemente negativo.\n"
    "La línea horizontal de alfa = 0 marca la división física fundamental entre choques de fonones y generación térmica de portadores."
)

# ==============================================================================
# SLIDE 7: VALIDACIÓN DE RESULTADOS: MATRIZ DE CONTINGENCIA FÍSICA
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Validación Experimental: Matriz de Contingencia Física")

# 3 Tarjetas con borde negro
w_card7 = 3.65
h_card7 = 3.4
y_card7 = 1.6

# Conductores (Borde negro, texto negro)
add_card(s7, 0.8, y_card7, w_card7, h_card7)
bc = s7.shapes.add_textbox(Inches(1.0), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfc = bc.text_frame
tfc.word_wrap = True
p = tfc.paragraphs[0]
p.text = "Conductores (Metales)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

p_num = tfc.add_paragraph()
p_num.text = "35 / 35"
p_num.font.size = Pt(32)
p_num.font.bold = True
p_num.font.color.rgb = COLOR_NEGRO
p_num.alignment = PP_ALIGN.CENTER

p_p = tfc.add_paragraph()
p_p.text = "100 % Pureza"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_NEGRO
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfc.add_paragraph()
p_sub.text = "\nAsignados íntegramente al Cluster 0. Cero falsos negativos."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_NEGRO

# Aislantes (Borde negro, texto negro)
add_card(s7, 4.85, y_card7, w_card7, h_card7)
ba = s7.shapes.add_textbox(Inches(5.05), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfa = ba.text_frame
tfa.word_wrap = True
p = tfa.paragraphs[0]
p.text = "Aislantes (Dieléctricos)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

p_num = tfa.add_paragraph()
p_num.text = "10 / 10"
p_num.font.size = Pt(32)
p_num.font.bold = True
p_num.font.color.rgb = COLOR_NEGRO
p_num.alignment = PP_ALIGN.CENTER

p_p = tfa.add_paragraph()
p_p.text = "100 % Pureza"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_NEGRO
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfa.add_paragraph()
p_sub.text = "\nAsignados íntegramente al Cluster 1. Coincidencia total con física."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_NEGRO

# Semiconductores (Borde negro, texto negro)
add_card(s7, 8.9, y_card7, w_card7, h_card7)
bs = s7.shapes.add_textbox(Inches(9.1), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfs = bs.text_frame
tfs.word_wrap = True
p = tfs.paragraphs[0]
p.text = "Semiconductores"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

p_num = tfs.add_paragraph()
p_num.text = "10 / 12"
p_num.font.size = Pt(32)
p_num.font.bold = True
p_num.font.color.rgb = COLOR_NEGRO
p_num.alignment = PP_ALIGN.CENTER

p_p = tfs.add_paragraph()
p_p.text = "83.3 % Pureza"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_NEGRO
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfs.add_paragraph()
p_sub.text = "\n10 al Cluster 2. 2 semimetales clasificados en cluster 0 por conducción cuasi-metálica."
p_sub.font.size = Pt(10.5)
p_sub.font.color.rgb = COLOR_NEGRO

# Barra inferior con borde negro e imagen LaTeX de la silueta
add_card(s7, 0.8, 5.25, 11.733, 1.55)
b_sil = s7.shapes.add_textbox(Inches(1.1), Inches(5.35), Inches(11.1), Inches(0.35))
p = b_sil.text_frame.paragraphs[0]
p.text = "Métrica Matemática Complementaria (No Supervisada):"
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

if LATEX_SILHOUETTE.exists():
    s7.shapes.add_picture(str(LATEX_SILHOUETTE), Inches(2.2), Inches(5.75), width=Inches(8.8))

set_speaker_notes(s7,
    "GUION SLIDE 7:\n"
    "En cuanto a validación, la prueba reina es la Matriz de Contingencia Física:\n"
    "- 100% de pureza en conductores (35 de 35 metales en cluster 0).\n"
    "- 100% de pureza en aislantes (10 de 10 dieléctricos en cluster 1).\n"
    "- En semiconductores, los 10 materiales tecnológicos puros forman el cluster 2. "
    "Los dos restantes son semimetales cuyo transporte a 300 K es prácticamente metálico.\n"
    "Y como métrica matemática complementaria, la fórmula en LaTeX de Silhouette Score arroja 0.7858."
)

# ==============================================================================
# SLIDE 8: CONCLUSIONES RESUMIDAS
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Conclusiones")

# Recuadro con borde negro y texto unificado en negro
add_card(s8, 1.2, 1.7, 10.933, 5.0)
b_c = s8.shapes.add_textbox(Inches(1.6), Inches(2.0), Inches(10.1), Inches(4.4))
tf_c = b_c.text_frame
tf_c.word_wrap = True

p = tf_c.paragraphs[0]
p.text = "Puntos Clave del Proyecto"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO
p.space_after = Pt(14)

concl_puntos = [
    ("Física de bandas sin supervisión:", " DBSCAN descubre de manera autónoma las 3 fases de conducción (conductores, aislantes y semiconductores) a partir de propiedades macroscópicas."),
    ("Inmune a densidades dispares:", " Supera a K-Means agrupando simultáneamente la ultra-densidad de los metales y la dispersión de 12 órdenes de magnitud de los aislantes."),
    ("Variables óptimas:", " La escala logarítmica log₁₀(ρ) y el coeficiente térmico cuántico α bastan para separar completamente los regímenes de transporte."),
    ("Validación rotunda:", " 100% de pureza en conductores y aislantes con Silhouette Score = 0.7858.")
]
for tit, desc in concl_puntos:
    p = tf_c.add_paragraph()
    p.text = f"✔  {tit} {desc}"
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(12)

set_speaker_notes(s8,
    "GUION SLIDE 8:\n"
    "Para concluir:\n"
    "1. DBSCAN demuestra que la densidad espacial macroscópica refleja con total fidelidad la física cuántica de bandas.\n"
    "2. Ha demostrado ser la herramienta correcta frente a K-Means al tolerar densidades desiguales.\n"
    "3. Con solo dos variables físicas y una estandarización rigurosa, se obtiene una pureza del 100% en conductores y aislantes.\n"
    "Muchas gracias."
)

# ==============================================================================
# APLICAR FUENTE ARIAL EN TODA LA PRESENTACIÓN
# ==============================================================================
def aplicar_fuente_arial(presentation):
    """Aplica estrictamente la fuente Arial a todos los textos, títulos y párrafos."""
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    paragraph.font.name = "Arial"
                    for run in paragraph.runs:
                        run.font.name = "Arial"

aplicar_fuente_arial(prs)

# ==============================================================================
# GUARDAR PRESENTACIONES
# ==============================================================================
try:
    OUTPUT_DIR_1.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_DIR_1))
    print(f"Presentacion guardada en: {OUTPUT_DIR_1}")
except PermissionError:
    print(f"Aviso: {OUTPUT_DIR_1.name} en problemas/ esta abierto. Cierralo para actualizarlo.")

try:
    OUTPUT_DIR_2.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_DIR_2))
    print(f"Presentacion guardada en: {OUTPUT_DIR_2}")
except PermissionError:
    print(f"Aviso: {OUTPUT_DIR_2.name} en presentacion/ esta abierto. Cierralo en PowerPoint para sobrescribirlo.")
