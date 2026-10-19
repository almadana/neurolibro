#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 4.31 a 4.44.

Los originales de site/assets/media no se modifican. La 4.33 es un grabado
sin rótulos y la 4.41 no tiene texto: no se regeneran. Los créditos quedan
en inglés.
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
GRAY = (219, 219, 219)
PEACH = (255, 232, 205)
PEACH_DEEP = (255, 222, 179)
CYAN_BG = (235, 253, 255)
RED = (210, 28, 28)
BLUE = (35, 35, 210)
TEAL = (0, 140, 155)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def erase_midgray(image: Image.Image, box, scale: int = 1, lo: int = 70, hi: int = 185) -> None:
    """Quita rótulos grises y conserva las líneas negras y los rellenos de color."""
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            average = (red + green + blue) / 3
            if lo < average < hi and max(red, green, blue) - min(red, green, blue) < 28:
                ink.append((x, y))
    blocked = set(ink)
    for x, y in ink:
        replacement = None
        for step in range(1, 18):
            for nx, ny in ((x, y - step), (x, y + step), (x - step, y), (x + step, y)):
                if 0 <= nx < image.width and 0 <= ny < image.height and (nx, ny) not in blocked:
                    replacement = pixels[nx, ny]
                    break
            if replacement is not None:
                break
        if replacement is not None:
            pixels[x, y] = replacement


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 220) -> None:
    """Quita la tinta gris del rótulo y conserva los rellenos de color."""
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


def cover(image, box, text, *, scale=1, align="center", bold=True, size=None,
          fill=BLACK, plate=WHITE, threshold=220):
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
    """pad = (izquierda, arriba, derecha, abajo) en píxeles del original."""
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


def figure_4_31() -> None:
    scale = 4
    image = open_scaled("200f8ee0758648bd-em_spectrum.svg-350x166.png", scale, pad=(0, 0, 0, 18))
    cover(image, (236, 4, 348, 18), "← frecuencia creciente", scale=scale, size=22)
    cover(image, (16, 40, 78, 56), "rayos γ", scale=scale, size=20, plate=GRAY, threshold=140)
    cover(image, (84, 40, 114, 56), "rayos X", scale=scale, size=16, plate=GRAY, threshold=140)
    cover(image, (166, 40, 210, 62), "microondas", scale=scale, size=15, plate=GRAY, threshold=140)
    cover(image, (213, 40, 235, 64), "radio\nFM", scale=scale, size=13, plate=GRAY, threshold=140)
    cover(image, (237, 40, 255, 64), "ondas\nAM", scale=scale, size=13, plate=GRAY, threshold=140)
    cover(image, (258, 38, 346, 58), "ondas de radio largas", scale=scale, size=15, plate=GRAY, threshold=140)
    cover(image, (228, 78, 348, 92), "longitud de onda (λ) creciente →", scale=scale, size=15)
    cover(image, (108, 96, 164, 106), "Espectro visible", scale=scale, size=18)
    for box, word in (
        ((46, 136, 68, 152), "Vi"),
        ((68, 138, 78, 152), ""),
        ((76, 136, 100, 152), "Az"),
        ((106, 136, 126, 152), "Ve"),
        ((130, 136, 150, 152), "Am"),
        ((148, 136, 168, 152), "Na"),
        ((180, 136, 208, 152), "Ro"),
    ):
        cover(image, box, word, scale=scale, size=22)
    write(
        image, (4, 166, 346, 182),
        "Vi violeta · Az azul · Ve verde · Am amarillo · Na naranja · Ro rojo",
        scale=scale, size=22, bold=False,
    )
    save(image, "es-fig-4-31.png")


def figure_4_32() -> None:
    scale = 4
    image = open_scaled("c35a7c41661b43bd-em_wave-350x138.png", scale)
    cover(image, (34, 26, 158, 39), "H: componente del campo magnético",
          scale=scale, size=16, fill=RED, align="left")
    cover(image, (100, 108, 250, 126), "E: componente del campo eléctrico",
          scale=scale, size=18, fill=BLUE, align="left")
    cover(image, (248, 58, 348, 78), "Longitud\nde onda", scale=scale, size=18, fill=(70, 70, 70))
    save(image, "es-fig-4-32.png")


def figure_4_34() -> None:
    scale = 4
    # Margen extra: el español de varios rótulos no cabe en los 70 px originales.
    shift_x = 24
    image = open_scaled("9cfa18c6f88442c2-eye-350x200.jpeg", scale, pad=(shift_x, 0, 70, 8))

    def box(coords):
        left, top, right, bottom = coords
        return (left + shift_x, top, right + shift_x, bottom)

    left = (
        ((1, 24, 68, 44), "Músculo recto\nlateral", "right"),
        ((1, 44, 68, 58), "Esclerótica", "right"),
        ((1, 58, 68, 72), "Coroides", "right"),
        ((1, 74, 68, 90), "Retina", "right"),
        ((1, 96, 68, 112), "Fóvea central", "right"),
        ((1, 118, 70, 136), "Nervio óptico (II)", "right"),
        ((1, 138, 70, 162), "Arteria y vena\ncentrales de la retina", "right"),
        ((1, 162, 70, 180), "Disco óptico\n(punto ciego)", "right"),
        ((1, 176, 58, 194), "Músculo recto\nmedial", "right"),
    )
    for coords, text, align in left:
        cover(image, box(coords), text, scale=scale, align=align, size=28)
    right = (
        ((268, 4, 418, 20), "Cavidad posterior"),
        ((268, 18, 418, 34), "Cámara vítrea"),
        ((268, 32, 418, 48), "Seno venoso escleral"),
        ((268, 46, 418, 60), "(conducto de Schlemm)"),
        ((268, 58, 418, 74), "Ligamentos suspensorios"),
        ((268, 72, 360, 86), "Cristalino"),
        ((268, 84, 360, 96), "Córnea"),
        ((268, 94, 360, 106), "Iris"),
        ((268, 104, 360, 116), "Pupila"),
        ((268, 114, 418, 128), "Cavidad anterior"),
        ((268, 126, 418, 140), "(contiene humor acuoso)"),
        ((268, 140, 418, 152), "Cámara posterior"),
        ((268, 150, 418, 162), "Cámara anterior"),
        ((268, 160, 418, 174), "Ligamentos suspensorios"),
        ((268, 172, 418, 186), "Cuerpo ciliar"),
        ((268, 184, 418, 198), "Proceso ciliar"),
        ((268, 196, 418, 208), "Músculo ciliar"),
    )
    for coords, text in right:
        cover(image, box(coords), text, scale=scale, align="left", size=26, bold=False)
    save(image, "es-fig-4-34.png")


def figure_4_35() -> None:
    scale = 4
    image = open_scaled("3f1bae047f7cf245-fig4.35_newdraft-350x273.png", scale)
    cover(image, (292, 116, 348, 148), "Punto focal\nen la retina", scale=scale, size=18, align="left")
    save(image, "es-fig-4-35.png")


def figure_4_36() -> None:
    scale = 4
    image = open_scaled("f5f61ea16f4c983d-fig4.36_draft-350x273.png", scale)
    cover(image, (72, 10, 132, 26), "MIOPÍA", scale=scale, size=26)
    cover(image, (44, 36, 70, 54), "", scale=scale)
    cover(image, (2, 30, 46, 64), "Punto lejano\nnormal\n(infinito)", scale=scale, size=12, align="left")
    cover(image, (156, 54, 224, 70), "Músculos ciliares\ntotalmente relajados", scale=scale, size=13)
    cover(image, (274, 8, 348, 42), "Punto focal\npor delante\nde la retina", scale=scale, size=14, align="left")
    cover(image, (72, 80, 128, 100), "Punto lejano\nmiópico", scale=scale, size=14)
    cover(image, (150, 78, 220, 100), "Corregido con\nlente divergente", scale=scale, size=14)
    cover(image, (44, 100, 70, 116), "", scale=scale)
    cover(image, (2, 98, 48, 126), "Punto lejano\nnormal\n(infinito)", scale=scale, size=12, align="left")
    cover(image, (52, 138, 178, 156), "HIPERMETROPÍA", scale=scale, size=24)
    cover(image, (100, 184, 132, 202), "Punto cercano\nnormal", scale=scale, size=13)
    cover(image, (148, 188, 216, 208), "Músculos ciliares\ntotalmente contraídos", scale=scale, size=12)
    cover(image, (274, 152, 348, 178), "Punto focal\npor detrás\nde la retina", scale=scale, size=14, align="left")
    cover(image, (46, 214, 82, 232), "", scale=scale)
    cover(image, (2, 206, 50, 232), "Punto cercano\nhipermetrópico", scale=scale, size=12, align="left")
    cover(image, (100, 210, 140, 230), "Punto cercano\nnormal", scale=scale, size=14)
    cover(image, (148, 204, 220, 226), "Corregido con\nlente convergente", scale=scale, size=14)
    save(image, "es-fig-4-36.png")


def figure_4_37() -> None:
    scale = 4
    image = open_scaled("9ae31ed5103f7bcb-fig4.37_draft-1-350x273.png", scale)
    labels = (
        ((16, 127, 52, 143), "LUZ", 16, (186, 236, 236)),
        ((78, 0, 132, 20), "Célula\nhorizontal", 15, WHITE),
        ((132, 0, 214, 18), "Bastones y conos", 14, WHITE),
        ((198, 0, 275, 20), "Epitelio\npigmentario", 14, WHITE),
        ((48, 20, 108, 44), "Célula\nbipolar", 15, WHITE),
        ((18, 40, 88, 62), "Célula\namacrina", 14, WHITE),
        ((12, 62, 88, 84), "Célula\nganglionar", 14, WHITE),
        ((4, 84, 108, 110), "Fibras de la\ncélula ganglionar", 13, WHITE),
        ((250, 32, 320, 48), "Coroides", 16, WHITE),
        ((255, 66, 318, 82), "Esclerótica", 15, WHITE),
        ((308, 72, 348, 96), "Nervio\nóptico", 15, WHITE),
        ((146, 104, 168, 116), "Cono", 13, WHITE),
        ((68, 128, 108, 148), "Disco\nóptico", 14, WHITE),
        ((146, 150, 170, 162), "Bastón", 13, WHITE),
        ((8, 206, 95, 230), "Capa plexiforme\ninterna", 12, WHITE),
        ((12, 230, 78, 256), "Capa nuclear\ninterna", 12, WHITE),
        ((80, 240, 148, 268), "Capa plexiforme\nexterna", 12, WHITE),
        ((150, 246, 210, 272), "Capa nuclear\nexterna", 12, WHITE),
    )
    for box, text, size, plate in labels:
        cover(image, box, text, scale=scale, size=size, plate=plate)
    cover(image, (168, 106, 214, 120), "", scale=scale, plate=(230, 246, 246))
    cover(image, (168, 154, 214, 168), "", scale=scale, plate=(230, 246, 246))
    save(image, "es-fig-4-37.png")


def figure_4_38() -> None:
    scale = 4
    image = open_scaled("0fe316a4198614e9-spectral-sensitivity-1-350x235.png", scale)
    cover_vertical(
        image, (0, 18, 22, 196),
        "Sensibilidad (unidades arbitrarias)",
        scale=scale, size=28, plate=WHITE,
    )
    cover(image, (110, 208, 250, 232), "Longitud de onda (nm)", scale=scale, size=22, plate=WHITE)
    save(image, "es-fig-4-38.png")


def figure_4_39() -> None:
    scale = 4
    image = open_scaled("65a02c3ab3482566-fig4.39_draft-350x273.png", scale)
    labels = (
        ((6, 4, 52, 24), "discos\naislados", 14),
        ((52, 0, 148, 26), "pliegues de la\nmembrana plasmática", 13),
        ((52, 80, 155, 90), "seg. externo del bastón", 12),  # se tapa en gris más abajo
        ((18, 108, 78, 128), "BASTÓN", 22),
        ((68, 138, 112, 156), "seg.\nexterno", 12),
        ((112, 138, 140, 156), "seg.\ninterno", 12),
        ((140, 138, 174, 156), "mito-\ncondrias", 12),
        ((174, 138, 200, 156), "núcleo", 12),
        ((200, 138, 218, 156), "axón", 12),
        ((216, 138, 248, 156), "sinapsis", 12),
        ((16, 168, 78, 188), "CONO", 22),
        ((62, 186, 160, 206), "segmento externo\ndel cono", 13),
        ((4, 242, 95, 270), "pliegues de la\nmembrana plasmática", 13),
        ((148, 48, 214, 78), "terminal\nsináptica\ndel bastón", 13),
        ((198, 0, 248, 22), "cinta\nsináptica", 13),
        ((246, 0, 310, 22), "vesículas\nsinápticas", 13),
        ((218, 112, 272, 140), "prolongaciones\ncelulares", 11),
        ((278, 112, 348, 140), "conexión\nbasal", 11),
        ((248, 142, 348, 164), "H = prolong. de célula horizontal\nB = prolong. de célula bipolar", 11),
        ((145, 210, 210, 228), "terminal sináptica\ndel cono", 12),
        ((218, 246, 262, 268), "cinta\nsináptica", 12),
        ((262, 246, 312, 268), "vesículas\nsinápticas", 12),
        ((312, 246, 348, 270), "prolong.", 12),
    )
    for box, text, size in labels:
        plate = (229, 229, 229) if text.startswith("seg. externo del") else WHITE
        cover(image, box, text, scale=scale, size=size, plate=plate)
    save(image, "es-fig-4-39.png")


def figure_4_40() -> None:
    scale = 2
    image = open_scaled("3f33ac5b3cd1e878-image11.png", scale)
    cover(image, (360, 0, 980, 32), "Activación de la fototransducción", scale=scale, size=36)
    steps = ((70, 500, 175, 534), (290, 500, 410, 534), (480, 500, 590, 534),
             (670, 500, 790, 534), (950, 500, 1060, 534))
    for index, box in enumerate(steps, start=1):
        cover(image, box, f"Paso {index}", scale=scale, size=28, plate=PEACH)
    cover(image, (1040, 292, 1120, 324), "Abierto", scale=scale, size=26, plate=PEACH_DEEP)
    cover(image, (1040, 420, 1140, 452), "Cerrado", scale=scale, size=26, plate=PEACH_DEEP)
    save(image, "es-fig-4-40.png")


def figure_4_42() -> None:
    scale = 4
    image = open_scaled("37fe07406c4e659d-fig4.42_draft-350x273.png", scale)
    labels = (
        ((40, 2, 310, 22), "ENTRADA A LA CORTEZA VISUAL", 18),
        ((8, 24, 55, 40), "Objeto", 16),
        ((98, 100, 132, 116), "Nervios\nópticos", 11),
        ((6, 116, 58, 134), "Quiasma\nóptico", 12),
        ((138, 100, 185, 112), "ipsilateral", 11),
        ((138, 114, 195, 128), "contralateral", 11),
        ((82, 136, 118, 152), "Tractos\nópticos", 11),
        ((155, 134, 202, 162), "Núcleo\ngeniculado\nlateral", 11),
        ((2, 168, 28, 182), "dorsal", 12),
        ((190, 164, 222, 178), "dorsal", 12),
        ((86, 186, 116, 198), "ventral", 12),
        ((58, 226, 145, 246), "Vía\nmagnocelular", 12),
        ((55, 248, 148, 270), "Vía\nparvocelular", 12),
        ((148, 84, 214, 106), "Funciones\nde integración", 12),
        ((140, 116, 212, 138), "Entrada sensorial\n(aferente)", 11),
        ((136, 154, 212, 182), "Salida a otras\npartes del encéfalo\n(eferente)", 11),
        ((178, 198, 252, 222), "Capa desde el\nnúcleo geniculado\nlateral", 11),
        ((220, 228, 285, 250), "Ojo\ncontralateral", 13),
        ((286, 228, 348, 250), "Ojo\nipsilateral", 13),
    )
    for box, text, size in labels:
        cover(image, box, text, scale=scale, size=size)
    for box in (
        (68, 100, 98, 116),
        (145, 116, 192, 132),
        (128, 140, 156, 162),
        (58, 136, 82, 150),
        (62, 188, 86, 200),
    ):
        cover(image, box, "", scale=scale)
    save(image, "es-fig-4-42.png")


def figure_4_43() -> None:
    scale = 4
    shift_x = 8
    image = open_scaled(
        "43d62d76b56a212d-1424_visual_streams-350x169.jpeg",
        scale, pad=(shift_x, 0, 55, 0),
    )

    def box(coords):
        left, top, right, bottom = coords
        return (left + shift_x, top, right + shift_x, bottom)

    cover(image, box((2, 2, 62, 18)), "Lóbulo frontal", scale=scale, size=18, align="left")
    cover(image, box((268, 2, 400, 18)), "Lóbulo parietal", scale=scale, size=18, align="left")
    cover(image, box((268, 34, 400, 78)), "Vía visual dorsal;\nesta parte determina\n«¿dónde está?»",
          scale=scale, size=16, align="left")
    cover(image, box((278, 78, 400, 96)), "Lóbulo occipital", scale=scale, size=18, align="left")
    cover(image, box((268, 108, 400, 152)), "Vía visual ventral;\nesta parte determina\n«¿qué es?»",
          scale=scale, size=16, align="left")
    cover(image, box((8, 148, 90, 166)), "Lóbulo temporal", scale=scale, size=18, align="left")
    save(image, "es-fig-4-43.png")


def figure_4_44() -> None:
    scale = 4
    image = open_scaled("a32fee9bdbc8341d-fig4.44_draft-350x273.png", scale, pad=(0, 0, 36, 0))
    cover(image, (48, 8, 100, 28), "CONOS", scale=scale, size=22)
    cover(image, (108, 4, 188, 44), "EXCITACIÓN /\nINHIBICIÓN", scale=scale, size=14, fill=TEAL)
    cover(image, (188, 6, 275, 30), "CANALES", scale=scale, size=20)
    cover(image, (58, 52, 96, 74), "AZUL", scale=scale, size=16)
    cover(image, (58, 134, 96, 158), "VERDE", scale=scale, size=16)
    cover(image, (58, 218, 96, 242), "ROJO", scale=scale, size=16)
    cover(image, (292, 52, 384, 72), "AZUL-AMARILLO", scale=scale, size=14, align="left")
    cover(image, (292, 138, 384, 158), "LUMINANCIA", scale=scale, size=14, align="left")
    cover(image, (292, 218, 384, 238), "ROJO-VERDE", scale=scale, size=14, align="left")
    save(image, "es-fig-4-44.png")


def main() -> None:
    figure_4_31()
    figure_4_32()
    figure_4_34()
    figure_4_35()
    figure_4_36()
    figure_4_37()
    figure_4_38()
    figure_4_39()
    figure_4_40()
    figure_4_42()
    figure_4_43()
    figure_4_44()


if __name__ == "__main__":
    main()
