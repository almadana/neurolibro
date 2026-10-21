#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 6.10 y 6.11.

Los originales de site/assets/media no se modifican. El crédito de Dekaban y
Sadowsky queda en el atributo title. La firma «ELIZA WOLFSON» del dibujo 6.11
no se tapa.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
RED = (255, 86, 100)


def face(size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(SANS, max(8, round(size)))


def load_rgb(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    canvas = Image.new("RGB", image.size, WHITE)
    canvas.paste(image, mask=image.split()[-1])
    return canvas


def cover(image: Image.Image, box, scale: int) -> None:
    x0, y0, x1, y1 = [round(value * scale) for value in box]
    ImageDraw.Draw(image).rectangle([x0, y0, x1, y1], fill=WHITE)


def is_cyan(pixel) -> bool:
    red, green, blue = pixel
    return blue > red + 8 and green > red + 8


def erase_text(source: Image.Image, image: Image.Image, box, scale: int) -> None:
    """Tapa la letra gris y deja el relleno celeste y el trazo pegado a él."""
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


def write(image, box, text, *, fill=BLACK, size, align="center"):
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(image)
    chosen = face(size)
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


def rotated(image, text, center, size, fill) -> None:
    chosen = face(size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    left, top, right, bottom = probe.textbbox((0, 0), text, font=chosen)
    plate = Image.new("RGBA", (right - left + 4, bottom - top + 4), (0, 0, 0, 0))
    ImageDraw.Draw(plate).text((2 - left, 2 - top), text, font=chosen, fill=fill + (255,))
    turned = plate.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    image.paste(
        turned,
        (round(center[0] - turned.width / 2), round(center[1] - turned.height / 2)),
        turned,
    )


def figure_6_10() -> None:
    scale = 2
    image = load_rgb(MEDIA / "5942945f0c676843-brain_weight_age.gif")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    cover(image, (14, 100, 46, 268), scale)
    rotated(
        image,
        "Peso encefálico (kg)",
        (28 * scale, 183 * scale),
        30,
        BLACK,
    )
    cover(image, (12, 364, 78, 392), scale)
    cover(image, (12, 390, 100, 416), scale)
    write(
        image,
        (17 * scale, 366 * scale, 120 * scale, 390 * scale),
        "Varones",
        fill=BLUE,
        size=34,
        align="left",
    )
    write(
        image,
        (17 * scale, 392 * scale, 140 * scale, 416 * scale),
        "Mujeres",
        fill=RED,
        size=34,
        align="left",
    )
    image.save(OUT / "es-fig-6-10.png")


def figure_6_11() -> None:
    scale = 6
    image = load_rgb(MEDIA / "3cb51e6eb7a447da-fig6.10_draft-350x273.png")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    source = image.copy()

    erase_text(source, image, (20, 10, 64, 26), scale)
    write(image, (16 * scale, 4 * scale, 150 * scale, 40 * scale), "Joven", size=52)

    erase_text(source, image, (255, 10, 336, 36), scale)
    write(
        image,
        (210 * scale, 4 * scale, 346 * scale, 48 * scale),
        "Cambios asociados\ncon la edad",
        size=36,
    )

    erase_text(source, image, (18, 86, 56, 102), scale)
    write(image, (8 * scale, 82 * scale, 62 * scale, 104 * scale), "Surcos", size=32)

    erase_text(source, image, (276, 56, 344, 76), scale)
    write(
        image,
        (248 * scale, 50 * scale, 346 * scale, 96 * scale),
        "Ventrículos\nagrandados",
        size=30,
        align="right",
    )

    erase_text(source, image, (252, 114, 344, 134), scale)
    write(
        image,
        (220 * scale, 108 * scale, 346 * scale, 148 * scale),
        "Surcos\nensanchados",
        size=30,
        align="right",
    )

    erase_text(source, image, (18, 170, 72, 182), scale)
    write(image, (8 * scale, 158 * scale, 88 * scale, 182 * scale), "Neuronas", size=32)

    erase_text(source, image, (18, 212, 60, 230), scale)
    write(
        image,
        (6 * scale, 206 * scale, 90 * scale, 234 * scale),
        "Vaina de\nmielina",
        size=28,
    )

    erase_text(source, image, (268, 172, 344, 188), scale)
    write(
        image,
        (230 * scale, 164 * scale, 346 * scale, 214 * scale),
        "Neuronas\ndañadas y\nque mueren",
        size=26,
        align="right",
    )

    erase_text(source, image, (278, 212, 344, 236), scale)
    write(
        image,
        (210 * scale, 206 * scale, 346 * scale, 268 * scale),
        "Vaina de mielina\nrota e\nincompleta",
        size=26,
        align="right",
    )

    image.save(OUT / "es-fig-6-11.png")


def main() -> None:
    figure_6_10()
    figure_6_11()


if __name__ == "__main__":
    main()
