#!/usr/bin/env python3
"""Genera las versiones en español de las figuras 2.20–2.23b.

El script no altera las imágenes fuente. Las coordenadas se expresan en el
sistema de cada original y luego se escalan junto con las imágenes.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MEDIA = ROOT / "site" / "assets" / "media"

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_OBLIQUE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"


def load_scaled(filename: str, scale: int) -> Image.Image:
    image = Image.open(MEDIA / filename).convert("RGB")
    return image.resize(
        (image.width * scale, image.height * scale), Image.Resampling.LANCZOS
    )


def box(draw: ImageDraw.ImageDraw, scale: int, xy, fill) -> None:
    draw.rectangle(tuple(round(value * scale) for value in xy), fill=fill)


def font(path: str, points: float, scale: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, round(points * scale))


def text(
    draw: ImageDraw.ImageDraw,
    scale: int,
    xy,
    value: str,
    *,
    points: float,
    face: str = FONT_REGULAR,
    anchor: str = "la",
    align: str = "left",
    spacing: float = 1,
) -> None:
    draw.multiline_text(
        (round(xy[0] * scale), round(xy[1] * scale)),
        value,
        font=font(face, points, scale),
        fill="black",
        anchor=anchor,
        align=align,
        spacing=round(spacing * scale),
    )


def erase_with_sampled_rows(
    image: Image.Image, scale: int, xy, sample_x: float
) -> None:
    """Cubre texto sobre fondos con degradado usando el color de cada fila."""
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = (round(value * scale) for value in xy)
    sx = min(image.width - 1, round(sample_x * scale))
    for y in range(top, bottom + 1):
        draw.line((left, y, right, y), fill=image.getpixel((sx, y)))


def figure_220() -> None:
    scale = 2
    image = load_scaled(
        "c9e889291cd4feac-cajalhippocampus_modified-1024x555.png", scale
    )
    draw = ImageDraw.Draw(image)
    white = (255, 255, 255)
    inset_gray = image.getpixel((70 * scale, 470 * scale))

    # Rótulos del esquema principal. CA1 y CA3 se conservan.
    box(draw, scale, (170, 105, 227, 142), white)
    text(draw, scale, (198, 124), "CE", points=27, face=FONT_BOLD, anchor="mm")
    box(draw, scale, (557, 135, 619, 174), white)
    text(draw, scale, (587, 154), "GD", points=27, face=FONT_BOLD, anchor="mm")

    # Circuito inserto: se cambian todas las apariciones visibles de EC/DG.
    box(draw, scale, (48, 396, 98, 424), inset_gray)
    text(draw, scale, (52, 410), "CE2", points=20, anchor="lm")
    box(draw, scale, (48, 426, 99, 454), inset_gray)
    text(draw, scale, (52, 440), "CE3", points=20, anchor="lm")
    box(draw, scale, (25, 492, 139, 521), inset_gray)
    text(draw, scale, (30, 507), "CE profunda", points=17, anchor="lm")
    box(draw, scale, (177, 395, 218, 422), white)
    text(draw, scale, (180, 409), "GD", points=20, anchor="lm")

    image.save(HERE / "es-fig-2-20.png", optimize=True)


def figure_221() -> None:
    scale = 3
    image = load_scaled(
        "d1091a26bed28e25-blausen_0216_cerebrospinalsystem-350x263.png", scale
    )
    draw = ImageDraw.Draw(image)
    white = (255, 255, 255)

    replacements = [
        ((112, 3, 237, 26), (175, 15), "Sistema de LCR", 12, FONT_BOLD, "mm", "center"),
        ((2, 40, 86, 76), (5, 45), "Ventrículos\nlaterales", 11, FONT_REGULAR, "la", "left"),
        ((3, 108, 70, 142), (5, 111), "Tercer\nventrículo", 10.5, FONT_REGULAR, "la", "left"),
        ((244, 28, 350, 66), (247, 31), "Líquido\ncefalorraquídeo", 9.5, FONT_REGULAR, "la", "left"),
        ((276, 83, 332, 103), (278, 87), "Encéfalo", 10.5, FONT_REGULAR, "la", "left"),
        ((284, 126, 335, 146), (286, 130), "Cráneo", 10.5, FONT_REGULAR, "la", "left"),
        ((262, 176, 350, 210), (265, 180), "Cuarto\nventrículo", 10.5, FONT_REGULAR, "la", "left"),
    ]
    for rect, position, label, points, face, anchor, align in replacements:
        box(draw, scale, rect, white)
        text(
            draw,
            scale,
            position,
            label,
            points=points,
            face=face,
            anchor=anchor,
            align=align,
            spacing=0,
        )

    image.save(HERE / "es-fig-2-21.png", optimize=True)


def figure_222() -> None:
    scale = 4
    image = load_scaled(
        "d19226e2c7f63aae-1316_meningeal_layersn-1-350x190.png", scale
    )
    draw = ImageDraw.Draw(image)
    background = image.getpixel((348 * scale, 188 * scale))

    replacements = [
        ((77, 0, 105, 11), (80, 2), "Venas", 5.5),
        ((190, 0, 285, 12), (201, 2), "Seno sagital superior", 4.8),
        ((287, 30, 350, 42), (289, 33), "Hueso", 5.5),
        ((287, 49, 350, 60), (289, 52), "Duramadre", 5.5),
        ((287, 60, 350, 73), (289, 62), "Espacio subdural", 4.9),
        ((0, 54, 69, 67), (2, 57), "Aracnoides", 5.3),
        ((0, 68, 69, 88), (2, 71), "Espacio\nsubaracnoideo", 4.8),
        ((0, 91, 57, 104), (2, 94), "Piamadre", 5.3),
        ((0, 125, 70, 138), (2, 128), "Vena cerebral", 5.0),
        ((287, 125, 350, 139), (289, 128), "Corteza cerebral", 4.8),
    ]
    for rect, position, label, points in replacements:
        box(draw, scale, rect, background)
        text(
            draw,
            scale,
            position,
            label,
            points=points,
            anchor="la",
            spacing=0,
        )

    image.save(HERE / "es-fig-2-22.png", optimize=True)


def figure_223b() -> None:
    scale = 3
    image = load_scaled("0d37411e27493b93-bloodvessels-350x589.jpg", scale)
    original_scaled = image.copy()
    draw = ImageDraw.Draw(image)
    white = image.getpixel((345 * scale, 10 * scale))

    # Texto superior, fuera del tejido.
    box(draw, scale, (110, 37, 342, 56), white)
    text(
        draw,
        scale,
        (113, 41),
        "Superficie del encéfalo (piamadre)",
        points=10.5,
        face=FONT_OBLIQUE,
    )

    # Rótulos ubicados sobre el fondo beige (conserva su degradado).
    erase_with_sampled_rows(image, scale, (236, 67, 339, 92), 330)
    erase_with_sampled_rows(image, scale, (265, 151, 335, 177), 330)
    erase_with_sampled_rows(image, scale, (5, 177, 76, 291), 330)
    erase_with_sampled_rows(image, scale, (145, 348, 339, 430), 330)

    # Recupera en el bloque izquierdo los segmentos rojos y sus contornos
    # negros; así el fondo del texto se limpia sin borrar el vaso sanguíneo.
    vessel_rect = tuple(round(value * scale) for value in (5, 177, 76, 291))
    vessel_crop = original_scaled.crop(vessel_rect)
    vessel_mask = Image.new("L", vessel_crop.size)
    pixels = vessel_crop.load()
    mask_pixels = vessel_mask.load()
    for y in range(vessel_crop.height):
        for x in range(vessel_crop.width):
            red, green, blue = pixels[x, y]
            if red > 110 and green < 80 and blue < 65 and red - green > 55:
                mask_pixels[x, y] = 255
    vessel_mask = vessel_mask.filter(ImageFilter.MaxFilter(7))
    image.paste(vessel_crop, vessel_rect[:2], vessel_mask)
    draw = ImageDraw.Draw(image)

    text(draw, scale, (241, 72), "Tejido encefálico", points=10.5, face=FONT_OBLIQUE)
    text(draw, scale, (266, 156), "Hacia las venas", points=9.5)
    text(
        draw,
        scale,
        (7, 181),
        "Las células\nmusculares\nlisas y pericitos\ncontrolan\nel flujo\nsanguíneo",
        points=8.2,
        spacing=0,
    )
    text(
        draw,
        scale,
        (151, 354),
        "Los capilares se ramifican en\n"
        "vénulas y venas, que drenan la\n"
        "sangre hacia la superficie del\n"
        "encéfalo en la piamadre.",
        points=10,
        face=FONT_OBLIQUE,
        spacing=0,
    )

    # Se restituyen dos líneas guía tapadas al reemplazar el bloque izquierdo.
    line_width = max(1, round(0.8 * scale))
    draw.line(
        (73 * scale, 195 * scale, 99 * scale, 184 * scale),
        fill="black",
        width=line_width,
    )
    draw.polygon(
        [
            (99 * scale, 184 * scale),
            (94 * scale, 183 * scale),
            (96 * scale, 188 * scale),
        ],
        fill="black",
    )
    draw.line(
        (78 * scale, 168 * scale, 110 * scale, 155 * scale),
        fill="black",
        width=line_width,
    )
    draw.polygon(
        [
            (110 * scale, 155 * scale),
            (105 * scale, 155 * scale),
            (107 * scale, 160 * scale),
        ],
        fill="black",
    )

    image.save(HERE / "es-fig-2-23b.png", optimize=True)


def main() -> None:
    figure_220()
    figure_221()
    figure_222()
    figure_223b()


if __name__ == "__main__":
    main()
