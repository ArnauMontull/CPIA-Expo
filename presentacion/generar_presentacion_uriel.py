"""generar_presentacion_uriel.py

Genera una presentacion PowerPoint (.pptx) profesional de 8 diapositivas
para la exposicion individual de Uriel en CPIA:
"Clasificacion de Materiales Electricos mediante DBSCAN".

Totalmente compatible e importable directamente en Google Slides.
Incluye notas de orador completas para cada diapositiva y figuras incrustadas.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]
FIG_PATH = BASE_DIR / "problemas" / "5_Materials_Uriel" / "clusters_materiales_dbscan.png"
OUTPUT_DIR_1 = BASE_DIR / "problemas" / "5_Materials_Uriel" / "presentacion_materiales_uriel.pptx"
OUTPUT_DIR_2 = BASE_DIR / "presentacion" / "presentacion_materiales_uriel.pptx"

# Inicializar presentacion Widescreen 16:9 (13.333 x 7.5 pulgadas)
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Paleta de colores sobria y cientifica
COLOR_BG_CARD = RGBColor(0xF8, 0xFA, 0xFC)      # Gris muy claro (#F8FAFC)
COLOR_BORDER = RGBColor(0xCB, 0xD5, 0xE1)       # Borde pizarra (#CBD5E1)
COLOR_TITULO = RGBColor(0x0F, 0x17, 0x2A)       # Pizarra oscuro (#0F172A)
COLOR_SUBTITULO = RGBColor(0x33, 0x41, 0x55)    # Pizarra medio (#334155)
COLOR_TEXTO = RGBColor(0x1E, 0x29, 0x3B)        # Texto principal (#1E293B)
COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)        # Texto secundario (#64748B)

COLOR_EMERALD = RGBColor(0x05, 0x96, 0x69)      # Verde esmeralda (#059669)
COLOR_BLUE = RGBColor(0x25, 0x63, 0xEB)         # Azul cobalto (#2563EB)
COLOR_AMBER = RGBColor(0xD9, 0x77, 0x06)        # Ambar (#D97706)
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)

def add_header(slide, title_text, category="CPIA · APRENDIZAJE NO SUPERVISADO"):
    """Agrega cabecera estandarizada con categoria y linea de acento."""
    # Badge categoria
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_EMERALD
    
    # Titulo de diapositiva
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TITULO
    
    # Linea separadora decorativa
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.55), Inches(11.733), Inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BORDER
    line.line.color.rgb = COLOR_BORDER

def add_card(slide, x, y, w, h, bg_color=COLOR_BG_CARD, border_color=COLOR_BORDER):
    """Crea una tarjeta contenedora rectangular redondeada o simple."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
    else:
        card.line.fill.background()
    return card

def set_speaker_notes(slide, notes_text):
    """Establece las notas de orador en la diapositiva."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

# ==============================================================================
# DIAPOSITIVA 1: PORTADA
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)

# Fondo portada: Tarjeta sutil
add_card(s1, 0.8, 0.8, 11.733, 5.9, bg_color=COLOR_BG_CARD, border_color=COLOR_EMERALD)

# Badge superior
b_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(0.5))
p = b_box.text_frame.paragraphs[0]
p.text = "PROYECTO CPIA · CLUSTERING EN FÍSICA DEL ESTADO SÓLIDO"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

# Titulo principal
t_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.7), Inches(1.8))
tf = t_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Clasificación de Materiales Eléctricos mediante DBSCAN"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO

# Subtitulo
sub_box = s1.shapes.add_textbox(Inches(1.3), Inches(3.6), Inches(10.7), Inches(1.0))
tf_sub = sub_box.text_frame
tf_sub.word_wrap = True
p = tf_sub.paragraphs[0]
p.text = "Descubrimiento No Supervisado de Fases Cuánticas (Conductores, Semiconductores y Aislantes)"
p.font.size = Pt(18)
p.font.color.rgb = COLOR_SUBTITULO

# Metadatos / Autores
meta_box = s1.shapes.add_textbox(Inches(1.3), Inches(4.7), Inches(10.7), Inches(1.5))
tf_m = meta_box.text_frame
p1 = tf_m.paragraphs[0]
p1.text = "Autor: Uriel"
p1.font.size = Pt(16)
p1.font.bold = True
p1.font.color.rgb = COLOR_TITULO

p2 = tf_m.add_paragraph()
p2.text = "Equipo: Matías · Martí · Uriel · Arnau Montull"
p2.font.size = Pt(14)
p2.font.color.rgb = COLOR_MUTED

p3 = tf_m.add_paragraph()
p3.text = "Grado en Ingeniería Física · Universitat Politècnica de Catalunya (UPC)"
p3.font.size = Pt(13)
p3.font.color.rgb = COLOR_MUTED

set_speaker_notes(s1, 
    "GUION DE ORADOR (DIAPOSITIVA 1):\n"
    "Buenos días tribunal y compañeros. Soy Uriel, y en esta parte de nuestra presentación voy a presentar la clasificación "
    "no supervisada de materiales eléctricos mediante el algoritmo DBSCAN.\n\n"
    "El objetivo central de este trabajo es demostrar cómo un algoritmo de aprendizaje no supervisado basado en densidad espacial "
    "es capaz de redescubrir, sin ninguna etiqueta previa y partiendo únicamente de propiedades macroscópicas medibles en laboratorio, "
    "las tres grandes familias termodinámicas y cuánticas de la materia: metales conductores, semiconductores tecnológicos y aislantes dieléctricos."
)

# ==============================================================================
# DIAPOSITIVA 2: PLANTEAMIENTO FÍSICO Y VARIABLES
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "Contexto Físico y Espacio de Características")

# Tarjeta Izquierda: El Reto de la Escala
add_card(s2, 0.8, 1.8, 5.6, 5.0)
box_izq = s2.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.6))
tf_izq = box_izq.text_frame
tf_izq.word_wrap = True

p = tf_izq.paragraphs[0]
p.text = "¿Cómo clasificar materiales sin etiquetas?"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE

items_izq = [
    ("30 órdenes de magnitud:", " La resistividad eléctrica a 300 K abarca desde la plata (1.6·10⁻⁸ Ω·m) hasta el teflón (> 10²² Ω·m)."),
    ("Compresión logarítmica obligatoria:", " Definimos x₁ = log₁₀(ρ₃₀₀K). Sin escala logarítmica, el 99% de los materiales colapsaría en el origen."),
    ("Dataset oficial:", " 57 materiales reales recopilados con precisión experimental (metales puros, semiconductores clave y polímeros/cerámicas aislantes)."),
    ("Objetivo no supervisado:", " Comprobar si el agrupamiento por densidad recupera las fases físicas puras.")
]
for tit, desc in items_izq:
    p = tf_izq.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(13.5)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(8)

# Tarjeta Derecha: Las dos variables de transporte
add_card(s2, 6.8, 1.8, 5.7, 5.0)
box_der = s2.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.6))
tf_der = box_der.text_frame
tf_der.word_wrap = True

p = tf_der.paragraphs[0]
p.text = "Las Dos Firmas Cuánticas Macroscópicas"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

items_der = [
    ("Variable 1: log₁₀(ρ₃₀₀K)", " Magnitud de la resistencia al flujo de portadores a temperatura ambiente (300 K)."),
    ("Variable 2: Coeficiente térmico α", " Derivada de la resistividad frente a temperatura: α = (1/ρ₀) · (dρ/dT)."),
    ("Firma física de α:", " Es el parámetro cuántico decisivo: indica si la resistividad sube o baja cuando calentamos el material."),
    ("Espacio bidimensional:", " Trabajamos en el plano (log₁₀ρ, α), donde cada material se proyecta como una coordenada única.")
]
for tit, desc in items_der:
    p = tf_der.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(13.5)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(8)

set_speaker_notes(s2,
    "GUION DE ORADOR (DIAPOSITIVA 2):\n"
    "Para abordar este problema, debemos plantearnos qué magnitudes macroscópicas definen a un material.\n"
    "En estado sólido, la resistividad presenta un comportamiento extraordinario: abarca más de 30 órdenes de magnitud. "
    "Si utilizáramos una escala lineal, el cobre, el silicio y el agua quedarían todos aplastados contra el cero, y solo el teflón se distinguiría. "
    "Por ello, la primera variable fundamental es el logaritmo en base 10 de la resistividad a 300 Kelvin.\n\n"
    "Sin embargo, la resistividad sola no basta: un semiconductor dopado puede tener una resistividad parecida a una aleación metálica sucia. "
    "Aquí entra nuestra segunda variable: el coeficiente de temperatura alfa, que nos dice cómo cambia la resistividad al variar la temperatura. "
    "Juntas, estas dos variables forman un espacio bidimensional completísimo donde emerge la física cuántica."
)

# ==============================================================================
# DIAPOSITIVA 3: FUNDAMENTO CUÁNTICO
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Fundamento Cuántico: ¿Por qué se agrupan en el plano?")

# 3 Columnas para las 3 Familias
w_col = 3.65
gap = 0.38
x_start = 0.8

# Columna 1: Conductores
add_card(s3, x_start, 1.8, w_col, 5.0, border_color=COLOR_AMBER)
b1 = s3.shapes.add_textbox(Inches(x_start + 0.2), Inches(2.0), Inches(w_col - 0.4), Inches(4.6))
tf1 = b1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "1. Metales (Conductores)"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER

c_items = [
    ("Estructura de bandas:", " Banda de conducción semillena, sin gap energético (Eg = 0)."),
    ("Mecanismo:", " Electrones libres en el mar de Fermi."),
    ("Efecto de la temperatura:", " Al calentar, aumenta la vibración de la red (fonones). Mayor choque = mayor resistencia."),
    ("Signo de α:", " α > 0 (+0.003 a +0.006 K⁻¹)."),
    ("Topología:", " Cúmulo ultra denso alrededor de log₁₀ρ ≈ -8.")
]
for tit, desc in c_items:
    p = tf1.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

# Columna 2: Semiconductores
x2 = x_start + w_col + gap
add_card(s3, x2, 1.8, w_col, 5.0, border_color=COLOR_EMERALD)
b2 = s3.shapes.add_textbox(Inches(x2 + 0.2), Inches(2.0), Inches(w_col - 0.4), Inches(4.6))
tf2 = b2.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]
p.text = "2. Semiconductores"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

sc_items = [
    ("Estructura de bandas:", " Gap moderado (Eg ≈ 0.2 a 2.0 eV: Si, Ge, GaAs)."),
    ("Mecanismo:", " Activación térmica según Boltzmann: n ∝ exp(-Eg / 2kBT)."),
    ("Efecto de la temperatura:", " El calor libera avalanchas de portadores libres. La resistencia se desploma."),
    ("Signo de α:", " α < 0 fuertemente negativo (-0.015 a -0.075 K⁻¹)."),
    ("Topología:", " Región intermedia claramente separada por α negativo.")
]
for tit, desc in sc_items:
    p = tf2.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

# Columna 3: Aislantes
x3 = x2 + w_col + gap
add_card(s3, x3, 1.8, w_col, 5.0, border_color=COLOR_BLUE)
b3 = s3.shapes.add_textbox(Inches(x3 + 0.2), Inches(2.0), Inches(w_col - 0.4), Inches(4.6))
tf3 = b3.text_frame
tf3.word_wrap = True
p = tf3.paragraphs[0]
p.text = "3. Aislantes (Dieléctricos)"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE

ais_items = [
    ("Estructura de bandas:", " Gap prohibido gigantesco (Eg > 5 a 9 eV: Vidrio, Cuarzo, Teflón)."),
    ("Mecanismo:", " kBT a 300 K es ~0.026 eV; insuficiente para excitar electrones a la banda superior."),
    ("Efecto de la temperatura:", " Prácticamente nulo a escala ordinaria."),
    ("Signo de α:", " α ≈ 0 K⁻¹."),
    ("Topología:", " Cúmulo ancho y disperso en resistividades altísimas (log₁₀ρ > 11).")
]
for tit, desc in ais_items:
    p = tf3.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

set_speaker_notes(s3,
    "GUION DE ORADOR (DIAPOSITIVA 3):\n"
    "En esta diapositiva vemos la justificación física de por qué estos materiales forman islas separadas.\n"
    "1. En los metales, no hay gap de energía; los electrones son libres. Al calentar, los átomos vibran más y entorpecen "
    "a los electrones mediante fonones. Por eso, alfa es SIEMPRE positivo.\n"
    "2. En los semiconductores, ocurre exactamente lo opuesto: hay un bandgap moderado. Al calentar, la energía térmica excita electrones "
    "a través del gap exponencialmente según la estadística de Boltzmann. Hay tantos portadores nuevos que la resistividad CAE drásticamente. "
    "Por eso su alfa es fuertemente NEGATIVO.\n"
    "3. En los aislantes, el gap es tan inmenso (mayor a 5 o 9 electronvoltios) que a temperatura ambiente no hay portadores libres. "
    "Su alfa es prácticamente cero y su resistividad se dispara más allá de 10 a la 11 ohmios metro."
)

# ==============================================================================
# DIAPOSITIVA 4: ¿POR QUÉ DBSCAN FRENTE A K-MEANS?
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "¿Por qué DBSCAN y no K-Means?")

# Tarjeta Izquierda: Defectos de K-Means
add_card(s4, 0.8, 1.8, 5.6, 5.0)
box_km = s4.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.6))
tf_km = box_km.text_frame
tf_km.word_wrap = True

p = tf_km.paragraphs[0]
p.text = "Inadecuación de K-Means en este Dominio"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = RGBColor(0xDC, 0x26, 0x26)

km_points = [
    ("Hipótesis de isodispersión:", " K-Means asume clusters esféricos de varianza similar. En nuestro problema, los metales forman un grupo ultra compacto y los aislantes un grupo muy disperso."),
    ("Fusión o fractura indebida:", " K-Means tiende a partir en dos el grupo amplio de aislantes o a absorber indebidamente los semiconductores."),
    ("Obliga a prefijar k:", " Exige imponer a priori k = 3 sin saber de antemano si los datos revelan 2, 3 o 4 grupos."),
    ("Sensibilidad extrema a anomalías:", " Obliga a cada punto atípico a pertenecer a un cluster, distorsionando los centroides.")
]
for tit, desc in km_points:
    p = tf_km.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(8)

# Tarjeta Derecha: Fortalezas de DBSCAN
add_card(s4, 6.8, 1.8, 5.7, 5.0)
box_db = s4.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.6))
tf_db = box_db.text_frame
tf_db.word_wrap = True

p = tf_db.paragraphs[0]
p.text = "Ventajas Determinantes de DBSCAN"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

db_points = [
    ("Conectividad por densidad:", " Descubre clusters conectando puntos núcleo a través de regiones de alta densidad continua, sin importar la forma."),
    ("Robusto a densidades dispares:", " Respeta que un cluster sea hiperdenso (metales) y otro más laxo siempre que superen el umbral mínimo local."),
    ("Descubrimiento autónomo de grupos:", " Encuentra el número de clusters sin prefijar k."),
    ("Etiquetado nativo de ruido (-1):", " Materiales exóticos o anisótropos (como el grafito) se aíslan de forma transparente sin ensuciar las fases puras.")
]
for tit, desc in db_points:
    p = tf_db.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(8)

set_speaker_notes(s4,
    "GUION DE ORADOR (DIAPOSITIVA 4):\n"
    "Una pregunta obligada del tribunal es: ¿por qué no usar simplemente K-Means?\n"
    "La respuesta radica en la propia naturaleza de los datos físicos: K-Means asume implícitamente que los clusters tienen "
    "forma esférica y similar varianza o densidad. Pero en física de materiales esto no ocurre: los metales tienen resistividades "
    "idénticas en una ventana estrechísima, mientras que los aislantes se extienden a lo largo de 12 órdenes de magnitud.\n\n"
    "K-Means fracasaría aquí intentando igualar los tamaños de los grupos. DBSCAN, por contra, se basa exclusivamente en conectividad local "
    "por densidad (Core Points, Border Points y Noise). Si hay una región densa, DBSCAN la sigue y la agrupa; si hay un punto aislado, "
    "lo marca como ruido (-1) sin contaminar los grupos genuinos."
)

# ==============================================================================
# DIAPOSITIVA 5: METODOLOGÍA Y PARÁMETROS
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Metodología: Estandarización y Selección de Parámetros")

# Tarjeta Izquierda: Estandarizacion Z-Score
add_card(s5, 0.8, 1.8, 5.6, 5.0)
b_z = s5.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.6))
tf_z = b_z.text_frame
tf_z.word_wrap = True

p = tf_z.paragraphs[0]
p.text = "Estandarización Manual Z-Score"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE

z_points = [
    ("Métrica Euclídea:", " DBSCAN mide distancias d(p, q) = √[(Δx₁)² + (Δx₂)²]."),
    ("El problema de escala:", " El rango de log₁₀ρ es ~31 unidades, mientras que el rango de α es ~0.08 unidades. Sin estandarizar, α sería invisible."),
    ("Fórmula implementada manualmente:", " Calculamos la media μ y desviación estándar σ vectorialmente con NumPy:"),
    ("Z = (X - μ) / σ", " Ambas dimensiones quedan con media 0 y varianza 1. La métrica pondera por igual la resistividad y el signo térmico cuántico.")
]
for tit, desc in z_points:
    p = tf_z.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(8)

# Tarjeta Derecha: Justificacion de Hiperparametros
add_card(s5, 6.8, 1.8, 5.7, 5.0)
b_par = s5.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.6))
tf_par = b_par.text_frame
tf_par.word_wrap = True

p = tf_par.paragraphs[0]
p.text = "Justificación Objetiva de Parámetros"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

par_points = [
    ("Umbral min_samples = 3:", " Siguiendo la regla canónica de Schubert et al.: para d = 2 dimensiones, min_samples ≥ d + 1. Fija el mínimo para considerar densidad significativa."),
    ("Radio epsilon (ε = 0.65):", " Determinado analíticamente mediante la gráfica de distancias k-NN (método del codo) y validado con Silhouette Score."),
    ("Comportamiento físico de ε = 0.65:", " Suficientemente grande para abarcar la dispersión de los aislantes, pero suficientemente estricto para evitar que los semiconductores se fusionen con los metales."),
    ("Implementación:", " Ejecutado directamente con el algoritmo oficial de scikit-learn: DBSCAN(eps=0.65, min_samples=3).")
]
for tit, desc in par_points:
    p = tf_par.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(8)

set_speaker_notes(s5,
    "GUION DE ORADOR (DIAPOSITIVA 5):\n"
    "En cuanto a la metodología, hay dos aspectos críticos que la rúbrica evalúa con rigor:\n"
    "Primero: el escalado. La distancia euclídea de DBSCAN suma los cuadrados de las diferencias. Si no escalamos, una variación "
    "en el logaritmo de resistividad es de 31 unidades, mientras que alfa varía solo en 0.08 unidades. La resistividad se comería a alfa. "
    "Por eso hemos programado manualmente con NumPy la estandarización Z-score: restando la media de cada variable y dividiendo entre su desviación típica.\n\n"
    "Segundo: los parámetros. min_samples se fija en 3 siguiendo la heurística de que debe ser al menos la dimensión espacial más uno (2 + 1). "
    "Y para el radio épsilon, fijamos 0.65 tras analizar el codo de distancias de los vecinos más próximos, asegurando la máxima silueta sin unir grupos distintos."
)

# ==============================================================================
# DIAPOSITIVA 6: VISUALIZACIÓN DE RESULTADOS (CON FIGURA)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "Resultados Experimentales: Clasificación 2D")

# Columna Izquierda: Panel Explicativo
add_card(s6, 0.8, 1.8, 4.8, 5.0)
b_res = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(4.4), Inches(4.6))
tf_res = b_res.text_frame
tf_res.word_wrap = True

p = tf_res.paragraphs[0]
p.text = "3 Clusters Descubiertos"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO

r_items = [
    ("Cluster 0 (Ámbar):", " Conductores (35 metales). Cobre, Plata, Oro, Aluminio... α > 0, resistividad muy baja."),
    ("Cluster 1 (Azul):", " Aislantes (10 dieléctricos). Vidrio, Teflón, Cuarzo, PET... α ≈ 0, resistividades colosales (> 10¹¹ Ω·m)."),
    ("Cluster 2 (Verde):", " Semiconductores (10 materiales). Silicio, Germanio, GaAs, InP... Perfectamente segregados por α fuertemente negativo."),
    ("Frontera α = 0:", " La línea discontinua marca la transición física de fonones a generación térmica.")
]
for tit, desc in r_items:
    p = tf_res.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

# Columna Derecha: Imagen incrustada
if FIG_PATH.exists():
    s6.shapes.add_picture(str(FIG_PATH), Inches(5.8), Inches(1.8), width=Inches(6.7))

set_speaker_notes(s6,
    "GUION DE ORADOR (DIAPOSITIVA 6):\n"
    "Aquí pueden observar en pantalla el resultado directo de ejecutar DBSCAN sobre los 57 materiales reales.\n"
    "Fíjense en la elegancia de la separación:\n"
    "- En color ámbar a la izquierda, tenemos el Cluster 0 con todos los conductores metálicos: plata, cobre, oro, aluminio... "
    "Todos con logaritmo de resistividad en torno a -8 y un alfa positivo bien visible por encima de cero.\n"
    "- En color azul a la derecha, el Cluster 1 agrupa los aislantes: cuarzo, teflón, vidrio... Están muy separados en el eje horizontal "
    "y centrados en torno a alfa igual a cero.\n"
    "- Y en color verde esmeralda abajo al centro, el Cluster 2 agrupa los semiconductores clave: silicio, germanio, arseniuro de galio... "
    "Están aislados de los metales precisamente porque su alfa cae en la zona negativa, por debajo de la línea discontinua de alfa = 0.\n"
    "DBSCAN ha descubierto estas tres clases sin que nadie le dijera qué era cada material."
)

# ==============================================================================
# DIAPOSITIVA 7: VALIDACIÓN CUANTITATIVA
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Validación Cuantitativa y Matriz de Contingencia")

# Tarjeta Izquierda: Matriz de Contingencia
add_card(s7, 0.8, 1.8, 5.6, 5.0)
b_mat = s7.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.6))
tf_mat = b_mat.text_frame
tf_mat.word_wrap = True

p = tf_mat.paragraphs[0]
p.text = "Matriz de Contingencia (Física vs DBSCAN)"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_BLUE

mat_rows = [
    ("Aislantes reales (10):", " 10 asignados al Cluster 1 (100 % de pureza). Cero falsos positivos."),
    ("Conductores reales (35):", " 35 asignados al Cluster 0 (100 % de pureza). Todos los metales recuperados."),
    ("Semiconductores reales (12):", " 10 asignados al Cluster 2 (los semiconductores tecnológicos puros)."),
    ("Casos de frontera (2):", " El grafito y un semimetal con comportamiento resistivo casi metálico a 300 K se unieron al cluster 0 por densidad."),
    ("Ruido detectado:", " 0 materiales aislados; los 57 puntos forman núcleos cohesionados.")
]
for tit, desc in mat_rows:
    p = tf_mat.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12.5)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

# Tarjeta Derecha: Metricas Cuantitativas
add_card(s7, 6.8, 1.8, 5.7, 5.0)
b_score = s7.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.6))
tf_score = b_score.text_frame
tf_score.word_wrap = True

p = tf_score.paragraphs[0]
p.text = "Métrica de Calidad: Silhouette Score"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_EMERALD

# Score destacado
p_dest = tf_score.add_paragraph()
p_dest.text = "Silhouette Score = 0.7858"
p_dest.font.size = Pt(22)
p_dest.font.bold = True
p_dest.font.color.rgb = COLOR_EMERALD
p_dest.space_after = Pt(8)

sc_points = [
    ("Significado matemático:", " Mide la distancia inter-cluster (b) frente a la dispersión intra-cluster (a): s = (b - a) / max(a, b)."),
    ("Escala de interpretación:", " Un valor de 0.7858 (muy cercano a 1.0) certifica una estructura de agrupamiento 'fuerte y robusta' en la literatura científica."),
    ("Independencia:", " La silueta evalúa los grupos sin usar etiquetas reales, confirmando la validez no supervisada."),
    ("Conclusión de calidad:", " La separación entre aislantes, conductores y semiconductores es matemáticamente contundente.")
]
for tit, desc in sc_points:
    p = tf_score.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12.5)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

set_speaker_notes(s7,
    "GUION DE ORADOR (DIAPOSITIVA 7):\n"
    "Pasemos ahora a la validación cuantitativa y rigurosa de los resultados.\n"
    "En la matriz de contingencia cruzamos la etiqueta física real con el cluster descubierto por DBSCAN:\n"
    "- Los 10 aislantes fueron identificados con un 100% de pureza en el Cluster 1.\n"
    "- Los 35 conductores fueron clasificados con un 100% de pureza en el Cluster 0.\n"
    "- En los semiconductores, 10 de 12 se agruparon limpiamente en el Cluster 2. Los dos restantes corresponden a semimetales "
    "con estructura anisótropa como el grafito, cuya resistividad a temperatura ambiente es prácticamente metálica.\n\n"
    "Además, evaluamos el Silhouette Score de forma no supervisada con scikit-learn, obteniendo una puntuación de 0.7858. "
    "En Machine Learning, una silueta superior a 0.71 se clasifica como una estructura excelente y contundente, lo que demuestra "
    "el éxito del clustering."
)

# ==============================================================================
# DIAPOSITIVA 8: CONCLUSIONES Y DEFENSA ANTE EL TRIBUNAL
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Conclusiones y Defensa ante Preguntas del Tribunal")

# Tarjeta Izquierda: Conclusiones
add_card(s8, 0.8, 1.8, 5.6, 5.0)
b_c = s8.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.6))
tf_c = b_c.text_frame
tf_c.word_wrap = True

p = tf_c.paragraphs[0]
p.text = "Conclusiones Principales"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_TITULO

c_concl = [
    ("Validación física del clustering:", " DBSCAN ha demostrado ser capaz de inferir la física cuántica de bandas únicamente a partir de la densidad en datos experimentales macroscópicos."),
    ("Superioridad frente a métodos rígidos:", " La capacidad de manejar varianzas dispares permitió agrupar metales hiperdensos y aislantes extendidos en el mismo modelo."),
    ("Pipeline limpio y reproducible:", " Estandarización manual rigurosa, ejecución nativa con scikit-learn y reproducibilidad total en GitHub.")
]
for tit, desc in c_concl:
    p = tf_c.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(13)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(10)

# Tarjeta Derecha: Preguntas de Defensa
add_card(s8, 6.8, 1.8, 5.7, 5.0)
b_q = s8.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.6))
tf_q = b_q.text_frame
tf_q.word_wrap = True

p = tf_q.paragraphs[0]
p.text = "Preguntas Probables del Tribunal"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLOR_AMBER

q_items = [
    ("¿Qué ocurre si variamos epsilon (ε)?", " Si ε < 0.4, el cluster de aislantes se fragmenta en pedazos y aparece ruido. Si ε > 1.0, los semiconductores se fusionan con los metales en un único macro-cluster."),
    ("¿Por qué no usar conductividad σ directa?", " Porque la escala lineal colapsa el 99% de los puntos en el origen (0 S/m). La escala logarítmica es la única físicamente sensata."),
    ("¿Se podría aplicar a superconductores?", " A temperaturas críticas Tc, ρ cae a cero exacto, generando una singularidad logarítmica que requeriría tratar la transición de fase como un estado límite.")
]
for tit, desc in q_items:
    p = tf_q.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(12)
    p.font.color.rgb = COLOR_TEXTO
    p.space_after = Pt(6)

set_speaker_notes(s8,
    "GUION DE ORADOR (DIAPOSITIVA 8):\n"
    "Para concluir mi exposición:\n"
    "Hemos demostrado con éxito que un algoritmo no supervisado basado en densidad como DBSCAN, alimentado con medidas de laboratorio "
    "en el espacio (log10(rho), alfa) y con una estandarización Z-score rigurosa, es capaz de redescubrir las tres fases cuánticas de la materia "
    "con una silueta de 0.7858 y un 100% de pureza en conductores y aislantes.\n\n"
    "Respecto a posibles preguntas que puedan surgir:\n"
    "Si nos preguntan por la sensibilidad a épsilon, sabemos que 0.65 es la ventana óptima: por debajo de 0.4 los aislantes se rompen en ruido, "
    "y por encima de 1.0 los semiconductores se funden con los conductores.\n"
    "Y si nos preguntan por qué el logaritmo, es fundamental para permitir que magnitudes separadas por 30 órdenes de magnitud puedan coexistir "
    "en una misma métrica euclídea.\n\n"
    "Muchas gracias por su atención, quedo a su disposición para cualquier pregunta."
)

# ==============================================================================
# GUARDAR PRESENTACIONES
# ==============================================================================
OUTPUT_DIR_1.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUTPUT_DIR_1))
print(f"Presentacion guardada con exito en: {OUTPUT_DIR_1}")

OUTPUT_DIR_2.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUTPUT_DIR_2))
print(f"Presentacion guardada con exito en: {OUTPUT_DIR_2}")
