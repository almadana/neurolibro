#!/usr/bin/env python3
"""Recrea las figuras 2.9–2.11 con sus rótulos en español.

Las ilustraciones originales se conservan como base. El script amplía cada
imagen 4×, cubre únicamente los rótulos ingleses y compone sus equivalentes en
español con una tipografía sans que admite caracteres acentuados.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MEDIA = ROOT / "site" / "assets" / "media"
SCALE = 4
WHITE = (255, 255, 255)
BLACK = (24, 24, 24)

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-BoldOblique.ttf"


def sc(value):
    if isinstance(value, tuple):
        return tuple(round(v * SCALE) for v in value)
    return round(value * SCALE)


def font(size, style="regular"):
    path = {
        "regular": FONT_REGULAR,
        "bold": FONT_BOLD,
        "italic": FONT_ITALIC,
    }[style]
    return ImageFont.truetype(path, sc(size))


def base_image(filename):
    source = Image.open(MEDIA / filename).convert("RGB")
    return source.resize(
        (source.width * SCALE, source.height * SCALE),
        Image.Resampling.LANCZOS,
    )


def restore_source_crop(image, filename, box):
    """Restaura una atribución del original después de limpiar rótulos."""
    source = Image.open(MEDIA / filename).convert("RGB")
    crop = source.crop(box).resize(
        ((box[2] - box[0]) * SCALE, (box[3] - box[1]) * SCALE),
        Image.Resampling.LANCZOS,
    )
    image.paste(crop, sc((box[0], box[1])))


def fit_font(draw, text, box, maximum, minimum=3.5, style="regular", spacing=0.6):
    """Elige el mayor cuerpo que cabe en box (coordenadas del original)."""
    width = sc(box[2] - box[0])
    height = sc(box[3] - box[1])
    size = maximum
    while size >= minimum:
        candidate = font(size, style)
        bounds = draw.multiline_textbbox(
            (0, 0), text, font=candidate, spacing=sc(spacing), align="center"
        )
        if bounds[2] - bounds[0] <= width and bounds[3] - bounds[1] <= height:
            return candidate
        size -= 0.25
    return font(minimum, style)


def label(
    image,
    cover,
    text,
    place=None,
    maximum=6,
    minimum=3.5,
    style="regular",
    anchor="mm",
    align="center",
    pad=1.5,
    erase=True,
):
    """Tapa un rótulo fuente y escribe su traducción."""
    draw = ImageDraw.Draw(image)
    x0, y0, x1, y1 = cover
    if erase:
        draw.rectangle(sc((x0 - pad, y0 - pad, x1 + pad, y1 + pad)), fill=WHITE)
    target = place or cover
    tx0, ty0, tx1, ty1 = target
    selected = fit_font(
        draw, text, target, maximum, minimum=minimum, style=style, spacing=0.6
    )
    if anchor == "mm":
        xy = sc(((tx0 + tx1) / 2, (ty0 + ty1) / 2))
    elif anchor == "lm":
        xy = sc((tx0, (ty0 + ty1) / 2))
    else:
        xy = sc((tx1, (ty0 + ty1) / 2))
    draw.multiline_text(
        xy,
        text,
        font=selected,
        fill=BLACK,
        anchor=anchor,
        align=align,
        spacing=sc(0.6),
    )


def figure_2_9():
    image = base_image("995726c5c0663efb-fig2.9_draft-1-350x211.png")
    specs = [
        ((29, 110, 65, 126), "RECEPTOR\nSENSITIVO", (20, 104, 67, 118), 5.5),
        ((31, 165, 60, 180), "MÚSCULO", (30, 164, 63, 178), 5.5),
        ((84, 81, 123, 98), "NEURONA\nSENSITIVA", (87, 78, 133, 98), 5.5),
        ((100, 142, 141, 160), "NEURONA\nMOTORA", (101, 140, 146, 160), 5.5),
        (
            (117, 45, 174, 72),
            "CUERPO CELULAR\nNEURONAL EN EL\nGANGLIO DE LA\nRAÍZ DORSAL",
            (126, 37, 180, 72),
            5.2,
        ),
        (
            (167, 40, 239, 64),
            "LOS AXONES ASCIENDEN\nPOR LA COLUMNA DORSAL\nHASTA EL BULBO RAQUÍDEO",
            (178, 31, 245, 64),
            5.0,
        ),
        ((226, 45, 282, 66), "COLUMNA\nDORSAL", (250, 42, 287, 65), 5.3),
        ((267, 46, 345, 68), "ZONA DE ENTRADA\nDE LA RAÍZ DORSAL", (286, 43, 349, 68), 4.8),
        ((290, 68, 348, 87), "ASTA\nDORSAL", (312, 68, 349, 87), 5.3),
        ((299, 90, 350, 112), "COLUMNA\nLATERAL", (310, 91, 349, 111), 5.2),
        ((286, 112, 345, 132), "ASTA\nVENTRAL", (305, 112, 349, 131), 5.2),
        (
            (264, 130, 345, 152),
            "ZONA DE SALIDA\nDE LA RAÍZ VENTRAL",
            (282, 131, 349, 152),
            4.8,
        ),
        ((221, 141, 278, 157), "COLUMNA\nVENTRAL", (239, 141, 278, 157), 5.2),
    ]
    draw = ImageDraw.Draw(image)
    # La columna derecha estaba demasiado comprimida para limpiar cada palabra
    # sin dejar artefactos: se recompone el pequeño conjunto de líneas guía.
    draw.rectangle(sc((284, 39, 350, 154)), fill=WHITE)
    for start, end in [
        ((259, 72), (291, 54)),
        ((269, 84), (296, 75)),
        ((278, 100), (299, 100)),
        ((270, 116), (296, 121)),
        ((259, 127), (285, 142)),
    ]:
        draw.line((sc(start), sc(end)), fill=(86, 86, 86), width=sc(0.8))
    for cover, *_ in specs:
        label(image, cover, "", maximum=3.5)
    for cover, text, place, maximum in specs:
        label(image, cover, text, place=place, maximum=maximum, erase=False)
    restore_source_crop(
        image,
        "995726c5c0663efb-fig2.9_draft-1-350x211.png",
        (197, 157, 258, 164),
    )
    image.save(HERE / "es-fig-2-9.png", optimize=True)


def figure_2_10():
    image = base_image("bbf7aeda45c7da9c-fig2.9_draft-350x273.png")
    specs = [
        ((143, 20, 217, 35), "PROSENCÉFALO", (148, 18, 227, 36), 8.2, "italic"),
        ((83, 37, 141, 51), "DIENCÉFALO", (91, 37, 143, 51), 5.3, "bold"),
        ((106, 47, 141, 61), "TÁLAMO", (106, 48, 141, 60), 4.8, "bold"),
        ((63, 55, 117, 70), "HIPOTÁLAMO", (68, 57, 117, 69), 4.7, "bold"),
        (
            (193, 37, 260, 55),
            "HEMISFERIOS\nCEREBRALES",
            (214, 36, 263, 55),
            4.8,
            "bold",
        ),
        ((38, 165, 107, 184), "TRONCO\nENCEFÁLICO", (38, 164, 108, 190), 7.5, "italic"),
        ((100, 168, 149, 182), "MESENCÉFALO", (108, 168, 153, 182), 4.2, "bold"),
        ((116, 179, 150, 194), "PUENTE", (124, 181, 150, 193), 4.8, "bold"),
        ((136, 191, 187, 207), "BULBO\nRAQUÍDEO", (150, 190, 188, 207), 4.4, "bold"),
        ((261, 165, 350, 187), "CEREBELO", (280, 165, 350, 190), 8.0, "italic"),
        ((137, 230, 229, 251), "MÉDULA ESPINAL", (145, 230, 232, 252), 7.4, "italic"),
    ]
    for cover, *_ in specs:
        label(image, cover, "", maximum=3.5)
    for cover, text, place, maximum, style in specs:
        label(
            image,
            cover,
            text,
            place=place,
            maximum=maximum,
            minimum=3.2,
            style=style,
            erase=False,
        )
    restore_source_crop(
        image,
        "bbf7aeda45c7da9c-fig2.9_draft-350x273.png",
        (269, 181, 349, 187),
    )
    image.save(HERE / "es-fig-2-10.png", optimize=True)


def draw_vertical_region_bar(image, x0, boundaries):
    """Reconstruye la clave vertical mesencéfalo–puente–bulbo."""
    draw = ImageDraw.Draw(image)
    draw.rectangle(sc((x0 - 2, boundaries[0] - 2, x0 + 12, boundaries[-1] + 2)), fill=WHITE)
    segments = [
        (boundaries[0], boundaries[1], (195, 247, 248), "MESENCÉFALO"),
        (boundaries[1], boundaries[2], (76, 218, 224), "PUENTE"),
        (boundaries[2], boundaries[3], (180, 243, 244), "BULBO"),
    ]
    for top, bottom, color, text in segments:
        draw.rectangle(sc((x0, top, x0 + 8, bottom)), fill=color)
        layer = Image.new("RGBA", (sc(42), sc(12)), (255, 255, 255, 0))
        ld = ImageDraw.Draw(layer)
        fnt = fit_font(ld, text, (0, 0, 42, 12), 4.2, minimum=2.8, style="bold")
        ld.text(sc((21, 6)), text, font=fnt, fill=BLACK, anchor="mm")
        layer = layer.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
        image.paste(
            layer,
            (sc(x0 + 1) - layer.width // 2, sc((top + bottom) / 2) - layer.height // 2),
            layer,
        )


def figure_2_11():
    image = base_image("641c96057471d24c-fig2.10_draft-350x397.png")
    # Títulos de los cuatro paneles.
    title_specs = [
        ((35, 7, 105, 20), "VISTA VENTRAL"),
        ((241, 7, 316, 20), "VISTA DORSAL"),
        ((27, 205, 137, 226), "NÚCLEOS\nSENSITIVOS/MOTORES"),
        ((229, 205, 332, 226), "NÚCLEOS\nNEUROMODULADORES"),
    ]
    for cover, text in title_specs:
        label(image, cover, "", maximum=3.5)
    for cover, text in title_specs:
        label(image, cover, text, maximum=7.2, minimum=4.3, style="italic", erase=False)

    # Vista ventral.
    ventral = [
        ((70, 32, 104, 39), "NERVIO ÓPTICO"),
        ((82, 37, 147, 50), "BASE DEL HIPOTÁLAMO"),
        ((92, 45, 146, 59), "CUERPOS MAMILARES"),
        ((97, 53, 159, 68), "PEDÚNCULO CEREBRAL"),
        ((101, 61, 147, 77), "TRACTO ÓPTICO"),
        ((96, 69, 159, 86), "NERVIO OCULOMOTOR"),
        ((96, 77, 153, 95), "NERVIO TROCLEAR"),
        ((97, 85, 155, 104), "NERVIO TRIGÉMINO"),
        ((97, 93, 145, 112), "BASE DEL PUENTE"),
        ((98, 101, 156, 122), "NERVIO ABDUCENS"),
        ((99, 109, 139, 131), "NERVIO FACIAL"),
        ((96, 117, 172, 140), "NERVIO VESTIBULOCOCLEAR"),
        ((95, 125, 157, 149), "NERVIO HIPOGLOSO"),
        ((89, 133, 170, 158), "NERVIO ACCESORIO ESPINAL"),
        ((85, 142, 160, 167), "NÚCLEO OLIVAR INFERIOR"),
        ((87, 151, 125, 176), "PIRÁMIDE"),
    ]
    for cover, *_ in ventral:
        label(image, cover, "", maximum=3.5)
    for cover, text in ventral:
        label(image, cover, text, maximum=4.45, minimum=2.75, style="bold", erase=False)

    # Vista dorsal.
    dorsal = [
        ((189, 49, 220, 58), "TÁLAMO"),
        ((180, 60, 220, 76), "COLÍCULO\nSUPERIOR"),
        ((180, 74, 220, 90), "COLÍCULO\nINFERIOR"),
        ((189, 90, 222, 104), "NERVIO\nTROCLEAR"),
        ((178, 103, 224, 125), "PEDÚNCULO\nCEREBELOSO\nSUPERIOR"),
        ((190, 124, 230, 146), "PEDÚNCULO\nCEREBELOSO\nMEDIO"),
        ((214, 149, 242, 164), "COLUMNA\nDORSAL"),
    ]
    for cover, *_ in dorsal:
        label(image, cover, "", maximum=3.5)
    for cover, text in dorsal:
        label(image, cover, text, maximum=4.6, minimum=2.8, style="bold", erase=False)

    # Núcleos neuromoduladores y zonas reticulares.
    modulatory = [
        (
            (195, 232, 235, 251),
            "ÁREA TEGMENTAL\nVENTRAL\n(DOPAMINA)",
            (187, 230, 242, 252),
        ),
        (
            (169, 255, 225, 277),
            "NÚCLEO\nPEDUNCULOPONTINO\n(ACETILCOLINA)",
            (165, 254, 230, 278),
        ),
        (
            (194, 279, 232, 297),
            "LOCUS COERULEUS\n(NORADRENALINA)",
            (186, 278, 238, 298),
        ),
        (
            (192, 299, 233, 315),
            "NÚCLEOS DEL RAFE\n(SEROTONINA)",
            (185, 298, 239, 316),
        ),
        (
            (188, 319, 233, 339),
            "TRACTO\nRETICULOESPINAL\nMEDIAL",
            (181, 318, 240, 340),
        ),
        (
            (186, 342, 234, 362),
            "TRACTO\nRETICULOESPINAL\nLATERAL",
            (178, 341, 241, 363),
        ),
        ((300, 277, 333, 296), "ZONA\nRETICULAR\nLATERAL", (296, 276, 340, 297)),
        ((306, 303, 340, 322), "ZONA\nRETICULAR\nMEDIAL", (300, 302, 345, 323)),
        ((301, 333, 339, 352), "ZONA\nRETICULAR\nMEDIANA", (295, 332, 345, 353)),
    ]
    draw = ImageDraw.Draw(image)
    draw.rectangle(sc((173, 227, 239, 364)), fill=WHITE)
    draw.rectangle(sc((297, 274, 350, 354)), fill=WHITE)
    for cover, *_ in modulatory:
        label(image, cover, "", maximum=3.5)
    for cover, text, place in modulatory:
        label(
            image,
            cover,
            text,
            place=place,
            maximum=4.5,
            minimum=2.65,
            style="bold",
            erase=False,
        )

    draw_vertical_region_bar(image, 10, (61, 90, 116, 146))
    draw_vertical_region_bar(image, 332, (62, 96, 127, 159))

    # Clave sensitivo/motor del panel inferior izquierdo.
    draw = ImageDraw.Draw(image)
    draw.rectangle(sc((18, 377, 114, 392)), fill=WHITE)
    draw.rectangle(sc((19, 379, 66, 389)), fill=(139, 139, 139))
    draw.rectangle(sc((66, 379, 113, 389)), fill=(83, 223, 228))
    draw.text(
        sc((42.5, 384)),
        "SENSITIVO",
        font=font(3.6, "bold"),
        fill=WHITE,
        anchor="mm",
    )
    draw.text(
        sc((89.5, 384)),
        "MOTOR",
        font=font(3.6, "bold"),
        fill=BLACK,
        anchor="mm",
    )
    image.save(HERE / "es-fig-2-11.png", optimize=True)


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    figure_2_9()
    figure_2_10()
    figure_2_11()


if __name__ == "__main__":
    main()
