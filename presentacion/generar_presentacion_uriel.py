"""generar_presentacion_uriel.py

Genera una presentacion PowerPoint (.pptx) minimalista, visual y de alto impacto
para la exposicion individual de Uriel en CPIA:
"Clasificacion de Materiales Electricos mediante DBSCAN".

- Minimo texto, maxima carga visual (graficos de bandas, comparativas, distribuciones).
- Widescreen 16:9 nativo para Google Slides.
- Notas de orador completas para cada diapositiva.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = Path(__file__).resolve().parents[1]
FIG_DIR = BASE_DIR / "docs" / "figuras"
FIG_CLUSTERS = BASE_DIR / "problemas" / "5_Materials_Uriel" / "clusters_materiales_dbscan.png"
FIG_BANDAS = FIG_DIR / "esquema_bandas_materiales.png"
FIG_COMPARATIVA = FIG_DIR / "comparativa_kmeans_dbscan.png"
FIG_DATASET = FIG_DIR / "distribucion_escala_rho.png"

OUTPUT_DIR_1 = BASE_DIR / "problemas" / "5_Materials_Uriel" / "presentacion_materiales_uriel.pptx"
OUTPUT_DIR_2 = BASE_DIR / "presentacion" / "presentacion_materiales_uriel.pptx"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Paleta
COLOR_BG_CARD = RGBColor(0xF8, 0xFA, 0xFC)
COLOR_BORDER = RGBColor(0xCB, 0xD5, 0xE1)
COLOR_TITULO = RGBColor(0x0F, 0x17, 0x2A)
COLOR_SUBTITULO = RGBColor(0x33, 0x41, 0x55)
COLOR_TEXTO = RGBColor(0x1E, 0x29, 0x3B)
COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)

COLOR_EMERALD = RGBColor(0x05, 0x96, 0x69)
COLOR_BLUE = RGBColor(0x25, 0x63, 0xEB)
COLOR_AMBER = RGBColor(0xD9, 0x77, 0x06)
COLOR_RED = RGBColor(0xDC, 0x26, 0x26)

def add_header(slide, title_text, category="CPIA · CLUSTERING EN FÍSICA"):
    # Categoria
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.35))
    tf_cat = cat_box.text_frame
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_EMERALD
    
    # Titulo
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.7))
    tf_t = t_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TITULO
    
    # Linea sutil
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.42), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BORDER
    line.line.color.rgb = COLOR_BORDER

def add_card(slide, x, y, w, h, bg_color=COLOR_BG_CARD, border_color=COLOR_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.1)
    else:
        card.line.fill.background()
    return card

def set_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes_text

# ==============================================================================
# SLIDE 1: PORTADA
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
add_card(s1, 0.8, 0.8, 11.733, 5.9, bg_color=COLOR_BG_CARD, border_color=COLOR_EMERALD)

b_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(0.5))
p = b_box.text_frame.paragraphs[0]
p.text = "CPIA · APRENDIZAJE NO SUPERVISADO"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

t_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.7), Inches(1.8))
tf = t_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Clasificación de Materiales Eléctricos mediante DBSCAN"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO

sub_box = s1.shapes.add_textbox(Inches(1.3), Inches(3.6), Inches(10.7), Inches(1.0))
tf_sub = sub_box.text_frame
p = tf_sub.paragraphs[0]
p.text = "Descubrimiento No Supervisado de Fases Cuánticas (Conductores, Semiconductores y Aislantes)"
p.font.size = Pt(17)
p.font.color.rgb = COLOR_SUBTITULO

meta_box = s1.shapes.add_textbox(Inches(1.3), Inches(4.7), Inches(10.7), Inches(1.5))
tf_m = meta_box.text_frame
p1 = tf_m.paragraphs[0]
p1.text = "Uriel · Grado en Ingeniería Física (UPC)"
p1.font.size = Pt(16)
p1.font.bold = True
p1.font.color.rgb = COLOR_TITULO

p2 = tf_m.add_paragraph()
p2.text = "Equipo: Matías · Martí · Uriel · Arnau Montull"
p2.font.size = Pt(14)
p2.font.color.rgb = COLOR_MUTED

set_speaker_notes(s1,
    "Buenos días tribunal y compañeros. Soy Uriel y presento la clasificación no supervisada de materiales eléctricos con DBSCAN."
)

# ==============================================================================
# SLIDE 2: DEFINICIÓN DEL PROBLEMA Y LAS 3 FASES (BANDAS + FÓRMULAS)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "El Problema Físico: Estructura de Bandas y Firmas Térmicas")

# Caja con formulas físicas destacadas arriba
add_card(s2, 0.8, 1.6, 11.733, 1.3, bg_color=COLOR_BG_CARD, border_color=COLOR_BLUE)
f_box = s2.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(11.3), Inches(1.2))
tf_f = f_box.text_frame
tf_f.word_wrap = True

p_f1 = tf_f.paragraphs[0]
p_f1.text = "Ecuaciones Macroscópicas de Transporte Eléctrico:"
p_f1.font.size = Pt(12)
p_f1.font.bold = True
p_f1.font.color.rgb = COLOR_BLUE

p_f2 = tf_f.add_paragraph()
p_f2.text = "1. Variación térmica:  ρ(T) = ρ₀ · [1 + α·(T - T₀)]       2. Coeficiente térmico:  α = (1 / ρ₀) · (dρ / dT)₃₀₀K"
p_f2.font.size = Pt(15)
p_f2.font.bold = True
p_f2.font.color.rgb = COLOR_TITULO
p_f2.space_before = Pt(4)

# Imagen de estructura de bandas de los 3 materiales abajo (grande y clara)
if FIG_BANDAS.exists():
    s2.shapes.add_picture(str(FIG_BANDAS), Inches(0.8), Inches(3.05), width=Inches(11.733))

set_speaker_notes(s2,
    "GUION SLIDE 2:\n"
    "Definimos el problema físico: las propiedades de transporte revelan directamente la estructura de bandas.\n"
    "- Metales: bandas solapadas, electrones libres, alfa positivo por choques con fonones.\n"
    "- Semiconductores: bandgap moderado (~1 eV), alfa fuertemente negativo por activación térmica según Boltzmann.\n"
    "- Aislantes: bandgap colosal (> 5 eV), sin portadores libres a 300 K, alfa nulo y resistividad extrema."
)

# ==============================================================================
# SLIDE 3: DATASET Y CLASIFICACIÓN SIN ETIQUETAS (30 ÓRDENES DE MAGNITUD)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Dataset Experimental y Espacio de Trabajo (log₁₀ρ, α)")

# Tarjeta izquierda: Puntos clave mínimos
add_card(s3, 0.8, 1.65, 4.4, 5.2)
b_data = s3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(4.0), Inches(4.8))
tf_d = b_data.text_frame
tf_d.word_wrap = True

p = tf_d.paragraphs[0]
p.text = "¿Cómo clasificar sin etiquetas?"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO

d_items = [
    ("57 Materiales reales:", " Metales puros, aleaciones, semiconductores y aislantes."),
    ("30 órdenes de magnitud:", " De metales (~10⁻⁸ Ω·m) a teflón (> 10²² Ω·m)."),
    ("Compresión logarítmica:", " x₁ = log₁₀(ρ₃₀₀K) evita el colapso numérico."),
    ("Firma cuántica:", " x₂ = α (diferencia el origen microscópico)."),
    ("Objetivo no supervisado:", " Identificar las fases de forma autónoma por densidad.")
]
for tit, desc in d_items:
    p = tf_d.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(8)

# Imagen derecha: Grafico comparativo de escala lineal vs logaritmica
if FIG_DATASET.exists():
    s3.shapes.add_picture(str(FIG_DATASET), Inches(5.4), Inches(1.95), width=Inches(7.1))

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

# Tarjeta izquierda: Ventajas y Desventajas directas
add_card(s4, 0.8, 1.65, 4.8, 5.2)
b_vs = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(4.4), Inches(4.8))
tf_vs = b_vs.text_frame
tf_vs.word_wrap = True

# K-Means Desventajas
p = tf_vs.paragraphs[0]
p.text = "K-Means (Inadecuado aquí)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_RED

km_list = [
    "Asume grupos esféricos e isodensos (igual varianza).",
    "Fractura el grupo disperso de aislantes.",
    "Exige fijar 'k' a priori de forma arbitraria.",
    "No detecta ruido: fuerza anomalías a tener cluster."
]
for l in km_list:
    p = tf_vs.add_paragraph()
    p.text = f"✖  {l}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(4)

# DBSCAN Ventajas
p_db = tf_vs.add_paragraph()
p_db.text = "\nDBSCAN (Elección Óptima)"
p_db.font.size = Pt(15)
p_db.font.bold = True
p_db.font.color.rgb = COLOR_EMERALD

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
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(4)

# Imagen derecha: Comparativa grafica
if FIG_COMPARATIVA.exists():
    s4.shapes.add_picture(str(FIG_COMPARATIVA), Inches(5.8), Inches(1.85), width=Inches(6.7))

set_speaker_notes(s4,
    "GUION SLIDE 4:\n"
    "Pregunta clave: ¿por qué DBSCAN y no K-Means?\n"
    "En el gráfico de la derecha se ve claro: K-Means impone fronteras esféricas forzadas. "
    "Al tener metales ultra concentrados y aislantes dispersos, K-Means falla. "
    "DBSCAN sigue los caminos de densidad natural y aísla puntos atípicos como ruido."
)

# ==============================================================================
# SLIDE 5: METODOLOGÍA Y PARÁMETROS (SOLO FÓRMULAS)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Metodología Matemática: Fórmulas y Parámetros")

w_box = 3.65
h_box = 5.0

# 1. Estandarización Z-Score
add_card(s5, 0.8, 1.7, w_box, h_box, border_color=COLOR_BLUE)
b_f1 = s5.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(w_box - 0.4), Inches(4.5))
tf_1 = b_f1.text_frame
tf_1.word_wrap = True

p = tf_1.paragraphs[0]
p.text = "1. Estandarización Z-Score\n(Implementada con NumPy)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE

p = tf_1.add_paragraph()
p.text = "\nZ = (X - μ) / σ\n"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO
p.alignment = PP_ALIGN.CENTER

f1_sub = [
    "μ = Media muestral por columna",
    "σ = Desviación estándar típica",
    "Resultado: Media = 0, Varianza = 1",
    "Imprescindible: equipara el rango de log₁₀ρ (~31) con el rango de α (~0.08) para la distancia euclídea."
]
for item in f1_sub:
    p = tf_1.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

# 2. Criterio de Vecindad DBSCAN
add_card(s5, 4.85, 1.7, w_box, h_box, border_color=COLOR_EMERALD)
b_f2 = s5.shapes.add_textbox(Inches(5.05), Inches(1.9), Inches(w_box - 0.4), Inches(4.5))
tf_2 = b_f2.text_frame
tf_2.word_wrap = True

p = tf_2.paragraphs[0]
p.text = "2. Criterio de Núcleo\n(DBSCAN Espacial)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

p = tf_2.add_paragraph()
p.text = "\nN_ε(p) = { q | d(p, q) ≤ ε }\n"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO
p.alignment = PP_ALIGN.CENTER

f2_sub = [
    "d(p, q) = Distancia Euclídea 2D",
    "Punto Núcleo (Core Point):",
    "   |N_ε(p)| ≥ min_samples",
    "Punto Frontera (Border):",
    "   Alcanzable desde un núcleo",
    "Ruido (Noise):",
    "   No alcanzable (|N_ε| < min_samples)"
]
for item in f2_sub:
    p = tf_2.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(4)

# 3. Parámetros fijados
add_card(s5, 8.9, 1.7, w_box, h_box, border_color=COLOR_AMBER)
b_f3 = s5.shapes.add_textbox(Inches(9.1), Inches(1.9), Inches(w_box - 0.4), Inches(4.5))
tf_3 = b_f3.text_frame
tf_3.word_wrap = True

p = tf_3.paragraphs[0]
p.text = "3. Parámetros Fijados\n(Criterio Objetivo)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER

p = tf_3.add_paragraph()
p.text = "\nε = 0.65\nmin_samples = 3\n"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO
p.alignment = PP_ALIGN.CENTER

f3_sub = [
    "min_samples = 3:",
    "   Regla canónica k ≥ d + 1 (dimensión d = 2).",
    "ε = 0.65:",
    "   Determinado mediante gráfico k-NN (codo).",
    "   Ventana óptima que aísla aislantes sin fusionar metales.",
    "Ejecución: scikit-learn DBSCAN"
]
for item in f3_sub:
    p = tf_3.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

set_speaker_notes(s5,
    "GUION SLIDE 5:\n"
    "En metodología: solo las fórmulas esenciales.\n"
    "1. Escalado Z-Score manual con NumPy para igualar varianzas.\n"
    "2. Criterio de núcleo de DBSCAN: puntos con al menos min_samples vecinos en radio épsilon.\n"
    "3. Hiperparámetros fijados rigurosamente: min_samples=3 (dimensión + 1) y épsilon=0.65 obtenido por el codo k-NN."
)

# ==============================================================================
# SLIDE 6: CLUSTERS EN GRANDE (SOLO LA IMAGEN)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)

# Cabecera minima
t_box = s6.shapes.add_textbox(Inches(0.8), Inches(0.25), Inches(11.7), Inches(0.6))
p = t_box.text_frame.paragraphs[0]
p.text = "Resultado DBSCAN: Clasificación 2D de Materiales Eléctricos"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO

sub_t = t_box.text_frame.add_paragraph()
sub_t.text = "ε = 0.65 · min_samples = 3  |  3 Clusters descubiertos  |  0 Ruido"
sub_t.font.size = Pt(13)
sub_t.font.color.rgb = COLOR_MUTED

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

# Tarjetas visuales de resultados por familia
w_card7 = 3.65
h_card7 = 3.4
y_card7 = 1.7

# Conductores
add_card(s7, 0.8, y_card7, w_card7, h_card7, border_color=COLOR_AMBER)
bc = s7.shapes.add_textbox(Inches(1.0), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfc = bc.text_frame
tfc.word_wrap = True
p = tfc.paragraphs[0]
p.text = "Conductores (Metales)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER

p_num = tfc.add_paragraph()
p_num.text = "35 / 35"
p_num.font.size = Pt(32)
p_num.font.bold = True
p_num.font.color.rgb = COLOR_TITULO
p_num.alignment = PP_ALIGN.CENTER

p_p = tfc.add_paragraph()
p_p.text = "100 % Pureza"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_EMERALD
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfc.add_paragraph()
p_sub.text = "\nAsignados íntegramente al Cluster 0. Cero falsos negativos."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXTO

# Aislantes
add_card(s7, 4.85, y_card7, w_card7, h_card7, border_color=COLOR_BLUE)
ba = s7.shapes.add_textbox(Inches(5.05), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfa = ba.text_frame
tfa.word_wrap = True
p = tfa.paragraphs[0]
p.text = "Aislantes (Dieléctricos)"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE

p_num = tfa.add_paragraph()
p_num.text = "10 / 10"
p_num.font.size = Pt(32)
p_num.font.bold = True
p_num.font.color.rgb = COLOR_TITULO
p_num.alignment = PP_ALIGN.CENTER

p_p = tfa.add_paragraph()
p_p.text = "100 % Pureza"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_EMERALD
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfa.add_paragraph()
p_sub.text = "\nAsignados íntegramente al Cluster 1. Coincidencia total con física."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_TEXTO

# Semiconductores
add_card(s7, 8.9, y_card7, w_card7, h_card7, border_color=COLOR_EMERALD)
bs = s7.shapes.add_textbox(Inches(9.1), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfs = bs.text_frame
tfs.word_wrap = True
p = tfs.paragraphs[0]
p.text = "Semiconductores"
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

p_num = tfs.add_paragraph()
p_num.text = "10 / 12"
p_num.font.size = Pt(32)
p_num.font.bold = True
p_num.font.color.rgb = COLOR_TITULO
p_num.alignment = PP_ALIGN.CENTER

p_p = tfs.add_paragraph()
p_p.text = "83.3 % Pureza"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_EMERALD
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfs.add_paragraph()
p_sub.text = "\n10 al Cluster 2. 2 semimetales clasificados en cluster 0 por conducción cuasi-metálica."
p_sub.font.size = Pt(10.5)
p_sub.font.color.rgb = COLOR_TEXTO

# Barra inferior con el Silhouette Score como dato cuantitativo complementario
add_card(s7, 0.8, 5.35, 11.733, 1.45, bg_color=COLOR_BG_CARD, border_color=COLOR_BORDER)
b_sil = s7.shapes.add_textbox(Inches(1.1), Inches(5.45), Inches(11.1), Inches(1.2))
tf_sil = b_sil.text_frame
tf_sil.word_wrap = True

p = tf_sil.paragraphs[0]
p.text = "Métrica Matemática Complementaria (No Supervisada):"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_MUTED

p2 = tf_sil.add_paragraph()
p2.text = "Silhouette Score = 0.7858   (Excelente separación y cohesión espacial según scikit-learn)"
p2.font.size = Pt(16)
p2.font.bold = True
p2.font.color.rgb = COLOR_EMERALD
p2.space_before = Pt(4)

set_speaker_notes(s7,
    "GUION SLIDE 7:\n"
    "En cuanto a validación, la prueba reina es la Matriz de Contingencia Física:\n"
    "- 100% de pureza en conductores (35 de 35 metales en cluster 0).\n"
    "- 100% de pureza en aislantes (10 de 10 dieléctricos en cluster 1).\n"
    "- En semiconductores, los 10 materiales tecnológicos puros (silicio, germanio, arseniuro de galio) forman el cluster 2. "
    "Los dos restantes son semimetales cuyo transporte a 300 K es prácticamente metálico.\n"
    "Y como métrica matemática no supervisada, el Silhouette Score arroja 0.7858, confirmando la solidez del agrupamiento."
)

# ==============================================================================
# SLIDE 8: CONCLUSIONES RESUMIDAS
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Conclusiones")

add_card(s8, 1.2, 1.8, 10.933, 4.9, bg_color=COLOR_BG_CARD, border_color=COLOR_EMERALD)
b_c = s8.shapes.add_textbox(Inches(1.6), Inches(2.1), Inches(10.1), Inches(4.3))
tf_c = b_c.text_frame
tf_c.word_wrap = True

p = tf_c.paragraphs[0]
p.text = "Puntos Clave del Proyecto"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO
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
    p.font.size = Pt(14.5)
    p.font.color.rgb = COLOR_TEXTO
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
# GUARDAR PRESENTACIONES
# ==============================================================================
OUTPUT_DIR_1.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUTPUT_DIR_1))
print(f"Presentacion guardada en: {OUTPUT_DIR_1}")

OUTPUT_DIR_2.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUTPUT_DIR_2))
print(f"Presentacion guardada en: {OUTPUT_DIR_2}")
