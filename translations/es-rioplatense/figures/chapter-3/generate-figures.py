#!/usr/bin/env python3
"""Localiza los rótulos ingleses de las figuras del capítulo de electrofisiología.

Se borra solo la tinta del rótulo original y se escribe el español encima,
sin un recuadro que tape el dibujo. Los originales de site/assets/media no se
modifican.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLUE = (37, 81, 159)
NAVY = (28, 39, 71)
YELLOW = (255, 238, 18)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def face(size: float, bold: bool) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def is_light(pixel) -> bool:
    return sum(pixel) / 3 > 165 and max(pixel) - min(pixel) < 140


def background_at(pixels, x, y, step, width, height):
    for _ in range(64):
        y += step
        if y < 0 or y >= height:
            return None
        pixel = pixels[x, y]
        if is_light(pixel):
            return pixel
    return None


def erase(image: Image.Image, box, scale: int = 1) -> None:
    """Sustituye la tinta por el papel de arriba y de abajo."""
    left, top, right, bottom = scale_box(box, scale)
    pad = max(1, scale)
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(image.width - 1, right + pad)
    bottom = min(image.height - 1, bottom + pad)
    pixels = image.load()
    span = max(1, bottom - top)
    for x in range(left, right + 1):
        above = background_at(pixels, x, top, -1, image.width, image.height)
        below = background_at(pixels, x, bottom, 1, image.width, image.height)
        if above is None:
            above = below or WHITE
        if below is None:
            below = above
        for y in range(top, bottom + 1):
            blend = (y - top) / span
            pixels[x, y] = tuple(
                round(above[channel] * (1 - blend) + below[channel] * blend)
                for channel in range(3)
            )


def paint(image: Image.Image, box, color, scale: int = 1) -> None:
    left, top, right, bottom = scale_box(box, scale)
    draw = ImageDraw.Draw(image)
    draw.rectangle((left, top, right, bottom), fill=color)


def write(
    image: Image.Image,
    box,
    text: str,
    *,
    scale: int = 1,
    fill=BLACK,
    extra=(2, 2),
    align: str = "center",
    bold: bool = True,
    at=None,
) -> None:
    target = at or box
    max_w = (target[2] - target[0] + extra[0]) * scale
    max_h = (target[3] - target[1] + extra[1]) * scale
    draw = ImageDraw.Draw(image)
    size = max(8, (target[3] - target[1]) * scale * (0.72 if "\n" in text else 0.86))
    chosen = face(size, bold)
    spacing = max(1, scale)
    bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    for _ in range(18):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.9
        chosen = face(size, bold)
        bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = target[0] * scale - bounds[0]
    elif align == "right":
        x = target[2] * scale - width - bounds[0]
    else:
        x = (target[0] + target[2]) / 2 * scale - width / 2 - bounds[0]
    y = (target[1] + target[3]) / 2 * scale - height / 2 - bounds[1]
    draw.multiline_text(
        (round(x), round(y)),
        text,
        font=chosen,
        fill=fill,
        spacing=spacing,
        align=align,
    )


def cover(image, box, text, *, scale=1, fill=BLACK, extra=(2, 2), align="center", bold=True, bg=None, at=None):
    if bg is None:
        erase(image, box, scale)
    else:
        paint(image, box, bg, scale)
    write(image, box, text, scale=scale, fill=fill, extra=extra, align=align, bold=bold, at=at)


def cover_vertical(image, box, text, *, fill, bg, scale=1):
    """El original lee de arriba hacia abajo; el español conserva ese sentido."""
    paint(image, box, bg, scale)
    left, top, right, bottom = scale_box(box, scale)
    max_w = (bottom - top) + 2 * scale
    max_h = (right - left) + scale
    size = max_h * 0.8
    chosen = face(size, True)
    probe = ImageDraw.Draw(image)
    bounds = probe.textbbox((0, 0), text, font=chosen)
    for _ in range(16):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.9
        chosen = face(size, True)
        bounds = probe.textbbox((0, 0), text, font=chosen)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    strip = Image.new("RGBA", (width + 4, height + 4), (0, 0, 0, 0))
    ImageDraw.Draw(strip).text((-bounds[0] + 2, -bounds[1] + 2), text, font=chosen, fill=fill)
    turned = strip.rotate(-90, expand=True)
    x = left + (right - left - turned.width) // 2
    y = top + (bottom - top - turned.height) // 2
    image.paste(turned, (x, y), turned)


def open_rgb(name: str, scale: int = 1) -> Image.Image:
    image = Image.open(MEDIA / name).convert("RGB")
    if scale == 1:
        return image
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)


def save_png(image: Image.Image, name: str) -> None:
    image.save(OUT / name, optimize=True)
    print(name, image.size)


def handwriting_mask(image: Image.Image) -> np.ndarray:
    """Máscara de la letra gris, sin los trazos largos ni el relleno de la pila."""
    pixels = np.array(image.convert("RGB"))
    peak = pixels.max(axis=2).astype(int)
    valley = pixels.min(axis=2).astype(int)
    ink = (peak < 175) & ((peak - valley) < 28) & (peak > 55)
    height, width = ink.shape
    for y in range(height):
        xs = np.where(ink[y])[0]
        if len(xs) < 18:
            continue
        breaks = np.where(np.diff(xs) > 2)[0]
        starts = np.r_[0, breaks + 1]
        ends = np.r_[breaks, len(xs) - 1]
        for start, end in zip(starts, ends):
            if end - start > 22:
                ink[y, xs[start] : xs[end] + 1] = False
    for x in range(width):
        ys = np.where(ink[:, x])[0]
        if len(ys) < 18:
            continue
        breaks = np.where(np.diff(ys) > 2)[0]
        starts = np.r_[0, breaks + 1]
        ends = np.r_[breaks, len(ys) - 1]
        for start, end in zip(starts, ends):
            if end - start > 16:
                ink[ys[start] : ys[end] + 1, x] = False
    return ink


def figure_3_1() -> None:
    scale = 3
    native = Image.open(MEDIA / "325a5a997d631142-fig3.1_draft-350x273.png").convert("RGB")
    mask = handwriting_mask(native)
    dilated = mask.copy()
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dx == 0 and dy == 0:
                continue
            shifted = np.zeros_like(mask)
            src_y = slice(max(0, -dy), mask.shape[0] - max(0, dy))
            src_x = slice(max(0, -dx), mask.shape[1] - max(0, dx))
            dst_y = slice(max(0, dy), mask.shape[0] - max(0, -dy))
            dst_x = slice(max(0, dx), mask.shape[1] - max(0, -dx))
            shifted[dst_y, dst_x] = mask[src_y, src_x]
            dilated |= shifted
    pixels = np.array(native)
    peak = pixels.max(axis=2).astype(int)
    valley = pixels.min(axis=2).astype(int)
    cyan = (pixels[:, :, 2] > pixels[:, :, 0] + 25) & (pixels[:, :, 1] > pixels[:, :, 0] + 10)
    fringe = dilated & (peak < 230) & ((peak - valley) < 45) & ~cyan
    native_px = native.load()
    height, width = fringe.shape
    ys, xs = np.where(fringe)
    blocked = set(zip(xs.tolist(), ys.tolist()))
    for x, y in zip(xs.tolist(), ys.tolist()):
        replacement = None
        for step in range(1, 16):
            for nx, ny in ((x, y - step), (x, y + step), (x - step, y), (x + step, y)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in blocked:
                    replacement = native_px[nx, ny]
                    break
            if replacement is not None:
                break
        native_px[x, y] = replacement or WHITE
    image = native.resize((native.width * scale, native.height * scale), Image.Resampling.LANCZOS)
    labels = (
        ((18, 27, 114, 48), "Circuito\neléctrico"),
        ((150, 27, 252, 48), "Circuitos\ny caños"),
        ((32, 70, 60, 82), "Polo +"),
        ((62, 70, 92, 82), "Polo −"),
        ((40, 108, 96, 120), "Pila"),
        ((96, 96, 142, 116), "Corriente"),
        ((138, 62, 186, 84), "Altura =\nvoltaje"),
        ((168, 96, 250, 116), "Diámetro =\nresistencia"),
        ((150, 124, 220, 136), "Caño = cable"),
        ((176, 140, 256, 158), "Estrecho =\nresistencia"),
        ((244, 84, 318, 106), "Canilla =\nllave"),
        ((288, 118, 348, 150), "Caudal =\ncorriente"),
        ((2, 144, 40, 160), "Llave"),
        ((44, 122, 104, 138), "Lámpara"),
        ((118, 198, 170, 214), "Llave"),
        ((208, 200, 260, 216), "Corriente"),
        ((222, 166, 262, 180), "Cable"),
        ((146, 164, 204, 178), "Voltaje"),
        ((170, 232, 240, 250), "Resistencia"),
    )
    for box, text in labels:
        write(image, box, text, scale=scale, extra=(0, 0))
    save_png(image, "es-fig-3-1.png")


def figure_3_2() -> None:
    source = Image.open(MEDIA / "514059ac494fb401-axonwire.gif")
    source.seek(0)
    edited = source.convert("RGB")
    cover(edited, (800, 180, 890, 220), "Cable", extra=(8, 2))
    cover(edited, (1020, 180, 1110, 220), "Axón", extra=(8, 2))
    patch_box = (790, 170, 1160, 230)
    patch = edited.crop(patch_box)
    palette = source.convert("RGB").quantize(colors=128)
    frames = []
    total = source.n_frames
    for index in range(total):
        source.seek(index)
        frame = source.convert("RGB")
        frame.paste(patch, patch_box[:2])
        reduced = frame.quantize(palette=palette, dither=Image.Dither.NONE)
        reduced.info.pop("transparency", None)
        frames.append(reduced)
    frames[0].save(
        OUT / "es-fig-3-2.gif",
        save_all=True,
        append_images=frames[1:],
        duration=40,
        loop=0,
        disposal=2,
        optimize=False,
    )
    print("es-fig-3-2.gif", total, "cuadros")


def figure_3_6() -> None:
    raster = OUT / "_vclamp.png"
    subprocess.run(
        [
            "magick",
            "-background",
            "white",
            "-density",
            "90",
            str(MEDIA / "d7aab448e3659822-2560px-voltage_clamp_setup.svg.svg"),
            "-resize",
            "1600x",
            str(raster),
        ],
        check=True,
        capture_output=True,
    )
    image = Image.open(raster).convert("RGB")
    labels = (
        ((1144, 74, 1518, 240), "Generador de señales\ncon voltaje\nde comando", (4, 2)),
        ((670, 100, 920, 270), "Amplificador\ndel potencial\nde membrana", (4, 2)),
        ((190, 136, 470, 296), "Electrodo\nde registro\nintracelular", (4, 2)),
        ((48, 498, 440, 560), "Axón gigante de calamar", (8, 2)),
        ((700, 448, 990, 610), "Electrodo de\nreferencia\nextracelular", (4, 2)),
        ((165, 664, 530, 770), "Electrodo de paso\nde corriente", (6, 2)),
        ((1340, 658, 1568, 772), "Amplificador de\nretroalimentación", (4, 2)),
        ((848, 918, 1032, 1020), "Amperímetro", (6, 4)),
    )
    for box, text, extra in labels:
        cover(image, box, text, extra=extra)
    save_png(image, "es-fig-3-6.png")
    raster.unlink(missing_ok=True)


def figure_3_10() -> None:
    image = open_rgb("71af76f796a06945-icfecf_fig.png")
    cover_vertical(image, (6, 124, 56, 696), "Concentración (mEq/l)", fill=BLACK, bg=WHITE)
    cover(image, (80, 8, 420, 62), "Extracelular", extra=(8, 2))
    cover(image, (90, 800, 420, 858), "Intracelular", extra=(8, 2))
    cover(image, (1004, 124, 1166, 170), "cationes", extra=(4, 2), align="right")
    cover(image, (1004, 214, 1160, 254), "aniones", extra=(4, 2), align="right")
    cover_vertical(image, (536, 462, 578, 730), "Bicarbonato", fill=BLACK, bg=WHITE)
    cover_vertical(image, (620, 452, 664, 612), "Proteína", fill=WHITE, bg=NAVY)
    cover_vertical(image, (700, 162, 752, 362), "Sulfato", fill=BLACK, bg=WHITE)
    cover_vertical(image, (778, 574, 830, 814), "fosfato", fill=BLACK, bg=WHITE)
    save_png(image, "es-fig-3-10.png")


def outside_inside(image, outside, inside) -> None:
    cover(image, outside, "Exterior", extra=(4, 2))
    cover(image, inside, "Interior", extra=(4, 2))


def figure_3_11() -> None:
    image = open_rgb("fa9ac6226d2844c2-transporters.png")
    outside_inside(image, (168, 228, 440, 278), (184, 856, 416, 906))
    save_png(image, "es-fig-3-11.png")


def figure_3_13() -> None:
    image = open_rgb("b7afb890fb6896a8-restingmempot.png")
    cover(image, (340, 62, 620, 112), "Exterior", extra=(6, 2))
    cover(image, (30, 132, 132, 180), "Bajo", extra=(4, 2))
    cover(image, (24, 672, 136, 732), "Alto", extra=(4, 2))
    cover(
        image,
        (1145, 360, 1495, 472),
        "Canal de fuga\nde potasio",
        extra=(4, 2),
    )
    cover(image, (1360, 4, 1505, 86), "ion K+", extra=(4, 2))
    cover(image, (340, 638, 575, 690), "Interior", bg=WHITE, extra=(4, 2))
    ovals = (
        (1169, 658, 1382, 802),
        (781, 701, 994, 846),
        (1526, 777, 1739, 921),
        (415, 837, 628, 981),
    )
    for left, top, right, bottom in ovals:
        cover(
            image,
            (left + 34, top + 58, right - 24, top + 90),
            "Proteína",
            bg=YELLOW,
            extra=(2, 1),
        )
    save_png(image, "es-fig-3-13.png")


def figure_3_14() -> None:
    scale = 3
    image = open_rgb("daf84e79b95610c9-restingmempot2-350x161.png", scale)
    cover(
        image,
        (250, 58, 310, 77),
        "Canal de\nfuga de K+",
        scale=scale,
        bg=WHITE,
        extra=(0, 0),
    )
    ovals = (
        (256, 107, 290, 129),
        (193, 114, 227, 137),
        (315, 127, 348, 149),
        (134, 136, 167, 158),
    )
    for left, top, right, bottom in ovals:
        cover(
            image,
            (left + 2, top + 4, right - 2, bottom - 3),
            "Proteína",
            scale=scale,
            bg=YELLOW,
            extra=(1, 0),
        )
    save_png(image, "es-fig-3-14.png")


def figure_3_15() -> None:
    image = open_rgb("f26792b984adf374-ek.png")
    outside_inside(image, (326, 64, 600, 116), (326, 640, 560, 692))
    cover(image, (836, 48, 980, 96), "ion K+", extra=(4, 2))
    cover(image, (786, 372, 1034, 480), "Canal de\npotasio", bg=WHITE, extra=(4, 2))
    save_png(image, "es-fig-3-15.png")


def figure_3_16() -> None:
    image = open_rgb("ef144b39ebf9f28f-ena.png")
    outside_inside(image, (168, 258, 440, 312), (184, 690, 416, 742))
    cover(image, (980, 786, 1146, 824), "ion Na+", bg=WHITE, extra=(2, 1), align="right")
    cover(image, (862, 456, 1108, 562), "Canal de\nsodio", bg=WHITE, extra=(4, 2))
    save_png(image, "es-fig-3-16.png")


def figure_3_17() -> None:
    image = open_rgb("3a4a8049168967b9-ecl.png")
    outside_inside(image, (168, 258, 440, 312), (184, 690, 416, 742))
    cover(image, (990, 760, 1144, 840), "ion Cl−", extra=(2, 2), align="right")
    cover(image, (862, 456, 1108, 562), "Canal de\ncloruro", bg=WHITE, extra=(4, 2))
    save_png(image, "es-fig-3-17.png")


def figure_3_18() -> None:
    image = open_rgb("4da9aacd0a42e484-nernst-equation.png")
    labels = (
        ((448, 200, 772, 314), "Constante universal\nde los gases", (4, 2)),
        ((808, 200, 1100, 262), "Temperatura", (6, 2)),
        ((2, 458, 252, 580), "Potencial\nde equilibrio", (4, 4)),
        ((1570, 448, 1900, 520), "Gradiente de\nconcentración", (2, 4)),
        ((478, 820, 830, 932), "Valencia\n(carga del ion)", (4, 2)),
        ((882, 836, 1112, 948), "Constante\nde Faraday", (4, 2)),
    )
    for box, text, extra in labels:
        cover(image, box, text, fill=BLUE, extra=extra)
    # La palabra «gradient» queda sobre la flecha; se borra solo esa tinta.
    erase(image, (1714, 527, 1894, 553))
    original = Image.open(MEDIA / "4da9aacd0a42e484-nernst-equation.png").convert("RGB")
    source = original.load()
    pixels = image.load()
    for y in range(516, 527):
        for x in range(1640, 1895):
            red, green, blue = source[x, y]
            if blue > 80 and red < 90:
                pixels[x, y] = (red, green, blue)
    save_png(image, "es-fig-3-18.png")


def figure_3_19() -> None:
    scale = 4
    image = open_rgb("521f2bd608b9cf57-ghkeqn-350x231.png", scale)
    labels = (
        ((8, 50, 78, 104), "Potencial\nde membrana", (2, 2)),
        ((96, 48, 278, 104), "Permeabilidad de la\nmembrana a distintos iones", (2, 2)),
        ((110, 148, 328, 210), "Gradientes de\nconcentración", (2, 2)),
    )
    for box, text, extra in labels:
        cover(image, box, text, scale=scale, fill=BLUE, bg=BLACK, extra=extra)
    save_png(image, "es-fig-3-19.png")


def figure_3_20() -> None:
    image = open_rgb("034c1069bdd9fa39-nakatpase.png")
    outside_inside(image, (170, 280, 446, 334), (182, 698, 416, 748))
    paint(image, (232, 448, 286, 500), WHITE)
    paint(image, (232, 518, 286, 586), WHITE)
    cover(image, (286, 456, 430, 494), "ion Na+", bg=WHITE, extra=(2, 1))
    cover(image, (286, 534, 400, 570), "ion K+", bg=WHITE, extra=(2, 1))
    original = Image.open(MEDIA / "034c1069bdd9fa39-nakatpase.png").convert("RGB")
    source = original.load()
    pixels = image.load()
    for y in range(430, 600):
        for x in range(180, 232):
            pixels[x, y] = source[x, y]
    save_png(image, "es-fig-3-20.png")


def main() -> int:
    figure_3_1()
    figure_3_2()
    figure_3_6()
    figure_3_10()
    figure_3_11()
    figure_3_13()
    figure_3_14()
    figure_3_15()
    figure_3_16()
    figure_3_17()
    figure_3_18()
    figure_3_19()
    figure_3_20()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
