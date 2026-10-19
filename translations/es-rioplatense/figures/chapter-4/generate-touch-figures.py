#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 4.1–4.4, 4.6, 4.7, 4.8 y 4.10.

Los originales de site/assets/media no se modifican. En los homúnculos solo se
traduce el título grande: los nombres de las partes del cuerpo están rotados
y ocupan unos pocos píxeles, y taparlos destruiría el mapa.
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
BLACK = (0, 0, 0)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def is_light(pixel) -> bool:
    return sum(pixel) / 3 > 165 and max(pixel) - min(pixel) < 150


def background_at(pixels, x, y, step, width, height):
    for _ in range(80):
        y += step
        if y < 0 or y >= height:
            return None
        pixel = pixels[x, y]
        if is_light(pixel):
            return pixel
    return None


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 128) -> None:
    """Quita solo la tinta oscura del rótulo y deja el dibujo de alrededor."""
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            if (red + green + blue) / 3 < threshold and max(red, green, blue) - min(red, green, blue) < 40:
                ink.append((x, y))
    blocked = set(ink)
    for x, y in ink:
        replacement = None
        for step in range(1, 28):
            for nx, ny in ((x, y - step), (x, y + step), (x - step, y), (x + step, y)):
                if 0 <= nx < image.width and 0 <= ny < image.height and (nx, ny) not in blocked:
                    replacement = pixels[nx, ny]
                    break
            if replacement is not None:
                break
        pixels[x, y] = replacement or WHITE


def write(image, box, text, *, scale=1, fill=BLACK, align="center", bold=True):
    max_w = max(8, (box[2] - box[0]) * scale)
    max_h = max(8, (box[3] - box[1]) * scale)
    draw = ImageDraw.Draw(image)
    size = max(8, (box[3] - box[1]) * scale * (0.42 if "\n" in text else 0.78))
    chosen = face(size, bold)
    spacing = max(1, round(scale * 0.4))
    bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    for _ in range(24):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.9
        chosen = face(size, bold)
        bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = box[0] * scale - bounds[0]
    elif align == "right":
        x = box[2] * scale - width - bounds[0]
    else:
        x = (box[0] + box[2]) / 2 * scale - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 * scale - height / 2 - bounds[1]
    draw.multiline_text(
        (round(x), round(y)), text, font=chosen, fill=fill,
        spacing=spacing, align=align,
    )


def erase_gray(image: Image.Image, box, scale: int = 1) -> None:
    """Borra letra gris y conserva los trazos negros y el relleno celeste."""
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            average = (red + green + blue) / 3
            if 15 < average < 235 and max(red, green, blue) - min(red, green, blue) < 32:
                ink.append((x, y))
    blocked = set(ink)
    for x, y in ink:
        replacement = None
        for step in range(1, 30):
            for nx, ny in ((x, y - step), (x, y + step), (x - step, y), (x + step, y)):
                if 0 <= nx < image.width and 0 <= ny < image.height and (nx, ny) not in blocked:
                    replacement = pixels[nx, ny]
                    break
            if replacement is not None:
                break
        if replacement is not None:
            pixels[x, y] = replacement


def cover(image, box, text, *, scale=1, align="center", bold=True, threshold=230):
    erase(image, box, scale, threshold)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=WHITE)
    write(image, box, text, scale=scale, align=align, bold=bold)


def cover_vertical(image, box, text, *, scale=1, fill=BLACK, threshold=230):
    """Texto que se lee de abajo hacia arriba, como el eje de la figura original."""
    erase(image, box, scale, threshold)
    left, top, right, bottom = scale_box(box, scale)
    max_w = max(8, bottom - top - scale)
    max_h = max(8, right - left - scale)
    size = max_h * 0.8
    chosen = face(size, True)
    probe = ImageDraw.Draw(image)
    bounds = probe.textbbox((0, 0), text, font=chosen)
    for _ in range(20):
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


def figure_4_1() -> None:
    scale = 4
    image = open_scaled("f1e45fefac9ada9b-fig4.1_draft-350x273.png", scale)
    labels = (
        ((96, 10, 176, 30), "Piel glabra"),
        ((176, 10, 246, 30), "Piel con pelo"),
        ((248, 8, 322, 28), "Pelo"),
        ((8, 28, 92, 44), "Epidermis", "right"),
        ((8, 48, 92, 64), "Dermis", "right"),
        ((248, 58, 348, 74), "Folículo piloso", "left"),
        ((248, 76, 340, 92), "Adipocitos", "left"),
        ((2, 220, 74, 246), "Corpúsculo\nde Pacini"),
        ((76, 220, 146, 246), "Discos\nde Merkel"),
        ((146, 220, 208, 246), "Corpúsculo\nde Meissner"),
        ((212, 220, 272, 246), "Terminaciones\nde Ruffini"),
        ((274, 220, 348, 246), "Terminaciones\nnerviosas libres"),
        ((80, 246, 270, 268), "Estructuras accesorias"),
    )
    for item in labels:
        box, text, *rest = item
        cover(image, box, text, scale=scale, align=rest[0] if rest else "center")
    save(image, "es-fig-4-1.png")


def figure_4_2() -> None:
    scale = 4
    image = open_scaled("aa82fe27adbbafdc-fig4.2_draft-350x288.png", scale)
    # El español de los núcleos queda arriba; hay que borrar el inglés original.
    for old in (
        (188, 42, 242, 74),
        (228, 48, 278, 80),
        (258, 55, 318, 90),
        (300, 108, 348, 155),
        (248, 236, 332, 262),
        (40, 46, 78, 76),
        (0, 68, 48, 100),
        (90, 200, 150, 230),
    ):
        erase_gray(image, old, scale)
    labels = (
        ((0, 56, 44, 88), "Fibra\nnerviosa"),
        ((28, 40, 74, 74), "Vaso\nsanguíneo"),
        ((8, 142, 72, 172), "Vaina de\nmielina"),
        ((78, 198, 140, 228), "Nodo de\nRanvier"),
        ((158, 4, 224, 46), "Cápsula\nexterna"),
        ((226, 4, 286, 46), "Núcleo\nexterno"),
        ((288, 4, 348, 46), "Núcleo\ninterno"),
        ((286, 78, 346, 96), "Laminillas", "left"),
        ((286, 98, 348, 122), "Cuerpo celular\nde las laminillas", "left"),
        ((292, 124, 348, 150), "Axón\namielínico", "left"),
        ((176, 232, 236, 258), "Rama\nterminal"),
        ((248, 232, 328, 258), "Rama\nultraterminal"),
    )
    for item in labels:
        box, text, *rest = item
        cover(image, box, text, scale=scale, align=rest[0] if rest else "center")
    save(image, "es-fig-4-2.png")


def figure_4_3() -> None:
    scale = 4
    image = open_scaled("cf135f24d0bf8fb1-fig-4.3-stimulus-intensity-350x220.png", scale)
    cover_vertical(
        image, (4, 40, 22, 186), "Magnitud del potencial de receptor",
        scale=scale,
    )
    cover(
        image, (80, 198, 280, 218), "Intensidad del estímulo en el receptor",
        scale=scale,
    )
    save(image, "es-fig-4-3.png")


def figure_4_4() -> None:
    scale = 4
    image = open_scaled("648fd06b6e6bd1a3-fig4.4_draft-350x273.png", scale)
    labels = (
        ((36, 86, 118, 114), "Piel"),
        ((0, 242, 62, 270), "Corpúsculo\nde Pacini"),
        ((200, 12, 275, 40), "Prolongaciones\naxónicas"),
        ((175, 142, 245, 176), "Ganglio de la\nraíz dorsal"),
        ((258, 152, 318, 180), "Cuerpo\ncelular"),
    )
    for box, text in labels:
        cover(image, box, text, scale=scale)
    save(image, "es-fig-4-4.png")


def figure_4_6() -> None:
    scale = 4
    image = open_scaled("29479c8d06c70f10-fig4.6_draft-350x157.png", scale)
    labels = (
        ((12, 72, 72, 96), "Receptor\nsensitivo", 140),
        ((18, 132, 58, 148), "Piel"),
        ((76, 34, 148, 58), "Prolongación\naxónica periférica"),
        ((145, 6, 190, 28), "Cuerpo\ncelular"),
        ((138, 132, 205, 156), "Ganglio de la\nraíz dorsal"),
        ((208, 34, 278, 58), "Prolongación\naxónica central"),
        ((288, 6, 346, 40), "Terminales\naxónicas"),
        ((292, 132, 346, 152), "Médula\nespinal"),
    )
    for box, text, *rest in labels:
        cover(image, box, text, scale=scale, threshold=rest[0] if rest else 230)
    for leftover in (
        (78, 56, 148, 74),
        (208, 56, 278, 74),
        (292, 48, 346, 90),
    ):
        erase_gray(image, leftover, scale)
    save(image, "es-fig-4-6.png")


def figure_4_7() -> None:
    scale = 4
    image = open_scaled("cc2e94083f8750fe-fig4.7_draft-350x273.png", scale)
    labels = (
        ((250, 20, 308, 38), "Corteza", "left"),
        ((214, 40, 308, 84), "Núcleo ventral\nposterolateral\ndel tálamo", "left"),
        ((108, 50, 172, 70), "Tálamo", "right"),
        ((220, 84, 308, 112), "Tracto del\nlemnisco medial", "left"),
        ((220, 112, 308, 140), "Núcleo de la\ncolumna dorsal", "left"),
        ((220, 140, 308, 168), "Tracto de la\ncolumna dorsal", "left"),
        ((145, 128, 205, 152), "Aferente\nsensitiva"),
        ((95, 140, 145, 162), "Raíz\ndorsal"),
        ((55, 158, 115, 188), "Ganglio de\nla raíz dorsal"),
        ((4, 228, 62, 258), "Receptor\nsensitivo"),
    )
    for item in labels:
        box, text, *rest = item
        cover(image, box, text, scale=scale, align=rest[0] if rest else "center")
    # La barra original mide unos 8 px: se borra el inglés y el español
    # queda en el margen blanco, donde sí se puede leer.
    erase_gray(image, (314, 12, 326, 262), scale)
    cover_vertical(image, (327, 16, 349, 64), "Encéfalo", scale=scale)
    cover_vertical(image, (327, 70, 349, 146), "Tronco encefálico", scale=scale)
    cover_vertical(image, (327, 158, 349, 258), "Médula espinal", scale=scale)
    save(image, "es-fig-4-7.png")


def figure_4_8() -> None:
    scale = 4
    image = open_scaled("aa40d916fd2b0a98-fig4.8_draft-350x288.png", scale)
    cover(image, (210, 258, 325, 282), "Corteza sensitiva", scale=scale)
    save(image, "es-fig-4-8.png")


def figure_4_10() -> None:
    scale = 4
    image = open_scaled("c072269665d435ef-fig4.10_draft-350x288.png", scale)
    cover(image, (130, 248, 230, 274), "Corteza motora", scale=scale)
    save(image, "es-fig-4-10.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    figure_4_1()
    figure_4_2()
    figure_4_3()
    figure_4_4()
    figure_4_6()
    figure_4_7()
    figure_4_8()
    figure_4_10()


if __name__ == "__main__":
    main()
