"""generar_presentacion_uriel.py

Genera la presentacio PowerPoint (.pptx) en CATALÀ per a Uriel:
- Tots els textos en català (diapositives, notes d'orador, títols).
- Tots els requadres arrodonits amb vora NEGRA sòlida.
- Sense barres/ratlles sota els títols.
- Tot el text unificat en color NEGRE pur i font Arial.
- Totes les fórmules matemàtiques en estil LaTeX Computer Modern incrustades com a imatges.
- Inclou les imatges de l'abans (materiales_antes_clustering.png), el després (clusters_materiales_dbscan.png)
  i el panell comparatiu (comparativa_abans_despres_dbscan.png).
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
FIG_ANTES = BASE_DIR / "problemas" / "5_Materials_Uriel" / "materiales_antes_clustering.png"
FIG_COMPARATIVA_ABANS_DESPRES = BASE_DIR / "problemas" / "5_Materials_Uriel" / "comparativa_abans_despres_dbscan.png"
FIG_BANDAS = FIG_DIR / "esquema_bandas_materiales.png"
FIG_COMPARATIVA = FIG_DIR / "comparativa_kmeans_dbscan.png"
FIG_DATASET = FIG_DIR / "distribucion_escala_rho.png"

# Fórmules LaTeX
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

# Paleta unificada: Tot el text i vores en NEGRE
COLOR_NEGRO = RGBColor(0x00, 0x00, 0x00)
COLOR_BG_CARD = RGBColor(0xFF, 0xFF, 0xFF)      # Blanc pur
COLOR_BORDER_BLACK = RGBColor(0x00, 0x00, 0x00) # Vora NEGRA

def add_header(slide, title_text, category="CPIA · APRENENTATGE NO SUPERVISAT"):
    """Capçalera neta: categoria i títol en negre, sense cap ratlla a sota."""
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_cat = cat_box.text_frame
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = COLOR_NEGRO
    
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.7))
    tf_t = t_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(23)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_NEGRO

def add_card(slide, x, y, w, h, bg_color=COLOR_BG_CARD):
    """Crea un requadre de cantonades arrodonides amb vora NEGRA estricta."""
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
p.text = "CPIA · APRENENTATGE NO SUPERVISAT"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

t_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.7), Inches(1.8))
tf = t_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Classificació de Materials Elèctrics mitjançant DBSCAN"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

sub_box = s1.shapes.add_textbox(Inches(1.3), Inches(3.6), Inches(10.7), Inches(1.0))
tf_sub = sub_box.text_frame
p = tf_sub.paragraphs[0]
p.text = "Descobriment No Supervisat de Fases Quàntiques (Conductors, Semiconductors i Aïllants)"
p.font.size = Pt(17)
p.font.color.rgb = COLOR_NEGRO

meta_box = s1.shapes.add_textbox(Inches(1.3), Inches(4.7), Inches(10.7), Inches(1.5))
tf_m = meta_box.text_frame
p1 = tf_m.paragraphs[0]
p1.text = "Uriel · Grau en Enginyeria Física (UPC)"
p1.font.size = Pt(16)
p1.font.bold = True
p1.font.color.rgb = COLOR_NEGRO

p2 = tf_m.add_paragraph()
p2.text = "Equip: Matías · Martí · Uriel · Arnau Montull"
p2.font.size = Pt(14)
p2.font.color.rgb = COLOR_NEGRO

set_speaker_notes(s1,
    "GUIÓ SLIDE 1:\n"
    "Bon dia tribunal i companys. Sóc l'Uriel i presento la classificació no supervisada de materials elèctrics mitjançant DBSCAN."
)

# ==============================================================================
# SLIDE 2: DEFINICIÓ DEL PROBLEMA I LES 3 FASES (BANDES + FÓRMULES LATEX)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "El Problema Físic: Estructura de Bandes i Signatures Tèrmiques")

# Requadre superior amb vora negra per a les fórmules LaTeX
add_card(s2, 0.8, 1.45, 11.733, 1.25)

tit_f = s2.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(0.3))
p = tit_f.text_frame.paragraphs[0]
p.text = "Equacions Macroscòpiques de Transport Elèctric:"
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

if LATEX_TRANSPORTE.exists():
    s2.shapes.add_picture(str(LATEX_TRANSPORTE), Inches(2.4), Inches(1.82), width=Inches(8.5))

if FIG_BANDAS.exists():
    s2.shapes.add_picture(str(FIG_BANDAS), Inches(0.8), Inches(2.85), width=Inches(11.733))

set_speaker_notes(s2,
    "GUIÓ SLIDE 2:\n"
    "Definim el problema físic a partir de les equacions de transport:\n"
    "- La variació tèrmica de la resistivitat rho(T) i la seva derivada tèrmica alfa.\n"
    "- Metalls: bandes solapades, electrons lliures, alfa positiu per xocs amb fonons de la xarxa.\n"
    "- Semiconductors: bandgap moderat, alfa negatiu per activació tèrmica exponencial segons Boltzmann.\n"
    "- Aïllants: bandgap colossal (> 5 eV), sense portadors lliures a 300 K, alfa nul i resistivitat gegantina."
)

# ==============================================================================
# SLIDE 3: DATASET I CLASSIFICACIÓ SENSE ETIQUETES (FOTO ABANS DEL CLUSTERING)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "Dataset Experimental i Espai de Treball (log₁₀ρ, α)")

add_card(s3, 0.8, 1.6, 4.6, 5.3)
b_data = s3.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(4.2), Inches(5.0))
tf_d = b_data.text_frame
tf_d.word_wrap = True

p = tf_d.paragraphs[0]
p.text = "Com classificar sense etiquetes?"
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

if LATEX_COORDENADAS.exists():
    s3.shapes.add_picture(str(LATEX_COORDENADAS), Inches(1.0), Inches(2.3), width=Inches(4.1))

b_data2 = s3.shapes.add_textbox(Inches(1.0), Inches(3.1), Inches(4.2), Inches(3.7))
tf_d2 = b_data2.text_frame
tf_d2.word_wrap = True

d_items = [
    ("57 Materials reals:", " Metalls purs, aliatges, semiconductors i dielèctrics."),
    ("30 ordres de magnitud:", " De conductors (~10⁻⁸ Ω·m) a tefló (> 10²² Ω·m)."),
    ("Compressió logarítmica:", " Evita el col·lapse numèric a l'origen."),
    ("Signatura quàntica:", " α delata l'origen microscòpic del transport."),
    ("Dades sense etiquetar:", " L'algorisme ha de descobrir l'estructura sol.")
]
for i, (tit, desc) in enumerate(d_items):
    p = tf_d2.paragraphs[0] if i == 0 else tf_d2.add_paragraph()
    p.text = f"• {tit}{desc}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(7)

# Imatge del pla ABANS del clustering
if FIG_ANTES.exists():
    s3.shapes.add_picture(str(FIG_ANTES), Inches(5.6), Inches(1.6), width=Inches(6.9))
elif FIG_DATASET.exists():
    s3.shapes.add_picture(str(FIG_DATASET), Inches(5.6), Inches(1.9), width=Inches(6.9))

set_speaker_notes(s3,
    "GUIÓ SLIDE 3:\n"
    "Disposem de 57 materials reals al dataset.\n"
    "A la dreta veiem l'espai bidimensional físic ABANS d'aplicar cap algorisme: els materials en brut sense etiquetes. "
    "El logaritme de resistivitat desplega els 30 ordres de magnitud i alfa separa els règims microscòpics."
)

# ==============================================================================
# SLIDE 4: PER QUÈ DBSCAN I NO K-MEANS? (LLISTA AVANTATGES/INCONVENIENTS + FIGURA)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "Per què DBSCAN i no K-Means?")

add_card(s4, 0.8, 1.6, 4.8, 5.3)
b_vs = s4.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(4.4), Inches(5.0))
tf_vs = b_vs.text_frame
tf_vs.word_wrap = True

p = tf_vs.paragraphs[0]
p.text = "K-Means (Inadequat en aquest domini)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

km_list = [
    "Assumeix grups esfèrics i isodensos (igual variància).",
    "Fractura el grup dispers d'aïllants.",
    "Exigeix prefixar 'k' a priori de forma arbitrària.",
    "No detecta soroll: força anomalies a tenir clúster."
]
for l in km_list:
    p = tf_vs.add_paragraph()
    p.text = f"✖  {l}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(4)

p_db = tf_vs.add_paragraph()
p_db.text = "\nDBSCAN (Elecció Òptima)"
p_db.font.size = Pt(15)
p_db.font.bold = True
p_db.font.color.rgb = COLOR_NEGRO

db_list = [
    "Connecta per densitat local de qualsevol forma.",
    "Tolera metalls hiperdensos i aïllants laxos.",
    "Descobreix el nombre de clústers sense prefixar k.",
    "Etiqueta soroll i anomalies de forma nativa (-1)."
]
for l in db_list:
    p = tf_vs.add_paragraph()
    p.text = f"✔  {l}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(4)

if FIG_COMPARATIVA.exists():
    s4.shapes.add_picture(str(FIG_COMPARATIVA), Inches(5.8), Inches(1.8), width=Inches(6.7))

set_speaker_notes(s4,
    "GUIÓ SLIDE 4:\n"
    "Pregunta clau: per què DBSCAN i no K-Means?\n"
    "Al gràfic de la dreta es veu clar: K-Means imposa fronteres esfèriques forçades. "
    "En tenir metalls ultra concentrats i aïllants dispersos, K-Means falla. "
    "DBSCAN segueix els camins de densitat natural i aïlla punts atípics com a soroll."
)

# ==============================================================================
# SLIDE 5: METODOLOGIA I PARÀMETRES (NOMÉS FÓRMULES LATEX)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "Metodologia Matemàtica: Fórmules i Paràmetres")

w_box = 3.65
h_box = 5.2
y_s5 = 1.6

# 1. Estandarditzacio Z-Score
add_card(s5, 0.8, y_s5, w_box, h_box)
b_f1 = s5.shapes.add_textbox(Inches(1.0), Inches(y_s5 + 0.15), Inches(w_box - 0.4), Inches(1.0))
p = b_f1.text_frame.paragraphs[0]
p.text = "1. Estandardització Z-Score\n(Implementada amb NumPy)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

if LATEX_ZSCORE.exists():
    s5.shapes.add_picture(str(LATEX_ZSCORE), Inches(0.95), Inches(y_s5 + 0.95), width=Inches(3.35))

b_f1_desc = s5.shapes.add_textbox(Inches(1.0), Inches(y_s5 + 2.45), Inches(w_box - 0.4), Inches(2.7))
tf_1_desc = b_f1_desc.text_frame
tf_1_desc.word_wrap = True

f1_sub = [
    "μ = Mitjana mostral per columna",
    "σ = Desviació estàndard típica",
    "Resultat: Mitjana = 0, Variància = 1",
    "Imprescindible: equipara el rang de log₁₀ρ (~31) amb el d'α (~0.08) per a la distància euclidiana."
]
for i, item in enumerate(f1_sub):
    p = tf_1_desc.paragraphs[0] if i == 0 else tf_1_desc.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(5)

# 2. Criteri de Veinat DBSCAN
add_card(s5, 4.85, y_s5, w_box, h_box)
b_f2 = s5.shapes.add_textbox(Inches(5.05), Inches(y_s5 + 0.15), Inches(w_box - 0.4), Inches(1.0))
p = b_f2.text_frame.paragraphs[0]
p.text = "2. Criteri de Nucli\n(DBSCAN Espacial)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

if LATEX_NUCLEO.exists():
    s5.shapes.add_picture(str(LATEX_NUCLEO), Inches(5.0), Inches(y_s5 + 0.95), width=Inches(3.35))

b_f2_desc = s5.shapes.add_textbox(Inches(5.05), Inches(y_s5 + 2.45), Inches(w_box - 0.4), Inches(2.7))
tf_2_desc = b_f2_desc.text_frame
tf_2_desc.word_wrap = True

f2_sub = [
    "d(p, q) = Distància Euclidiana en 2D",
    "Punt Nucli (Core Point):",
    "   |N_ε(p)| ≥ min_samples",
    "Punt Frontera (Border):",
    "   Assolible des d'un nucli",
    "Soroll (Noise):",
    "   No assolible (|N_ε| < min_samples)"
]
for i, item in enumerate(f2_sub):
    p = tf_2_desc.paragraphs[0] if i == 0 else tf_2_desc.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(4)

# 3. Parametres fixats
add_card(s5, 8.9, y_s5, w_box, h_box)
b_f3 = s5.shapes.add_textbox(Inches(9.1), Inches(y_s5 + 0.15), Inches(w_box - 0.4), Inches(1.0))
p = b_f3.text_frame.paragraphs[0]
p.text = "3. Paràmetres Fixats\n(Criteri Objectiu)"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

if LATEX_PARAMETROS.exists():
    s5.shapes.add_picture(str(LATEX_PARAMETROS), Inches(9.05), Inches(y_s5 + 0.95), width=Inches(3.35))

b_f3_desc = s5.shapes.add_textbox(Inches(9.1), Inches(y_s5 + 2.45), Inches(w_box - 0.4), Inches(2.7))
tf_3_desc = b_f3_desc.text_frame
tf_3_desc.word_wrap = True

f3_sub = [
    "min_samples = 3:",
    "   Regla canònica k ≥ d + 1 (dimensió d = 2).",
    "ε = 0.65:",
    "   Determinat mitjançant gràfic k-NN (colze).",
    "   Finestra òptima que aïlla aïllants sense fusionar metalls.",
    "Execució: scikit-learn DBSCAN"
]
for i, item in enumerate(f3_sub):
    p = tf_3_desc.paragraphs[0] if i == 0 else tf_3_desc.add_paragraph()
    p.text = f"• {item}"
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(5)

set_speaker_notes(s5,
    "GUIÓ SLIDE 5:\n"
    "En metodologia: fórmules en LaTeX clares i netes.\n"
    "1. Escalat Z-Score manual amb NumPy per igualar variàncies.\n"
    "2. Criteri de nucli de DBSCAN: punts amb almenys min_samples veïns en radi èpsilon.\n"
    "3. Hiperparàmetres fixats rigorosament: min_samples=3 (dimensió + 1) i èpsilon=0.65 obtingut pel colze k-NN."
)

# ==============================================================================
# SLIDE 6: COMPARATIVA DIRECTA ABANS I DESPRÉS DE L'AGRUPAMENT
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)

t_box = s6.shapes.add_textbox(Inches(0.8), Inches(0.25), Inches(11.7), Inches(0.6))
p = t_box.text_frame.paragraphs[0]
p.text = "Resultat DBSCAN: Abans i Després de l'Agrupament"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

sub_t = t_box.text_frame.add_paragraph()
sub_t.text = "Dades Experimentals en Brut vs. 3 Clústers Purs Descoberts (ε = 0.65, min_samples = 3)"
sub_t.font.size = Pt(13)
sub_t.font.color.rgb = COLOR_NEGRO

if FIG_COMPARATIVA_ABANS_DESPRES.exists():
    s6.shapes.add_picture(str(FIG_COMPARATIVA_ABANS_DESPRES), Inches(0.8), Inches(1.3), width=Inches(11.733))
elif FIG_CLUSTERS.exists():
    s6.shapes.add_picture(str(FIG_CLUSTERS), Inches(1.1), Inches(1.15), width=Inches(11.1))

set_speaker_notes(s6,
    "GUIÓ SLIDE 6:\n"
    "Aquest és el panell comparatiu d'abans i després en pantalla gran:\n"
    "- A l'esquerra: les 57 dades experimentals en brut tal com entren a l'algorisme, sense etiquetes de classe.\n"
    "- A la dreta: el descobriment autònom de les 3 classes físiques pures per connectivitat de densitat amb DBSCAN:\n"
    "  • Clúster 0 (ambre): 35 metalls conductors amb alfa > 0.\n"
    "  • Clúster 1 (blau): 10 aïllants dielèctrics amb alfa proper a zero i resistivitat gegant.\n"
    "  • Clúster 2 (verd): 10 semiconductors per sota de la frontera física alfa = 0.\n"
    "- La línia d'alfa = 0 separa clarament la conducció per fonons de l'activació tèrmica."
)

# ==============================================================================
# SLIDE 7: VALIDACIÓ EXPERIMENTAL: MATRIU DE CONTINGÈNCIA FÍSICA
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "Validació Experimental: Matriu de Contingència Física")

w_card7 = 3.65
h_card7 = 3.4
y_card7 = 1.6

# Conductors
add_card(s7, 0.8, y_card7, w_card7, h_card7)
bc = s7.shapes.add_textbox(Inches(1.0), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfc = bc.text_frame
tfc.word_wrap = True
p = tfc.paragraphs[0]
p.text = "Conductors (Metalls)"
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
p_p.text = "100 % Puresa"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_NEGRO
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfc.add_paragraph()
p_sub.text = "\nAssignats íntegrament al Clúster 0. Zero falsos negatius."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_NEGRO

# Aïllants
add_card(s7, 4.85, y_card7, w_card7, h_card7)
ba = s7.shapes.add_textbox(Inches(5.05), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfa = ba.text_frame
tfa.word_wrap = True
p = tfa.paragraphs[0]
p.text = "Aïllants (Dielèctrics)"
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
p_p.text = "100 % Puresa"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_NEGRO
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfa.add_paragraph()
p_sub.text = "\nAssignats íntegrament al Clúster 1. Coincidència total amb la física."
p_sub.font.size = Pt(11)
p_sub.font.color.rgb = COLOR_NEGRO

# Semiconductors
add_card(s7, 8.9, y_card7, w_card7, h_card7)
bs = s7.shapes.add_textbox(Inches(9.1), Inches(y_card7 + 0.2), Inches(w_card7 - 0.4), Inches(3.0))
tfs = bs.text_frame
tfs.word_wrap = True
p = tfs.paragraphs[0]
p.text = "Semiconductors"
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
p_p.text = "83.3 % Puresa"
p_p.font.size = Pt(16)
p_p.font.bold = True
p_p.font.color.rgb = COLOR_NEGRO
p_p.alignment = PP_ALIGN.CENTER

p_sub = tfs.add_paragraph()
p_sub.text = "\n10 al Clúster 2. 2 semimetalls classificats al clúster 0 per conducció cuasimetàl·lica."
p_sub.font.size = Pt(10.5)
p_sub.font.color.rgb = COLOR_NEGRO

# Barra inferior amb la silueta en LaTeX
add_card(s7, 0.8, 5.25, 11.733, 1.55)
b_sil = s7.shapes.add_textbox(Inches(1.1), Inches(5.35), Inches(11.1), Inches(0.35))
p = b_sil.text_frame.paragraphs[0]
p.text = "Mètrica Matemàtica Complementària (No Supervisada):"
p.font.size = Pt(11.5)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO

if LATEX_SILHOUETTE.exists():
    s7.shapes.add_picture(str(LATEX_SILHOUETTE), Inches(2.2), Inches(5.75), width=Inches(8.8))

set_speaker_notes(s7,
    "GUIÓ SLIDE 7:\n"
    "Pel que fa a validació, la prova reina és la Matriu de Contingència Física:\n"
    "- 100% de puresa en conductors (35 de 35 metalls al clúster 0).\n"
    "- 100% de puresa en aïllants (10 de 10 dielèctrics al clúster 1).\n"
    "- En semiconductors, els 10 materials tecnològics purs formen el clúster 2. "
    "Els dos restants són semimetalls amb transport cuasimetàl·lic a 300 K.\n"
    "I com a mètrica matemàtica complementària, la fórmula de Silhouette Score dona 0.7858."
)

# ==============================================================================
# SLIDE 8: CONCLUSIONS RESUMIDES
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "Conclusions")

add_card(s8, 1.2, 1.7, 10.933, 5.0)
b_c = s8.shapes.add_textbox(Inches(1.6), Inches(2.0), Inches(10.1), Inches(4.4))
tf_c = b_c.text_frame
tf_c.word_wrap = True

p = tf_c.paragraphs[0]
p.text = "Punts Clau del Projecte"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = COLOR_NEGRO
p.space_after = Pt(14)

concl_puntos = [
    ("Física de bandes sense supervisió:", " DBSCAN descobreix de manera autònoma les 3 fases de conducció (conductors, aïllants i semiconductors) a partir de propietats macroscòpiques."),
    ("Immune a densitats dispars:", " Supera K-Means agrupant simultàniament la ultradensitat dels metalls i la dispersió de 12 ordres de magnitud dels aïllants."),
    ("Variables òptimes:", " L'escala logarítmica log₁₀(ρ) i el coeficient tèrmic quàntic α són suficients per separar completament els règims de transport."),
    ("Validació rotunda:", " 100% de puresa en conductors i aïllants amb Silhouette Score = 0.7858.")
]
for tit, desc in concl_puntos:
    p = tf_c.add_paragraph()
    p.text = f"✔  {tit} {desc}"
    p.font.size = Pt(14)
    p.font.color.rgb = COLOR_NEGRO
    p.space_after = Pt(12)

set_speaker_notes(s8,
    "GUIÓ SLIDE 8:\n"
    "Per concloure:\n"
    "1. DBSCAN demostra que la densitat espacial macroscòpica reflecteix fidelment la física quàntica de bandes.\n"
    "2. Ha demostrat ser l'eina adequada davant K-Means en tolerar densitats desiguals.\n"
    "3. Amb només dues variables físiques i una estandardització rigorosa, s'obté un 100% de puresa en conductors i aïllants.\n"
    "Moltes gràcies."
)

# ==============================================================================
# APLICAR FONT ARIAL A TOTA LA PRESENTACIÓ
# ==============================================================================
def aplicar_fuente_arial(presentation):
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    paragraph.font.name = "Arial"
                    for run in paragraph.runs:
                        run.font.name = "Arial"

aplicar_fuente_arial(prs)

# ==============================================================================
# GUARDAR PRESENTACIÓ EN AMBDUES UBICACIONS
# ==============================================================================
prs.save(OUTPUT_DIR_1)
print(f"Presentacio guardada a: {OUTPUT_DIR_1}")

try:
    prs.save(OUTPUT_DIR_2)
    print(f"Presentacio guardada a: {OUTPUT_DIR_2}")
except PermissionError:
    print(f"Avís: No s'ha pogut sobreescriure {OUTPUT_DIR_2} (pot estar obert a PowerPoint).")
