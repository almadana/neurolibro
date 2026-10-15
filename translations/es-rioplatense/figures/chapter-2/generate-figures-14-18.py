#!/usr/bin/env python3
"""Genera las figuras 2.14, 2.15, 2.17 y 2.18 localizadas al español.

Solo depende de Pillow. Las coordenadas están expresadas en píxeles de las
fuentes de 350 px y se escalan de forma uniforme para conservar la relación
de aspecto. Los rótulos ingleses se cubren antes de dibujar los equivalentes
españoles; no se alteran los archivos fuente.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


SCALE = 4
ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf")
FONT_OBLIQUE = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Oblique.ttf")

WHITE = (255, 255, 255, 255)
INK = (20, 20, 20, 255)
CYAN = (199, 243, 245, 255)


def S(value):
    if isinstance(value, tuple):
        return tuple(round(v * SCALE) for v in value)
    return round(value * SCALE)


def font(size, bold=False, oblique=False):
    path = FONT_BOLD if bold else FONT_OBLIQUE if oblique else FONT
    return ImageFont.truetype(str(path), S(size))


def open_scaled(name):
    image = Image.open(MEDIA / name).convert("RGBA")
    return image.resize(S(image.size), Image.Resampling.LANCZOS)


def cover(draw, box, fill=WHITE):
    draw.rectangle(S(box), fill=fill)


def label(
    draw,
    box,
    text,
    *,
    size=6,
    fill=WHITE,
    color=INK,
    bold=False,
    oblique=False,
    align="center",
    anchor="mm",
    spacing=1,
):
    """Cubre box y centra texto multilínea dentro del mismo."""
    scaled_box = S(box)
    draw.rectangle(scaled_box, fill=fill)
    x0, y0, x1, y1 = scaled_box
    x = {"left": x0 + S(1), "center": (x0 + x1) // 2, "right": x1 - S(1)}[align]
    text_anchor = {"left": "lm", "center": anchor, "right": "rm"}[align]
    draw.multiline_text(
        (x, (y0 + y1) // 2),
        text,
        font=font(size, bold=bold, oblique=oblique),
        fill=color,
        anchor=text_anchor,
        align=align,
        spacing=S(spacing),
    )


def line(draw, points, fill=INK, width=0.45):
    draw.line([S(p) for p in points], fill=fill, width=max(1, S(width)))


def save(image, name):
    image.convert("RGB").save(
        OUT / name,
        format="PNG",
        optimize=True,
        dpi=(300, 300),
    )


def figure_214():
    image = open_scaled("98c06cbebd865f84-fig2.14_draft-1-350x273.png")
    d = ImageDraw.Draw(image)

    # Rótulos internos y laterales. Los conectores de capas se restauran.
    label(d, (174, 51, 215, 65), "FIBRAS\nPARALELAS", size=4.4, fill=CYAN)
    label(d, (286, 59, 336, 76), "CAPA\nMOLECULAR", size=4.1)
    label(d, (286, 77, 341, 97), "CAPA DE CÉLULAS\nDE PURKINJE", size=3.7)
    label(d, (286, 98, 341, 119), "CAPA\nGRANULOSA", size=4.0)
    label(d, (286, 125, 340, 153), "SUSTANCIA\nBLANCA", size=4.1)
    line(d, [(282, 62), (282, 144)])
    for y in (68, 87, 108, 136):
        line(d, [(282, y), (286, y)])

    label(d, (245, 109, 282, 124), "CÉLULA DE\nPURKINJE", size=4.0, fill=CYAN)
    label(d, (194, 126, 233, 141), "CÉLULAS\nGRANULOSAS", size=4.0, fill=CYAN)
    label(d, (239, 182, 294, 207), "AXÓN DE CÉLULA\nDE PURKINJE", size=3.7)
    label(d, (190, 211, 236, 233), "FIBRA\nMUSGOSA", size=4.0)
    label(
        d,
        (124, 231, 208, 252),
        "FIBRA TREPADORA DEL\nCOMPLEJO OLIVAR INFERIOR",
        size=3.7,
    )

    save(image, "es-fig-2-14.png")


def figure_215():
    image = open_scaled("8921635897b2df43-fig2.15_draft-350x273.png")
    d = ImageDraw.Draw(image)

    # Se limpia el margen superior completo para eliminar rótulos muy
    # próximos entre sí; luego se restauran sus líneas guía.
    cover(d, (0, 15, 245, 60))
    label(d, (24, 22, 72, 49), "SUSTANCIA\nGRIS", size=4.2)
    label(d, (80, 17, 137, 46), "SUSTANCIA\nBLANCA", size=4.2)
    label(d, (183, 20, 241, 51), "CUERPO\nCALLOSO", size=4.2)
    line(d, [(50, 49), (88, 88)])
    line(d, [(109, 46), (124, 91)])
    line(d, [(211, 51), (198, 135)])
    label(d, (59, 53, 121, 81), "CORTEZA\nCEREBRAL", size=4.1)
    label(d, (270, 96, 326, 127), "NÚCLEO\nCAUDADO", size=4.2)
    label(d, (277, 139, 330, 170), "NÚCLEOS\nBASALES", size=4.2)
    label(d, (150, 225, 263, 255), "HIPOCAMPO", size=4.3)

    label(d, (13, 109, 63, 124), "DIENCÉFALO", size=4.3)
    label(d, (25, 131, 61, 144), "TÁLAMO", size=4.2)
    label(d, (22, 151, 68, 165), "HIPOTÁLAMO", size=4.0)
    # Restaura la llave que agrupa tálamo e hipotálamo.
    line(d, [(60, 127), (55, 127), (55, 167), (60, 167)])

    save(image, "es-fig-2-15.png")


def figure_217():
    image = open_scaled("389ba38c4a042596-fig2.16_draft-350x350.png")
    d = ImageDraw.Draw(image)

    label(
        d,
        (48, 4, 304, 19),
        "CORTEZA CEREBRAL: ARQUITECTURA CELULAR",
        size=7.2,
        bold=True,
        oblique=True,
    )
    label(d, (70, 22, 137, 34), "CORTEZA MOTORA", size=4.6)
    label(d, (211, 22, 286, 34), "CORTEZA SENSORIAL", size=4.6)
    label(d, (140, 52, 213, 76), "FUNCIONES\nINTEGRADORAS", size=4.0)
    label(d, (142, 91, 211, 107), "ENTRADA SENSORIAL\n(AFERENTE)", size=3.8)
    label(
        d,
        (139, 111, 216, 138),
        "SALIDA HACIA\nOTRAS REGIONES\nDEL ENCÉFALO\n(EFERENTE)",
        size=3.35,
    )

    label(
        d,
        (43, 179, 307, 196),
        "CORTEZA CEREBRAL: ARQUITECTURA FUNCIONAL",
        size=7.0,
        bold=True,
        oblique=True,
    )
    # Rótulos superiores de los mapas corticales.
    label(d, (20, 195, 58, 218), "LÓBULO\nFRONTAL", size=3.6)
    label(d, (58, 195, 93, 214), "MOTORA", size=3.7)
    label(d, (91, 195, 141, 216), "SOMATO-\nSENSORIAL", size=3.45)
    label(d, (125, 202, 180, 230), "LÓBULO\nPARIETAL", size=3.4)
    label(d, (195, 197, 231, 217), "LÓBULO\nFRONTAL", size=3.6)
    label(d, (229, 194, 264, 214), "MOTORA", size=3.7)
    label(d, (262, 194, 313, 215), "SOMATO-\nSENSORIAL", size=3.45)
    label(d, (312, 204, 349, 229), "LÓBULO\nPARIETAL", size=3.35)

    # Funciones. Se mantienen intactos todos los números de Brodmann.
    label(d, (0, 218, 39, 241), "ÁREA DE\nBROCA", size=3.5)
    label(d, (0, 294, 42, 322), "COGNICIÓN", size=3.6)
    label(d, (38, 312, 66, 337), "VISIÓN", size=3.5)
    label(d, (63, 313, 108, 338), "AUDICIÓN", size=3.6)
    label(d, (108, 311, 166, 338), "LÓBULO\nTEMPORAL", size=3.5)
    label(d, (154, 216, 179, 242), "VISIÓN", size=3.2)
    label(d, (178, 217, 223, 243), "COGNICIÓN", size=3.5)
    label(d, (178, 297, 223, 324), "EMOCIONES", size=3.45)
    label(d, (140, 299, 179, 326), "VISIÓN", size=3.5)
    label(d, (205, 314, 249, 338), "COGNICIÓN", size=3.45)
    label(d, (244, 314, 286, 338), "OLFACCIÓN", size=3.45)
    label(d, (282, 302, 321, 338), "LÓBULO\nTEMPORAL", size=3.35)
    label(d, (305, 292, 349, 323), "ÁREA DE\nWERNICKE", size=3.35)
    label(d, (316, 318, 349, 338), "VISIÓN", size=3.5)
    label(
        d,
        (92, 339, 258, 350),
        "LOS NÚMEROS CORRESPONDEN A ÁREAS DE BRODMANN",
        size=3.15,
    )

    save(image, "es-fig-2-17.png")


def figure_218():
    image = open_scaled("3c45d3848ee5b2b8-anatomy_of_the_basal_ganglia-350x262.jpeg")
    d = ImageDraw.Draw(image)

    orange = (242, 153, 0, 255)
    orange_light = (245, 163, 17, 255)
    green = (25, 168, 95, 255)
    yellow = (236, 184, 55, 255)
    pink = (206, 66, 92, 255)

    label(d, (139, 97, 180, 122), "CUERPO DEL\nNÚCLEO\nCAUDADO", size=4.4, fill=orange, bold=True)
    label(d, (101, 139, 145, 166), "CABEZA DEL\nNÚCLEO\nCAUDADO", size=4.25, fill=orange_light, bold=True)
    label(d, (224, 122, 269, 151), "COLA DEL\nNÚCLEO\nCAUDADO", size=4.15, fill=orange, bold=True)
    label(d, (143, 136, 198, 159), "PUTAMEN", size=4.8, fill=orange_light, bold=True)
    label(d, (147, 155, 225, 190), "GLOBO\nPÁLIDO", size=4.4, fill=yellow, bold=True)
    label(d, (187, 109, 231, 127), "TÁLAMO", size=4.8, fill=green, bold=True)
    label(d, (111, 188, 162, 215), "NÚCLEO\nACCUMBENS", size=4.3, fill=pink, bold=True)

    save(image, "es-fig-2-18.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    figure_214()
    figure_215()
    figure_217()
    figure_218()
    print("Generadas:", ", ".join(f"es-fig-2-{n}.png" for n in (14, 15, 17, 18)))


if __name__ == "__main__":
    main()
