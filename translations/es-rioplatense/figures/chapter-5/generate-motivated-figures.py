#!/usr/bin/env python3
"""Localiza los rótulos de las figuras de conducta motivada (5.21 a 5.26).

Los originales de site/assets/media no se modifican. Quedan en inglés los
créditos y la palabra PUTAMEN, idéntica en español. No se tapa el dibujo,
las flechas ni las líneas guía.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
WALL = (157, 196, 209)
BEAM = (112, 224, 228)
RADIATOR = (204, 228, 228)
PALE = (236, 247, 247)
STEM = (112, 212, 236)
STEM_DARK = (80, 154, 172)
AXIS = (186, 230, 232)
BAR = (46, 92, 96)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def _replace(image, ink):
    pixels = image.load()
    blocked = set(ink)
    for x, y in ink:
        replacement = None
        for step in range(1, 24):
            for nx, ny in ((x, y - step), (x, y + step), (x - step, y), (x + step, y)):
                if 0 <= nx < image.width and 0 <= ny < image.height and (nx, ny) not in blocked:
                    replacement = pixels[nx, ny]
                    break
            if replacement is not None:
                break
        pixels[x, y] = replacement or WHITE


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 248) -> None:
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            average = (red + green + blue) / 3
            if average < threshold and max(red, green, blue) - min(red, green, blue) < 42:
                ink.append((x, y))
    _replace(image, ink)


def erase_gray(image, box, scale=1, low=30, high=200) -> None:
    """Quita rótulos grises y deja trazos oscuros y rellenos de color."""
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            average = (red + green + blue) / 3
            if low <= average <= high and max(red, green, blue) - min(red, green, blue) < 36:
                ink.append((x, y))
    _replace(image, ink)


def erase_light(image, box, scale=1, low=205) -> None:
    """Quita texto claro sobre un relleno oscuro."""
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            average = (red + green + blue) / 3
            if average >= low and max(red, green, blue) - min(red, green, blue) < 28:
                ink.append((x, y))
    _replace(image, ink)


def write(image, box, text, *, scale=1, fill=BLACK, align="center", bold=True, size=None):
    max_w = max(8, (box[2] - box[0]) * scale - 2)
    max_h = max(8, (box[3] - box[1]) * scale - 2)
    draw = ImageDraw.Draw(image)
    if size is None:
        size = (box[3] - box[1]) * scale * (0.38 if "\n" in text else 0.72)
    chosen = face(size, bold)
    spacing = max(1, round(size * 0.12))
    bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    for _ in range(28):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.9
        chosen = face(size, bold)
        bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = box[0] * scale + 1 - bounds[0]
    elif align == "right":
        x = box[2] * scale - width - 1 - bounds[0]
    else:
        x = (box[0] + box[2]) / 2 * scale - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 * scale - height / 2 - bounds[1]
    draw.multiline_text(
        (round(x), round(y)), text, font=chosen, fill=fill,
        spacing=spacing, align=align,
    )


def cover(image, box, text, *, scale=1, align="center", bold=True, size=None,
          fill=BLACK, plate=WHITE, threshold=248):
    erase(image, box, scale, threshold=threshold)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    if text:
        write(image, box, text, scale=scale, align=align, bold=bold, size=size, fill=fill)


def cover_vertical(image, box, text, *, scale=1, fill=BLACK, size=None, plate=WHITE):
    erase(image, box, scale)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    max_w = max(8, bottom - top - 4)
    max_h = max(8, right - left - 4)
    if size is None:
        size = max_h * 0.72
    chosen = face(size, True)
    probe = ImageDraw.Draw(image)
    bounds = probe.textbbox((0, 0), text, font=chosen)
    for _ in range(24):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.9
        chosen = face(size, True)
        bounds = probe.textbbox((0, 0), text, font=chosen)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    strip = Image.new("RGBA", (width + 4, height + 4), (0, 0, 0, 0))
    ImageDraw.Draw(strip).text((-bounds[0] + 2, -bounds[1] + 2), text, font=chosen, fill=fill)
    turned = strip.rotate(90, expand=True)
    x = left + (right - left - turned.width) // 2
    y = top + (bottom - top - turned.height) // 2
    image.paste(turned, (x, y), turned)


def open_scaled(name: str, scale: int, pad=(0, 0, 0, 0), color=WHITE) -> Image.Image:
    image = Image.open(MEDIA / name).convert("RGB")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)
    left, top, right, bottom = (value * scale for value in pad)
    if left or top or right or bottom:
        canvas = Image.new("RGB", (image.width + left + right, image.height + top + bottom), color)
        canvas.paste(image, (left, top))
        return canvas
    return image


def save(image: Image.Image, name: str) -> None:
    image.save(OUT / name, optimize=True)
    print(name, image.size)


def figure_5_21() -> None:
    scale = 4
    image = open_scaled("0bcec61f2242cd97-skinner_box_scheme_01.svg-350x352.png", scale)
    # La palabra llega al marco de madera: se borra ahí sin pintar el cielo.
    erase(image, (236, 112, 262, 132), scale, threshold=190)
    cover(image, (206, 112, 238, 132), "Luces", scale=scale, size=30, plate=WALL, fill=BLACK)
    # Las letras «ts» quedan sobre el marco de madera; el borrado no las toma por el color.
    cover(image, (239, 112, 264, 132), "", scale=scale, plate=(193, 155, 120))
    ImageDraw.Draw(image).line(
        [(166 * scale, 142 * scale), (204 * scale, 124 * scale)],
        fill=(12, 12, 12), width=5,
    )
    save(image, "es-fig-5-21.png")


def figure_5_22() -> None:
    scale = 4
    image = open_scaled("86b4a68f2b0d1b8d-fig5.22_draft-350x273.png", scale)
    cover(image, (96, 15, 268, 42), "Homeostasis por\nretroalimentación negativa", scale=scale, size=28)
    cover(image, (98, 50, 152, 84), "Entrada de\ninformación\npor vía aferente", scale=scale, size=15)
    cover(image, (107, 94, 136, 162), "", scale=scale)
    cover(image, (154, 116, 198, 134), "Termorreceptor", scale=scale, size=15)
    cover(image, (16, 142, 96, 182), "Cambio detectado\npor el receptor", scale=scale, size=13)
    cover(image, (156, 88, 216, 110), "Centro de\ncontrol", scale=scale, size=16)
    erase_gray(image, (210, 42, 340, 58), scale, low=20, high=250)
    cover(image, (240, 56, 334, 88), "Salida de\ninformación\npor vía eferente", scale=scale, size=15)
    erase(image, (246, 103, 322, 118), scale, threshold=210)
    write(image, (252, 104, 316, 117), "Efector", scale=scale, size=18)
    cover(image, (16, 186, 100, 232), "Influencias\nambientales\ncambian la\nvariable", scale=scale, size=13)
    erase_gray(image, (60, 160, 155, 215), scale, low=20, high=250)
    cover(image, (108, 164, 176, 182), "Desequilibrio", scale=scale, size=14)
    cover(image, (128, 207, 242, 219), "Variable de la homeostasis", scale=scale, size=16, plate=BEAM)
    cover(
        image, (272, 158, 346, 214),
        "La respuesta del efector\nretroalimenta la variable\nhacia la homeostasis",
        scale=scale, size=13,
    )
    erase_gray(image, (210, 208, 300, 266), scale, low=20, high=250)
    cover(image, (292, 228, 348, 248), "Reequilibrio", scale=scale, size=14)
    save(image, "es-fig-5-22.png")


def figure_5_23() -> None:
    scale = 4
    image = open_scaled(
        "3195cdaf96f47773-1920px-key_hypothalamic_nuclei_and_other_areas_involved_in_g.png",
        scale,
    )
    cover(image, (52, 58, 118, 70), "Cuerpo calloso", scale=scale, size=16, plate=PALE)
    cover(image, (196, 70, 236, 80), "Tálamo", scale=scale, size=16, plate=PALE)
    erase(image, (168, 108, 278, 120), scale, threshold=230)
    cover(
        image, (274, 106, 322, 124),
        "Núcleos\nhipotalámicos\nlaterales",
        scale=scale, size=12, plate=PALE,
    )
    cover(image, (186, 128, 272, 148), "Cuerpo mamilar", scale=scale, size=13, align="left", plate=WHITE)
    cover(image, (78, 156, 148, 170), "Quiasma óptico", scale=scale, size=15, plate=PALE)
    cover(
        image, (172, 150, 228, 186),
        "Núcleo\nventromedial del\nhipotálamo",
        scale=scale, size=12, plate=(151, 213, 232), fill=BLACK,
    )
    cover(
        image, (170, 204, 224, 222),
        "Tronco\nencefálico",
        scale=scale, size=12, plate=STEM, fill=BLACK,
    )
    save(image, "es-fig-5-23.png")


def figure_5_24() -> None:
    scale = 4
    image = open_scaled("af15e1b279047183-fig5.24_draft-350x273.png", scale)
    cover(image, (62, 194, 158, 214), "Tipo silvestre", scale=scale, size=22)
    cover(image, (168, 194, 268, 214), "Ratón ob/ob", scale=scale, size=22)
    save(image, "es-fig-5-24.png")


def figure_5_25() -> None:
    scale = 4
    image = open_scaled("8a89a94df4fd3c25-fig5.25_draft-3-350x273.png", scale)
    plot = (149, 237, 241)
    pale_plot = (224, 250, 251)
    cover(image, (40, 2, 310, 20), "Duración de la alimentación y la bebida", scale=scale, size=20)
    erase(image, (114, 26, 156, 36), scale, threshold=200)
    cover(image, (130, 26, 158, 38), "Luz", scale=scale, size=15, plate=pale_plot)
    cover(image, (186, 22, 238, 36), "Oscuridad", scale=scale, size=13, plate=plot)
    erase(image, (114, 148, 156, 162), scale, threshold=200)
    cover(image, (130, 150, 158, 162), "Luz", scale=scale, size=15, plate=pale_plot)
    cover(image, (186, 148, 238, 162), "Oscuridad", scale=scale, size=13, plate=plot)
    cover_vertical(image, (46, 54, 58, 116), "% de actividad", scale=scale, size=15, plate=WHITE)
    cover_vertical(image, (46, 174, 58, 236), "% de actividad", scale=scale, size=15, plate=WHITE)
    erase_gray(image, (110, 132, 220, 146), scale, low=30, high=190)
    cover(image, (118, 128, 214, 139), "Tiempo (horas)", scale=scale, size=15, plate=plot)
    erase_gray(image, (110, 246, 220, 262), scale, low=30, high=190)
    cover(image, (118, 246, 214, 257), "Tiempo (horas)", scale=scale, size=15, plate=plot)
    for box in ((148, 96, 220, 128), (148, 214, 220, 246)):
        erase_light(image, box, scale, low=140)
        write(image, box, "Comer y beber\nhomeostáticos", scale=scale, size=13, fill=WHITE)
    cover(
        image, (268, 76, 348, 110),
        "Anticipatoria\n(no homeostática)\ncomer/beber",
        scale=scale, size=13,
    )
    cover(
        image, (268, 190, 348, 224),
        "Anticipatoria\n(no homeostática)\ncomer/beber",
        scale=scale, size=13,
    )
    save(image, "es-fig-5-25.png")


def figure_5_26() -> None:
    scale = 4
    image = open_scaled(
        "72837103cc645e2c-dopaminergic_pathways.svg-1-1024x705-1-350x245.png",
        scale,
    )
    cover(image, (2, 108, 58, 128), "Vía\nmesocortical", scale=scale, size=14, align="left")
    cover(image, (2, 136, 58, 156), "Vía\nnigroestriatal", scale=scale, size=14, align="left")
    cover(image, (2, 172, 56, 198), "Vía tubero-\ninfundibular", scale=scale, size=13, align="left")
    cover(image, (4, 210, 60, 232), "Vía\nmesolímbica", scale=scale, size=14, align="left")
    cover(image, (244, 4, 348, 16), "Estriado dorsal", scale=scale, size=15, align="left")
    cover(image, (276, 22, 340, 34), "Tálamo", scale=scale, size=15, align="left")
    cover(image, (286, 68, 348, 82), "Hipotálamo", scale=scale, size=15, align="left")
    cover(image, (292, 94, 348, 116), "Núcleo\naccumbens", scale=scale, size=14, align="left")
    cover(image, (286, 136, 348, 150), "Cerebelo", scale=scale, size=15, align="left")
    cover(image, (250, 176, 330, 198), "Sustancia\nnegra", scale=scale, size=14, align="left")
    cover(image, (236, 210, 348, 226), "Área tegmental ventral", scale=scale, size=14, align="left")
    cover(image, (132, 207, 176, 217), "Hipófisis", scale=scale, size=14)
    erase_gray(image, (166, 158, 198, 244), scale, low=15, high=120)
    cover_vertical(
        image, (181, 166, 191, 236), "Médula espinal",
        scale=scale, size=14, plate=(168, 236, 238),
    )
    save(image, "es-fig-5-26.png")


def main() -> None:
    figure_5_21()
    figure_5_22()
    figure_5_23()
    figure_5_24()
    figure_5_25()
    figure_5_26()


if __name__ == "__main__":
    main()
