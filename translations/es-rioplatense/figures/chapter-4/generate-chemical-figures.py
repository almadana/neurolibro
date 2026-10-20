#!/usr/bin/env python3
"""Localiza los rótulos de las figuras 4.46 a 4.52.

Los originales de site/assets/media no se modifican. La 4.49b solo tiene
las subunidades α y βγ: no se regenera. ENaC, Na+ y los créditos quedan.
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
BLACK = (20, 20, 20)
BLUE = (181, 198, 231)
CYAN = (73, 209, 209)
PEACH = (247, 203, 172)
YELLOW = (254, 229, 153)
GREEN = (197, 224, 179)
PURPLE = (187, 150, 214)
PINK = (240, 177, 205)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 220) -> None:
    left, top, right, bottom = scale_box(box, scale)
    left, top = max(0, left), max(0, top)
    right, bottom = min(image.width - 1, right), min(image.height - 1, bottom)
    pixels = image.load()
    ink = []
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            red, green, blue = pixels[x, y]
            average = (red + green + blue) / 3
            if average < threshold and max(red, green, blue) - min(red, green, blue) < 42:
                ink.append((x, y))
    blocked = set(ink)
    for x, y in ink:
        replacement = None
        for step in range(1, 24):
            for nx, ny in ((x, y - step), (x, y + step), (x - step, y), (x + step, y)):
                if 0 <= nx < image.width and 0 <= ny < image.height and (nx, ny) not in blocked:
                    replacement = pixels[nx, ny]
                    break
            if replacement is not None:
                break
        pixels[x, y] = replacement or WHITE


def write(image, box, text, *, scale=1, fill=BLACK, align="center", bold=True, size=None):
    max_w = max(8, (box[2] - box[0]) * scale - 2)
    max_h = max(8, (box[3] - box[1]) * scale - 2)
    draw = ImageDraw.Draw(image)
    if size is None:
        size = (box[3] - box[1]) * scale * (0.38 if "\n" in text else 0.72)
    chosen = face(size, bold)
    spacing = max(1, round(size * 0.12))
    bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    for _ in range(28):
        if bounds[2] - bounds[0] <= max_w and bounds[3] - bounds[1] <= max_h:
            break
        size *= 0.9
        chosen = face(size, bold)
        bounds = draw.multiline_textbbox((0, 0), text, font=chosen, spacing=spacing, align=align)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if align == "left":
        x = box[0] * scale + 1 - bounds[0]
    elif align == "right":
        x = box[2] * scale - width - 1 - bounds[0]
    else:
        x = (box[0] + box[2]) / 2 * scale - width / 2 - bounds[0]
    y = (box[1] + box[3]) / 2 * scale - height / 2 - bounds[1]
    draw.multiline_text(
        (round(x), round(y)), text, font=chosen, fill=fill,
        spacing=spacing, align=align,
    )


def cover(image, box, text, *, scale=1, align="center", bold=True, size=None,
          fill=BLACK, plate=WHITE, threshold=220):
    erase(image, box, scale, threshold=threshold)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    if text:
        write(image, box, text, scale=scale, align=align, bold=bold, size=size, fill=fill)


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


def figure_4_46() -> None:
    scale = 2
    image = open_scaled("ca5c359c21cdafe2-1402_the_tongue.jpg", scale, pad=(0, 0, 28, 6))
    cover(image, (328, 154, 478, 172), "Botones gustativos", scale=scale, size=24, align="left")
    cover(image, (430, 186, 590, 210), "Papila circunvalada", scale=scale, size=26, align="left")
    cover(image, (638, 396, 770, 418), "Pelos gustativos", scale=scale, size=24, align="left")
    cover(image, (824, 396, 936, 420), "Poro gustativo", scale=scale, size=24, align="left")
    cover(image, (548, 582, 648, 620), "Botones\ngustativos", scale=scale, size=20, align="left")
    cover(image, (18, 676, 160, 700), "Papila fungiforme", scale=scale, size=24)
    cover(image, (234, 676, 360, 700), "Papila filiforme", scale=scale, size=24)
    cover(image, (446, 676, 570, 700), "Papila foliada", scale=scale, size=24)
    cover(image, (648, 714, 746, 736), "Célula basal", scale=scale, size=24, align="left")
    cover(image, (782, 714, 936, 738), "Célula de transición", scale=scale, size=22, align="left")
    cover(image, (648, 742, 790, 768), "Célula gustativa", scale=scale, size=24, align="left")
    save(image, "es-fig-4-46.png")


def figure_4_47() -> None:
    scale = 2
    shift = 16
    image = open_scaled("1764d3b14590a55b-tastepathway.png", scale, pad=(shift, 0, 12, 0))

    def box(coords):
        return (coords[0] + shift, coords[1], coords[2] + shift, coords[3])

    gray = (221, 221, 221)
    cover(image, box((555, 158, 790, 192)), "Corteza gustativa", scale=scale, size=32)
    cover(image, box((530, 206, 830, 272)), "Núcleo ventral posteromedial\ndel tálamo", scale=scale, size=28)
    cover(image, box((240, 304, 322, 352)), "Nervio\ncraneal X", scale=scale, size=22, plate=gray)
    cover(image, box((0, 374, 142, 426)), "Núcleo del\ntracto solitario", scale=scale, size=24, align="left")
    cover(image, box((412, 494, 508, 542)), "Nervio\ncraneal VII", scale=scale, size=22)
    cover(image, box((612, 494, 760, 522)), "Bulbo raquídeo", scale=scale, size=26)
    cover(image, box((266, 548, 354, 590)), "Nervio\ncraneal IX", scale=scale, size=22, plate=gray)
    cover(image, box((1020, 404, 1210, 466)), "Núcleo del\ntracto solitario", scale=scale, size=26)
    save(image, "es-fig-4-47.png")


def figure_4_48() -> None:
    scale = 2
    image = open_scaled("a89f371ee13aa94c-fig-4.48-3-1.png", scale)
    cover(image, (22, 28, 255, 88), "Núcleo ventral\nposteromedial\ndel tálamo", scale=scale, size=26, plate=BLUE)
    cover(image, (36, 160, 228, 300), "Núcleo del\ntracto\nsolitario", scale=scale, size=32, plate=CYAN)
    cover(image, (438, 18, 662, 132), "Cortezas gustativas\ninsular y frontal", scale=scale, size=28, plate=PEACH)
    cover(image, (420, 168, 640, 210), "Hipotálamo", scale=scale, size=30, plate=YELLOW)
    cover(image, (448, 252, 658, 312), "Amígdala", scale=scale, size=32, plate=GREEN)
    cover(image, (262, 378, 548, 452), "Botones gustativos\n(dos tercios anteriores\nde la lengua)", scale=scale, size=22, plate=PURPLE)
    cover(image, (262, 468, 548, 540), "Botones gustativos\n(tercio posterior\nde la lengua)", scale=scale, size=22, plate=PURPLE)
    cover(image, (286, 548, 548, 622), "Botones gustativos\n(epiglotis)", scale=scale, size=24, plate=PURPLE)
    cover(image, (588, 378, 718, 452), "Nervio\ncraneal VII", scale=scale, size=24, plate=PINK)
    cover(image, (588, 468, 718, 542), "Nervio\ncraneal IX", scale=scale, size=24, plate=PINK)
    cover(image, (588, 552, 718, 626), "Nervio\ncraneal X", scale=scale, size=24, plate=PINK)
    save(image, "es-fig-4-48.png")


def figure_4_49a() -> None:
    scale = 4
    image = open_scaled("aace358be442fe4a-enac-350x206.png", scale)
    cover(image, (302, 76, 338, 104), "Canal\nselectivo\nde H+", scale=scale, size=13)
    save(image, "es-fig-4-49a.png")


def figure_4_49() -> None:
    scale = 2
    image = open_scaled("4a4ae3823fce9ff8-tastemap-1024x364.png", scale)
    cover(image, (592, 108, 760, 132), "Amargo", scale=scale, size=28, align="left")
    cover(image, (592, 214, 760, 238), "Ácido", scale=scale, size=28, align="left")
    cover(image, (592, 288, 760, 308), "Dulce", scale=scale, size=26, align="left")
    cover(image, (592, 310, 760, 332), "Salado", scale=scale, size=26, align="left")
    cover(image, (592, 336, 780, 360), "Umami", scale=scale, size=26, align="left")
    save(image, "es-fig-4-49.png")


def figure_4_50() -> None:
    scale = 4
    shift = 72
    image = open_scaled(
        "8737af0baf93d17c-1403_olfaction-e1673886095275-350x234.jpg",
        scale,
        pad=(shift, 4, 96, 8),
    )

    def box(coords):
        return (coords[0] + shift, coords[1] + 4, coords[2] + shift, coords[3] + 4)

    cover(image, box((-48, 16, 72, 36)), "Bulbo olfativo", scale=scale, size=18, align="left")
    cover(image, box((124, 16, 190, 40)), "Tracto\nolfativo", scale=scale, size=14, align="left")
    cover(image, box((130, 44, 196, 64)), "Epitelio\nolfativo", scale=scale, size=14, align="left")
    cover(image, box((-58, 58, 74, 76)), "Cornetes nasales", scale=scale, size=16, align="left")
    cover(image, box((-58, 76, 52, 100)), "Aire\ninhalado", scale=scale, size=15, align="left")
    cover(image, box((48, 208, 180, 228)), "(a) Cavidad nasal", scale=scale, size=16, align="left")

    cover(image, box((298, 17, 445, 32)), "Tracto olfativo", scale=scale, size=15, align="left")
    cover(image, box((298, 36, 445, 50)), "Células mitrales", scale=scale, size=15, align="left")
    cover(image, box((298, 48, 445, 62)), "Neuronas olfativas", scale=scale, size=15, align="left")
    cover(image, box((298, 66, 445, 80)), "Hueso etmoides", scale=scale, size=15, align="left")
    cover(image, box((298, 90, 445, 116)), "Filamentos del\nnervio olfativo", scale=scale, size=14, align="left")
    cover(image, box((298, 114, 445, 128)), "Tejido conectivo", scale=scale, size=15, align="left")
    cover(image, box((298, 126, 445, 142)), "Glándula olfativa", scale=scale, size=15, align="left")
    cover(image, box((298, 144, 445, 158)), "Receptor olfativo", scale=scale, size=15, align="left")
    cover(image, box((298, 166, 445, 180)), "Dendrita", scale=scale, size=15, align="left")
    cover(image, box((298, 178, 445, 192)), "Moco", scale=scale, size=15, align="left")
    cover(image, box((128, 164, 206, 188)), "Cilios\nolfativos", scale=scale, size=13, align="left")
    cover(image, box((198, 196, 400, 216)), "Aire inhalado con\nmoléculas odorantes", scale=scale, size=14, align="left")
    cover(image, box((220, 214, 410, 230)), "(b) Sistema olfativo", scale=scale, size=15, align="left")
    save(image, "es-fig-4-50.png")


def figure_4_51() -> None:
    scale = 4
    shift = 110
    image = open_scaled(
        "7eba4eaa421de0a9-nerv_372-350x250.jpeg",
        scale,
        pad=(shift, 0, 80, 8),
    )

    def box(coords):
        return (coords[0] + shift, coords[1], coords[2] + shift, coords[3])

    cover(image, box((-100, 36, 68, 60)), "Tracto olfativo", scale=scale, size=18, align="right")
    cover(image, box((-100, 58, 68, 124)), "Corteza olfativa\ndel lóbulo temporal\n(percepción consciente\ndel olfato)", scale=scale, size=15, align="right")
    cover(image, box((-100, 124, 68, 166)), "Hipocampo\n(memoria olfativa)", scale=scale, size=16, align="right")
    cover(image, box((-100, 164, 68, 214)), "Amígdala\n(respuestas\nemocionales)", scale=scale, size=15, align="right")
    cover(image, box((286, 28, 420, 50)), "Bulbo olfativo", scale=scale, size=18, align="left")
    cover(image, box((286, 82, 420, 106)), "Hipotálamo", scale=scale, size=18, align="left")
    cover(image, box((286, 172, 424, 236)), "Formación reticular\n(respuestas viscerales\nal olfato)", scale=scale, size=15, align="left")
    save(image, "es-fig-4-51.png")


def figure_4_52() -> None:
    scale = 4
    image = open_scaled("7d56a52cd8bf8bbe-4.52-odorants-350x372.png", scale)
    cover(image, (36, 4, 155, 24), "ODORANTES", scale=scale, size=18, align="left")
    cover(image, (198, 4, 345, 24), "RECEPTORES", scale=scale, size=18, align="left")
    cover(image, (24, 130, 260, 160), "PATRÓN DE ACTIVACIÓN\nPERIFÉRICA", scale=scale, size=15, align="left")
    save(image, "es-fig-4-52.png")


def main() -> None:
    figure_4_46()
    figure_4_47()
    figure_4_48()
    figure_4_49a()
    figure_4_49()
    figure_4_50()
    figure_4_51()
    figure_4_52()


if __name__ == "__main__":
    main()
