#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 4.11, 4.12, 4.13 y 4.15.

Los originales de site/assets/media no se modifican. Los créditos de las
ilustraciones quedan en inglés.
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


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 220) -> None:
    """Quita la tinta gris del rótulo y conserva el relleno celeste."""
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


def blank(image, box, scale: int = 1) -> None:
    """Tapa un rótulo inglés, incluidos los bordes casi blancos."""
    erase(image, box, scale, threshold=250)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=WHITE)


def cover(image, box, text, *, scale=1, align="center", bold=True, size=None, fill=BLACK):
    erase(image, box, scale)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=WHITE)
    write(image, box, text, scale=scale, align=align, bold=bold, size=size, fill=fill)


def cover_vertical(image, box, text, *, scale=1, fill=BLACK, size=None):
    erase(image, box, scale)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=WHITE)
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


def open_scaled(name: str, scale: int) -> Image.Image:
    image = Image.open(MEDIA / name).convert("RGB")
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)


def save(image: Image.Image, name: str) -> None:
    image.save(OUT / name, optimize=True)
    print(name, image.size)


def figure_4_11() -> None:
    scale = 4
    image = open_scaled(
        "1397e14ead57d619-lossy-page1-1008px-hyperalgesia_and_allodynia.tif_-350x238.jpg",
        scale,
    )
    cover_vertical(image, (1, 24, 28, 178), "Intensidad del dolor", scale=scale, size=34)
    cover(image, (44, 10, 148, 34), "Hiperalgesia", scale=scale, align="left", size=42)
    cover(image, (174, 74, 226, 96), "Lesión", scale=scale, size=40)
    cover(image, (274, 86, 342, 130), "dolor\nnormal", scale=scale, size=36)
    cover(image, (40, 110, 122, 134), "Alodinia", scale=scale, align="left", size=40)
    cover(image, (236, 152, 340, 194), "umbral normal\ndel dolor", scale=scale, align="right", size=32)
    blank(image, (210, 172, 240, 196), scale)
    cover(image, (70, 208, 310, 236), "Intensidad del estímulo", scale=scale, size=48)
    save(image, "es-fig-4-11.png")


def figure_4_12() -> None:
    scale = 4
    image = open_scaled("8f6a0764b104f35d-fig4.12_draft-350x211.png", scale)
    blank(image, (74, 50, 102, 70), scale)
    cover(image, (2, 34, 50, 80), "Terminación\nnerviosa\nsensitiva", scale=scale, size=22)
    cover(image, (92, 74, 148, 92), "Nociceptor", scale=scale, size=26)
    blank(image, (146, 54, 202, 84), scale)
    cover(
        image, (118, 30, 174, 78),
        "Cuerpo celular\n(ganglio de la\nraíz dorsal)",
        scale=scale, size=16,
    )
    blank(image, (174, 46, 214, 58), scale)
    cover(image, (206, 40, 292, 58), "Interneurona", scale=scale, size=22)
    cover(image, (112, 126, 176, 152), "Neurona\nmotora", scale=scale, size=22)
    cover(image, (40, 154, 96, 172), "Músculo", scale=scale, size=24)
    blank(image, (198, 126, 302, 144), scale)
    cover(image, (198, 144, 328, 162), "Médula espinal", scale=scale, size=22)
    y = round(131 * scale)
    x0, x1 = round(208 * scale), round(292 * scale)
    draw = ImageDraw.Draw(image)
    draw.line((x0, y, x1, y), fill=BLACK, width=3)
    head = 10
    draw.polygon([(x0, y), (x0 + head, y - head // 2), (x0 + head, y + head // 2)], fill=BLACK)
    draw.polygon([(x1, y), (x1 - head, y - head // 2), (x1 - head, y + head // 2)], fill=BLACK)
    save(image, "es-fig-4-12.png")


def figure_4_13() -> None:
    scale = 4
    image = open_scaled("0ef0e47c7622099d-fig4.13_draft-350x273.png", scale)
    erase(image, (16, 12, 82, 36), scale)
    cover(image, (4, 4, 86, 36), "Corteza\ncingulada", scale=scale, align="right", size=24)
    cover(image, (6, 56, 62, 74), "Ínsula", scale=scale, align="right", size=26)
    erase(image, (12, 104, 96, 128), scale)
    cover(
        image, (2, 98, 108, 132),
        "Núcleo laminar\ncentral del tálamo",
        scale=scale, align="right", size=22,
    )
    erase(image, (258, 36, 349, 49), scale)
    cover(
        image, (258, 34, 349, 50),
        "Tálamo ventral\nposterolateral (VPL)",
        scale=scale, align="left", size=16,
    )
    erase(image, (148, 154, 214, 176), scale)
    cover(image, (140, 148, 222, 180), "Tracto\nespinotalámico", scale=scale, size=22)
    erase(image, (96, 188, 150, 214), scale)
    cover(image, (78, 184, 148, 216), "Estímulo\nnociceptivo", scale=scale, size=22)
    erase(image, (308, 232, 349, 258), scale)
    cover(image, (300, 228, 349, 262), "Columna\nvertebral", scale=scale, align="right", size=18)
    save(image, "es-fig-4-13.png")


def figure_4_15() -> None:
    scale = 4
    image = open_scaled("b8477f6481a7737f-fig4.15_draft-350x273.png", scale)
    blank(image, (52, 70, 88, 88), scale)
    cover(image, (28, 56, 108, 88), "Neurona\ndel tacto", scale=scale, size=22)
    blank(image, (206, 66, 268, 98), scale)
    cover(
        image, (186, 52, 308, 88),
        "Célula de transmisión\nde la lámina I",
        scale=scale, size=20,
    )
    x = round(229 * scale)
    draw = ImageDraw.Draw(image)
    draw.line((x, round(86 * scale), x, round(112 * scale)), fill=(70, 70, 70), width=2)
    blank(image, (62, 134, 120, 156), scale)
    cover(image, (4, 128, 120, 158), "Célula de\nla lámina II", scale=scale, align="right", size=20)
    blank(image, (46, 200, 102, 214), scale)
    cover(image, (28, 198, 120, 218), "Nociceptor", scale=scale, size=22)
    save(image, "es-fig-4-15.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    figure_4_11()
    figure_4_12()
    figure_4_13()
    figure_4_15()


if __name__ == "__main__":
    main()
