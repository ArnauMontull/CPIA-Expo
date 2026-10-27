# Genera presentacion/expo_arnau.pptx: presentacio sobre el problema de les explosions nuclears (en catala, amb notes de l'orador)
# Les figures venen de presentacion/figuras_cat/ (generades amb presentacion/figuras_cat.py)
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

AQUI = Path(__file__).resolve().parent
FIG = AQUI / 'figuras_cat'

# Paleta: blau fosc (sismograma) amb taronja com a accent, els mateixos colors que les figures
NAVY = RGBColor(0x1B, 0x24, 0x30)
INK = RGBColor(0x11, 0x18, 0x27)
FONS = RGBColor(0xF4, 0xF5, 0xF7)
BLANC = RGBColor(0xFF, 0xFF, 0xFF)
TARONJA = RGBColor(0xE8, 0x71, 0x0A)
BLAU = RGBColor(0x3B, 0x7E, 0xA1)
GRIS = RGBColor(0x5B, 0x63, 0x70)
GRIS_CLAR = RGBColor(0xE3, 0xE6, 0xEA)
VERMELL = RGBColor(0xC0, 0x39, 0x2B)
VERD = RGBColor(0x2E, 0x7D, 0x32)
LLETRA = 'Calibri'

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BUIDA = prs.slide_layouts[6]
numero = [0]


def fons(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def text(slide, x, y, w, h, contingut, mida=18, color=INK, negreta=False, alineacio=PP_ALIGN.LEFT,
         ancora=MSO_ANCHOR.TOP, cursiva=False, espai=6):
    """contingut: text o llista de paragrafs; un paragraf pot ser un text o una llista de (text, negreta, color)."""
    caixa = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    marc = caixa.text_frame
    marc.word_wrap = True
    marc.margin_left = marc.margin_right = marc.margin_top = marc.margin_bottom = 0
    marc.vertical_anchor = ancora
    paragrafs = contingut if isinstance(contingut, list) else [contingut]
    for i, par in enumerate(paragrafs):
        p = marc.paragraphs[0] if i == 0 else marc.add_paragraph()
        p.alignment = alineacio
        p.space_after = Pt(espai)
        trossos = par if isinstance(par, list) else [(par, negreta, color)]
        for t, n, c in trossos:
            r = p.add_run()
            r.text = t
            r.font.name = LLETRA
            r.font.size = Pt(mida)
            r.font.bold = n
            r.font.italic = cursiva
            r.font.color.rgb = c
    return caixa


def targeta(slide, x, y, w, h, color=BLANC, vora=GRIS_CLAR):
    forma = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    forma.adjustments[0] = 0.05
    forma.fill.solid()
    forma.fill.fore_color.rgb = color
    if vora is None:
        forma.line.fill.background()
    else:
        forma.line.color.rgb = vora
        forma.line.width = Pt(1)
    forma.shadow.inherit = False
    return forma


def cercle(slide, x, y, d, color, etiqueta, mida=20, color_text=BLANC):
    forma = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    forma.fill.solid()
    forma.fill.fore_color.rgb = color
    forma.line.fill.background()
    forma.shadow.inherit = False
    marc = forma.text_frame
    marc.margin_left = marc.margin_right = marc.margin_top = marc.margin_bottom = 0
    marc.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = marc.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = etiqueta
    r.font.name = LLETRA
    r.font.size = Pt(mida)
    r.font.bold = True
    r.font.color.rgb = color_text


def figura(slide, nom, x, y, w, h, vora=True, fons_blanc=True):
    """Posa la figura dins d'una targeta blanca, ajustada a w x h i centrada."""
    if fons_blanc:
        targeta(slide, x, y, w, h, vora=GRIS_CLAR if vora else None)
    ample, alt = Image.open(FIG / nom).size
    marge = 0.12
    ws, hs = w - 2 * marge, h - 2 * marge
    escala = min(ws / ample, hs / alt)
    iw, ih = ample * escala, alt * escala
    slide.shapes.add_picture(str(FIG / nom), Inches(x + (w - iw) / 2), Inches(y + (h - ih) / 2), Inches(iw), Inches(ih))


def diapo(titol, notes, fosc=False):
    slide = prs.slides.add_slide(BUIDA)
    numero[0] += 1
    fons(slide, NAVY if fosc else FONS)
    if titol:
        text(slide, 0.6, 0.42, 12.1, 0.9, titol, 34, BLANC if fosc else NAVY, True, ancora=MSO_ANCHOR.MIDDLE)
    if not fosc:
        text(slide, 0.6, 7.02, 6, 0.3, 'Arnau Montull · CPIA · Explosions nuclears amb DBSCAN', 10, GRIS)
        text(slide, 11.9, 7.02, 0.85, 0.3, str(numero[0]), 10, GRIS, alineacio=PP_ALIGN.RIGHT)
    slide.notes_slide.notes_text_frame.text = notes
    return slide


def estadistica(slide, x, y, w, gran, petit, color=TARONJA, mida=48, text_color=GRIS):
    text(slide, x, y, w, 0.9, gran, mida, color, True, ancora=MSO_ANCHOR.BOTTOM)
    text(slide, x, y + 0.95, w, 0.6, petit, 14, text_color)


# ---------------------------------------------------------------- 1. Portada
s = diapo(None, """Bon dia. Soc l'Arnau i us explicaré el meu problema: com es pot saber, només amb dades sísmiques, si un esdeveniment és un terratrèmol o una explosió nuclear.
Ho farem amb un algorisme no supervisat, DBSCAN, sobre el catàleg sísmic de l'USGS.""", fosc=True)
text(s, 0.8, 0.9, 7.2, 0.4, 'CPIA · APRENENTATGE NO SUPERVISAT I DETECCIÓ D\'ANOMALIES', 13, TARONJA, True)
text(s, 0.8, 1.9, 6.3, 2.6, 'Terratrèmol o explosió nuclear?', 44, BLANC, True, ancora=MSO_ANCHOR.TOP, espai=0)
text(s, 0.8, 4.2, 6.2, 1.2, 'Detectar assajos nuclears al catàleg de l\'USGS amb DBSCAN, sense llegir l\'etiqueta', 20, RGBColor(0xC9, 0xD1, 0xDB))
text(s, 0.8, 6.2, 6.5, 0.4, 'Arnau Montull Bainad', 18, BLANC, True)
figura(s, 'mapa_simple.png', 7.6, 1.7, 5.2, 3.5)

# ---------------------------------------------------------------- 2. Per que importa
s = diapo('Per què importa saber-ho', """Des de la Segona Guerra Mundial, la dissuasió nuclear ha evitat guerres a gran escala entre potències nuclears, i els estats han intentat limitar qui té accés a l'arma amb tractats: el de No Proliferació del 1968 i el que prohibeix tots els assajos, el CTBT del 1996, que encara no ha entrat en vigor.
Un tractat només serveix si es pot verificar. I la manera de fer-ho a distància és la sismologia: Corea del Nord va anunciar els seus assajos, però les xarxes sísmiques globals els van registrar de manera independent i en van permetre la localització i la mida.
La nostra pregunta és una versió simple d'aquesta idea.""")
targetes = [
    ('Dissuasió', 'Des de la Segona Guerra Mundial, cap guerra a gran escala entre potències nuclears.', NAVY),
    ('Tractats', 'No Proliferació (1968) i CTBT (1996, encara no en vigor): cal poder verificar-los.', BLAU),
    ('Corea del Nord', 'Assajos el 2006 i el 2017, registrats de manera independent per les xarxes sísmiques.', TARONJA),
]
for i, (cap, cos, color) in enumerate(targetes):
    x = 0.6 + i * 4.15
    targeta(s, x, 1.7, 3.85, 3.4)
    cercle(s, x + 0.35, 2.05, 0.8, color, str(i + 1), 28)
    text(s, x + 0.35, 3.1, 3.2, 0.5, cap, 24, NAVY, True)
    text(s, x + 0.35, 3.75, 3.2, 1.3, cos, 17, GRIS)
targeta(s, 0.6, 5.5, 12.1, 1.15, color=NAVY, vora=None)
text(s, 1.0, 5.5, 11.3, 1.15, 'Verificar a distància, només amb dades sísmiques, és el que dona sentit als tractats.', 24, BLANC, True,
     ancora=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 3. La pregunta
s = diapo('La pregunta', """La pregunta és: pot un algorisme que no veu l'etiqueta assenyalar les explosions nuclears d'un catàleg de gairebé tres-cents mil esdeveniments?
Només li donem dues coses de cada esdeveniment: on és i a quina profunditat. L'etiqueta que diu «explosió nuclear» no l'utilitzem per entrenar res; només al final, per comprovar si ho ha fet bé.""")
text(s, 0.6, 1.6, 12.1, 1.5, [[('Pot un algorisme no supervisat assenyalar les explosions nuclears ', False, INK), ('sense llegir l\'etiqueta', True, TARONJA), ('?', False, INK)]], 32)
cartes = [('ENTRADA', 'Posició (latitud i longitud) i profunditat de cada esdeveniment.', BLAU),
          ('SORTIDA', 'Cada esdeveniment queda marcat com a sospitós o no sospitós.', TARONJA),
          ('L\'ETIQUETA', 'Només serveix per avaluar el resultat. Mai per entrenar.', NAVY)]
for i, (cap, cos, color) in enumerate(cartes):
    x = 0.6 + i * 4.15
    targeta(s, x, 3.6, 3.85, 2.7)
    text(s, x + 0.35, 3.9, 3.2, 0.4, cap, 14, color, True)
    text(s, x + 0.35, 4.45, 3.2, 1.7, cos, 20, INK)

# ---------------------------------------------------------------- 4. Les dades
s = diapo('Les dades: tot el catàleg de l\'USGS', """Utilitzem el catàleg de l'USGS: tots els esdeveniments de magnitud 4,5 o més entre 1951 i 2025, de qualsevol tipus. Són 298.127 esdeveniments. Només 614 estan etiquetats com a explosió nuclear.
A més de terratrèmols i explosions nuclears hi ha 100 esdeveniments d'altres tipus: erupcions volcàniques, altres explosions, esfondraments de mina, etc. No els traiem, perquè en un cas real també hi serien.
Al mapa, en gris els terratrèmols i en vermell les explosions nuclears: es concentren en uns pocs punts.""")
estadistica(s, 0.6, 1.6, 4.2, '298 127', 'esdeveniments de magnitud 4,5 o més', NAVY)
estadistica(s, 0.6, 3.4, 4.2, '614', 'etiquetats com a explosió nuclear', TARONJA)
estadistica(s, 0.6, 5.2, 4.2, '1951–2025', 'catàleg USGS, de tots els tipus d\'esdeveniment', BLAU, 40)
figura(s, 'mapa_simple.png', 5.1, 1.6, 7.6, 5.1)

# ---------------------------------------------------------------- 5. Dues pistes
s = diapo('Dues pistes físiques', """Hi ha dues pistes. La primera: un terratrèmol és el lliscament d'una falla a desenes de quilòmetres de profunditat, i la mediana de profunditat al catàleg és de 33 km. Una explosió nuclear és un pols de pressió gairebé a la superfície.
La segona: les proves es fan sempre als mateixos polígons d'assaig, com Nevada o Semipalatinsk, de manera que formen grups molt compactes al mapa.
Combinant les dues, un grup d'esdeveniments molt junts i molt superficials és sospitós.""")
figura(s, 'fuentes.png', 0.6, 1.6, 7.4, 3.5)
cartes = [('1', 'Es repeteixen als polígons', 'Nevada, Semipalatinsk, Mururoa… formen grups compactes.'),
          ('2', 'Passen gairebé a la superfície', 'Terratrèmols: mediana de 33 km; només un 0,25 % és a menys de 2,5 km.')]
for i, (n, cap, cos) in enumerate(cartes):
    y = 1.6 + i * 1.85
    targeta(s, 8.3, y, 4.4, 1.7)
    cercle(s, 8.55, y + 0.25, 0.6, TARONJA, n, 22)
    text(s, 9.35, y + 0.2, 3.2, 0.4, cap, 16, NAVY, True)
    text(s, 9.35, y + 0.85, 3.2, 0.8, cos, 14, GRIS)
text(s, 0.6, 5.5, 12.1, 1.2, [[('Un grup d\'esdeveniments ', False, INK), ('molt junts', True, BLAU), (' i ', False, INK), ('molt superficials', True, TARONJA), (' és sospitós.', False, INK)]], 30,
     ancora=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 6. Profunditat
s = diapo('La profunditat separa les dues classes', """Aquí es veu la profunditat de cada classe, com a fracció del total. Els terratrèmols, en gris, es reparteixen per tot el rang i tenen pics a 10 i a 33 km, que són profunditats que el catàleg fixa quan no pot calcular-les. Les explosions, en vermell, estan gairebé totes a 0 km.
En taronja, la finestra de profunditat que fem servir: de 0 a 2,5 km.""")
figura(s, 'profunditat.png', 0.6, 1.6, 7.8, 5.1)
text(s, 8.8, 1.8, 3.9, 0.5, 'Finestra [0; 2,5) km', 22, TARONJA, True)
text(s, 8.8, 2.5, 3.9, 3.8, [
    'Les explosions es concentren a prop de 0 km.',
    'Els terratrèmols es reparteixen per tot el rang.',
    'La finestra s\'aplica a la mediana de cada clúster, no a cada esdeveniment.'], 18, INK, espai=12)

# ---------------------------------------------------------------- 6b. Com funciona DBSCAN (1): punts centrals, frontera i soroll
s = diapo('Com funciona DBSCAN: tres tipus de punts', """DBSCAN agrupa per densitat i només té dos paràmetres: un radi, epsilon, i un nombre mínim de veïns dins d'aquest radi.
Amb això, cada punt es classifica en un de tres tipus. Punt central, en blau: té com a mínim el nombre mínim de veïns dins del radi. Punt frontera, en vermell: no arriba al mínim, però és dins del radi d'un punt central. I soroll, en negre: no és cap de les dues coses.
Aquesta captura és d'una demo en línia de Philippe Fournier-Viger, amb epsilon igual a 1 i mínim de 3 veïns. Una nota: a la demo el veïnat no compta el punt mateix, i a scikit-learn sí. Per això el nostre v_min igual a 2 equival al MinPts igual a 1 de la demo.""")
figura(s, 'dbscan_demo_eps1.png', 0.6, 1.5, 5.5, 5.05)
text(s, 0.6, 6.6, 5.5, 0.3, 'Captura: demo de Ph. Fournier-Viger, ε = 1, MinPts = 3', 10, GRIS)
text(s, 6.6, 1.55, 6.1, 0.5, 'Dos paràmetres', 22, NAVY, True)
text(s, 6.6, 2.1, 6.1, 0.8, [[('ε', True, TARONJA), (' (radi del veïnat) i ', False, INK), ('MinPts', True, TARONJA), (' (veïns mínims dins del radi)', False, INK)]], 18)
tipus = [(RGBColor(0x1F, 0x3A, 0xE8), 'Punt central', 'Té com a mínim MinPts veïns dins del radi ε.'),
         (RGBColor(0xE0, 0x1B, 0x1B), 'Punt frontera', 'No arriba al mínim, però és dins del radi d\'un punt central.'),
         (INK, 'Soroll', 'No és central ni és a prop de cap punt central.')]
for i, (color, cap, cos) in enumerate(tipus):
    y = 3.0 + i * 1.12
    targeta(s, 6.6, y, 6.1, 0.98)
    cercle(s, 6.85, y + 0.26, 0.46, color, '', 12)
    text(s, 7.55, y + 0.1, 5.0, 0.4, cap, 18, NAVY, True)
    text(s, 7.55, y + 0.5, 5.0, 0.45, cos, 14, GRIS)
text(s, 6.6, 6.45, 6.1, 0.5, 'A la demo, el veïnat no compta el propi punt; a scikit-learn sí. El nostre v_min = 2 equival a MinPts = 1 de la demo.', 11, GRIS)

# ---------------------------------------------------------------- 6c. Com funciona DBSCAN (2): efecte de eps
s = diapo('L\'efecte del radi ε', """Aquí es veu què passa quan canviem el radi sobre els mateixos punts.
Amb epsilon igual a 0,5, el radi és tan petit que cap punt arriba al mínim de veïns: tot és soroll. Amb epsilon igual a 1 apareixen dos grups centrals. Amb epsilon igual a 2, els cercles creixen, es toquen i els grups s'ajunten, i queda menys soroll.
Un epsilon massa petit deixa tot com a soroll, i un de massa gran fon grups diferents. Per això en el nostre problema hem validat el radi provant-ne molts valors.""")
tres = [('dbscan_demo_eps05.png', 'ε = 0,5', 'Massa petit: tot és soroll.'),
        ('dbscan_demo_eps1.png', 'ε = 1', 'Apareixen grups centrals.'),
        ('dbscan_demo_eps2.png', 'ε = 2', 'Els grups creixen i s\'ajunten.')]
for i, (nom, cap, cos) in enumerate(tres):
    x = 0.6 + i * 4.15
    figura(s, nom, x, 1.5, 3.85, 3.95)
    text(s, x + 0.1, 5.55, 3.7, 0.5, cap, 22, TARONJA, True)
    text(s, x + 0.1, 6.05, 3.7, 0.4, cos, 16, INK)
text(s, 0.6, 6.55, 12.1, 0.3, 'Captures: demo de Ph. Fournier-Viger (philippe-fournier-viger.com/tools/dbscan_clusters_demo.php), MinPts = 3', 10, GRIS)

# ---------------------------------------------------------------- 6d. Com funciona DBSCAN (3): de punts a clusters
s = diapo('De punts a clústers', """Un clúster es forma així: els punts centrals que estan a menys d'un radi l'un de l'altre queden al mateix grup, i el grup creix de punt en punt, com una cadena. Els punts frontera s'hi afegeixen, i el soroll queda fora.
A l'esquerra, la classificació; a la dreta, el resultat final, amb cada clúster d'un color i el soroll amagat.
En el nostre problema, cada sisme és un punt amb latitud i longitud, la distància és la de haversine sobre l'esfera, el radi és de 25 km i el mínim és de 2.""")
figura(s, 'dbscan_demo_eps1.png', 0.6, 1.5, 4.6, 4.3)
cercle(s, 5.35, 3.35, 0.6, TARONJA, '→', 24)
figura(s, 'dbscan_demo_clusters.png', 6.1, 1.5, 4.6, 4.3)
text(s, 0.6, 5.9, 4.6, 0.4, 'Classificació dels punts', 15, GRIS, alineacio=PP_ALIGN.CENTER)
text(s, 6.1, 5.9, 4.6, 0.4, 'Clústers (el soroll s\'amaga)', 15, GRIS, alineacio=PP_ALIGN.CENTER)
text(s, 11.0, 1.7, 1.8, 3.9, [[('Al nostre cas', True, TARONJA)], 'Punt = sisme', 'Distància: haversine', 'ε = 25 km', 'v_min = 2'], 14, INK, espai=8)
text(s, 0.6, 6.45, 12.1, 0.3, 'Captures: demo de Ph. Fournier-Viger (philippe-fournier-viger.com/tools/dbscan_clusters_demo.php), ε = 1, MinPts = 3', 10, GRIS)

# ---------------------------------------------------------------- 7. Com funciona
s = diapo('Com funciona: quatre passos', """El mètode té quatre passos.
Primer, DBSCAN agrupa els esdeveniments que estan a prop, mesurant la distància sobre l'esfera amb la fórmula de haversine. Un grup és una cadena d'esdeveniments a menys de 25 km l'un de l'altre; els que estan sols són soroll.
Segon, calculem la mediana de profunditat de cada grup. Tercer, un grup és sospitós si aquesta mediana és menor de 2,5 km. Quart, comparem amb l'etiqueta per comptar encerts, falsos positius i falsos negatius.""")
passos = [('1', 'Agrupar', 'DBSCAN amb distància haversine sobre l\'esfera'),
          ('2', 'Profunditat', 'Mediana de profunditat de cada clúster'),
          ('3', 'Sospitós', 'Si la mediana és menor de 2,5 km'),
          ('4', 'Comparar', 'Amb l\'etiqueta: encerts, FP i FN')]
for i, (n, cap, cos) in enumerate(passos):
    x = 0.6 + i * 3.1
    targeta(s, x, 1.7, 2.85, 3.1)
    cercle(s, x + 0.3, 2.0, 0.75, NAVY if i != 2 else TARONJA, n, 26)
    text(s, x + 0.3, 3.0, 2.3, 0.5, cap, 22, NAVY, True)
    text(s, x + 0.3, 3.65, 2.3, 1.1, cos, 15, GRIS)
targeta(s, 0.6, 5.2, 12.1, 1.4, color=NAVY, vora=None)
parametres = [('ε = 25 km', 'radi del veïnat'), ('v_min = 2', 'sismes mínims per grup'), ('[0; 2,5) km', 'finestra de profunditat')]
for i, (gran, petit) in enumerate(parametres):
    x = 1.0 + i * 3.9
    text(s, x, 5.35, 3.6, 0.6, gran, 28, TARONJA, True)
    text(s, x, 6.0, 3.6, 0.4, petit, 14, RGBColor(0xC9, 0xD1, 0xDB))

# ---------------------------------------------------------------- 7b. Precisio, recall i F1
s = diapo('Com mesurem: precisió, recall i F₁', """Per saber si el detector funciona, comptem quatre coses. Encert, o vertader positiu: l'hem marcat i és una explosió. Fals positiu: l'hem marcat però no ho és. Fals negatiu: és una explosió i no l'hem marcat. I vertader negatiu: no l'hem marcat i no ho és.
La precisió respon a: de tot el que marquem, quant és explosió? El recall: de totes les explosions, quantes trobem? I la F1 és la mitjana harmònica de les dues, de manera que només és alta si totes dues ho són.
No fem servir l'exactitud, perquè les classes estan molt desequilibrades: un detector que no marqués mai res encertaria el 99,8 %.""")
quadrats = [('Encert (TP)', 'Marcat i és explosió', '551', VERD), ('Fals positiu (FP)', 'Marcat, però no és explosió', '57', TARONJA),
            ('Fals negatiu (FN)', 'Explosió que no marquem', '63', NAVY), ('Vertader negatiu (TN)', 'No marcat i no és explosió', '297 456', GRIS)]
for i, (cap, cos, num, color) in enumerate(quadrats):
    x = 0.6 + (i % 2) * 3.0
    y = 1.6 + (i // 2) * 2.4
    targeta(s, x, y, 2.85, 2.25)
    text(s, x + 0.25, y + 0.2, 2.4, 0.9, num, 32, color, True, ancora=MSO_ANCHOR.BOTTOM)
    text(s, x + 0.25, y + 1.15, 2.4, 0.4, cap, 15, NAVY, True)
    text(s, x + 0.25, y + 1.55, 2.4, 0.6, cos, 12, GRIS)
definicions = [('Precisió', 'TP / (TP + FP)', 'De tot el que marquem, quant és explosió?', '90,6 %', NAVY),
               ('Recall', 'TP / (TP + FN)', 'De totes les explosions, quantes trobem?', '89,7 %', NAVY),
               ('F₁', '2·TP / (2·TP + FP + FN)', 'Mitjana harmònica: només és alta si les dues ho són.', '0,902', TARONJA)]
for i, (cap, formula, cos, valor, color) in enumerate(definicions):
    y = 1.6 + i * 1.62
    targeta(s, 6.85, y, 5.85, 1.48)
    text(s, 7.1, y + 0.15, 2.6, 0.45, cap, 20, color, True)
    text(s, 7.1, y + 0.62, 3.4, 0.4, formula, 15, INK, True)
    text(s, 7.1, y + 1.0, 3.7, 0.45, cos, 12, GRIS)
    text(s, 10.8, y, 1.7, 1.48, valor, 28, color, True, alineacio=PP_ALIGN.RIGHT, ancora=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 6.55, 12.1, 0.4, 'No usem l\'exactitud: un detector que no marqués mai res encertaria el 99,8 %.', 15, INK, True)

# ---------------------------------------------------------------- 8. Nevada
s = diapo('Exemple: el polígon de Nevada', """Aquí hi ha un zoom al polígon de Nevada. A l'esquerra, els epicentres tal com els veu l'algorisme, sense etiquetes. A la dreta, els clústers: en blau els no sospitosos i en taronja els sospitosos, perquè la seva mediana de profunditat és menor de 2,5 km.
Els cercles negres petits són les explosions reals. Veieu que cauen dins del clúster taronja: l'algorisme les ha trobat sense saber-ho.""")
figura(s, 'deteccion_nevada.png', 0.6, 1.5, 12.1, 4.55)
text(s, 0.6, 6.25, 12.1, 0.6, 'En taronja, els clústers sospitosos; amb un cercle negre, les explosions reals. Les han trobat sense llegir l\'etiqueta.', 16, GRIS)

# ---------------------------------------------------------------- 9. Parametres
s = diapo('Per què aquests paràmetres', """Els paràmetres estan fixats. La finestra de 2,5 km és un criteri físic, i no una finestra estreta al voltant de 0 km, perquè volem que l'algorisme pugui detectar proves futures: el catàleg podria registrar-les a una profunditat que no sigui exactament 0 km, i no volem dependre que l'etiquetatge sigui perfecte.
El radi de 25 km és del ordre de la mida d'un polígon d'assaig i, com veurem, és el que dona menys falsos positius.
I amb v_min igual a 2, els sismes aïllats són soroll: això treu molts terratrèmols superficials, a canvi de perdre explosions que van ser assajos aïllats.""")
cartes = [('Finestra [0; 2,5) km', 'Un màxim de 2,5 km, i no només 0 km: volem detectar proves futures, encara que el catàleg no les posi exactament a 0 km.', NAVY),
          ('ε = 25 km', 'Del ordre de la mida d\'un polígon d\'assaig. És el valor amb menys falsos positius entre 5 i 100 km.', TARONJA),
          ('v_min = 2', 'Els sismes sols en 25 km són soroll (2,4 %). Amb v_min = 1: 28 FN però 115 FP; amb v_min = 2: 63 FN i 57 FP.', BLAU)]
for i, (cap, cos, color) in enumerate(cartes):
    x = 0.6 + i * 4.15
    targeta(s, x, 1.6, 3.85, 3.7)
    text(s, x + 0.35, 1.9, 3.2, 0.6, cap, 24, color, True)
    text(s, x + 0.35, 2.7, 3.2, 2.5, cos, 18, INK)
targeta(s, 0.6, 5.6, 12.1, 1.1, color=NAVY, vora=None)
text(s, 1.0, 5.6, 11.3, 1.1, 'Els tres paràmetres són fixos per a tot el catàleg: no es tornen a ajustar per a cada zona.', 22, BLANC, True,
     ancora=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 10. Validacio eps
s = diapo('Validació de ε: de 5 en 5 km', """Per justificar el radi hem provat tots els valors de 5 a 100 km, de 5 en 5.
La silueta, que és la mètrica típica sense etiquetes, és negativa en tots els casos i no ens diu res, perquè DBSCAN uneix cadenes allargades i la silueta penalitza els grups no compactes.
En canvi, els errors sí que expliquen alguna cosa. Els falsos positius tenen el mínim, 57, a 25 km. I a partir de 55 km els falsos negatius salten de 60 a gairebé 290: els grups d'explosions es fonen amb grups de terratrèmols més profunds i la seva mediana deixa de ser superficial.
Cal dir que aquí sí que mirem l'etiqueta per triar el radi, i per això el mètode és híbrid.""")
figura(s, 'errors_eps.png', 0.6, 1.6, 7.6, 5.1)
text(s, 8.6, 1.7, 4.1, 5, [
    [('La silueta no serveix: ', True, NAVY), ('és negativa per a tots els ε.', False, INK)],
    [('Mínim de FP a 25 km: ', True, TARONJA), ('57 falsos positius.', False, INK)],
    [('Des de 55 km, els FN salten: ', True, NAVY), ('de ~60 a ~290. Els grups d\'explosions es fonen amb terratrèmols profunds.', False, INK)]], 18, INK, espai=14)

# ---------------------------------------------------------------- 11. Resultat
s = diapo('Resultat', """El resultat final, amb els paràmetres fixos: de les 614 explosions, en detectem 551, amb 57 falsos positius i 63 falsos negatius. Això és una precisió del 90,6 %, un recall del 89,7 % i una F1 de 0,902, en un catàleg de gairebé tres-cents mil esdeveniments.
Al mapa, en verd els encerts, en taronja els falsos positius i en negre els falsos negatius.""")
estadistica(s, 0.6, 1.5, 3.8, '0,902', 'F₁: mitjana harmònica de precisió i recall', TARONJA, 66)
estadistica(s, 0.6, 3.5, 1.9, '90,6 %', 'precisió', NAVY, 34)
estadistica(s, 2.6, 3.5, 1.9, '89,7 %', 'recall', NAVY, 34)
text(s, 0.6, 5.25, 3.8, 1.5, [[('551', True, VERD), (' encerts', False, INK)], [('57', True, TARONJA), (' falsos positius', False, INK)], [('63', True, INK), (' falsos negatius', False, INK)]], 20, espai=4)
figura(s, 'resultado.png', 4.7, 1.6, 8.0, 5.1)

# ---------------------------------------------------------------- 12. Mapa de clusters
s = diapo('Què hi ha darrere de cada clúster', """DBSCAN no sap res d'història, però els clústers que troba són els polígons d'assaig de la Guerra Freda. En verd, les explosions que es detecten, i amb una creu negra, les que no.
Nevada concentra 230 explosions en un sol clúster. Semipalatinsk surt partit en dos, Balapan i Degelen, amb 178 explosions en total. Mururoa té 74 explosions lluny de qualsevol zona sísmica: és el cas més fàcil.""")
figura(s, 'mapa_clusters.png', 0.6, 1.5, 12.1, 3.95)
cartes = [('Nevada', '230 explosions en un sol clúster.'), ('Semipalatinsk', '178 explosions, en dos clústers: Balapan i Degelen.'), ('Mururoa', '74 explosions lluny de qualsevol zona sísmica.')]
for i, (cap, cos) in enumerate(cartes):
    x = 0.6 + i * 4.15
    targeta(s, x, 5.7, 3.85, 1.15)
    text(s, x + 0.3, 5.82, 3.3, 0.4, cap, 18, TARONJA, True)
    text(s, x + 0.3, 6.25, 3.3, 0.55, cos, 14, INK)

# ---------------------------------------------------------------- 12b. Explosions nuclears civils sovietiques
s = diapo('Les explosions nuclears civils soviètiques', """Entre els falsos negatius hi ha un grup que cal explicar: les explosions nuclears pacífiques o civils de la Unió Soviètica. Era un programa civil, separat dels assajos militars, que va durar aproximadament de 1965 a 1988, amb un centenar llarg d'explosions; la xifra habitual és d'unes 120.
S'utilitzaven per crear cavitats subterrànies on emmagatzemar gas, com les 15 d'Astracan que sí que detectem; per estimular jaciments de petroli i de gas; per fer sondeigs sísmics profunds; per excavar canals i embassaments; i fins i tot per apagar focs de pous de gas.
Per què ens afecten? Perquè no es feien als polígons militars sinó en llocs aïllats de Sibèria, dels Urals i del Kazakhstan. Amb v_min igual a 2, una explosió que és sola en un radi de 25 km és soroll. Cal ser prudents: dedueixo que moltes de les 40 explosions aïllades són d'aquest programa pel lloc on són, però no ho he comprovat explosió per explosió.""")
text(s, 0.6, 1.55, 3.6, 0.9, '~120', 66, TARONJA, True, ancora=MSO_ANCHOR.BOTTOM)
text(s, 0.6, 2.5, 3.6, 0.9, 'explosions civils, de 1965 a 1988 (xifra habitual)', 15, GRIS)
text(s, 0.6, 3.6, 3.6, 1.6, 'Un programa civil, separat dels assajos militars.', 17, INK, True)
usos = [('Emmagatzemar gas', 'Doms de sal. Les 15 d\'Astracan sí que es detecten.', NAVY),
        ('Estimular jaciments', 'Petroli i gas.', BLAU),
        ('Sondeig sísmic profund', 'Explorar l\'escorça terrestre.', NAVY),
        ('Canals i embassaments', 'Moure grans volums de terra.', BLAU),
        ('Apagar focs de pous', 'De gas.', NAVY)]
for i, (cap, cos, color) in enumerate(usos):
    x = 4.5 + (i % 2) * 4.15
    y = 1.55 + (i // 2) * 1.3
    ample = 3.95 if i < 4 else 8.1
    targeta(s, x, y, ample, 1.18)
    cercle(s, x + 0.25, y + 0.29, 0.6, color, str(i + 1), 20)
    text(s, x + 1.1, y + 0.14, ample - 1.3, 0.4, cap, 17, NAVY, True)
    text(s, x + 1.1, y + 0.6, ample - 1.3, 0.55, cos, 14, GRIS)
targeta(s, 0.6, 5.65, 12.1, 1.2, color=NAVY, vora=None)
text(s, 1.0, 5.65, 5.6, 1.2, 'Per què ens afecten?', 24, TARONJA, True, ancora=MSO_ANCHOR.MIDDLE)
text(s, 5.4, 5.65, 7.1, 1.2, 'No es feien als polígons militars, sinó en llocs aïllats de Sibèria, els Urals i el Kazakhstan: amb v_min = 2, una explosió sola en 25 km és soroll.',
     15, BLANC, ancora=MSO_ANCHOR.MIDDLE)

# ---------------------------------------------------------------- 13. On falla
s = diapo('On falla el mètode', """Els 63 falsos negatius tenen explicació.
Quaranta són explosions aïllades, probablement civils soviètiques a Rússia i el Kazakhstan: com que estan soles en 25 km, amb v_min igual a 2 són soroll.
Divuit són de Lop Nur, a la Xina: caiguts al costat de terratrèmols del Tian Shan, la mediana del clúster puja a 15,7 km i es perd tot el grup.
La Bomba Tsar va ser una explosió aèria a 4 km d'altura, i el catàleg la registra a menys 4 km, per sobre de la superfície: queda fora de la finestra. I l'assaig Shoal del 1963, a Fallon, es va fer enmig d'una zona amb terratrèmols reals.""")
cartes = [('40 de 63', 'Explosions aïllades', 'Assajos sols en 25 km, probablement civils soviètics: queden com a soroll.', NAVY),
          ('18 de 63', 'Lop Nur (Xina)', 'Barrejades amb 29 terratrèmols del Tian Shan: la mediana del clúster és de 15,7 km.', TARONJA),
          ('1961', 'Bomba Tsar', 'Explosió aèria a 4 km d\'altura: el catàleg la posa a −4 km, fora de la finestra.', BLAU),
          ('1963', 'Assaig Shoal (Fallon)', '12 kt en granit, enmig d\'una zona amb terratrèmols reals.', GRIS)]
for i, (gran, cap, cos, color) in enumerate(cartes):
    x = 0.6 + (i % 2) * 6.15
    y = 1.6 + (i // 2) * 2.65
    targeta(s, x, y, 5.95, 2.45)
    text(s, x + 0.4, y + 0.25, 5.2, 0.8, gran, 38, color, True)
    text(s, x + 0.4, y + 1.0, 5.2, 0.4, cap, 20, NAVY, True)
    text(s, x + 0.4, y + 1.45, 5.2, 0.9, cos, 15, GRIS)

# ---------------------------------------------------------------- 14. Limitacions
s = diapo('Limitacions: què no podem concloure', """Cal ser honestos amb les limitacions.
Primer, el mètode és híbrid: l'agrupament és no supervisat i la finestra és física, però el radi l'he triat mirant l'etiqueta. Segon, el catàleg posa 0,0 km al 85 % de les explosions; una finestra molt estreta mesuraria aquesta convenció i no la física. Tercer, mantenim els 100 esdeveniments d'altres tipus, i 14 dels 57 falsos positius ho són; sense ells, la F1 seria 0,912. I quart, no hi ha un conjunt de prova separat.""")
cartes = [('Enfocament híbrid', 'L\'agrupament és no supervisat, però ε s\'ha triat mirant l\'etiqueta.'),
          ('Convenció del catàleg', 'El 85 % de les explosions figura a 0,0 km: una finestra estreta mediria la convenció, no la física.'),
          ('Altres esdeveniments', '14 dels 57 FP són explosions, esfondraments o voladures. Sense ells, F₁ = 0,912.'),
          ('Sense conjunt de prova', 'S\'ajusta i s\'avalua sobre el mateix catàleg.')]
for i, (cap, cos) in enumerate(cartes):
    x = 0.6 + (i % 2) * 6.15
    y = 1.6 + (i // 2) * 2.6
    targeta(s, x, y, 5.95, 2.4)
    text(s, x + 0.4, y + 0.3, 5.2, 0.5, cap, 22, TARONJA, True)
    text(s, x + 0.4, y + 1.0, 5.2, 1.3, cos, 17, INK)

# ---------------------------------------------------------------- 15. Conclusions
s = diapo(None, """Per acabar. Un agrupament sense etiquetes, combinat amb una pista física, la profunditat de cada grup, recupera el 90 % de les explosions nuclears d'un catàleg de gairebé tres-cents mil esdeveniments, amb 57 falsos positius.
La senyal útil és doble i física: repetició als mateixos polígons i profunditat gairebé nul·la. I com a millores: triar ε en un subconjunt i avaluar-lo en un altre, afegir la magnitud i la forma d'ona, i fer servir la llista oficial del DOE en lloc de l'etiqueta de l'USGS.
Moltes gràcies. Teniu alguna pregunta?""", fosc=True)
text(s, 0.8, 0.7, 11.5, 0.4, 'CONCLUSIONS', 14, TARONJA, True)
text(s, 0.8, 1.3, 11.8, 2.2, 'Un agrupament sense etiquetes i una pista física recuperen el 90 % de les explosions', 38, BLANC, True)
estadistica(s, 0.8, 3.7, 3.6, '0,902', 'F₁ sobre 298 127 esdeveniments', TARONJA, 48, RGBColor(0xC9, 0xD1, 0xDB))
estadistica(s, 4.8, 3.7, 3.6, '57', 'falsos positius', BLANC, 48, RGBColor(0xC9, 0xD1, 0xDB))
estadistica(s, 8.8, 3.7, 3.6, '551 / 614', 'explosions detectades', BLANC, 48, RGBColor(0xC9, 0xD1, 0xDB))
text(s, 0.8, 5.8, 11.8, 1.0, 'Pistes per investigar, no veredictes. Gràcies, preguntes?', 24, RGBColor(0xC9, 0xD1, 0xDB))

desti = AQUI / 'expo_arnau.pptx'
try:
    prs.save(desti)
except PermissionError:
    # El fitxer esta obert a PowerPoint: es desa amb un altre nom
    desti = AQUI / 'expo_arnau_nou.pptx'
    prs.save(desti)
print('guardat', desti, len(prs.slides._sldIdLst), 'diapositives')
