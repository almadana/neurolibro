#!/usr/bin/env python3
"""Genera las figuras 2.1–2.4 con sus rótulos en español rioplatense.

Requiere Pillow. Los originales se leen desde site/assets/media y nunca se
modifican. Las coordenadas se expresan en el sistema de cada imagen original.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT), size)


def centered(draw, box, text, face, fill="black", spacing=4):
    """Centra texto, incluso si contiene saltos de línea."""
    left, top, right, bottom = box
    bounds = draw.multiline_textbbox((0, 0), text, font=face, spacing=spacing,
                                     align="center")
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    x = left + (right - left - width) / 2
    y = top + (bottom - top - height) / 2 - bounds[1]
    draw.multiline_text((x, y), text, font=face, fill=fill, spacing=spacing,
                        align="center")


def scaled_box(box, scale):
    return tuple(round(value * scale) for value in box)


def cover_and_center(draw, box, text, face, scale=1, fill="white",
                     text_fill="black", spacing=4):
    box = scaled_box(box, scale)
    draw.rectangle(box, fill=fill)
    centered(draw, box, text, face, text_fill, spacing)


def figure_2_1():
    src = MEDIA / "fd4262e91dcea23c-cnsandpns.png"
    image = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(image)

    cover_and_center(
        draw, (105, 0, 605, 78),
        "Sistema nervioso central\nEncéfalo y médula espinal",
        font(24), fill="white", spacing=3,
    )
    cover_and_center(
        draw, (705, 0, 1279, 78),
        "Sistema nervioso periférico\nNervios craneales y espinales",
        font(24), fill="white", spacing=3,
    )
    cover_and_center(draw, (675, 123, 802, 166), "Aferente", font(23))
    cover_and_center(draw, (1025, 123, 1152, 158), "Eferente", font(23))
    image.save(OUT / "es-fig-2-1.png", optimize=True)


def figure_2_2():
    src = MEDIA / "f58a720c5e597674-nervous-system-divisions-350x287.png"
    scale = 4
    image = Image.open(src).convert("RGBA").resize(
        (350 * scale, 287 * scale), Image.Resampling.LANCZOS
    )
    draw = ImageDraw.Draw(image)

    labels = [
        ((101, 4, 199, 51), "Sistema\nnervioso", (216, 189, 152, 255), 11),
        ((33, 81, 130, 128), "Sistema nervioso\ncentral", (224, 176, 138, 255), 10),
        ((171, 81, 268, 128), "Sistema nervioso\nperiférico", (140, 181, 126, 255), 10),
        ((70, 157, 167, 205), "Sistema nervioso\nsomático", (240, 223, 185, 255), 10),
        ((212, 157, 309, 205), "Sistema nervioso\nautónomo", (177, 203, 218, 255), 10),
        ((3, 235, 101, 282), "Sistema nervioso\nsimpático", (189, 216, 232, 255), 9),
        ((125, 235, 224, 282), "Sistema nervioso\nparasimpático", (137, 190, 215, 255), 9),
        ((249, 235, 347, 282), "Sistema nervioso\nentérico", (75, 119, 139, 255), 9),
    ]
    for box, text, color, size in labels:
        inset = (box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3)
        cover_and_center(
            draw, inset, text, font(size * scale, bold=True), scale=scale,
            fill=color, spacing=scale,
        )
    image.save(OUT / "es-fig-2-2.png", optimize=True)


def figure_2_3():
    src = MEDIA / "791c94d2ba007f45-fig2.2_draft-350x211.png"
    scale = 4
    image = Image.open(src).convert("RGBA").resize(
        (350 * scale, 211 * scale), Image.Resampling.LANCZOS
    )
    draw = ImageDraw.Draw(image)
    labels = [
        ((19, 106, 69, 131), "RECEPTOR\nSENSITIVO", 5),
        ((74, 80, 108, 94), "NEURONA\nSENSITIVA", 5),
        ((116, 50, 145, 68), "GANGLIO DE LA\nRAÍZ DORSAL", 4),
        ((153, 34, 184, 48), "RAÍZ\nDORSAL", 5),
        ((205, 39, 235, 50), "SINAPSIS", 5),
        ((89, 132, 123, 155), "NEURONA\nMOTORA", 5),
        ((26, 163, 50, 176), "MÚSCULO", 5),
        ((140, 157, 173, 180), "RAÍZ\nVENTRAL", 5),
        ((198, 132, 239, 145), "MÉDULA ESPINAL", 5),
    ]
    for box, text, size in labels:
        cover_and_center(
            draw, box, text, font(size * scale, bold=True), scale=scale,
            fill=(255, 255, 255, 255), spacing=scale,
        )
    image.save(OUT / "es-fig-2-3.png", optimize=True)


def draw_rotated_label(image, box, text, face, background):
    """Cubre un rótulo vertical y escribe su reemplazo rotado 90 grados."""
    left, top, right, bottom = box
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, fill=background)
    layer = Image.new("RGBA", (bottom - top, right - left), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    centered(layer_draw, (0, 0, layer.width, layer.height), text, face)
    layer = layer.rotate(90, expand=True)
    image.alpha_composite(layer, (left, top))


def figure_2_4():
    src = MEDIA / "3fdd9e921d502e00-fig2.3-4.5_draft-350x273.png"
    scale = 4
    image = Image.open(src).convert("RGBA").resize(
        (350 * scale, 273 * scale), Image.Resampling.LANCZOS
    )
    draw = ImageDraw.Draw(image)

    cover_and_center(draw, (37, 18, 76, 31), "VÉRTEBRAS",
                     font(5 * scale, bold=True), scale=scale,
                     fill=(255, 255, 255, 255))
    cover_and_center(draw, (98, 18, 133, 31), "NERVIOS",
                     font(5 * scale, bold=True), scale=scale,
                     fill=(255, 255, 255, 255))
    cover_and_center(draw, (208, 14, 279, 31), "DERMATOMAS",
                     font(8 * scale, bold=True), scale=scale,
                     fill=(255, 255, 255, 255))
    cover_and_center(draw, (36, 229, 69, 244), "CÓCCIX",
                     font(4 * scale, bold=True), scale=scale,
                     fill=(255, 255, 255, 255))

    # Las bandas y sus colores forman parte del original; solo se repinta el
    # interior donde estaba el nombre inglés.
    vertical = [
        ((22, 39, 32, 100), "CERVICAL", (161, 239, 242, 255)),
        ((22, 101, 32, 180), "TORÁCICA", (102, 102, 102, 255)),
        ((22, 181, 32, 228), "LUMBAR", (193, 245, 247, 255)),
        ((22, 229, 32, 269), "SACRA", (102, 102, 102, 255)),
    ]
    for box, text, color in vertical:
        draw_rotated_label(
            image, scaled_box(box, scale), text,
            font(4 * scale, bold=True), color,
        )
    image.save(OUT / "es-fig-2-4.png", optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    figure_2_1()
    figure_2_2()
    figure_2_3()
    figure_2_4()
    for number in range(1, 5):
        path = OUT / f"es-fig-2-{number}.png"
        with Image.open(path) as image:
            print(f"{path.name}: {image.width} × {image.height} px")


if __name__ == "__main__":
    main()
