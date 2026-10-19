#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 4.17 a 4.30.

Los originales de site/assets/media no se modifican. La 4.26 solo tiene
letras y números, y las 4.28 y 4.30 no tienen rótulos: no se regeneran.
Los créditos quedan en inglés. K+, Ca2+, Hz, A, B y C se conservan.
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
CYAN = (239, 252, 253)
SHADE = (224, 250, 251)
BAR = (163, 163, 163)
LAV = (230, 228, 241)
PINK = (246, 200, 194)
YELLOW = (255, 250, 212)
PEACH = (242, 206, 180)
PINK_BG = (254, 235, 230)
YELLOW_BG = (251, 250, 212)
OVAL = (172, 172, 172)
BROWN = (70, 40, 30)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 220) -> None:
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


def local_color(image: Image.Image, box, scale: int, fallback=LAV):
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    samples = []
    step_x = max(1, (right - left) // 8)
    step_y = max(1, (bottom - top) // 8)
    for y in range(top, bottom + 1, step_y):
        for x in range(left, right + 1, step_x):
            pixel = image.getpixel((x, y))
            if sum(pixel) / 3 > 195:
                samples.append(pixel)
    if not samples:
        return fallback
    samples.sort(key=lambda pixel: sum(pixel))
    return samples[len(samples) // 2]


def cover(image, box, text, *, scale=1, align="center", bold=True, size=None,
          fill=BLACK, plate=WHITE, threshold=220):
    if plate is None:
        plate = local_color(image, box, scale)
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


def open_scaled(name: str, scale: int, pad=(0, 0, 0, 0)) -> Image.Image:
    image = Image.open(MEDIA / name).convert("RGB")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)
    left, top, right, bottom = (value * scale for value in pad)
    if left or top or right or bottom:
        canvas = Image.new("RGB", (image.width + left + right, image.height + top + bottom), WHITE)
        canvas.paste(image, (left, top))
        return canvas
    return image


def save(image: Image.Image, name: str) -> None:
    image.save(OUT / name, optimize=True)
    print(name, image.size)


def figure_4_17() -> None:
    scale = 4
    image = open_scaled("129f1de0045caff6-fig4.17_draft-350x273.png", scale)
    cover(image, (24, 28, 78, 49), "FUENTE\nSONORA", scale=scale, size=16)
    for box, _text in (
        ((96, 46, 142, 55), "comprimido"),
        ((149, 46, 179, 55), "enrarecido"),
        ((185, 46, 233, 55), "comprimido"),
        ((240, 46, 270, 55), "enrarecido"),
    ):
        cover(image, box, _text, scale=scale, size=14, fill=WHITE, plate=BAR, threshold=200)
    cover(image, (150, 132, 184, 144), "UN CICLO", scale=scale, size=14, plate=SHADE)
    cover_vertical(image, (46, 152, 64, 220), "PRESIÓN DEL AIRE", scale=scale, size=15)
    cover(image, (230, 240, 290, 255), "DISTANCIA", scale=scale, size=18)
    save(image, "es-fig-4-17.png")


def figure_4_18() -> None:
    scale = 4
    image = open_scaled("916e46c4a88cbffc-fig4.18_draft-350x273.png", scale, pad=(0, 0, 18, 0))
    cover(image, (125, 6, 215, 18), "FRECUENCIA", scale=scale, size=18, plate=CYAN)
    cover(image, (125, 98, 230, 112), "AMPLITUD", scale=scale, size=18, plate=CYAN)
    cover(image, (140, 176, 205, 190), "FASE", scale=scale, size=18, plate=CYAN)
    cover(image, (98, 84, 142, 96), "UN CICLO", scale=scale, size=13, plate=CYAN)
    for top, bottom in ((21, 46), (55, 78), (104, 127), (138, 161), (191, 215), (230, 253)):
        cover_vertical(image, (68, top, 84, bottom), "PRESIÓN", scale=scale, size=13, plate=CYAN)
    # TIME está escrito sobre el eje. Se tapa y se redibuja la línea.
    for top, bottom, axis_y in (
        (26, 42, 34), (55, 72, 64), (108, 124, 116),
        (142, 158, 150), (198, 216, 206), (228, 244, 236),
    ):
        cover(image, (252, top, 282, bottom), "", scale=scale, plate=CYAN)
        y = axis_y * scale
        ImageDraw.Draw(image).line((248 * scale, y, 286 * scale, y), fill=(45, 45, 45), width=3)
        cover(image, (286, top, 364, bottom), "TIEMPO", scale=scale, size=13, plate=WHITE, align="left")
    save(image, "es-fig-4-18.png")


def figure_4_19() -> None:
    scale = 4
    image = open_scaled("869884865fc84c02-fig4.19_draft-2-350x168.png", scale, pad=(0, 0, 16, 0))
    cover(image, (286, 36, 360, 54), "CLARINETE", scale=scale, size=18, align="left")
    cover(image, (286, 88, 350, 106), "VIOLÍN", scale=scale, size=18, align="left")
    cover_vertical(image, (58, 48, 72, 74), "PRESIÓN", scale=scale, size=12, plate=CYAN)
    cover_vertical(image, (58, 98, 72, 124), "PRESIÓN", scale=scale, size=12, plate=CYAN)
    cover(image, (242, 52, 286, 72), "", scale=scale, plate=CYAN)
    cover(image, (242, 102, 286, 122), "", scale=scale, plate=CYAN)
    draw = ImageDraw.Draw(image)
    draw.line((230 * scale, 62 * scale, 292 * scale, 62 * scale), fill=(20, 20, 20), width=4)
    draw.line((230 * scale, 112 * scale, 292 * scale, 112 * scale), fill=(20, 20, 20), width=4)
    cover(image, (292, 54, 360, 70), "TIEMPO", scale=scale, size=14, align="left")
    cover(image, (292, 104, 360, 120), "TIEMPO", scale=scale, size=14, align="left")
    save(image, "es-fig-4-19.png")


def figure_4_20() -> None:
    scale = 4
    shift = 42
    image = open_scaled(
        "f020a86861bff419-1404_the_structures_of_the_ear-e1671098730834-350x216.jpeg",
        scale, pad=(shift, 0, 78, 4),
    )

    def box(coords):
        left, top, right, bottom = coords
        return (left + shift, top, right + shift, bottom)

    cover(image, (2, 64, 78, 82), "Aurícula", scale=scale, align="right", size=22)
    cover(image, (2, 114, 78, 140), "Conducto\nauditivo", scale=scale, align="right", size=20)
    cover(image, box((138, 16, 184, 42)), "Martillo", scale=scale, size=16)
    cover(image, box((184, 16, 224, 42)), "Yunque", scale=scale, size=16)
    cover(image, box((268, 16, 426, 46)), "Estribo (unido\na la ventana oval)", scale=scale, align="left", size=16)
    right = (
        ((268, 48, 426, 70), "Vestíbulo"),
        ((268, 70, 426, 90), "Nervio vestibular"),
        ((268, 90, 426, 110), "Nervio coclear"),
        ((268, 110, 426, 130), "Ventana redonda"),
        ((268, 130, 426, 150), "Cóclea"),
        ((262, 154, 426, 178), "Trompa de Eustaquio"),
    )
    for coords, text in right:
        cover(image, box(coords), text, scale=scale, align="left", size=18)
    cover(image, box((118, 168, 188, 190)), "Membrana\ntimpánica", scale=scale, size=15)
    cover(image, box((192, 168, 248, 190)), "Cavidad\ntimpánica", scale=scale, size=15)
    cover(image, box((40, 200, 125, 214)), "Oído externo", scale=scale, size=16)
    cover(image, box((145, 200, 215, 214)), "Oído medio", scale=scale, size=16)
    cover(image, box((220, 200, 290, 214)), "Oído interno", scale=scale, size=16)
    save(image, "es-fig-4-20.png")


def figure_4_21a() -> None:
    scale = 4
    shift = 28
    image = open_scaled(
        "58ab1074327bfe15-fig4boutheear-e1673866017641-350x188.jpeg",
        scale, pad=(shift, 4, 24, 8),
    )

    def box(coords):
        left, top, right, bottom = coords
        return (left + shift, top + 4, right + shift, bottom + 4)

    cover(image, box((36, 12, 72, 26)), "base", scale=scale, size=16, fill=BROWN, plate=None)
    cover(image, box((322, 14, 348, 26)), "ápex", scale=scale, size=15, fill=BROWN, plate=None)
    cover(image, box((100, 14, 175, 42)), "membrana\nde Reissner", scale=scale, size=14, fill=BROWN, plate=None)
    cover(image, box((2, 40, 48, 64)), "ventana\noval", scale=scale, size=14, fill=BROWN, plate=None)
    cover(image, box((2, 82, 42, 98)), "estribo", scale=scale, size=14, fill=BROWN, plate=None)
    cover(image, box((4, 100, 40, 118)), "", scale=scale, plate=None)
    cover(image, box((2, 128, 52, 154)), "ventana\nredonda", scale=scale, size=13, fill=BROWN, plate=None)
    cover(image, box((155, 68, 255, 82)), "rampa vestibular", scale=scale, size=14, fill=BROWN, plate=PINK, threshold=160)
    cover(image, box((165, 90, 240, 106)), "rampa media", scale=scale, size=14, fill=BROWN, plate=YELLOW, threshold=160)
    cover(image, box((155, 110, 255, 124)), "rampa timpánica", scale=scale, size=14, fill=BROWN, plate=PINK, threshold=160)
    cover(image, box((286, 40, 338, 54)), "perilinfa", scale=scale, size=14, fill=BROWN, plate=None)
    cover(image, box((268, 136, 340, 152)), "endolinfa", scale=scale, size=15, fill=BROWN, plate=None)
    cover(image, box((292, 158, 368, 176)), "helicotrema", scale=scale, size=14, fill=BROWN, plate=None)
    cover(image, box((100, 152, 170, 180)), "membrana\nbasilar", scale=scale, size=14, fill=BROWN, plate=None)
    save(image, "es-fig-4-21a.png")


def figure_4_21b() -> None:
    scale = 4
    shift = 36
    image = open_scaled(
        "cd91aaf1ee11e54c-cochlea-350x291.jpeg",
        scale, pad=(shift, 0, 28, 0),
    )

    def box(coords):
        left, top, right, bottom = coords
        return (left + shift, top, right + shift, bottom)

    cover(image, box((160, 4, 220, 40)), "rampa\nvestibular", scale=scale, size=14, fill=BROWN, plate=None)
    cover(image, box((262, 28, 348, 52)), "membrana\nde Reissner", scale=scale, size=14, fill=BROWN, plate=None, align="left")
    cover(image, box((2, 104, 72, 130)), "rampa media\n(conducto coclear)", scale=scale, size=12, fill=BROWN, plate=None, align="right")
    cover(image, box((2, 155, 70, 180)), "membrana\ntectoria", scale=scale, size=13, fill=BROWN, plate=None, align="right")
    cover(image, box((2, 208, 72, 230)), "órgano de Corti", scale=scale, size=13, fill=BROWN, plate=None, align="right")
    cover(image, box((8, 255, 120, 290)), "pared ósea\nde la cóclea", scale=scale, size=13, fill=BROWN, plate=None)
    cover(image, box((148, 258, 230, 292)), "membrana\nbasilar", scale=scale, size=13, fill=BROWN, plate=None)
    cover(image, box((286, 214, 350, 252)), "rampa\ntimpánica", scale=scale, size=14, fill=BROWN, plate=None, align="left")
    cover(image, box((290, 145, 350, 175)), "nervio\ncoclear", scale=scale, size=14, fill=BROWN, plate=None, align="left")
    save(image, "es-fig-4-21b.png")


def figure_4_21c() -> None:
    scale = 4
    shift = 8
    image = open_scaled(
        "a256c0bf454f671c-cochleasection-e1666299017854-350x213.jpeg",
        scale, pad=(shift, 0, 36, 6),
    )

    def box(coords):
        left, top, right, bottom = coords
        return (left + shift, top, right + shift, bottom)

    labels = (
        ((185, 28, 270, 48), "rampa vestibular", 14),
        ((95, 42, 160, 62), "rampa media", 14),
        ((175, 58, 235, 86), "membrana\ntectoria", 13),
        ((288, 70, 360, 90), "haz de cilios", 14),
        ((95, 68, 155, 96), "célula ciliada\nexterna", 12),
        ((292, 112, 360, 142), "célula ciliada\ninterna", 13),
        ((232, 136, 278, 160), "arco de\nCorti", 13),
        ((292, 158, 360, 200), "fibras del\nganglio espiral", 12),
        ((178, 164, 240, 184), "rampa timpánica", 12),
        ((100, 176, 155, 208), "células\nde sostén", 12),
        ((158, 180, 205, 210), "células\npilares", 12),
        ((0, 142, 42, 172), "células\nde sostén", 11),
        ((36, 188, 95, 216), "membrana\nbasilar", 13),
    )
    for coords, text, size in labels:
        cover(image, box(coords), text, scale=scale, size=size, fill=BROWN, plate=(232, 230, 242))
    save(image, "es-fig-4-21c.png")


def figure_4_22() -> None:
    scale = 3
    image = open_scaled("f87e6220f67ef4d6-fig-22-sd329_1_017iedit-1-350x479.png", scale)
    cover(image, (4, 2, 78, 16), "ENDOLINFA", scale=scale, size=16, plate=YELLOW_BG)
    cover(image, (4, 418, 78, 436), "PERILINFA", scale=scale, size=16, plate=PINK_BG)
    cover(image, (130, 170, 215, 190), "despolarización", scale=scale, size=15, plate=PEACH)
    cover(image, (258, 182, 348, 214), "canal de calcio\ndependiente de voltaje", scale=scale, size=13, align="left", plate=PINK_BG)
    cover(image, (248, 310, 340, 328), "glutamato", scale=scale, size=15, align="left", plate=PINK_BG)
    cover(image, (230, 358, 345, 376), "neurotransmisor", scale=scale, size=15, align="left", plate=PINK_BG)
    cover(image, (248, 404, 360, 422), "nervio coclear", scale=scale, size=15, align="left", plate=PINK_BG)
    save(image, "es-fig-4-22.png")


def figure_4_23() -> None:
    scale = 4
    image = open_scaled("f66832aedb191c8a-fig4.23_draft-350x273.png", scale, pad=(0, 0, 40, 0))
    ovals = (
        ((62, 32, 84, 48), "ganglio\nespiral"),
        ((102, 30, 124, 48), "complejo\nnuclear\ncoclear"),
        ((142, 30, 164, 48), "complejo\nolivar\nsuperior"),
        ((183, 30, 205, 48), "colículo\ninferior"),
        ((223, 30, 245, 48), "núcleo\ngeniculado\nmedial"),
        ((263, 30, 285, 48), "corteza\nauditiva"),
    )
    for box, text in ovals:
        cover(image, box, text, scale=scale, size=11, fill=BLACK, plate=OVAL)
    cover(image, (78, 8, 112, 26), "nervio\ncoclear", scale=scale, size=11)
    cover(image, (118, 8, 155, 26), "cuerpo\ntrapezoide", scale=scale, size=11)
    cover(image, (162, 8, 198, 26), "lemnisco\nlateral", scale=scale, size=11)
    right = (
        ((252, 82, 385, 102), "corteza auditiva"),
        ((252, 104, 385, 128), "núcleo geniculado\nmedial"),
        ((252, 142, 385, 162), "colículo inferior"),
        ((252, 182, 385, 202), "lemnisco lateral"),
        ((252, 224, 385, 250), "complejo olivar\nsuperior"),
    )
    for box, text in right:
        cover(image, box, text, scale=scale, size=15, align="left")
    cover(image, (118, 176, 158, 198), "ganglio\nespiral", scale=scale, size=11)
    cover(image, (160, 166, 208, 194), "núcleos del\ncomplejo nuclear\ncoclear", scale=scale, size=11)
    cover(image, (62, 244, 115, 266), "cóclea", scale=scale, size=14)
    cover(image, (118, 246, 168, 268), "nervio\ncoclear", scale=scale, size=12)
    cover(image, (172, 246, 225, 268), "cuerpo\ntrapezoide", scale=scale, size=12)
    save(image, "es-fig-4-23.png")


def figure_4_24() -> None:
    scale = 4
    image = open_scaled("16d67b6dbb468690-4.27-350x309.png", scale, pad=(0, 0, 8, 0))
    cover(image, (176, 16, 350, 30), "LÓBULO PARIETAL: VÍA DEL «DÓNDE»", scale=scale, size=16)
    cover(image, (8, 228, 198, 246), "LÓBULO TEMPORAL: VÍA DEL «QUÉ»", scale=scale, size=15)
    save(image, "es-fig-4-24.png")


def figure_4_25() -> None:
    scale = 4
    image = open_scaled("dd7040dc73628f68-fig-4.25-edit-350x419.png", scale)
    cover(image, (88, 4, 155, 42), "membrana\nbasilar", scale=scale, size=14, fill=BROWN, plate=None)
    save(image, "es-fig-4-25.png")


def figure_4_27() -> None:
    scale = 4
    image = open_scaled("06aa15d3796b0161-fig4.27_draft-350x273.png", scale, pad=(0, 0, 8, 0))
    cover(image, (48, 6, 302, 42), "EL PRINCIPIO DE LA ANDANADA", scale=scale, size=18)
    cover(image, (278, 58, 352, 90), "onda sonora\nde alta frecuencia", scale=scale, size=13, align="left")
    cover(image, (278, 128, 352, 168), "respuestas neurales\nindividuales", scale=scale, size=13, align="left")
    cover(image, (278, 186, 356, 224), "actividad neural\ncolectiva total en\nel nervio coclear", scale=scale, size=12, align="left")
    save(image, "es-fig-4-27.png")


def figure_4_29() -> None:
    scale = 4
    image = open_scaled("96c3e00777fe9301-fig4.29_draft-2-350x273.png", scale)
    cover(image, (100, 12, 142, 24), "SONIDO", scale=scale, size=14)
    cover(image, (168, 14, 310, 38), "núcleos de la oliva\nsuperior medial", scale=scale, size=12)
    cover(image, (12, 66, 162, 78), "axón del núcleo coclear izquierdo", scale=scale, size=12)
    cover(image, (190, 66, 346, 78), "axón del núcleo coclear derecho", scale=scale, size=12)
    save(image, "es-fig-4-29.png")


def main() -> None:
    figure_4_17()
    figure_4_18()
    figure_4_19()
    figure_4_20()
    figure_4_21a()
    figure_4_21b()
    figure_4_21c()
    figure_4_22()
    figure_4_23()
    figure_4_24()
    figure_4_25()
    figure_4_27()
    figure_4_29()


if __name__ == "__main__":
    main()
