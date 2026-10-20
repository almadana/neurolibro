#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 6.4 a 6.7.

Los originales de site/assets/media no se modifican. Quedan en inglés los
créditos. No se rotulan las flechas vacías de la figura 6.5. CRH, ACTH, 5-HT,
SERT y RECEPTOR se conservan.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_OBLIQUE = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE_TEXT = (36, 52, 170)
BEIGE = (254, 241, 203)
OVAL = (67, 117, 195)
RED = (220, 0, 0)


def face(size: float, path: str = FONT_BOLD) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def write(image, box, text, *, scale=1, fill=BLACK, align="center", size=None, font_path=FONT_BOLD):
    max_w = max(8, (box[2] - box[0]) * scale - 6)
    max_h = max(8, (box[3] - box[1]) * scale - 4)
    draw = ImageDraw.Draw(image)
    if size is None:
        size = (box[3] - box[1]) * scale * (0.38 if "\n" in text else 0.62)
    chosen = face(size, font_path)
    spacing = max(1, round(size * 0.12))
    bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    for _ in range(40):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.92
        chosen = face(size, font_path)
        bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = box[0] * scale + 3 - bounds[0]
    elif align == "right":
        x = box[2] * scale - width - 3 - bounds[0]
    else:
        x = (box[0] + box[2]) / 2 * scale - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 * scale - height / 2 - bounds[1]
    draw.multiline_text(
        (round(x), round(y)), text, font=chosen, fill=fill,
        spacing=spacing, align=align,
    )


def cover(image, box, text, *, scale=1, align="center", size=None, fill=BLACK, plate=WHITE, font_path=FONT_BOLD):
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    if text:
        write(
            image, box, text, scale=scale, align=align, size=size,
            fill=fill, font_path=font_path,
        )


def open_scaled(name: str, scale: int) -> Image.Image:
    image = Image.open(MEDIA / name)
    if image.mode == "P":
        image = image.convert("RGBA")
    if image.mode == "RGBA":
        canvas = Image.new("RGB", image.size, WHITE)
        canvas.paste(image, mask=image.split()[-1])
        image = canvas
    else:
        image = image.convert("RGB")
    if scale != 1:
        image = image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)
    return image


def save(image: Image.Image, name: str) -> None:
    path = OUT / name
    image.save(path, optimize=True)
    print(f"{name} {image.size[0]}x{image.size[1]}")


def figure_6_4() -> None:
    image = open_scaled("bc8772e51646df29-image1-2.png", 1)
    labels = [
        ((514, 12, 820, 58), "Trastornos afectivos"),
        ((938, 148, 1248, 190), "Trastornos\nunipolares"),
        ((516, 296, 802, 340), "Depresión mayor"),
        ((882, 296, 1058, 340), "Distimia"),
        ((1138, 300, 1296, 428), "Trastorno\nafectivo\nestacional"),
        ((1378, 300, 1614, 428), "Depresión\nasociada\nal parto"),
        ((128, 324, 400, 370), "Trastornos\nbipolares"),
        ((16, 474, 158, 518), "Bipolar I"),
        ((190, 474, 342, 518), "Bipolar II"),
        ((374, 476, 576, 518), "Ciclotimia"),
        ((1286, 540, 1468, 628), "Depresión\nperinatal"),
        ((1524, 540, 1724, 628), "Depresión\nposparto"),
    ]
    for box, text in labels:
        cover(image, box, text, scale=1)
    save(image, "es-fig-6-4.png")


def erase_triangle_text(image: Image.Image, scale: int) -> None:
    """Quita el texto negro o rojo apoyado en el triángulo, sin tocar el borde."""
    pixels = image.load()
    width, height = image.size

    def beige(x: int, y: int) -> bool:
        red, green, blue = pixels[x, y]
        return red > 220 and green > 190 and blue > 150 and red > blue + 20

    def pale(x: int, y: int) -> bool:
        return sum(pixels[x, y]) > 700

    fill = (255, 242, 204)
    for _ in range(5):
        targets = []
        for y in range(418 * scale, 660 * scale):
            for x in range(width):
                # Las flechas blancas entran por el centro del triángulo.
                if 390 * scale < x < 465 * scale and (y < 455 * scale or y > 615 * scale):
                    continue
                red, green, blue = pixels[x, y]
                if red > 250 and green > 250 and blue > 250:
                    continue
                if abs(red - fill[0]) <= 6 and abs(green - fill[1]) <= 6 and abs(blue - fill[2]) <= 8:
                    continue
                beige_n = white_n = 0
                for dy in (-6, -3, 3, 6):
                    for dx in (-8, -4, 4, 8):
                        nx, ny = x + dx, y + dy
                        if not (0 <= nx < width and 0 <= ny < height):
                            continue
                        nr, ng, nb = pixels[nx, ny]
                        if nr > 248 and ng > 248 and nb > 248:
                            white_n += 1
                        elif beige(nx, ny):
                            beige_n += 1
                if white_n == 0 and beige_n >= 3:
                    targets.append((x, y, fill))
                elif white_n >= 6 and beige_n == 0 and red < 80:
                    targets.append((x, y, WHITE))
        if not targets:
            break
        for x, y, color in targets:
            pixels[x, y] = color
    # Rellena el interior entre los dos bordes para borrar el halo que queda
    # junto al contorno, sobre todo en «of future».
    for y in range(428 * scale, 636 * scale):
        darks = [x for x in range(width) if sum(pixels[x, y]) < 120]
        if len(darks) < 8:
            continue
        left, right = darks[0], darks[-1]
        if right - left < 24 * scale:
            continue
        for x in range(left + 3, right - 2):
            if 390 * scale < x < 465 * scale and y < 455 * scale:
                continue
            pixels[x, y] = fill


def figure_6_5() -> None:
    scale = 2
    image = open_scaled("28f9d7c4373a908a-image2-4.png", scale)
    pale = image.getpixel((420 * scale, 40 * scale))
    cover(image, (360, 52, 500, 92), "Genético", scale=scale, fill=BLACK, plate=pale)
    cover(image, (180, 200, 355, 248), "Biológico", scale=scale, fill=BLACK, plate=pale)
    cover(image, (525, 200, 645, 242), "Social", scale=scale, fill=BLACK, plate=pale)
    cover(image, (278, 324, 612, 376), "Factores precipitantes", scale=scale, fill=BLACK, plate=WHITE)
    erase_triangle_text(image, scale)
    write(image, (150, 428, 340, 520), "Visiones negativas\ndel mundo", scale=scale, fill=BLACK)
    write(image, (520, 428, 710, 520), "Visiones negativas\nde uno mismo", scale=scale, fill=BLACK)
    write(image, (365, 458, 495, 528), "TRÍADA\nDE BECK", scale=scale, fill=RED)
    write(image, (310, 536, 545, 600), "Visiones negativas\ndel futuro", scale=scale, fill=BLACK)
    cover(image, (160, 742, 690, 792), "Pensamientos automáticos negativos", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (200, 900, 670, 955), "Síntomas de la depresión", scale=scale, fill=BLACK, plate=WHITE)
    save(image, "es-fig-6-5.png")


def figure_6_6() -> None:
    scale = 4
    image = open_scaled("ebbe53801b670915-ssri_how_they_work-350x248.jpeg", scale)
    cover(
        image, (126, 12, 224, 62),
        "NEURONA\nPRESINÁPTICA\n(CÉLULA EMISORA)",
        scale=scale, fill=BLUE_TEXT, plate=WHITE,
    )
    cover(
        image, (96, 200, 258, 236),
        "NEURONA POSTSINÁPTICA\n(CÉLULA RECEPTORA)",
        scale=scale, fill=BLUE_TEXT, plate=WHITE,
    )
    cover(image, (16, 40, 90, 54), "VESÍCULA", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (14, 126, 108, 140), "SEROTONINA", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (40, 140, 80, 152), "(5-HT)", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (248, 16, 344, 46), "SERT\n(TRANSPORTADOR\nDE 5-HT)", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (232, 140, 256, 152), "ISRS", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (146, 147, 208, 160), "SINAPSIS", scale=scale, fill=BLACK, plate=WHITE)
    save(image, "es-fig-6-6.png")


def erase_arrow_letters(image: Image.Image, scale: int) -> tuple[int, int]:
    """Rellena de negro el asta, incluidos los huecos del rótulo inglés."""
    pixels = image.load()
    centers = []
    for y in range(192 * scale, 242 * scale):
        xs = [x for x in range(210 * scale, 320 * scale) if sum(pixels[x, y]) < 90]
        if len(xs) < 4:
            continue
        span = xs[-1] - xs[0]
        if not (6 * scale <= span <= 28 * scale):
            continue
        for x in range(xs[0], xs[-1] + 1):
            pixels[x, y] = (0, 0, 0)
        centers.append(((xs[0] + xs[-1]) // 2, y))
    if not centers:
        return (0, 0)
    return centers[len(centers) // 2]


def write_stress(image: Image.Image, scale: int) -> None:
    pixels = image.load()
    left, top, right, bottom = scale_box((286, 246, 342, 266), scale)
    def splash(x: int, y: int) -> bool:
        if not (0 <= x < image.width and 0 <= y < image.height):
            return False
        red, green, blue = pixels[x, y]
        return 100 < red < 210 and green > 200 and blue > 200 and red < green - 20

    donors = []
    for y in list(range(top - 24, top - 2)) + list(range(bottom + 2, bottom + 24)):
        for x in range(left - 10, right + 10, 2):
            if splash(x, y):
                donors.append(pixels[x, y])
    if donors:
        for y in range(top, bottom):
            for x in range(left, right):
                pixels[x, y] = donors[(x + y * 3) % len(donors)]
    write(image, (286, 246, 342, 266), "ESTRÉS", scale=scale, fill=BLACK)


def figure_6_7_clean() -> None:
    scale = 4
    image = open_scaled("ce7bd4a699ac7f3d-fig6.6_draft-350x273.png", scale)
    cover(image, (8, 6, 102, 22), "EL EJE HHA", scale=scale, fill=BLACK, plate=WHITE, font_path=FONT_OBLIQUE)
    cover(image, (108, 8, 158, 22), "HIPOCAMPO", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (40, 41, 88, 51), "AMÍGDALA", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (16, 91, 78, 103), "HIPOTÁLAMO", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (54, 126, 108, 137), "HIPÓFISIS", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (246, 158, 286, 176), "", scale=scale, plate=WHITE)
    cover(image, (286, 150, 346, 186), "GLÁNDULA\nSUPRARRENAL", scale=scale, fill=BLACK, plate=WHITE)
    cover(image, (114, 230, 170, 248), "RIÑÓN", scale=scale, fill=BLACK, plate=WHITE)
    write_stress(image, scale)
    center = erase_arrow_letters(image, scale)
    if center != (0, 0):
        chosen = face(22)
        probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        bounds = probe.textbbox((0, 0), "GLUCOCORTICOIDES", font=chosen)
        label = Image.new("RGBA", (bounds[2] - bounds[0] + 4, bounds[3] - bounds[1] + 4), (0, 0, 0, 0))
        ImageDraw.Draw(label).text((2 - bounds[0], 2 - bounds[1]), "GLUCOCORTICOIDES", font=chosen, fill=WHITE)
        angle = -math.degrees(math.atan2(30, 49.5))
        rotated = label.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        image.paste(rotated, (center[0] - rotated.width // 2, center[1] - rotated.height // 2), rotated)
    save(image, "es-fig-6-7.png")


def main() -> None:
    figure_6_4()
    figure_6_5()
    figure_6_6()
    figure_6_7_clean()


if __name__ == "__main__":
    main()
