#!/usr/bin/env python3
"""Genera las figuras 2.24, 2.25, 2.27 y 2.33 con rótulos en español.

Los originales se leen desde site/assets/media y no se modifican. Las
coordenadas se expresan en el sistema de cada imagen original; el script
amplía 4× para mejorar la legibilidad.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
SCALE = 4
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size: float, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, round(size * SCALE))


def sc(box):
    return tuple(round(v * SCALE) for v in box)


def background_at(pixels, x, y, axis, step, width, height):
    """Busca el primer píxel claro al salir de la tinta, sin tomar flechas ni vasos."""
    for _ in range(48):
        if axis == "x":
            x += step
        else:
            y += step
        if x < 0 or y < 0 or x >= width or y >= height:
            return None
        pixel = pixels[x, y]
        if sum(pixel) / 3 > 160 and max(pixel) - min(pixel) < 130:
            return pixel
    return None


def erase(image, box):
    """Sustituye la tinta inglesa por el fondo de arriba y de abajo.

    Así se sigue el degradado vertical del dibujo y no aparece una banda clara.
    """
    left, top, right, bottom = sc(box)
    pad = SCALE
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(image.width - 1, right + pad)
    bottom = min(image.height - 1, bottom + pad)
    pixels = image.load()
    span = max(1, bottom - top)
    for x in range(left, right + 1):
        above = background_at(pixels, x, top, "y", -1, image.width, image.height)
        below = background_at(pixels, x, bottom, "y", 1, image.width, image.height)
        if above is None:
            above = below or (255, 255, 255)
        if below is None:
            below = above
        for y in range(top, bottom + 1):
            blend = (y - top) / span
            pixels[x, y] = tuple(
                round(above[channel] * (1 - blend) + below[channel] * blend)
                for channel in range(3)
            )


def cover(image, draw, box, text, *, size=5.2, extra=(2, 2), align="center", bold=True, at=None):
    """Borra el inglés y escribe el español en el mismo sitio, sin recuadro.

    `at` permite correr el texto nuevo cuando el español, ceñido a la
    izquierda, taparía una flecha. Si la traducción no cabe en la tinta
    original, se reduce la fuente antes de dejarla crecer más de `extra`
    píxeles originales.
    """
    erase(image, box)
    box = at or box
    max_w = (box[2] - box[0] + extra[0]) * SCALE
    max_h = (box[3] - box[1] + extra[1]) * SCALE
    spacing = max(1, SCALE // 2)
    chosen = size
    face = font(chosen, bold=bold)
    bounds = draw.multiline_textbbox((0, 0), text, font=face, spacing=spacing, align=align)
    for _ in range(14):
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        if width <= max_w and height <= max_h:
            break
        chosen *= 0.92
        face = font(chosen, bold=bold)
        bounds = draw.multiline_textbbox(
            (0, 0), text, font=face, spacing=spacing, align=align
        )
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = box[0] * SCALE - bounds[0]
    elif align == "right":
        x = box[2] * SCALE - width - bounds[0]
    else:
        x = (box[0] + box[2]) / 2 * SCALE - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 * SCALE - height / 2 - bounds[1]
    draw.multiline_text(
        (round(x), round(y)),
        text,
        font=face,
        fill="black",
        spacing=spacing,
        align=align,
    )


def load(name):
    source = Image.open(MEDIA / name).convert("RGB")
    return source.resize(
        (source.width * SCALE, source.height * SCALE),
        Image.Resampling.LANCZOS,
    )


def figure_2_24():
    image = load("9105900f30c4e57e-neuron-350x186.jpg")
    draw = ImageDraw.Draw(image)
    # Cajas medidas sobre la tinta, sin incluir dendritas, flechas ni mielina.
    labels = (
        ((92, 16, 124, 23), "Dendritas", (6, 2), "center"),
        ((77, 94, 109, 101), "Cuerpo\ncelular", (10, 8), "center"),
        ((104, 147, 126, 165), "Cono\naxónico", (6, 2), "center"),
        ((206, 179, 223, 185), "Axón", (8, 2), "center"),
        ((302, 140, 340, 155), "Terminal\npresináptica", (10, 4), "center"),
    )
    for box, text, extra, align in labels:
        cover(image, draw, box, text, extra=extra, align=align)
    image.save(OUT / "es-fig-2-24.png", optimize=True)
    print("es-fig-2-24.png:", image.size)


def figure_2_25():
    image = load("81e748e956354e13-neuron-types-350x277.jpg")
    draw = ImageDraw.Draw(image)
    # Rótulos del canal blanco central, entre las flechas.
    labels = (
        ((153, 23, 198, 33), "Dendritas", (4, 2)),
        ((153, 57, 198, 68), "Cuerpo celular", (6, 2)),
        ((163, 91, 187, 102), "Axón", (6, 2)),
        ((163, 163, 186, 171), "Axón", (6, 2)),
        ((153, 196, 198, 206), "Dendritas", (4, 2)),
        ((153, 230, 198, 242), "Cuerpo celular", (6, 2)),
        ((163, 266, 186, 274), "Axón", (6, 2)),
    )
    for box, text, extra in labels:
        cover(image, draw, box, text, extra=extra)
    image.save(OUT / "es-fig-2-25.png", optimize=True)
    print("es-fig-2-25.png:", image.size)


def figure_2_27():
    image = load("2116286238aaa711-dendrites-350x186.jpg")
    draw = ImageDraw.Draw(image)
    cover(image, draw, (92, 16, 124, 23), "Dendritas", extra=(6, 2))
    cover(
        image,
        draw,
        (282, 19, 316, 36),
        "Espinas\ndendríticas",
        extra=(30, 2),
        align="left",
        at=(296, 19, 348, 36),
    )
    image.save(OUT / "es-fig-2-27.png", optimize=True)
    print("es-fig-2-27.png:", image.size)


def figure_2_33():
    image = load("dc267e48064fd69d-pericyte-cartoon-350x258.jpg")
    draw = ImageDraw.Draw(image)
    labels = (
        ((82, 39, 156, 46), "Célula muscular\nlisa", (4, 10), "center"),
        ((91, 171, 120, 178), "Pericito", (4, 2), "center"),
        ((260, 41, 286, 48), "Neurona", (4, 2), "center"),
        ((235, 66, 268, 83), "Pie terminal\ndel astrocito", (8, 2), "center"),
        ((311, 102, 349, 118), "Célula\nendotelial", (0, 2), "right"),
        ((173, 136, 200, 153), "Lámina\nbasal", (6, 2), "center"),
        ((314, 154, 339, 160), "Luz", (2, 2), "center"),
        ((252, 196, 280, 205), "Pericito", (4, 2), "center"),
    )
    for box, text, extra, align in labels:
        cover(image, draw, box, text, extra=extra, align=align)
    image.save(OUT / "es-fig-2-33.png", optimize=True)
    print("es-fig-2-33.png:", image.size)


def main() -> int:
    figure_2_24()
    figure_2_25()
    figure_2_27()
    figure_2_33()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
