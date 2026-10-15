#!/usr/bin/env python3
"""Genera las figuras 2.5, 2.6 y 2.8 localizadas al español rioplatense."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
MEDIA = ROOT / "site" / "assets" / "media"
OUT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def wrap(draw, text, fnt, max_width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if draw.textbbox((0, 0), candidate, font=fnt)[2] <= max_width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return "\n".join(lines)


def fitted_text(draw, box, text, max_size, min_size=14, bold=False,
                fill="black", background="white", align="left", padding=4):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=background)
    for size in range(max_size, min_size - 1, -1):
        fnt = font(size, bold)
        rendered = wrap(draw, text, fnt, x1 - x0 - 2 * padding)
        spacing = max(2, size // 6)
        bounds = draw.multiline_textbbox(
            (0, 0), rendered, font=fnt, spacing=spacing, align=align
        )
        if bounds[3] - bounds[1] <= y1 - y0 - 2 * padding:
            break
    text_box = draw.multiline_textbbox(
        (0, 0), rendered, font=fnt, spacing=spacing, align=align
    )
    height = text_box[3] - text_box[1]
    y = y0 + max(padding, (y1 - y0 - height) / 2 - text_box[1])
    if align == "center":
        x = (x0 + x1) / 2
        anchor = "ma"
    elif align == "right":
        x = x1 - padding
        anchor = "ra"
    else:
        x = x0 + padding
        anchor = "la"
    draw.multiline_text(
        (x, y), rendered, font=fnt, fill=fill, spacing=spacing,
        align=align, anchor=anchor
    )


def scaled_box(box, scale):
    return tuple(round(value * scale) for value in box)


def figure_25():
    scale = 2
    src = MEDIA / "dc3d6976f3827ce9-updated-sns-pns-image-1024x807.png"
    im = Image.open(src).convert("RGBA").resize(
        (1024 * scale, 807 * scale), Image.Resampling.LANCZOS
    )
    draw = ImageDraw.Draw(im)

    labels = [
        ((126, 0, 353, 29), "Parasimpático", 21, True, "center"),
        ((702, 0, 873, 29), "Simpático", 21, True, "center"),
        ((0, 116, 180, 174), "Estimula el flujo\nde saliva", 18, True, "left"),
        ((310, 141, 410, 176), "Ganglio", 18, True, "center"),
        ((253, 174, 493, 217), "Bulbo raquídeo", 18, True, "center"),
        ((42, 214, 176, 270), "Disminuye la\nfrecuencia cardíaca", 18, True, "left"),
        ((397, 287, 487, 347), "Nervio\nvago", 18, True, "center"),
        ((31, 334, 169, 391), "Contrae los\nbronquios", 18, True, "left"),
        ((24, 440, 181, 525), "Estimula el\nperistaltismo y\nla secreción", 18, True, "left"),
        ((0, 563, 178, 621), "Estimula la\nliberación de bilis", 18, True, "left"),
        ((25, 709, 162, 766), "Contrae la\nvejiga", 18, True, "left"),
        ((865, 35, 1024, 68), "Dilata la pupila", 18, True, "left"),
        ((850, 120, 1024, 178), "Inhibe el flujo\nde saliva", 18, True, "left"),
        ((850, 214, 1024, 270), "Aumenta la\nfrecuencia cardíaca", 18, True, "left"),
        ((865, 325, 1024, 382), "Dilata los\nbronquios", 18, True, "left"),
        ((649, 391, 746, 449), "Plexo\nsolar", 18, True, "center"),
        ((859, 429, 1024, 512), "Inhibe el\nperistaltismo y\nla secreción", 18, True, "left"),
        ((858, 528, 1024, 608), "Convierte el\nglucógeno en\nglucosa", 18, True, "left"),
        ((850, 616, 1024, 696), "Secreción de\nadrenalina y\nnoradrenalina", 18, True, "left"),
        ((858, 707, 1024, 791), "Inhibe la\ncontracción de\nla vejiga", 18, True, "left"),
        ((532, 721, 706, 807), "Cadena de\nganglios\nsimpáticos", 18, True, "left"),
    ]
    for box, text, size, bold, align in labels:
        fitted_text(
            draw, scaled_box(box, scale), text, size * scale, 12 * scale,
            bold=bold, align=align, padding=3 * scale
        )
    im.save(OUT / "es-fig-2-5.png", optimize=True)


def figure_26():
    scale = 2
    src = MEDIA / "a129bbcc70d9249a-image6.png"
    original = Image.open(src).convert("RGBA")
    im = original.resize(
        (original.width * scale, original.height * scale),
        Image.Resampling.LANCZOS
    )
    draw = ImageDraw.Draw(im)

    # El original tenía una franja transparente con RGB inglés invisible.
    # Se normaliza a blanco para que el título traducido sea siempre legible.
    draw.rectangle((0, 0, im.width, 43 * scale), fill="white")
    fitted_text(
        draw, scaled_box((250, 0, 795, 40), scale), "Sistema nervioso autónomo",
        21 * scale, 16 * scale, bold=True, background="white",
        align="center", padding=2 * scale
    )

    headings = [
        ((266, 56, 520, 91), "Parasimpático", (201, 227, 240, 255)),
        ((541, 56, 740, 91), "Simpático", (249, 222, 208, 255)),
    ]
    for box, text, background in headings:
        fitted_text(
            draw, scaled_box(box, scale), text, 19 * scale, 14 * scale,
            bold=True, background=background, align="center", padding=2 * scale
        )

    boxes = [
        ((30, 275, 276, 467),
         "Neurona preganglionar: el soma suele estar en el tronco encefálico "
         "o en la región sacra de la médula espinal", 19),
        ((407, 327, 613, 479),
         "Neurotransmisor liberado en la sinapsis preganglionar: acetilcolina", 18),
        ((768, 208, 1015, 312),
         "Neurona preganglionar: el soma suele estar en la médula espinal", 18),
        ((30, 614, 276, 782),
         "Neurona posganglionar: el soma suele estar en un ganglio cercano "
         "al órgano diana", 18),
        ((760, 657, 1015, 816),
         "Neurona posganglionar: el soma está en un ganglio simpático, "
         "ubicado junto a la médula espinal", 18),
        ((30, 956, 276, 1146),
         "Neurotransmisores liberados en la sinapsis posganglionar: "
         "acetilcolina u óxido nítrico", 18),
        ((768, 968, 1015, 1146),
         "Neurotransmisor liberado en la sinapsis posganglionar: noradrenalina", 18),
        ((242, 1277, 497, 1359),
         "Se activa la respuesta de «reposo y digestión»", 18),
        ((543, 1277, 797, 1359),
         "Se activa la respuesta de «lucha o huida»", 18),
    ]
    for box, text, size in boxes:
        fitted_text(
            draw, scaled_box(box, scale), text, size * scale, 11 * scale,
            background="white", align="left", padding=8 * scale
        )

    fitted_text(
        draw, scaled_box((302, 1158, 448, 1187), scale), "Órgano diana",
        17 * scale, 12 * scale, background="white", align="center", padding=1 * scale
    )
    fitted_text(
        draw, scaled_box((596, 1158, 744, 1187), scale), "Órgano diana",
        17 * scale, 12 * scale, background="white", align="center", padding=1 * scale
    )
    im.save(OUT / "es-fig-2-6.png", optimize=True)


def figure_28():
    scale = 4
    src = MEDIA / "30509afef1b2f511-brainslices-350x279.png"
    original = Image.open(src).convert("RGBA")
    im = original.resize(
        (original.width * scale, original.height * scale),
        Image.Resampling.LANCZOS
    )
    draw = ImageDraw.Draw(im)
    labels = [
        ((31, 25, 105, 57), "Plano frontal\no coronal"),
        ((38, 130, 105, 154), "Plano sagital"),
        ((27, 230, 105, 251), "Plano horizontal"),
    ]
    for box, text in labels:
        fitted_text(
            draw, scaled_box(box, scale), text, 8 * scale, 6 * scale,
            background="white", align="right", padding=1 * scale
        )
    im.save(OUT / "es-fig-2-8.png", optimize=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    figure_25()
    figure_26()
    figure_28()
    for name in ("es-fig-2-5.png", "es-fig-2-6.png", "es-fig-2-8.png"):
        image = Image.open(OUT / name)
        print(f"{name}: {image.width} × {image.height}")
