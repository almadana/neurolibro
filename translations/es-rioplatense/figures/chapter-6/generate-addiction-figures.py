#!/usr/bin/env python3
"""Localiza los rótulos de las figuras de adicción (6.1 a 6.3).

Los originales de site/assets/media no se modifican. Quedan en inglés los
créditos. Los recuadros vacíos de la figura 6.2 no se rotulan.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
ARROW = (157, 195, 230)


def face(size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def write(image, box, text, *, scale=1, fill=BLACK, align="center", size=None):
    max_w = max(8, (box[2] - box[0]) * scale - 4)
    max_h = max(8, (box[3] - box[1]) * scale - 4)
    draw = ImageDraw.Draw(image)
    if size is None:
        size = (box[3] - box[1]) * scale * (0.42 if "\n" in text else 0.72)
    chosen = face(size)
    spacing = max(1, round(size * 0.15))
    bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    for _ in range(30):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.92
        chosen = face(size)
        bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = box[0] * scale + 2 - bounds[0]
    elif align == "right":
        x = box[2] * scale - width - 2 - bounds[0]
    else:
        x = (box[0] + box[2]) / 2 * scale - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 * scale - height / 2 - bounds[1]
    draw.multiline_text(
        (round(x), round(y)), text, font=chosen, fill=fill,
        spacing=spacing, align=align,
    )


def cover(image, box, text, *, scale=1, align="center", size=None, fill=BLACK, plate=WHITE):
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    if text:
        write(image, box, text, scale=scale, align=align, size=size, fill=fill)


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


def figure_6_1() -> None:
    """Caja de autoestimulación. El crédito del borde inferior no se toca."""
    scale = 4
    pad = 70
    image = open_scaled("5e1a1ed70130ef7e-fig6.1_draft-350x273.png", scale, pad=(pad, 0, 0, 0))

    def shifted(box):
        left, top, right, bottom = box
        return (left + pad, top, right + pad, bottom)

    # Solo el gris de las palabras, a la izquierda de las líneas guía.
    cover(image, shifted((14, 76, 46, 84)), "", scale=scale)
    cover(image, shifted((14, 109, 34, 117)), "", scale=scale)
    cover(image, shifted((14, 141, 47, 154)), "", scale=scale)

    # El texto nuevo crece hacia el margen y termina antes de cada línea guía.
    write(image, (4, 64, pad + 40, 90), "Electrodo", scale=scale, align="right", size=36)
    write(image, (4, 100, pad + 30, 128), "Palanca", scale=scale, align="right", size=36)
    write(
        image, (4, 132, pad + 26, 176), "Estimulador\neléctrico",
        scale=scale, align="right", size=32,
    )
    save(image, "es-fig-6-1.png")


def figure_6_2() -> None:
    """La flecha azul es el único rótulo. Los recuadros rojo y verde están vacíos."""
    image = Image.open(MEDIA / "0648dc8b8e37dc1c-image2-3.png").convert("RGB")
    cover(
        image, (268, 372, 788, 422), "Vía dopaminérgica\nmesolímbica",
        scale=1, size=34, plate=ARROW,
    )
    save(image, "es-fig-6-2.png")


def figure_6_3() -> None:
    """Expresiones de agrado y aversión. El crédito entre las filas no se toca."""
    scale = 4
    image = open_scaled("398abb0e103d5dad-fig1.14_draft-350x273.png", scale)
    cover(image, (8, 4, 342, 36), "Reacción a sabores dulces", scale=scale, size=42)
    labels = (
        (28, 126, 112, 148, "Roedor"),
        (128, 126, 214, 148, "Primate"),
        (232, 126, 318, 148, "Humano"),
    )
    for box in labels:
        cover(image, box[:4], box[4], scale=scale, size=32)
    # El crédito queda en y 243-244. El título inferior empieza debajo.
    cover(image, (12, 247, 338, 270), "Reacción a sabores amargos", scale=scale, size=40)
    save(image, "es-fig-6-3.png")


def main() -> None:
    figure_6_1()
    figure_6_2()
    figure_6_3()


if __name__ == "__main__":
    main()
