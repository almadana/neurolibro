#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 6.12 a 6.15.

Los originales de site/assets/media no se modifican. Los créditos quedan en el
atributo title. La firma «ELIZA WOLFSON» de la figura 6.14 no se tapa.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (254, 254, 242)
GRAY = (212, 214, 227)


def face(size: float, path: str = SANS) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, max(8, round(size)))


def load_rgb(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    canvas = Image.new("RGB", image.size, WHITE)
    canvas.paste(image, mask=image.split()[-1])
    return canvas


def is_cyan(pixel) -> bool:
    red, green, blue = pixel
    return blue > red + 8 and green > red + 8


def erase_text(source: Image.Image, image: Image.Image, box, scale: int) -> None:
    x0, y0, x1, y1 = [round(value * scale) for value in box]
    width, height = source.size
    for y in range(max(0, y0), min(height, y1)):
        for x in range(max(0, x0), min(width, x1)):
            pixel = source.getpixel((x, y))
            if is_cyan(pixel):
                continue
            if any(
                is_cyan(source.getpixel((nx, ny)))
                for nx in range(max(0, x - 2), min(width, x + 3))
                for ny in range(max(0, y - 2), min(height, y + 3))
            ):
                continue
            image.putpixel((x, y), WHITE)


def blot_dark(image: Image.Image, box, scale: int, kind: str = "gray") -> None:
    """Reemplaza la tinta del rótulo por el color claro de al lado."""
    x0, y0, x1, y1 = [round(value * scale) for value in box]
    width, height = image.size
    pixels = image.load()

    def is_ink(pixel) -> bool:
        red, green, blue = pixel
        if kind == "pink":
            return red < 185 and (red - green) < 36 and abs(red - blue) < 40
        return 40 < red < 165 and (green - red) < 55 and abs(blue - red) < 55

    def is_fill(pixel) -> bool:
        red, green, blue = pixel
        if kind == "pink":
            return red > 200 and (red - green) > 40
        return red > 175 or (green - red) > 55

    ink = [
        (x, y)
        for y in range(max(0, y0), min(height, y1))
        for x in range(max(0, x0), min(width, x1))
        if is_ink(pixels[x, y])
    ]
    ink_pixels = set(ink)
    for x, y in ink:
        replacement = None
        for radius in range(2, 16):
            for nx, ny in (
                (x - radius, y),
                (x + radius, y),
                (x, y - radius),
                (x, y + radius),
            ):
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if (nx, ny) in ink_pixels:
                    continue
                candidate = pixels[nx, ny]
                if is_fill(candidate):
                    replacement = candidate
                    break
            if replacement:
                break
        if replacement:
            pixels[x, y] = replacement


def write(image, box, text, *, fill=BLACK, size, align="center", font_path=SANS):
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(image)
    chosen = face(size, font_path)
    spacing = max(0, round(size * 0.12))
    left, top, right, bottom = draw.multiline_textbbox(
        (0, 0), text, font=chosen, spacing=spacing, align=align
    )
    width = right - left
    height = bottom - top
    if align == "right":
        origin_x = x1 - width - left
    elif align == "left":
        origin_x = x0 - left
    else:
        origin_x = x0 + (x1 - x0 - width) / 2 - left
    origin_y = y0 + (y1 - y0 - height) / 2 - top
    draw.multiline_text(
        (origin_x, origin_y),
        text,
        font=chosen,
        fill=fill,
        spacing=spacing,
        align=align,
    )


def scaled(box, scale):
    return tuple(round(value * scale) for value in box)


def figure_6_12() -> None:
    scale = 4
    image = load_rgb(MEDIA / "b96e8d2b754400ff-dementia-pie-chart-1-350x247.png")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    source = image.copy()
    labels = [
        ((95, 6, 230, 24), (70, 2, 280, 28), "Causas de demencia", 28, "center"),
        ((4, 90, 78, 104), (2, 82, 88, 112), "Enfermedad\nde Alzheimer", 20, "left"),
        ((170, 34, 272, 48), (168, 28, 300, 56), "Demencia\nfrontotemporal", 18, "left"),
        ((205, 50, 286, 62), (200, 46, 310, 70), "Demencia\nde Parkinson", 18, "left"),
        ((230, 64, 258, 74), (228, 62, 280, 78), "Otras", 18, "left"),
        ((240, 78, 340, 94), (230, 74, 348, 108), "Demencia con\ncuerpos de Lewy", 16, "right"),
        ((255, 96, 290, 108), (248, 94, 320, 114), "Mixta", 18, "left"),
        ((255, 166, 330, 180), (240, 158, 346, 190), "Demencia\nvascular", 18, "right"),
    ]
    for erase_box, text_box, text, size, align in labels:
        erase_text(source, image, erase_box, scale)
        write(image, scaled(text_box, scale), text, size=size, align=align)
    image.save(OUT / "es-fig-6-12.png")


def paint_margin(image: Image.Image, box, scale: int) -> None:
    """Sustituye el rótulo con el cielo de los costados, sin arrastrar el dibujo."""
    x0, y0, x1, y1 = [round(value * scale) for value in box]
    width, height = image.size
    x0, y0 = max(1, x0), max(0, y0)
    x1, y1 = min(width - 1, x1), min(height, y1)
    pixels = image.load()

    def sky(pixel) -> bool:
        red, green, _blue = pixel
        return red > 150 and green > 210

    def find_sky(x: int, y: int, direction: int):
        for step in range(16):
            nx = x + direction * step
            if not 0 <= nx < width:
                break
            pixel = pixels[nx, y]
            if sky(pixel):
                return pixel
        return None

    span = max(1, x1 - x0)
    for y in range(y0, y1):
        left = find_sky(x0 - 1, y, -1)
        right = find_sky(x1, y, 1)
        if left is None and right is None:
            continue
        for x in range(x0, x1):
            if left and right:
                weight = (x - x0) / span
                pixels[x, y] = tuple(
                    round(left[channel] * (1 - weight) + right[channel] * weight)
                    for channel in range(3)
                )
            else:
                pixels[x, y] = left or right


def figure_6_13() -> None:
    scale = 6
    image = load_rgb(MEDIA / "34148220dfd1e3a1-6.12-alzheimers_disease_brain_comparison-350x158.png")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    labels = [
        ((8, 8, 56, 28), "Corteza\ncerebral", 16, "left"),
        ((2, 133, 64, 152), "Hipocampo", 16, "left"),
        ((62, 132, 132, 154), "Corteza\nentorrinal", 14, "left"),
        ((176, 12, 250, 42), "Encogimiento extremo\nde la corteza cerebral", 13, "left"),
        ((292, 8, 348, 50), "Ventrículos\nmuy agrandados", 12, "right"),
        ((166, 110, 236, 144), "Encogimiento\nextremo del\nhipocampo", 12, "left"),
    ]
    for box, text, size, align in labels:
        paint_margin(image, box, scale)
        write(image, scaled(box, scale), text, size=size, align=align)
    image.save(OUT / "es-fig-6-13.png")


def figure_6_14() -> None:
    scale = 6
    image = load_rgb(MEDIA / "947579af9a03af60-fig6.13_draft-1-350x181.png")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    source = image.copy()
    labels = [
        ((88, 20, 142, 36), (70, 12, 160, 42), "Sano", 32, "center"),
        ((188, 20, 264, 36), (170, 10, 280, 44), "Alzheimer", 30, "center"),
        ((20, 58, 55, 72), (8, 52, 80, 76), "Neuronas", 22, "left"),
        ((18, 98, 55, 116), (4, 92, 78, 122), "Vaina de\nmielina", 16, "left"),
        ((280, 46, 332, 72), (250, 40, 346, 82), "Neuronas\ndañadas y\nque mueren", 15, "right"),
        ((285, 74, 332, 96), (255, 72, 346, 102), "Ovillos\nde tau", 16, "right"),
        ((285, 100, 332, 122), (250, 98, 346, 128), "Placas de\namiloide", 16, "right"),
        ((280, 128, 340, 152), (220, 124, 346, 168), "Vaina de mielina\nrota e\nincompleta", 14, "right"),
    ]
    for erase_box, text_box, text, size, align in labels:
        erase_text(source, image, erase_box, scale)
        write(image, scaled(text_box, scale), text, size=size, align=align)
    image.save(OUT / "es-fig-6-14.png")


def figure_6_15() -> None:
    image = load_rgb(MEDIA / "2d53dbe0e1fadee2-2113ab_atherosclerosis.jpeg")
    draw = ImageDraw.Draw(image)
    labels = [
        ((24, 74, 228, 110), CREAM, (20, 70, 250, 112), "Arteria normal", 26, "left"),
        ((662, 118, 812, 190), CREAM, (640, 112, 820, 196), "Pared\narterial", 24, "left"),
        ((130, 346, 408, 380), CREAM, (120, 340, 430, 384), "Flujo sanguíneo normal", 24, "left"),
        ((208, 398, 385, 472), CREAM, (206, 396, 390, 470), "Flujo sanguíneo\nanómalo", 22, "left"),
        ((430, 408, 545, 448), CREAM, (420, 404, 560, 450), "Placa", 24, "center"),
        ((590, 444, 895, 478), GRAY, (600, 442, 890, 480), "Corte transversal", 24, "center"),
        ((18, 448, 178, 526), CREAM, (12, 442, 190, 530), "Estrechamiento\nde la arteria", 22, "left"),
        ((820, 820, 940, 862), GRAY, (810, 812, 950, 868), "Placa", 24, "center"),
        ((590, 864, 850, 908), GRAY, (590, 858, 860, 912), "Arteria estrechada", 24, "center"),
    ]
    for cover_box, color, text_box, text, size, align in labels:
        draw.rectangle(cover_box, fill=color)
        write(image, text_box, text, size=size, align=align, font_path=SANS_REGULAR)
    blot_dark(image, (1716, 828, 1844, 876), 1, kind="pink")
    write(
        image,
        (1708, 824, 1852, 878),
        "Placa",
        size=32,
        align="center",
    )
    image.save(OUT / "es-fig-6-15.png")


def main() -> None:
    figure_6_12()
    # La 6.13 tiene rótulos minúsculos sobre la acuarela. Cubrirlos deja
    # bandas o restos del inglés, así que se conserva el original y el pie
    # trae las equivalencias.
    figure_6_14()
    figure_6_15()


if __name__ == "__main__":
    main()
