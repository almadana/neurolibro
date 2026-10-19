#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 3.35–3.48.

Los originales de site/assets/media no se modifican. La fig. 3.34 es una foto
sin rótulos. En la fig. 3.41 los letreros celestes se traducen; los rótulos
grises del interior de la terminal ocupan unos pocos píxeles sobre el dibujo.
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
BLACK = (0, 0, 0)
CYAN = (166, 240, 243)
CREAM = (245, 245, 245)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(7, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 210) -> None:
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            average = (red + green + blue) / 3
            if 20 < average < threshold and max(red, green, blue) - min(red, green, blue) < 40:
                ink.append((x, y))
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
        if replacement is not None:
            pixels[x, y] = replacement


def write(image, box, text, *, scale=1, fill=BLACK, align="center", bold=True, size=None):
    max_w = max(8, (box[2] - box[0]) * scale - 2)
    max_h = max(8, (box[3] - box[1]) * scale - 2)
    draw = ImageDraw.Draw(image)
    if size is None:
        size = max(7, (box[3] - box[1]) * scale * (0.38 if "\n" in text else 0.72))
    chosen = face(size, bold)
    spacing = max(0, round(scale * 0.25))
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
        x = box[2] * scale - width - bounds[0] - 1
    else:
        x = (box[0] + box[2]) / 2 * scale - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 * scale - height / 2 - bounds[1]
    draw.multiline_text((round(x), round(y)), text, font=chosen, fill=fill, spacing=spacing, align=align)


def cover(image, box, text, *, scale=1, align="center", bold=True, fill=WHITE, ink=BLACK, threshold=220, size=None, plate=True):
    erase(image, box, scale, threshold)
    if plate and fill is not None:
        left, top, right, bottom = scale_box(box, scale)
        ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=fill)
    write(image, box, text, scale=scale, align=align, bold=bold, fill=ink, size=size)


def cover_vertical(image, box, text, *, scale=1, fill=BLACK, plate=WHITE):
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    max_w = max(8, bottom - top - scale)
    max_h = max(8, right - left - 2)
    size = max_h * 0.82
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


def open_scaled(name: str, scale: int) -> Image.Image:
    image = Image.open(MEDIA / name).convert("RGB")
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)


def save(image: Image.Image, name: str) -> None:
    image.save(OUT / name, optimize=True)
    print(name, image.size)


def fig_335():
    image = open_scaled("f552750b6ae6d17a-image3-350x193.jpeg", 4)
    names = [
        ((8, 88, 88, 106), "Morfina"),
        ((95, 88, 175, 106), "Oxicodona"),
        ((185, 88, 268, 106), "Hidrocodona"),
        ((272, 88, 346, 106), "Buprenorfina"),
        ((4, 176, 88, 192), "(1R, 2R)-\nTramadol"),
        ((92, 176, 178, 192), "(1S, 2S)-\nTramadol"),
        ((185, 176, 275, 192), "Dextropropoxifeno"),
        ((278, 176, 346, 192), "Metadona"),
    ]
    for box, text in names:
        cover(image, box, text, scale=4, bold=False)
    save(image, "es-fig-3-35.png")


def fig_336():
    image = open_scaled("a0a52f59e9cd09a8-image4-350x494.jpeg", 4)
    pink = (255, 233, 239)
    labels = [
        ((36, 16, 140, 40), "Absorción", CREAM),
        ((200, 16, 320, 40), "Metabolismo", CREAM),
        ((26, 34, 78, 50), "Luz", CREAM),
        ((200, 38, 275, 54), "Hígado", CREAM),
        ((140, 176, 255, 200), "Distribución", CREAM),
        ((96, 196, 160, 214), "Tejidos", pink),
        ((230, 194, 345, 214), "Sistema sanguíneo", pink),
        ((16, 372, 128, 400), "Eliminación", (248, 250, 237)),
        ((210, 354, 280, 374), "Riñones", (255, 254, 242)),
    ]
    for box, text, fill in labels:
        cover(image, box, text, scale=4, fill=fill)
    # «Mucosa» se escribe igual. La palabra vertical en inglés queda al lado del vaso.
    cover_vertical(image, (146, 88, 176, 172), "Linfa", scale=4, plate=(242, 250, 239))
    save(image, "es-fig-3-36.png")


def fig_337():
    image = open_scaled("1c11015f82c69567-screenshot-2022-11-07-at-12.44.40-350x287.png", 4)
    plot = (236, 241, 244)
    # El rótulo azul original va pegado al eje, dentro del gráfico.
    left, top, right, bottom = scale_box((48, 28, 78, 225), 4)
    pixels = image.load()
    for y in range(top, bottom):
        for x in range(left, right):
            red, green, blue = pixels[x, y]
            if blue > red + 8 and blue > 120 and red < 175:
                pixels[x, y] = plot
    cover(image, (118, 56, 214, 82), "Fase de\nabsorción", scale=4, fill=(245, 246, 247))
    cover(image, (198, 94, 332, 128), "Fase de\neliminación (T½)", scale=4, fill=(245, 246, 247))
    cover(image, (145, 258, 230, 284), "Tiempo", scale=4)
    cover_vertical(image, (0, 48, 28, 230), "Concentración plasmática", scale=4)
    save(image, "es-fig-3-37.png")


def fig_338():
    image = open_scaled("63a72b994f6088b9-image6-350x294.jpeg", 4)
    cover(
        image, (8, 0, 342, 38),
        "Concentración plasmática del fármaco\nen función del tiempo de respuesta",
        scale=4,
    )
    cover(image, (200, 42, 348, 58), "Vía de administración", scale=4, align="left")
    cover(image, (228, 60, 348, 76), "oral", scale=4, align="left", bold=False)
    cover(image, (228, 78, 348, 94), "IM (intramuscular)", scale=4, align="left", bold=False)
    cover(image, (228, 96, 348, 114), "IV (intravenosa)", scale=4, align="left", bold=False)
    cover(image, (145, 272, 220, 292), "Tiempo", scale=4)
    cover_vertical(image, (2, 50, 22, 250), "Concentración plasmática del fármaco", scale=4)
    save(image, "es-fig-3-38.png")


def fig_339():
    image = open_scaled("78b9de753a083bd1-fig3.38_draft-1-350x273.png", 4)
    cover(image, (16, 4, 334, 26), "Factores que afectan la solubilidad en la membrana", scale=4)
    headers = [
        ((8, 34, 112, 62), "Tamaño de la\nmolécula del fármaco"),
        ((114, 34, 224, 62), "Ionización de la\nmolécula del fármaco"),
        ((226, 34, 344, 62), "Liposolubilidad de la\nmolécula del fármaco"),
    ]
    pairs = [
        ((6, 64, 54, 86), "Pequeña"),
        ((56, 64, 108, 86), "Grande"),
        ((110, 64, 172, 86), "No ionizada"),
        ((174, 64, 224, 86), "Ionizada"),
        ((220, 64, 286, 86), "Lipofílica"),
        ((284, 64, 348, 86), "Hidrofílica"),
    ]
    for box, text in headers:
        cover(image, box, text, scale=4)
    for box, text in pairs:
        cover(image, box, text, scale=4, size=22)
    save(image, "es-fig-3-39.png")


def fig_340():
    image = open_scaled("9a33a675f3ab93b0-image8-350x186.jpeg", 4)
    cover(image, (32, 78, 100, 90), "Etanol", scale=4, size=28)
    cover(image, (118, 78, 215, 90), "Acetaldehído", scale=4, size=26)
    cover(image, (268, 78, 332, 90), "Acetato", scale=4, size=28)
    save(image, "es-fig-3-40.png")


def fig_341():
    image = open_scaled("b7ad2f2e56b1bd36-fig3.41_draft-350x273.png", 5)
    labels = [
        ((168, 4, 248, 43), "El fármaco inhibe\nla síntesis del\nneurotransmisor"),
        ((4, 34, 132, 58), "El fármaco\nsirve de precursor"),
        ((248, 50, 348, 78), "El fármaco estimula\nlos autorreceptores"),
        ((2, 66, 128, 94), "Impide almacenar\nel neurotransmisor\nen las vesículas"),
        ((274, 96, 348, 124), "El fármaco inhibe\nla degradación"),
        ((2, 112, 108, 142), "El fármaco inhibe\nla liberación"),
        ((262, 184, 348, 212), "El fármaco inhibe\nla recaptación"),
        ((2, 176, 108, 210), "El fármaco estimula\nla liberación"),
        ((128, 234, 236, 271), "El fármaco inhibe\nlos autorreceptores"),
        ((40, 214, 140, 240), "El fármaco estimula\nlos receptores\npostsinápticos"),
    ]
    for box, text in labels:
        cover(image, box, text, scale=5, fill=CYAN, ink=BLACK, threshold=180)
    save(image, "es-fig-3-41.png")


def fig_342():
    image = open_scaled("a232a347e871536a-fig3.42_draft-350x273.png", 4)
    cover(image, (130, 32, 230, 54), "Ligando (fármaco o\nneurotransmisor)", scale=4)
    cover(image, (46, 108, 82, 126), "Fuera", scale=4)
    cover(image, (46, 166, 82, 184), "Dentro", scale=4)
    cover(image, (95, 100, 150, 118), "Receptor", scale=4)
    cover(image, (188, 98, 270, 122), "Sitio de unión\ndel receptor", scale=4)
    cover(image, (95, 168, 155, 186), "Efector", scale=4)
    cover(image, (190, 188, 300, 214), "Efectos\nintracelulares", scale=4)
    save(image, "es-fig-3-42.png")


def fig_343():
    image = open_scaled("2c00003268e4012a-fig-1-2xedit-e1671112385977-350x276.png", 4)
    cover(image, (100, 248, 280, 274), "Concentración del fármaco", scale=4)
    cover_vertical(image, (0, 30, 20, 230), "Efecto (% del máximo)", scale=4)
    save(image, "es-fig-3-43.png")


def fig_344():
    image = open_scaled("1734d0da926a2095-3.43.-comparing-efficacy-and-potency-of-analgesic-drugs-e167.png", 4)
    arrow = (192, 244, 247)
    plot = (244, 253, 254)
    cover(image, (8, 0, 342, 16), "Curvas dosis-respuesta de cuatro analgésicos", scale=4)
    cover(image, (8, 16, 168, 46), "Más potente:\nla curva se desplaza a la izquierda", scale=4, fill=arrow, size=20)
    cover(image, (168, 16, 342, 46), "Menos potente:\nla curva se desplaza a la derecha", scale=4, fill=arrow, size=20)
    cover(image, (248, 58, 348, 72), "Efecto máximo", scale=4, align="left")
    cover(image, (278, 70, 348, 84), "Mayor eficacia", scale=4, align="left")
    cover(image, (278, 104, 348, 120), "Menor eficacia", scale=4, align="left")
    cover(
        image, (250, 116, 348, 140),
        "A menudo el dolor es demasiado intenso para cualquier dosis de aspirina.",
        scale=4, align="left", bold=False,
    )
    cover(
        image, (168, 146, 272, 188),
        "Hay que mirar siempre qué se mide: un efecto conductual (el dolor), no el efecto sobre el receptor.",
        scale=4, align="left", bold=False, fill=plot,
    )
    for box, text in (
        ((288, 140, 348, 152), "Aspirina"),
        ((288, 152, 348, 164), "Codeína"),
        ((288, 164, 348, 176), "Morfina"),
        ((288, 176, 348, 190), "Hidromorfona"),
    ):
        cover(image, box, text, scale=4, align="left", bold=False)
    cover_vertical(image, (0, 48, 14, 185), "Porcentaje de reducción del umbral del dolor", scale=4)
    cover(image, (110, 192, 240, 208), "Dosis (mg)", scale=4)
    save(image, "es-fig-3-44.png")


def fig_345():
    image = open_scaled("5afd302b438545d5-agonist-finished-edit-1-350x257.png", 4)
    cover(image, (8, 84, 78, 104), "Agonista", scale=4)
    cover(image, (88, 84, 160, 104), "Receptor", scale=4)
    cover(image, (165, 82, 345, 116), "Interacción\nagonista-receptor", scale=4)
    cover(image, (268, 36, 342, 66), "Acción o efecto\ndel fármaco", scale=4, fill=CYAN)
    cover(image, (8, 216, 85, 236), "Antagonista", scale=4)
    cover(image, (88, 216, 160, 236), "Receptor", scale=4)
    cover(image, (165, 214, 345, 250), "Interacción\nagonista-receptor", scale=4)
    cover(image, (268, 164, 344, 196), "Sin acción ni efecto\ndel fármaco", scale=4, fill=CYAN)
    save(image, "es-fig-3-45.png")


def fig_346():
    image = open_scaled("487bce58086d1ffd-3.45-antagonist-graphs-e1671097670538-350x535.png", 4)
    plot = (232, 246, 248)
    cover(image, (70, 0, 280, 16), "A) Antagonista competitivo", scale=4)
    cover(image, (80, 262, 310, 278), "B) Antagonista no competitivo", scale=4)
    ImageDraw.Draw(image).rectangle(scale_box((55, 228, 305, 244), 4), fill=plot)
    ImageDraw.Draw(image).line(scale_box((36, 232, 305, 232), 4), fill=(90, 90, 90), width=3)
    cover(image, (40, 246, 320, 262), "Concentración de agonista o de antagonista", scale=4, size=24)
    cover(image, (36, 516, 314, 534), "Concentración de agonista o de antagonista", scale=4, fill=WHITE, size=20)
    legend = (232, 246, 248)
    cover(image, (252, 136, 318, 148), "Agonista solo", scale=4, align="left", bold=False, fill=legend, size=16)
    cover(image, (252, 150, 322, 162), "Agonista + antagonista", scale=4, align="left", bold=False, fill=legend, size=14)
    cover(image, (252, 164, 318, 176), "Antagonista solo", scale=4, align="left", bold=False, fill=legend, size=16)
    cover(image, (248, 408, 318, 420), "Agonista solo", scale=4, align="left", bold=False, fill=legend, size=16)
    cover(image, (248, 422, 322, 434), "Agonista + antagonista", scale=4, align="left", bold=False, fill=legend, size=14)
    cover(image, (248, 436, 318, 448), "Antagonista solo", scale=4, align="left", bold=False, fill=legend, size=16)
    cover_vertical(image, (0, 40, 14, 200), "% de respuesta", scale=4)
    cover_vertical(image, (0, 290, 14, 500), "% de respuesta", scale=4)
    save(image, "es-fig-3-46.png")


def fig_347():
    image = open_scaled("8cd0b90d54a84fde-image17.jpeg", 2)
    cover(image, (720, 4, 880, 80), "Agonista\npleno", scale=2)
    cover(image, (720, 155, 880, 240), "Agonista\nparcial", scale=2)
    cover(image, (700, 310, 890, 400), "Antagonista\nneutro", scale=2)
    cover(image, (720, 465, 880, 555), "Agonista\ninverso", scale=2)
    cover(image, (250, 530, 370, 575), "Baja", scale=2)
    cover(image, (560, 530, 700, 580), "Alta", scale=2)
    cover(image, (370, 565, 560, 612), "Dosis", scale=2)
    cover_vertical(image, (0, 145, 158, 390), "Porcentaje de respuesta respecto del valor basal", scale=2)
    ImageDraw.Draw(image).rectangle(scale_box((148, 220, 172, 258), 2), fill=WHITE)
    save(image, "es-fig-3-47.png")


def fig_348():
    image = open_scaled("87e1f1bf6fd2353d-image18-350x231.jpeg", 4)
    cover(image, (36, 18, 128, 34), "Farmacocinética", scale=4, size=22)
    cover(image, (198, 18, 300, 34), "Farmacodinamia", scale=4, size=22)
    cover(image, (8, 58, 84, 92), "Adherencia y errores de medicación", scale=4, bold=False)
    cover(
        image, (86, 46, 176, 94),
        "Absorción, tamaño y composición corporal, unión a proteínas plasmáticas, líquidos y eliminación",
        scale=4, bold=False,
    )
    cover(
        image, (178, 48, 258, 90),
        "Interacción fármaco-receptor y estado funcional del receptor",
        scale=4, bold=False,
    )
    cover(image, (262, 58, 346, 90), "Tratamientos concomitantes", scale=4, bold=False)
    boxes = [
        ((14, 114, 54, 146), "Dosis prescripta"),
        ((64, 114, 124, 148), "Régimen realmente administrado"),
        ((132, 114, 202, 148), "Concentración del fármaco en el sitio de acción"),
        ((206, 114, 278, 148), "Intensidad del efecto farmacológico"),
        ((286, 114, 344, 148), "Resultado clínico"),
    ]
    for box, text in boxes:
        cover(image, box, text, scale=4, bold=False)
    cover(
        image, (78, 166, 346, 226),
        "(i) Factores fisiológicos (edad y función renal)\n"
        "(ii) Factores patológicos (p. ej., riñón, hígado y trastornos metabólicos)\n"
        "(iii) Variantes genéticas\n"
        "(iv) Interacciones entre fármacos\n"
        "(v) Aparición de resistencia o de tolerancia",
        scale=4, align="left", bold=False,
    )
    save(image, "es-fig-3-48.png")


def main():
    fig_335()
    fig_336()
    fig_337()
    fig_338()
    fig_339()
    fig_340()
    fig_341()
    fig_342()
    fig_343()
    fig_344()
    fig_345()
    fig_346()
    fig_347()
    fig_348()


if __name__ == "__main__":
    main()
