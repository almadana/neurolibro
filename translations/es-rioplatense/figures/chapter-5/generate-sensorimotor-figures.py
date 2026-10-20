#!/usr/bin/env python3
"""Localiza los rótulos de las figuras de integración sensitivomotora.

Los originales de site/assets/media no se modifican. Quedan en inglés los
créditos (Yale Peabody Museum y Eliza Wolfson), las letras A–C y las palabras
idénticas en español (PUTAMEN, ERROR, NO). No se tapa el dibujo, las flechas
ni las líneas guía.
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
CYAN = (83, 221, 227)
PALE = (171, 239, 241)
BUBBLE = (224, 250, 251)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 230) -> None:
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


def erase_gray(image: Image.Image, box, scale: int = 1, low: int = 90, high: int = 210) -> None:
    """Quita rótulos grises y deja los trazos oscuros del dibujo."""
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
          fill=BLACK, plate=WHITE, threshold=230):
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


def figure_5_16() -> None:
    scale = 4
    image = open_scaled("7732fa057b42210c-fig5.14_draft-350x273.png", scale)
    # El panel A es una foto: no se pinta. El crédito de Wolfson queda bajo el adulto.
    labels = [
        ((156, 30, 208, 48), "Renacuajo", 16),
        ((168, 54, 214, 70), "Embrión", 22),
        ((196, 78, 234, 98), "Huevo", 16),
        ((166, 106, 218, 122), "Esperma", 20),
        ((206, 108, 256, 133), "Adulto\nfijado", 16),
        ((262, 112, 318, 128), "Juvenil", 20),
        ((258, 74, 332, 96), "Larva que\nse fija", 18),
        ((258, 44, 336, 66), "Larva\nnadadora", 18),
        ((228, 22, 302, 42), "Larva que\neclosiona", 16),
        ((210, 60, 282, 82), "Ciclo de vida\nde la ascidia", 16),
        ((58, 163, 96, 176), "Estatocisto", 18),
        ((104, 160, 142, 180), "Vesícula\ncerebral", 16),
        ((144, 158, 176, 172), "Ocelo", 18),
        ((182, 156, 268, 176), "Sifón atrial\n(bloqueado)", 16),
        ((198, 178, 300, 196), "Cordón nervioso", 16),
        ((22, 176, 86, 198), "Sifón branquial\n(bloqueado)", 15),
        ((38, 198, 82, 218), "Papilas\nadhesivas", 16),
        ((58, 226, 100, 242), "Endostilo", 16),
        ((100, 242, 156, 266), "Saco branquial\n(faringe)", 15),
        ((158, 246, 192, 262), "Corazón", 16),
        ((196, 246, 242, 262), "Intestino", 16),
        ((208, 228, 258, 246), "Estómago", 16),
        ((236, 216, 286, 236), "Notocorda", 16),
    ]
    for box, text, size in labels:
        cover(image, box, text, scale=scale, size=size, threshold=245)
    erase_gray(image, (200, 40, 258, 68), scale, low=70, high=245)
    save(image, "es-fig-5-16.png")


def figure_5_17() -> None:
    scale = 4
    image = open_scaled("c319690c1a6b8da2-fig5.15_draft-350x211.png", scale)
    labels = [
        ((2, 96, 58, 118), "Receptor de\nestiramiento", 16),
        ((2, 118, 58, 140), "Huso\nmuscular", 16),
        ((2, 142, 64, 174), "Fibras\nmusculares\nextrafusales", 14),
        ((108, 78, 168, 108), "Neurona\nsensitiva", 18),
        ((140, 44, 188, 74), "Ganglio de\nla raíz\ndorsal", 14),
        ((176, 28, 220, 52), "Raíz\ndorsal", 16),
        ((222, 30, 276, 52), "Sinapsis", 18),
        ((118, 134, 168, 162), "Neurona\nmotora", 16),
        ((212, 130, 274, 140), "Médula espinal", 16),
        ((152, 158, 202, 186), "Raíz\nventral", 16),
    ]
    for box, text, size in labels:
        cover(image, box, text, scale=scale, size=size, threshold=245)
    save(image, "es-fig-5-17.png")


def figure_5_18() -> None:
    scale = 4
    image = open_scaled("42f44cd60ccded8e-fig5.16_draft-350x273.png", scale)
    excites = "Esta interneurona\nexcita una neurona\nmotora y provoca\nla contracción"
    inhibits = "Esta interneurona\ninhibe la neurona\nmotora e impide\nla contracción"
    muscle = "Este músculo lleva\ninformación desde\nel origen del dolor"
    axon = "Axón de la neurona\nsensitiva (brazo)"
    labels = [
        ((8, 20, 50, 40), "Encéfalo", 18),
        ((2, 52, 52, 80), "Médula\nespinal", 16),
        ((88, 2, 178, 42), excites, 13),
        ((96, 82, 176, 106), "Corte de la\nmédula espinal", 13),
        ((172, 68, 226, 98), "Neurona\nmotora", 15),
        ((232, 2, 308, 42), muscle, 14),
        ((310, 2, 350, 72), "Las dendritas de la\nneurona sensitiva\ndetectan el estímulo\ndoloroso", 11),
        ((268, 40, 346, 68), axon, 12),
        ((4, 142, 50, 160), "Encéfalo", 16),
        ((2, 158, 54, 180), "Neurona en\nel encéfalo", 13),
        ((2, 176, 42, 208), "Axón de una\nneurona del\nencéfalo", 11),
        ((2, 198, 52, 224), "Médula\nespinal", 14),
        ((88, 126, 178, 166), excites, 13),
        ((152, 148, 214, 186), "Axón de una\nneurona del\nencéfalo", 12),
        ((108, 208, 176, 238), "Corte de la\nmédula espinal", 13),
        ((170, 196, 226, 222), "Neurona\nmotora", 14),
        ((238, 140, 330, 176), muscle, 14),
        ((262, 176, 346, 210), axon, 12),
        ((88, 244, 180, 272), inhibits, 12),
    ]
    for box, text, size in labels:
        cover(image, box, text, scale=scale, size=size, threshold=245)
    erase_gray(image, (248, 64, 346, 96), scale)
    save(image, "es-fig-5-18.png")


def figure_5_19() -> None:
    scale = 4
    image = open_scaled(
        "c43b8098b6e2af50-5.17-oculomotor-loop-redraw-e1671538209998-350x488.png",
        scale,
    )
    cover(image, (16, 8, 176, 30), "Bucle del movimiento corporal", scale=scale, size=28)
    cover(image, (188, 8, 342, 30), "Bucle oculomotor", scale=scale, size=32)
    cover(
        image, (50, 40, 148, 80),
        "Corteza motora\nprimaria, premotora\ny suplementaria",
        scale=scale, size=26, plate=CYAN,
    )
    cover(
        image, (210, 40, 310, 80),
        "Campo ocular frontal\ny campo ocular\nsuplementario",
        scale=scale, size=26, plate=CYAN,
    )
    cover(image, (6, 84, 46, 104), "Corteza\nfrontal", scale=scale, size=16)
    cover(image, (136, 90, 180, 112), "Blancos\ncorticales", scale=scale, size=16)
    cover(image, (296, 90, 344, 112), "Blancos\ncorticales", scale=scale, size=16)
    cover_vertical(image, (4, 200, 40, 262), "Entrada cortical", scale=scale, size=22)
    cover(
        image, (52, 214, 146, 250),
        "Corteza motora,\npremotora y\nsomatosensitiva",
        scale=scale, size=26, plate=CYAN,
    )
    cover(
        image, (210, 214, 310, 252),
        "Corteza parietal\nposterior y\nprefrontal",
        scale=scale, size=26, plate=CYAN,
    )
    cover_vertical(image, (6, 278, 40, 334), "Estriado", scale=scale, size=26)
    cover(image, (214, 290, 306, 322), "Caudado\n(cuerpo)", scale=scale, size=28, plate=(124, 225, 229))
    cover_vertical(image, (6, 350, 40, 408), "Pálido", scale=scale, size=26)
    cover(
        image, (52, 358, 146, 400),
        "Globo pálido lateral,\nsegmento interno",
        scale=scale, size=24, plate=PALE,
    )
    cover(
        image, (214, 356, 306, 402),
        "Globo pálido,\nsegmento interno;\nsustancia negra\npars reticulata",
        scale=scale, size=22, plate=PALE,
    )
    cover_vertical(image, (6, 420, 40, 480), "Tálamo", scale=scale, size=26)
    cover(
        image, (48, 428, 150, 474),
        "Núcleos ventral\nlateral y ventral\nanterior",
        scale=scale, size=24, plate=BUBBLE,
    )
    cover(
        image, (214, 432, 306, 472),
        "Núcleos mediodorsal\ny ventral anterior",
        scale=scale, size=24, plate=BUBBLE,
    )
    save(image, "es-fig-5-19.png")


def figure_5_20() -> None:
    scale = 4
    image = open_scaled(
        "8d1932461c7dd0c8-fig-5.18-redraw-e1671538291618-350x161.png",
        scale,
    )
    cover(
        image, (14, 34, 80, 74),
        "Ejecutar la\nreacción\nconductual",
        scale=scale, size=22, plate=BUBBLE,
    )
    cover(
        image, (266, 32, 340, 76),
        "Mantener la\nconectividad\nactual",
        scale=scale, size=22, plate=BUBBLE,
    )
    cover(
        image, (12, 106, 82, 150),
        "Modificar la\nconectividad\nactual",
        scale=scale, size=22, plate=BUBBLE,
    )
    cover(
        image, (146, 110, 204, 146),
        "Generar\nla señal\nde error",
        scale=scale, size=22, plate=BUBBLE,
    )
    cover(image, (176, 80, 200, 93), "Sí", scale=scale, size=20)
    erase_gray(image, (6, 118, 30, 155), scale, low=40, high=230)
    erase_gray(image, (70, 118, 90, 155), scale, low=40, high=230)
    save(image, "es-fig-5-20.png")


def main() -> None:
    figure_5_16()
    figure_5_17()
    figure_5_18()
    figure_5_19()
    figure_5_20()


if __name__ == "__main__":
    main()
