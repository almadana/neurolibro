#!/usr/bin/env python3
"""Traduce los rótulos de las figuras 3.21 a 3.33 (transmisión neuronal).

Borra únicamente la tinta del inglés, dentro de cada caja, y escribe el
español encima. No pinta un recuadro. Los archivos de site/assets/media no
se modifican.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INK = (25, 25, 25)
SCALE = 4


def face(size: int, bold: bool) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, size))


def clamp_box(box, width, height):
    x0, y0, x1, y1 = box
    return (
        max(0, int(x0)),
        max(0, int(y0)),
        min(width - 1, int(x1)),
        min(height - 1, int(y1)),
    )


def letter_mask(arr: np.ndarray, box, plain: bool = False, soft: bool = False) -> np.ndarray:
    """Tinta de letras dentro de la caja: ni cian, ni trazos largos."""
    height, width = arr.shape[:2]
    x0, y0, x1, y1 = clamp_box(box, width, height)
    mask = np.zeros((height, width), dtype=bool)
    if x1 <= x0 or y1 <= y0:
        return mask
    region = arr[y0 : y1 + 1, x0 : x1 + 1]
    red = region[:, :, 0].astype(np.int16)
    green = region[:, :, 1].astype(np.int16)
    blue = region[:, :, 2].astype(np.int16)
    peak = np.maximum(np.maximum(red, green), blue)
    chroma = peak - np.minimum(np.minimum(red, green), blue)
    # El cian claro es dibujo. El texto verdeazulado oscuro sí se borra.
    cyan = (blue > red + 18) & (green > red + 8) & (peak > 165)
    if plain:
        # Incluye el halo gris de la cursiva, sin tocar el papel blanco.
        cand = (peak < 242) & (chroma < 36) & (peak > 20) & ~cyan
    else:
        limit = 230 if soft else 188
        cand = (peak < limit) & (chroma < 48) & (peak > 12) & ~cyan

    kept = cand.copy()
    if plain:
        grown = kept.copy()
        grown[1:] |= kept[:-1]
        grown[:-1] |= kept[1:]
        grown[:, 1:] |= kept[:, :-1]
        grown[:, :-1] |= kept[:, 1:]
        halo = grown & ~kept
        halo &= (chroma < 55) & (peak < 230) & (peak > 40)
        mask[y0 : y1 + 1, x0 : x1 + 1] = kept | halo
        return mask
    for y in range(kept.shape[0]):
        x = 0
        row = kept[y]
        while x < row.shape[0]:
            if not row[x]:
                x += 1
                continue
            end = x
            while end < row.shape[0] and row[end]:
                end += 1
            if end - x > 16:
                row[x:end] = False
            x = end
    for x in range(kept.shape[1]):
        y = 0
        while y < kept.shape[0]:
            if not kept[y, x]:
                y += 1
                continue
            end = y
            while end < kept.shape[0] and kept[end, x]:
                end += 1
            if end - y > 14:
                kept[y:end, x] = False
            y = end

    seen = np.zeros_like(kept)
    h, w = kept.shape
    ys, xs = np.where(kept)
    for y, x in zip(ys, xs):
        if seen[y, x]:
            continue
        stack = [(int(y), int(x))]
        seen[y, x] = True
        pts = []
        while stack:
            cy, cx = stack.pop()
            pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and kept[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        py = [p[0] for p in pts]
        px = [p[1] for p in pts]
        bw = max(px) - min(px) + 1
        bh = max(py) - min(py) + 1
        if len(pts) < 3 or len(pts) > 700 or bw > 110 or bh > 18:
            continue
        for py_i, px_i in pts:
            mask[y0 + py_i, x0 + px_i] = True

    if not mask.any():
        return mask
    dilated = mask.copy()
    ys, xs = np.where(mask)
    for y, x in zip(ys, xs):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = int(y) + dy, int(x) + dx
                if 0 <= ny < height and 0 <= nx < width:
                    dilated[ny, nx] = True
    halo = dilated & ~mask
    peak = arr.max(axis=2)
    chroma = peak.astype(np.int16) - arr.min(axis=2).astype(np.int16)
    halo &= (chroma < 42) & (peak > 70) & (peak < 235)
    return mask | halo


def erase_ink(arr: np.ndarray, box, plain: bool = False, soft: bool = False) -> int:
    mask = letter_mask(arr, box, plain=plain, soft=soft)
    count = int(mask.sum())
    if count == 0:
        return 0
    if plain:
        x0, y0, x1, y1 = clamp_box(box, arr.shape[1], arr.shape[0])
        region = arr[y0 : y1 + 1, x0 : x1 + 1]
        local = mask[y0 : y1 + 1, x0 : x1 + 1]
        light = (~local) & (region.max(axis=2) > 175)
        if light.any():
            background = np.median(region[light], axis=0).astype(np.uint8)
        else:
            background = np.array([255, 255, 255], dtype=np.uint8)
        arr[mask] = background
        return count
    height, width = mask.shape
    ys, xs = np.where(mask)
    for y, x in zip(ys.tolist(), xs.tolist()):
        replacement = None
        for radius in range(1, 18):
            for yy in (y - radius, y + radius):
                if 0 <= yy < height and not mask[yy, x]:
                    pixel = arr[yy, x]
                    peak = int(pixel.max())
                    chroma = peak - int(pixel.min())
                    if chroma < 80 or peak > 140:
                        replacement = pixel
                        break
            if replacement is not None:
                break
        if replacement is None:
            replacement = np.array([255, 255, 255], dtype=np.uint8)
        arr[y, x] = replacement
    return count


def text_size(font, text: str):
    lines = text.split("\n")
    widths = []
    heights = []
    for line in lines:
        bbox = font.getbbox(line or " ")
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    gap = max(1, font.size // 8)
    return max(widths), sum(heights) + gap * (len(lines) - 1), lines, heights


def fit_font(text: str, max_w: int, max_h: int, bold: bool) -> ImageFont.FreeTypeFont:
    size = min(64, max(max_h, 8))
    while size > 8:
        font = face(size, bold)
        width, height, _, _ = text_size(font, text)
        if width <= max_w and height <= max_h:
            return font
        size -= 1
    return face(8, bold)


def draw_label(image: Image.Image, box, text: str, angle: float, bold: bool) -> None:
    left, top, right, bottom = [round(value * SCALE) for value in box]
    left = max(0, left)
    top = max(0, top)
    right = min(image.width - 1, right)
    bottom = min(image.height - 1, bottom)
    box_w = max(8, right - left)
    box_h = max(8, bottom - top)
    if abs(angle) > 45:
        max_w, max_h = box_h - 2, box_w - 2
    else:
        max_w, max_h = box_w - 2, box_h - 2
    font = fit_font(text, max_w, max_h, bold)
    width, height, lines, heights = text_size(font, text)
    plate = Image.new("RGBA", (width + 4, height + 4), (0, 0, 0, 0))
    pen = ImageDraw.Draw(plate)
    y = 2
    gap = max(1, font.size // 8)
    for line, line_h in zip(lines, heights):
        pen.text((2, y), line, font=font, fill=INK + (255,))
        y += line_h + gap
    if angle:
        plate = plate.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    px = left + (box_w - plate.width) // 2
    py = top + (box_h - plate.height) // 2
    image.alpha_composite(plate, (max(0, px), max(0, py)))


def render(source_name: str, labels, dest_name: str) -> None:
    image = Image.open(MEDIA / source_name).convert("RGB")
    arr = np.array(image)
    print(f"\n{dest_name}")
    for spec in labels:
        box = spec["erase"]
        count = erase_ink(arr, box, plain=spec.get("plain", False), soft=spec.get("soft", False))
        flag = "" if count > 12 else "  BAJA"
        print(f"  {count:4d}px  {spec['text'].split(chr(10))[0][:42]}{flag}")
    scaled = Image.fromarray(arr).resize(
        (image.width * SCALE, image.height * SCALE), Image.Resampling.LANCZOS
    ).convert("RGBA")
    for spec in labels:
        draw_label(
            scaled,
            spec.get("draw", spec["erase"]),
            spec["text"],
            spec.get("angle", 0),
            spec.get("bold", False),
        )
    scaled.convert("RGB").save(OUT / dest_name, optimize=True)
    print("  ->", dest_name)


def lab(text, erase, draw=None, angle=0, bold=False, plain=False, soft=False):
    spec = {"text": text, "erase": erase, "angle": angle, "bold": bold, "plain": plain, "soft": soft}
    if draw:
        spec["draw"] = draw
    return spec


FIGURES = {
    "es-fig-3-21.png": (
        "2d6b287ead0b510d-fig3.21_draft-1-350x190.png",
        [
            lab("Dendritas", (24, 28, 66, 44)),
            lab("Potencial de acción", (145, 28, 232, 40), bold=True, plain=True),
            lab("Despolarización\nde la membrana", (146, 38, 230, 52)),
            lab("Soma", (54, 118, 76, 130)),
            lab("Cono\naxónico", (46, 144, 86, 162)),
            lab("Axón", (148, 128, 200, 150), draw=(160, 148, 192, 162), soft=True),
            lab("Botón\nterminal", (286, 52, 332, 74)),
            lab(
                "Onda de despolarización",
                (124, 120, 230, 142),
                draw=(128, 118, 226, 134),
                angle=12,
            ),
            lab(
                "Propagación local",
                (232, 106, 330, 122),
                draw=(214, 96, 308, 112),
                angle=8,
            ),
        ],
    ),
    "es-fig-3-22.png": (
        "6185596fb8552659-fig3.22_draft-350x273.png",
        [
            lab("El potencial de acción", (118, 6, 236, 24), bold=True, plain=True),
            lab("Umbral (−55 mV)", (16, 124, 100, 140)),
            lab("Potencial\nde reposo", (46, 144, 102, 170)),
            lab("Potencial\nde reposo", (262, 140, 328, 170)),
            lab("Reposo", (94, 216, 120, 226), bold=True, plain=True),
            lab("Despolariza", (120, 216, 152, 226), bold=True, plain=True),
            lab("Repolariza", (152, 216, 190, 226), bold=True, plain=True),
            lab("Hiperpolariza", (190, 216, 238, 226), bold=True, plain=True),
            lab("Reposo", (238, 216, 268, 226), bold=True, plain=True),
            lab("Tiempo\n(ms)", (90, 232, 118, 252)),
        ],
    ),
    "es-fig-3-23.png": (
        "80fc1c8839e46307-fig3.23_draft-1-350x273.png",
        [
            lab(
                "Despolarización subumbral:\nno abre los canales de voltaje",
                (92, 48, 172, 76),
            ),
            lab("Umbral −55 mV", (156, 78, 198, 92)),
            lab("−70 mV, reposo", (154, 92, 198, 110)),
            lab("Canales iónicos de la membrana", (200, 8, 340, 22), bold=True, plain=True),
            lab("De voltaje", (230, 22, 270, 36)),
            lab("Canal de Na⁺", (198, 34, 240, 48)),
            lab("Canal de K⁺", (250, 34, 298, 48)),
            lab("Bomba Na⁺/K⁺", (300, 30, 346, 48)),
            lab("Compuerta de\ninactivación", (198, 86, 254, 104)),
            lab("Siempre activa:\nmantiene los gradientes", (258, 92, 346, 116)),
            lab("Fuera", (4, 166, 26, 178)),
            lab("Dentro", (2, 200, 28, 214)),
            lab("Iones Na⁺", (30, 144, 70, 158)),
            lab("Iones K⁺", (8, 216, 56, 232)),
            lab("1. Reposo", (8, 244, 72, 258), bold=True, plain=True),
            lab("2. Despolariza", (74, 244, 146, 258), bold=True, plain=True),
            lab("3. Repolariza", (148, 244, 214, 258), bold=True, plain=True),
            lab("4. Hiperpolariza", (214, 244, 278, 258), bold=True, plain=True),
            lab("(poshiperpolarización)", (198, 258, 280, 270)),
            lab("5. Reposo", (282, 244, 346, 258), bold=True, plain=True),
        ],
    ),
    "es-fig-3-24.png": (
        "bad556209fdeecc8-fig3.24_draft-350x273.png",
        [
            lab(
                "Potencial de membrana (mV)",
                (28, 80, 40, 196),
                angle=90,
                bold=True,
                plain=True,
            ),
            lab("Potencial\nde acción", (112, 56, 168, 82)),
            lab("Permeabilidad\nal Na⁺", (110, 102, 178, 134)),
            lab("Permeabilidad\nal K⁺", (136, 140, 208, 170)),
            lab(
                "Permeabilidad relativa",
                (308, 78, 324, 192),
                angle=90,
                bold=True,
                plain=True,
            ),
            lab("Tiempo (ms)", (156, 234, 210, 250), bold=True, plain=True),
        ],
    ),
    "es-fig-3-25.png": (
        "46c693e1632f7fac-fig3.25_draft-350x273.png",
        [
            lab("Período refractario\nabsoluto", (64, 28, 128, 56), bold=True, plain=True),
            lab("Período refractario relativo", (146, 40, 288, 54), bold=True, plain=True),
            lab("Potencial\nde acción", (122, 58, 168, 78)),
            lab(
                "Potencial de membrana (mV)",
                (33, 80, 42, 196),
                angle=90,
                bold=True,
                plain=True,
            ),
            lab("Umbral de disparo", (148, 154, 268, 168), plain=True),
            lab("Potencial de reposo", (148, 172, 240, 190), plain=True),
            lab("Hiperpolarización de la membrana", (148, 198, 280, 214), plain=True),
            lab("Tiempo (ms)", (158, 236, 212, 250), bold=True, plain=True),
        ],
    ),
    "es-fig-3-26.png": (
        "dc2f3b2d2c555080-fig3.26_draft-2-350x273.png",
        [
            lab("Potencial de acción", (120, 16, 182, 30)),
            lab("Cono\naxónico", (64, 42, 100, 60)),
            lab("Axón no mielinizado", (8, 64, 128, 78), bold=True, plain=True),
            lab("Canales de\nNa⁺ y K⁺", (2, 114, 46, 140)),
            lab("Canales de Na⁺\ninactivados", (78, 144, 148, 160)),
            lab("Conductancia\npasiva", (172, 146, 230, 164)),
            lab("Axón mielinizado", (8, 166, 118, 180), bold=True, plain=True),
            lab("Conductancia pasiva", (70, 208, 155, 222)),
            lab("Conducción saltatoria", (64, 228, 165, 242)),
            lab("Mielina", (132, 250, 172, 266)),
            lab("Nodo de\nRanvier", (222, 250, 264, 270)),
        ],
    ),
    "es-fig-3-27.png": (
        "5181bc8ad8ac9a81-fig3.27_draft-1-350x273.png",
        [
            lab("Sinapsis", (248, 28, 318, 48), bold=True),
            lab("Potencial de acción\npresináptico", (168, 48, 246, 74)),
            lab("Neurona\npresináptica", (52, 78, 148, 108), bold=True),
            lab("Botón\nterminal", (168, 92, 218, 118)),
            lab("Iones Ca²⁺", (214, 96, 258, 118)),
            lab("Vesículas\nsinápticas", (268, 48, 346, 78)),
            lab("Iones Ca²⁺", (268, 74, 312, 96)),
            lab("Hendidura\nsináptica", (298, 86, 348, 116)),
            lab("Iones Na⁺", (214, 124, 258, 146)),
            lab("Canal de Na⁺/K⁺\nactivado por ligando", (228, 162, 300, 192)),
            lab("Neurona\npostsináptica", (68, 182, 168, 216), bold=True),
            lab(
                "Los PPSE llegan al cono\ny disparan el potencial",
                (198, 198, 286, 238),
            ),
            lab(
                "Despolarización que\npuede generar un PPSE",
                (286, 186, 350, 232),
            ),
        ],
    ),
    "es-fig-3-28.png": (
        "ee96c34d094c9819-fig3.28_draft-350x273.png",
        [
            lab("Potencial de acción\npresináptico", (112, 28, 180, 52)),
            lab("Entrada de Ca²⁺", (118, 50, 182, 72)),
            lab("Liberación de\nglutamato", (108, 66, 180, 100)),
            lab("El glutamato se une\nal receptor AMPA", (246, 74, 348, 108)),
            lab("Receptor AMPA", (48, 108, 150, 132), bold=True),
            lab("Iones Na⁺", (8, 116, 48, 136)),
            lab("Glutamato", (2, 138, 48, 156)),
            lab("Fuera", (36, 170, 64, 184), draw=(14, 166, 48, 184)),
            lab("Dentro", (36, 214, 64, 236), draw=(8, 216, 42, 234)),
            lab("Entrada de Na⁺", (96, 228, 148, 252)),
            lab("Receptor AMPA\n(canal de Na⁺/K⁺)", (2, 246, 58, 270)),
            lab("Iones K⁺", (60, 254, 98, 270)),
            lab("Entrada de Na⁺", (176, 138, 236, 158)),
            lab("PPSE", (250, 124, 348, 164), bold=True),
        ],
    ),
    "es-fig-3-29.png": (
        "d9443510c6fcbaac-fig3.29_draft-1-350x273.png",
        [
            lab("Receptor NMDA", (138, 2, 228, 18), bold=True),
            lab("Hendidura\nsináptica", (2, 12, 32, 54), angle=-90),
            lab("Ion Ca²⁺", (36, 14, 74, 34)),
            lab("Ion Na⁺", (136, 14, 176, 36)),
            lab("Fuera", (68, 36, 112, 54), bold=True),
            lab("Glutamato", (136, 38, 188, 56)),
            lab("Membrana\npolarizada", (0, 54, 36, 98), angle=-90),
            lab("Dentro", (68, 92, 108, 112), bold=True),
            lab("El Mg²⁺ es la\ncompuerta de voltaje", (96, 98, 168, 132)),
            lab("Ion K⁺", (128, 90, 186, 122), plain=True),
            lab(
                "La despolarización\nlibera el Mg²⁺ y\nel canal se abre",
                (262, 8, 350, 52),
            ),
            lab(
                "Membrana postsináptica\ndespolarizada",
                (268, 58, 350, 102),
            ),
            lab("Entrada de\nNa⁺ y Ca²⁺", (206, 124, 272, 152)),
            lab("Receptor metabotrópico", (46, 138, 210, 158), bold=True),
            lab("Glutamato", (142, 164, 190, 182)),
            lab("Receptor acoplado\na proteína G", (2, 236, 62, 268)),
            lab("Proteína G", (108, 246, 150, 266)),
            lab("Efector de\nla proteína G", (152, 240, 204, 268)),
            lab("Señalización\ncelular indirecta", (198, 240, 258, 268)),
            lab(
                "Activación prolongada\ndel canal (AMPA/NMDA)",
                (262, 242, 350, 272),
            ),
        ],
    ),
    "es-fig-3-30.png": (
        "481e705cbe2e82cf-fig3.30_draft-350x273.png",
        [
            lab("Umbral", (62, 158, 102, 174)),
            lab("Un PPSE\nno alcanza\nel umbral", (36, 200, 98, 230)),
            lab(
                "Varios PPSE de una\nsinapsis se suman\nen el tiempo",
                (142, 198, 214, 232),
            ),
            lab(
                "PPSE simultáneos de\nvarias sinapsis alcanzan\nel umbral",
                (252, 196, 328, 232),
            ),
            lab("Potencial\npostsináptico\nexcitatorio (PPSE)", (18, 232, 112, 270), bold=True, plain=True),
            lab("Sumación\ntemporal\nde los PPSE", (140, 232, 214, 270), bold=True, plain=True),
            lab("Sumación\nespacial\nde los PPSE", (252, 232, 324, 270), bold=True, plain=True),
        ],
    ),
    "es-fig-3-31.png": (
        "7d2e5d021e0ea1d6-fig3.31_draft-1-350x273.png",
        [
            lab("Potencial de acción\npresináptico", (118, 22, 186, 48)),
            lab("Iones Ca²⁺", (48, 62, 96, 84)),
            lab("Entrada\nde Ca²⁺", (156, 58, 198, 82)),
            lab("Liberación\nde GABA", (8, 82, 62, 114)),
            lab("Iones Cl⁻", (8, 114, 52, 136)),
            lab("Iones Na⁺", (8, 138, 48, 160)),
            lab("Hendidura\nsináptica", (176, 108, 220, 136)),
            lab("Entrada\nde Cl⁻", (176, 158, 220, 180)),
            lab("Receptores\nGABA-A", (40, 178, 88, 202)),
            lab("El GABA se une al\nreceptor postsináptico", (88, 190, 168, 220)),
            lab("PPSI", (228, 142, 328, 180), bold=True),
            lab("Hiperpolarización\ndel PPSI", (168, 228, 230, 258)),
        ],
    ),
    "es-fig-3-32.png": (
        "e0a4b84df4fa77d2-fig3.32_draft-350x350.png",
        [
            lab(
                "Las entradas sinápticas se integran en el cono axónico",
                (28, 6, 322, 22),
                bold=True,
                plain=True,
            ),
            lab("Cono\naxónico", (88, 42, 122, 64)),
            lab("Cono\naxónico", (248, 42, 286, 66)),
            lab(
                "La fuerza depende de la distancia de la sinapsis al cono",
                (8, 132, 204, 154),
                bold=True,
                plain=True,
            ),
            lab(
                "La superficie neuronal cambia la distancia efectiva al cono",
                (208, 128, 348, 154),
                bold=True,
                plain=True,
            ),
            lab("Sinapsis\ndendríticas", (8, 162, 52, 184)),
            lab("Sinapsis\nsomáticas", (78, 162, 122, 184)),
            lab("Las proximales\npesan más que\nlas distales", (6, 236, 68, 268)),
            lab("Las somáticas\npesan más que\nlas dendríticas", (74, 236, 136, 268)),
            lab("Las del axón\nson las\nmás fuertes", (144, 236, 204, 264)),
            lab("Un soma chico\nacorta la distancia\nal cono", (210, 236, 276, 268)),
            lab("Más superficie\nalarga la distancia\nal cono", (278, 236, 346, 268)),
            lab("Las sinapsis excitatorias pueden:", (28, 272, 186, 290), bold=True, plain=True),
            lab("quedar bajo la compuerta\nde sinapsis inhibitorias", (24, 288, 186, 308), bold=True, plain=True),
            lab("potenciarse con más canales\ndependientes de voltaje", (22, 306, 188, 332), bold=True, plain=True),
        ],
    ),
}


def write_gap_junction() -> None:
    svg = (MEDIA / "26ad04b4cffaa381-gap_cell_junction-en.svg").read_text(encoding="utf-8")
    replacements = {
        "Intercellular space": "Espacio intercelular",
        "Hydrophilic channel": "Canal hidrofílico",
        "2-4 nm space": "Espacio de 2-4 nm",
        "Hemichannel ": "Hemicanal ",
        "Plasma membranes": "Membranas plasmáticas",
        "connexin monomer": "monómero de conexina",
        ">Closed<": ">Cerrado<",
        ">Open<": ">Abierto<",
    }
    for source, target in replacements.items():
        if source not in svg:
            raise SystemExit(f"No está en el SVG: {source}")
        svg = svg.replace(source, target, 1)
    (OUT / "es-fig-3-33.svg").write_text(svg, encoding="utf-8")
    print("\nes-fig-3-33.svg")


def main() -> None:
    for dest, (source, labels) in FIGURES.items():
        render(source, labels, dest)
    write_gap_junction()


if __name__ == "__main__":
    main()
