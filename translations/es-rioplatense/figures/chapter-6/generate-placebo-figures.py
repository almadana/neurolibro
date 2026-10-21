#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 6.16 y 6.17 y de la Tabla 1.

Los originales de site/assets/media no se modifican. Los créditos quedan en el
atributo title.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_OBLIQUE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PAPER = (230, 227, 234)
BLUE = (46, 79, 154)
CELL_GRAY = (231, 230, 230)
CELL_GREEN = (198, 235, 182)
CELL_RED = (255, 0, 0)
BOX_FILL = (224, 250, 251)
BOX_EDGE = (150, 214, 220)


def face(size: float, path: str = SANS) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, max(8, round(size)))


def load_rgb(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    canvas = Image.new("RGB", image.size, WHITE)
    canvas.paste(image, mask=image.split()[-1])
    return canvas


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


def figure_6_16() -> None:
    scale = 4
    image = load_rgb(MEDIA / "6676a68f609ac14b-placebo-effect-1-e1671630329545-350x289.png")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(image)
    labels = [
        ((108, 12, 242, 32), "Efecto placebo", 30, "center"),
        ((118, 46, 232, 62), "Expectativas", 22, "center"),
        ((2, 68, 92, 86), "Condicionamiento", 18, "left"),
        ((248, 68, 348, 86), "Aprendizaje", 20, "right"),
        ((2, 130, 76, 156), "Claves\nverbales", 16, "left"),
        ((272, 128, 348, 160), "Claves\ncontextuales", 16, "right"),
        ((2, 202, 100, 222), "Emociones", 20, "left"),
        ((248, 200, 348, 222), "Motivación", 20, "right"),
    ]
    for box, text, size, align in labels:
        draw.rectangle(scaled(box, scale), fill=WHITE)
        write(image, scaled(box, scale), text, size=size, align=align)
    relief = scaled((78, 254, 272, 282), scale)
    draw.rounded_rectangle(relief, radius=8 * scale, fill=BOX_FILL, outline=BOX_EDGE, width=scale)
    write(image, relief, "Alivio de los síntomas", size=26, align="center")
    image.save(OUT / "es-fig-6-16.png")


def blot_ink(image: Image.Image, box) -> None:
    """Quita la tinta negra del cartel y la reemplaza por el papel de al lado."""
    x0, y0, x1, y1 = box
    pixels = image.load()
    width, height = image.size

    def low_chroma(pixel) -> bool:
        return max(pixel) - min(pixel) < 12

    def is_paper(pixel) -> bool:
        return min(pixel) > 210 and max(pixel) - min(pixel) < 22

    y_start, y_end = max(0, y0), min(height, y1)
    x_start, x_end = max(0, x0), min(width, x1)
    ink = []
    for y in range(y_start, y_end):
        for x in range(x_start, x_end):
            pixel = pixels[x, y]
            if max(pixel) >= 100 or not low_chroma(pixel):
                continue
            if any(
                0 <= nx < width and 0 <= ny < height and is_paper(pixels[nx, ny])
                for radius in (10, 28, 48)
                for nx, ny in ((x - radius, y), (x + radius, y), (x, y - radius), (x, y + radius))
            ):
                ink.append((x, y))
    painted = set(ink)
    for x, y in ink:
        pixels[x, y] = PAPER
    # Dos pasadas sobre el halo claro, sin entrar en el gris más oscuro del blíster.
    for _ in range(4):
        extra = []
        for x, y in list(painted):
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in painted or not (x_start <= nx < x_end and y_start <= ny < y_end):
                        continue
                    red, green, blue = pixels[nx, ny]
                    if min(red, green, blue) < 98 or max(red, green, blue) - min(red, green, blue) > 12:
                        continue
                    painted.add((nx, ny))
                    extra.append((nx, ny))
        for x, y in extra:
            pixels[x, y] = PAPER


def paste_rotated(image, text, origin, angle, size, fill=BLACK):
    chosen = face(size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    left, top, right, bottom = probe.textbbox((0, 0), text, font=chosen)
    layer = Image.new("RGBA", (right - left + 24, bottom - top + 24), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((12 - left, 12 - top), text, font=chosen, fill=fill + (255,))
    rotated = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    image.paste(rotated, origin, rotated)


def figure_6_17() -> None:
    image = load_rgb(MEDIA / "696bc3ec25d1a1b3-48558130407_a9b7577586_k.jpg")
    blot_ink(image, (620, 700, 1360, 1120))
    # El cartel está girado unos 14° en sentido horario.
    paste_rotated(image, "DIAGNÓSTICO:", (700, 700), -14, 70)
    paste_rotated(image, "EFECTO", (730, 830), -14, 132)
    paste_rotated(image, "PLACEBO", (760, 1000), -14, 92)
    image.save(OUT / "es-fig-6-17.png")


def figure_table() -> None:
    scale = 3
    width, height = 403 * scale, 140 * scale
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)
    left, right = 96 * scale, 390 * scale
    top, bottom = 28 * scale, 132 * scale
    mid_x = 239 * scale
    mid_y = 80 * scale
    draw.rectangle((left, top, right, bottom), outline=BLUE, width=3 * scale)
    draw.line((mid_x, top, mid_x, bottom), fill=BLUE, width=3 * scale)
    draw.line((left, mid_y, right, mid_y), fill=BLUE, width=3 * scale)

    def pill(box, color):
        pad = 8 * scale
        x0, y0, x1, y1 = box
        inner = (x0 + pad, y0 + pad, x1 - pad, y1 - pad)
        draw.rounded_rectangle(inner, radius=4 * scale, fill=color)
        return inner

    cells = [
        ((left, top, mid_x, mid_y), CELL_GRAY, "Positivo\ncorrecto", BLACK, SANS),
        ((mid_x, top, right, mid_y), CELL_GREEN, "Falso\npositivo", BLACK, SANS_OBLIQUE),
        ((left, mid_y, mid_x, bottom), CELL_RED, "Rechazo\nfalso", WHITE, SANS_OBLIQUE),
        ((mid_x, mid_y, right, bottom), CELL_GRAY, "Rechazo\ncorrecto", BLACK, SANS),
    ]
    for box, color, text, fill, font_path in cells:
        inner = pill(box, color)
        write(image, inner, text, fill=fill, size=28, align="center", font_path=font_path)
    write(image, (left, 2 * scale, mid_x, top), "Agente activo", size=28, align="center")
    write(image, (mid_x, 2 * scale, right, top), "Placebo", size=28, align="center")
    write(image, (4 * scale, top, left - 6 * scale, mid_y), "Alivio", size=26, align="right")
    write(image, (4 * scale, mid_y, left - 6 * scale, bottom), "Sin efecto", size=26, align="right")
    image.save(OUT / "es-tabla-6-1.png")


def main() -> None:
    figure_6_16()
    figure_6_17()
    figure_table()


if __name__ == "__main__":
    main()
