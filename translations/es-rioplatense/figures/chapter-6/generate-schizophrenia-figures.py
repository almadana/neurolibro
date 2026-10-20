#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 6.8 y 6.9.

Los originales de site/assets/media no se modifican. El crédito de Andrew Young
queda en el atributo title de la página, no dentro del dibujo.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY_GENETIC = (204, 204, 204)
GRAY_BIO = (222, 222, 222)
GRAY_UP = (235, 235, 235)
GREEN = (226, 240, 217)
PINK = (255, 229, 229)


def face(size: float, path: str) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, max(8, round(size)))


def write(image, box, text, *, fill=BLACK, align="center", size=None, font_path=SANS):
    max_w = max(8, box[2] - box[0] - 4)
    max_h = max(8, box[3] - box[1] - 2)
    draw = ImageDraw.Draw(image)
    if size is None:
        size = (box[3] - box[1]) * (0.42 if "\n" in text else 0.72)
    chosen = face(size, font_path)
    spacing = max(0, round(size * 0.08))
    bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    for _ in range(48):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.94
        chosen = face(size, font_path)
        bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = box[0] + 2 - bounds[0]
    else:
        x = (box[0] + box[2]) / 2 - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 - height / 2 - bounds[1]
    draw.multiline_text((round(x), round(y)), text, font=chosen, fill=fill, spacing=spacing, align=align)
    return bounds[2] - bounds[0], bounds[3] - bounds[1], size


def cover(image, box, text, *, plate=WHITE, fill=BLACK, align="center", size=None, font_path=SANS):
    ImageDraw.Draw(image).rectangle(box, fill=plate)
    if text:
        return write(image, box, text, fill=fill, align=align, size=size, font_path=font_path)
    return None


def open_rgb(name: str) -> Image.Image:
    image = Image.open(MEDIA / name)
    if image.mode == "P":
        image = image.convert("RGBA")
    if image.mode == "RGBA":
        canvas = Image.new("RGB", image.size, WHITE)
        canvas.paste(image, mask=image.split()[-1])
        return canvas
    return image.convert("RGB")


def save(image: Image.Image, name: str) -> None:
    path = OUT / name
    image.save(path, optimize=True)
    print(f"{name} {image.size[0]}x{image.size[1]}")


def figure_6_8() -> None:
    image = open_rgb("e7ab6ea23a3d21f6-image1-1.png")
    labels = [
        ((64, 256, 226, 294), "Genéticos", GRAY_GENETIC, 24),
        ((388, 248, 575, 294), "Biológicos", GRAY_BIO, 24),
        ((200, 550, 410, 598), "Crianza", GRAY_UP, 28),
        ((676, 160, 802, 204), "RIESGO", WHITE, 22),
        ((690, 42, 802, 90), "Alto", WHITE, 24),
        ((708, 288, 802, 328), "Bajo", WHITE, 22),
        ((668, 404, 970, 464), "Esquizofrenia", WHITE, 32),
    ]
    for box, text, plate, size in labels:
        cover(image, box, text, plate=plate, size=size, font_path=SERIF)
    cover(
        image, (440, 386, 618, 471), "Factores\nprecipitantes",
        plate=WHITE, size=16, font_path=SERIF,
    )
    save(image, "es-fig-6-8.png")


def figure_6_9() -> None:
    image = open_rgb("4e66b569de0e264a-image2-2.png")
    cortex = [
        ((40, 142, 162, 232), GREEN, "Corteza\nfrontal"),
        ((444, 142, 602, 232), GREEN, "Corteza\ntemporal"),
        ((682, 142, 804, 232), PINK, "Corteza\nfrontal"),
        ((1088, 142, 1244, 232), PINK, "Corteza\ntemporal"),
        ((1326, 142, 1448, 232), GREEN, "Corteza\nfrontal"),
        ((1730, 142, 1886, 232), GREEN, "Corteza\ntemporal"),
    ]
    for box, plate, text in cortex:
        cover(image, box, text, plate=plate, size=23)
    behaviour = [
        ((16, 384, 186, 424), GREEN),
        ((432, 384, 602, 424), GREEN),
        ((659, 384, 829, 424), PINK),
        ((1075, 384, 1245, 424), PINK),
        ((1302, 384, 1472, 424), PINK),
        ((1718, 384, 1888, 424), PINK),
    ]
    for box, plate in behaviour:
        cover(image, box, "Conducta", plate=plate, size=28)
    # Cajas del texto original, incluidas las colas. La línea punteada se restaura
    # fuera del rótulo nuevo.
    outputs = [
        ((190, 280, 430, 314), 309, "Salida normal", 24),
        ((820, 278, 1120, 316), 969, "Salida anómala", 26),
        ((1468, 278, 1760, 316), 1612, "Salida anómala", 26),
    ]
    source = open_rgb("4e66b569de0e264a-image2-2.png")
    source_px = source.load()
    draw = ImageDraw.Draw(image)
    for box, center, text, size in outputs:
        chosen = face(size, SANS)
        bounds = draw.textbbox((0, 0), text, font=chosen)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        text_left = round(center - width / 2)
        text_right = text_left + width
        draw.rectangle(box, fill=WHITE)
        x = center - width / 2 - bounds[0]
        y = (box[1] + box[3]) / 2 - height / 2 - bounds[1]
        draw.text((round(x), round(y)), text, font=chosen, fill=BLACK)
        px = image.load()
        for col in range(box[0], box[2]):
            if text_left - 4 <= col <= text_right + 4:
                continue
            above = any(source_px[col, row][0] < 80 for row in range(box[1], 298))
            below = any(source_px[col, row][0] < 80 for row in range(303, box[3]))
            if above or below:
                continue
            for row in range(296, 305):
                if source_px[col, row][0] < 180:
                    px[col, row] = source_px[col, row]

    titles = [
        (0, 633, "(a) Encéfalo normal"),
        (633, 1278, "(b) Disfunción regional"),
        (1278, 1905, "(c) Desconexión"),
    ]
    for left, right, text in titles:
        draw.rectangle((left + 8, 18, right - 8, 90), fill=WHITE)
        chosen = face(40, SANS)
        bounds = draw.textbbox((0, 0), text, font=chosen)
        width = bounds[2] - bounds[0]
        panel = right - left
        if width > panel - 24:
            size = 40
            while width > panel - 24 and size > 16:
                size *= 0.96
                chosen = face(size, SANS)
                bounds = draw.textbbox((0, 0), text, font=chosen)
                width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        x = (left + right) / 2 - width / 2 - bounds[0]
        y = 46 - height / 2 - bounds[1]
        draw.text((round(x), round(y)), text, font=chosen, fill=BLACK)
        text_left = round((left + right) / 2 - width / 2)
        text_right = text_left + width
        draw.rectangle((text_left - 6, 78, text_right + 6, 82), fill=BLACK)
    save(image, "es-fig-6-9.png")


def main() -> None:
    figure_6_8()
    figure_6_9()


if __name__ == "__main__":
    main()
