#!/usr/bin/env python3
"""Localiza los rótulos de las figuras del sistema motor.

Los originales de site/assets/media no se modifican. No se regeneran la 5.6b
(ya traducida en el capítulo 2), la 5.11 (foto) ni las 5.14a y 5.14b (no tienen
palabras). Los créditos, las letras A–C, C1–C8 y la fórmula de la acetilcolina
quedan. En la 5.3 los nombres de las partes del cuerpo siguen el dibujo y se
glosan en el epígrafe.
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
BUBBLE = (224, 250, 251)
GRAY = (229, 229, 229)


def face(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, max(8, round(size)))


def scale_box(box, scale: int):
    return tuple(round(value * scale) for value in box)


def erase(image: Image.Image, box, scale: int = 1, threshold: int = 230) -> None:
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
          fill=BLACK, plate=WHITE, threshold=230):
    erase(image, box, scale, threshold=threshold)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    if text:
        write(image, box, text, scale=scale, align=align, bold=bold, size=size, fill=fill)


def cover_vertical(image, box, text, *, scale=1, fill=BLACK, size=None, plate=WHITE):
    erase(image, box, scale)
    left, top, right, bottom = scale_box(box, scale)
    ImageDraw.Draw(image).rectangle((left, top, right, bottom), fill=plate)
    max_w = max(8, bottom - top - 4)
    max_h = max(8, right - left - 4)
    if size is None:
        size = max_h * 0.72
    chosen = face(size, True)
    probe = ImageDraw.Draw(image)
    bounds = probe.textbbox((0, 0), text, font=chosen)
    for _ in range(24):
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


def open_scaled(name: str, scale: int, pad=(0, 0, 0, 0), color=WHITE) -> Image.Image:
    image = Image.open(MEDIA / name).convert("RGB")
    image = image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)
    left, top, right, bottom = (value * scale for value in pad)
    if left or top or right or bottom:
        canvas = Image.new("RGB", (image.width + left + right, image.height + top + bottom), color)
        canvas.paste(image, (left, top))
        return canvas
    return image


def save(image: Image.Image, name: str) -> None:
    image.save(OUT / name, optimize=True)
    print(name, image.size)


def figure_5_1() -> None:
    scale = 4
    image = open_scaled("479e4214ae6dd258-fig5.1_draft-1-350x273.png", scale)
    cover(image, (92, 2, 200, 34), "La ubicación del durazno\nse comunica a la\ncorteza frontal",
          scale=scale, size=28)
    cover(image, (6, 78, 98, 152),
          "Los receptores llevan\ninformación sensitiva\ndesde los dedos, por\nneuronas sensitivas, a la\nmédula y a la corteza.\nAsí se comunican la\nposición de los dedos y\nel acto de agarrar\nun durazno.",
          scale=scale, size=22)
    erase(image, (200, 78, 258, 126), scale, threshold=248)
    cover(image, (252, 82, 348, 122),
          "Las áreas premotora\ny motora planifican\ny ejecutan el alcance",
          scale=scale, size=22)
    erase(image, (200, 130, 262, 176), scale, threshold=248)
    cover(image, (256, 136, 348, 172),
          "Los núcleos basales\ny partes del cerebelo\nrefinan estos\nmovimientos",
          scale=scale, size=22)
    cover(image, (8, 168, 150, 208),
          "Las neuronas motoras\nllevan las señales a la\nmédula y de ahí a los\nmúsculos del brazo",
          scale=scale, size=24)
    save(image, "es-fig-5-1.png")


def figure_5_2() -> None:
    scale = 4
    shift = 16
    image = open_scaled("18b034e6f20c86ec-motorregions-350x214.png", scale, pad=(0, shift, 40, 0))

    def moved(box):
        return (box[0], box[1] + shift, box[2], box[3] + shift)

    cover(image, moved((108, 0, 190, 12)), "Giro precentral", scale=scale, size=26)
    cover(image, moved((108, 12, 185, 34)), "Corteza motora\nprimaria", scale=scale, size=24)
    cover(image, moved((8, 16, 92, 34)), "Área premotora", scale=scale, size=22)
    cover(image, moved((198, 28, 310, 54)), "Corteza parietal\nposterior", scale=scale, size=24)
    cover(image, moved((4, 56, 72, 84)), "Corteza\nprefrontal", scale=scale, size=22)
    save(image, "es-fig-5-2.png")


def figure_5_3() -> None:
    image = open_scaled("d84740d7782fd9a7-fig5.3_draft.png", 1)
    cover(image, (286, 148, 800, 272),
          "ESTIMULACIÓN\nELÉCTRICA DE LA\nCORTEZA MOTORA",
          size=34, plate=BUBBLE)
    cover(image, (900, 148, 1460, 272),
          "ESTIMULA EL\nMOVIMIENTO DE\nPARTES DEL CUERPO",
          size=34, plate=BUBBLE)
    cover(image, (1520, 148, 1860, 272),
          "MAPA DE LA\nCORTEZA MOTORA:\nHOMÚNCULO",
          size=32, plate=BUBBLE)
    save(image, "es-fig-5-3.png")


def figure_5_4() -> None:
    scale = 4
    image = open_scaled("c0a4d0109aae3e6f-fig5.4_draft-350x273.png", scale)
    cover(image, (2, 48, 58, 72), "Corteza\nprefrontal", scale=scale, size=14)
    cover(image, (68, 26, 130, 48), "Corteza\npremotora", scale=scale, size=14)
    cover(image, (138, 16, 200, 38), "Corteza\nmotora primaria", scale=scale, size=14)
    cover(image, (266, 58, 342, 92),
          "Control de la mano\nen el espacio\ninferior del cuerpo",
          scale=scale, size=15, plate=GRAY)
    cover(image, (266, 148, 342, 178),
          "Control de la mano\nen el espacio\ncentral del cuerpo",
          scale=scale, size=15, plate=GRAY)
    cover(image, (266, 234, 342, 268),
          "Control de la boca:\nmasticación\ny lamido",
          scale=scale, size=15, plate=GRAY)
    save(image, "es-fig-5-4.png")


def figure_5_5() -> None:
    scale = 4
    image = open_scaled("503cc900fc8b3b95-corticospinal-tract-350x386.png", scale)
    cover(image, (204, 10, 270, 22), "Giro precentral", scale=scale, size=15)
    cover(image, (198, 122, 268, 134), "Pedúnculo cerebral", scale=scale, size=14)
    cover(image, (198, 136, 248, 148), "Mesencéfalo", scale=scale, size=14)
    cover(image, (196, 194, 252, 206), "Bulbo", scale=scale, size=15)
    cover(image, (94, 210, 168, 222), "Pirámides", scale=scale, size=15)
    cover(image, (94, 240, 174, 258), "Decusación\nde las pirámides", scale=scale, size=14)
    cover(image, (4, 270, 150, 298),
          "Tracto corticoespinal lateral\nMueve músculos de miembros\ny dedos del lado derecho",
          scale=scale, size=13, align="left")
    cover(image, (202, 268, 330, 290),
          "Tracto corticoespinal anterior\nMueve músculos cercanos\na la línea media",
          scale=scale, size=13)
    cover(image, (92, 306, 150, 328), "Hacia los\nmúsculos esqueléticos", scale=scale, size=12)
    cover(image, (172, 298, 258, 316), "Neurona motora\nsuperior", scale=scale, size=12)
    cover(image, (176, 328, 258, 344), "Médula espinal", scale=scale, size=13)
    cover(image, (122, 346, 182, 364), "Neurona motora\ninferior", scale=scale, size=12)
    cover(image, (90, 360, 116, 374), "Clave", scale=scale, size=13)
    cover(image, (114, 372, 176, 386), "Neurona\nmotora superior", scale=scale, size=11)
    cover(image, (200, 372, 272, 386), "Neurona\nmotora inferior", scale=scale, size=11)
    save(image, "es-fig-5-5.png")


def figure_5_6a() -> None:
    scale = 4
    image = open_scaled("f31619f16b3322e1-fig5.6a_v2_draft-350x211.png", scale)
    cover(image, (274, 12, 342, 36),
          "Columnas: tractos de\nsustancia blanca que llevan\ninformación hacia el encéfalo\ny desde él",
          scale=scale, size=10)
    cover(image, (188, 34, 268, 54), "Corte de la\nmédula espinal", scale=scale, size=12)
    cover(image, (142, 26, 198, 48), "Columna\ndorsal", scale=scale, size=12)
    cover(image, (82, 32, 148, 54), "Zona de entrada\nde la raíz dorsal", scale=scale, size=11)
    cover(image, (52, 50, 118, 70), "Raíz dorsal", scale=scale, size=12)
    cover(image, (4, 66, 108, 98), "Ganglio de\nla raíz dorsal", scale=scale, size=12)
    cover(image, (0, 88, 52, 114), "Neurona\nsensitiva", scale=scale, size=12)
    cover(image, (252, 50, 322, 72), "Asta dorsal", scale=scale, size=13)
    cover(image, (272, 74, 342, 98), "Columna\nlateral", scale=scale, size=12)
    cover(image, (228, 116, 322, 144), "Asta ventral", scale=scale, size=13)
    cover(image, (292, 132, 348, 168), "Neurona\nmotora", scale=scale, size=12)
    cover(image, (0, 136, 50, 162), "Neurona\nmotora", scale=scale, size=12)
    cover(image, (52, 122, 118, 144), "Raíz ventral", scale=scale, size=12)
    cover(image, (68, 140, 148, 164), "Zona de salida\nde la raíz ventral", scale=scale, size=11)
    cover(image, (136, 146, 196, 168), "Columna\nventral", scale=scale, size=12)
    cover(image, (178, 150, 298, 194),
          "Ramas colaterales de neuronas\nsensitivas pueden cruzar la\nlínea media e influir en las\nneuronas motoras de allí",
          scale=scale, size=12)
    save(image, "es-fig-5-6a.png")


def figure_5_7() -> None:
    scale = 4
    image = open_scaled("0be39cd639bcc82b-fig5.7_draft-350x273.png", scale)
    cover(image, (268, 100, 348, 132), "Flexión\ndel codo", scale=scale, size=20)
    cover(image, (278, 232, 348, 270), "Extensión\ndel codo", scale=scale, size=18)
    cover(image, (0, 0, 40, 16), "Vértebras", scale=scale, size=11)
    cover(image, (44, 0, 88, 16), "Nervios", scale=scale, size=12)
    cover(image, (100, 6, 168, 22), "Médula espinal", scale=scale, size=12)
    cover(image, (228, 14, 348, 46),
          "La neurona sensitiva C6\nsiente el dermatoma\ndel deltoides",
          scale=scale, size=12)
    cover(image, (228, 46, 332, 76),
          "Al contraerse, este\nmúsculo flexiona el codo\ny sube el antebrazo",
          scale=scale, size=11)
    cover(image, (186, 56, 250, 80),
          "La neurona motora\nC6 inerva el bíceps",
          scale=scale, size=11)
    cover(image, (86, 76, 190, 106),
          "Esta interneurona excita\nuna neurona motora y\ncontrae el músculo",
          scale=scale, size=11)
    cover(image, (0, 124, 42, 140), "Vértebras", scale=scale, size=11)
    cover(image, (44, 124, 88, 140), "Nervios", scale=scale, size=12)
    cover(image, (100, 130, 168, 148), "Médula espinal", scale=scale, size=12)
    cover(image, (186, 126, 282, 156),
          "La neurona sensitiva C7\nsiente el dermatoma\ndel tríceps",
          scale=scale, size=11)
    cover(image, (150, 168, 230, 198),
          "La neurona motora\nC7 inerva el tríceps",
          scale=scale, size=11)
    cover(image, (86, 196, 190, 228),
          "Esta interneurona excita\nuna neurona motora y\ncontrae el músculo",
          scale=scale, size=11)
    cover(image, (155, 234, 272, 268),
          "Al contraerse, este\nmúsculo extiende el codo\ny baja el antebrazo",
          scale=scale, size=11)
    save(image, "es-fig-5-7.png")


def figure_5_8a() -> None:
    scale = 4
    image = open_scaled("99165884b8f1c776-motorunitandpool-350x151.png", scale)
    cover(image, (8, 64, 72, 90), "Conjunto\nmotor", scale=scale, size=16)
    cover(image, (48, 0, 138, 18), "Unidad motora", scale=scale, size=14)
    cover(image, (102, 84, 178, 100), "Unidad motora", scale=scale, size=14)
    cover(image, (130, 128, 198, 146), "Unidad motora", scale=scale, size=14)
    save(image, "es-fig-5-8a.png")


def figure_5_8b() -> None:
    scale = 4
    image = open_scaled("ed844bb40a18446e-5.7-graph-1-e1674489871823-350x207.png", scale, pad=(8, 0, 16, 10))
    sx = 8
    cover_vertical(image, (sx + 0, 20, sx + 22, 168), "% de fuerza máxima", scale=scale, size=15)
    cover(image, (sx + 48, 150, sx + 86, 168), "Lentas", scale=scale, size=15)
    cover(image, (sx + 108, 116, sx + 168, 152),
          "Rápidas\nresistentes\na la fatiga", scale=scale, size=13)
    cover(image, (sx + 208, 28, sx + 262, 54), "Rápidas\nfatigables", scale=scale, size=14)
    cover(image, (sx + 286, 28, sx + 348, 48), "Salto", scale=scale, size=15)
    cover(image, (sx + 286, 72, sx + 350, 92), "Galope", scale=scale, size=15)
    cover(image, (sx + 286, 122, sx + 350, 144), "Carrera", scale=scale, size=15)
    cover(image, (sx + 286, 162, sx + 350, 182), "Marcha", scale=scale, size=15)
    cover(image, (sx + 70, 192, sx + 290, 207),
          "Porcentaje del conjunto motor reclutado",
          scale=scale, size=14)
    save(image, "es-fig-5-8b.png")


def figure_5_9() -> None:
    scale = 4
    image = open_scaled("c84e320197a4a038-neuromuscularjunction-350x196.png", scale, pad=(0, 8, 8, 4))
    sy = 8
    cover(image, (18, sy + 0, 110, sy + 12), "Neurotransmisor", scale=scale, size=14)
    cover(image, (18, sy + 12, 80, sy + 26), "Receptor", scale=scale, size=14)
    cover(image, (124, sy + 32, 176, sy + 48), "Colina", scale=scale, size=16)
    cover(image, (182, sy + 32, 234, sy + 48), "Acetato", scale=scale, size=16)
    cover(image, (168, sy + 68, 280, sy + 88), "Acetilcolinesterasa", scale=scale, size=15)
    cover(image, (160, sy + 128, 240, sy + 148), "Acetilcolina", scale=scale, size=16)
    cover(image, (118, sy + 168, 186, sy + 196), "Membrana\npresináptica", scale=scale, size=15)
    cover(image, (262, sy + 168, 348, sy + 196), "Pliegues\npostsinápticos", scale=scale, size=15)
    save(image, "es-fig-5-9.png")


def figure_5_10() -> None:
    scale = 4
    image = open_scaled("457e11b49c2c4320-screenshot-2022-12-19-at-13.43.18-350x176.png", scale)
    cover(image, (2, 6, 52, 18), "Marcha", scale=scale, size=13)
    cover(image, (2, 78, 55, 94), "Carrera", scale=scale, size=13)
    cover_vertical(image, (8, 34, 36, 66), "Pierna der. / izq.", scale=scale, size=11)
    cover_vertical(image, (148, 32, 210, 72), "Ciclo de la marcha", scale=scale, size=11)
    cover_vertical(image, (8, 96, 36, 128), "Pierna der. / izq.", scale=scale, size=11)
    cover_vertical(image, (148, 94, 210, 134), "Ciclo de la marcha", scale=scale, size=11)
    cover(image, (36, 146, 74, 172), "Apoyo", scale=scale, size=12)
    cover(image, (76, 146, 140, 172), "Balanceo", scale=scale, size=12)
    cover(image, (248, 60, 348, 78), "Entradas descendentes", scale=scale, size=12)
    cover(image, (200, 80, 270, 96), "Entradas sensitivas", scale=scale, size=11)
    cover(image, (272, 84, 300, 100), "GCP", scale=scale, size=13)
    cover(image, (308, 84, 348, 100), "Salida", scale=scale, size=13)
    save(image, "es-fig-5-10.png")


def figure_5_12() -> None:
    scale = 4
    image = open_scaled(
        "8e7d89a68e6519d7-purves-neuroscience-2004-fig18.5-1024x446-1-e1670322092807-3.png",
        scale,
    )
    cover(image, (188, 16, 275, 32), "Espinocerebelo", scale=scale, size=16)
    cover(image, (260, 40, 320, 54), "Vermis", scale=scale, size=15)
    cover(image, (64, 156, 176, 174), "Cerebrocerebelo", scale=scale, size=15)
    cover(image, (112, 200, 172, 216), "Flóculo", scale=scale, size=15)
    cover(image, (188, 204, 246, 220), "Nódulo", scale=scale, size=15)
    save(image, "es-fig-5-12.png")


def figure_5_13() -> None:
    scale = 5
    image = open_scaled(
        "e270b1a400f1f2d5-basalganglia-e1671098895434-350x137.png",
        scale, pad=(0, 0, 48, 0),
    )
    cover(image, (288, 38, 390, 52), "Estriado", scale=scale, size=15)
    cover(image, (288, 50, 390, 64), "Caudado", scale=scale, size=15)
    cover(image, (288, 64, 390, 78), "Putamen", scale=scale, size=15)
    cover(image, (288, 76, 395, 94), "Globo pálido", scale=scale, size=15)
    cover(image, (140, 124, 205, 137), "Sustancia negra", scale=scale, size=13)
    cover(image, (198, 124, 310, 137), "Núcleo subtalámico", scale=scale, size=13)
    save(image, "es-fig-5-13.png")


def figure_5_15() -> None:
    scale = 4
    image = open_scaled(
        "e5ebb99b19d88b64-1024px-blausen_0704_parkinsonsdisease-350x210.png",
        scale, pad=(0, 0, 12, 4),
    )
    cover(image, (100, 2, 255, 18), "Enfermedad de Parkinson", scale=scale, size=15)
    cover(image, (162, 20, 255, 36), "Sin Parkinson", scale=scale, size=14)
    cover(image, (178, 112, 242, 128), "Parkinson", scale=scale, size=14)
    cover(image, (246, 38, 320, 52), "Núcleo rojo", scale=scale, size=13)
    cover(image, (206, 94, 292, 106), "Formación reticular", scale=scale, size=12)
    cover(image, (200, 106, 286, 118), "Acueducto cerebral", scale=scale, size=12)
    cover(image, (296, 104, 358, 118), "Sustancia negra", scale=scale, size=12)
    cover(image, (140, 192, 230, 210), "Colículo superior", scale=scale, size=13)
    save(image, "es-fig-5-15.png")


def main() -> None:
    figure_5_1()
    figure_5_2()
    figure_5_3()
    figure_5_4()
    figure_5_5()
    figure_5_6a()
    figure_5_7()
    figure_5_8a()
    figure_5_8b()
    figure_5_9()
    figure_5_10()
    figure_5_12()
    figure_5_13()
    figure_5_15()


if __name__ == "__main__":
    main()
