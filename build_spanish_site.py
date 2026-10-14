#!/usr/bin/env python3
"""Construye la edición progresiva en español rioplatense."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
SOURCE_SITE = ROOT / "site"
OUTPUT_SITE = ROOT / "site-es"
TRANSLATIONS = ROOT / "translations" / "es-rioplatense"
MANIFEST_PATH = TRANSLATIONS / "manifest.json"


def translated_fragment(source: str) -> str:
    path = TRANSLATIONS / source
    if path.is_file():
        return path.read_text(encoding="utf-8")
    if path.is_dir():
        chunks = sorted(path.glob("*.html"))
        if not chunks:
            raise RuntimeError(f"No hay fragmentos HTML en {path}")
        return "\n".join(chunk.read_text(encoding="utf-8").strip() for chunk in chunks)
    raise RuntimeError(f"No existe la traducción {path}")


def replace_contents(target, fragment_html: str) -> None:
    target.clear()
    fragment = BeautifulSoup(fragment_html, "html.parser")
    for child in list(fragment.contents):
        target.append(child.extract())


def link_text(original: str, title: str) -> str:
    prefix = "← " if original.lstrip().startswith("←") else ""
    suffix = " →" if original.rstrip().endswith("→") else ""
    return f"{prefix}{title}{suffix}"


def spanish_footer() -> str:
    return """
<p><strong>Traducción:</strong> adaptación al español rioplatense; no constituye
una edición oficial ni implica el aval de la editora o de University of Sussex
Library.</p>
<p><strong>Fuente:</strong>
<a href="https://openpress.sussex.ac.uk/introductiontobiologicalpsychology/">
Introduction to Biological Psychology</a>, editado por la Dra. Catherine N.
Hall, University of Sussex Library (2023), DOI
<a href="https://doi.org/10.20919/ZDGF9829">10.20919/ZDGF9829</a>.</p>
<p>Contenido bajo
<a href="https://creativecommons.org/licenses/by-nc/4.0/">CC BY-NC 4.0</a>,
excepto donde se indique otra licencia. Esta traducción conserva las
atribuciones incluidas en el original.</p>
"""


def localize_interface(soup: BeautifulSoup) -> None:
    replacements = {
        "Skip to content": "Saltar al contenido",
        "☰ Contents": "☰ Índice",
        "Search": "Buscar",
        "Search text": "Texto de búsqueda",
        "⌂ Book home": "⌂ Inicio del libro",
        "Front matter": "Páginas preliminares",
        "Main Body": "Contenido principal",
    }
    for node in soup.find_all(string=True):
        text = str(node).strip()
        if text in replacements:
            node.replace_with(str(node).replace(text, replacements[text]))
    for node in soup.find_all(attrs={"aria-label": True}):
        node["aria-label"] = {
            "Table of contents": "Índice",
            "Previous and next pages": "Páginas anterior y siguiente",
        }.get(node["aria-label"], node["aria-label"])
    for field in soup.find_all("input", placeholder=True):
        if field["placeholder"] == "Search":
            field["placeholder"] = "Buscar"


def main() -> int:
    if not SOURCE_SITE.exists():
        raise SystemExit("Falta site/. Ejecutá primero: python build_static_book.py")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pages: dict[str, dict[str, str]] = manifest["pages"]

    if OUTPUT_SITE.exists():
        shutil.rmtree(OUTPUT_SITE)
    shutil.copytree(SOURCE_SITE, OUTPUT_SITE)

    translated_text: dict[str, str] = {}
    for filename, info in pages.items():
        output_page = OUTPUT_SITE / "pages" / filename
        if not output_page.exists():
            raise RuntimeError(f"No existe la página original {output_page}")
        soup = BeautifulSoup(output_page.read_text(encoding="utf-8"), "html.parser")
        content = soup.select_one(".pressbooks-content")
        heading = soup.select_one("article > h1")
        if content is None or heading is None:
            raise RuntimeError(f"Estructura inesperada en {output_page}")

        fragment = translated_fragment(info["source"])
        replace_contents(content, fragment)
        heading.string = info["title"]
        soup.html["lang"] = "es-AR"
        if soup.title:
            soup.title.string = f'{info["title"]} — Introducción a la psicología biológica'
        topbar = soup.select_one(".topbar > a")
        if topbar:
            topbar.string = "Introducción a la psicología biológica — traducción local"
        description = soup.find("meta", attrs={"name": "description"})
        if description:
            description["content"] = info["title"]
        footer = soup.select_one("footer")
        if footer:
            replace_contents(footer, spanish_footer())
        localize_interface(soup)

        output_page.write_text(str(soup), encoding="utf-8")
        translated_text[filename] = content.get_text(" ", strip=True)

    titles = {filename: info["title"] for filename, info in pages.items()}
    for page in OUTPUT_SITE.rglob("*.html"):
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        changed = False
        for anchor in soup.find_all("a", href=True):
            basename = Path(urlparse(anchor["href"]).path).name
            if basename in titles:
                anchor.string = link_text(anchor.get_text(" ", strip=True), titles[basename])
                changed = True
        if changed:
            page.write_text(str(soup), encoding="utf-8")

    index_path = OUTPUT_SITE / "index.html"
    index = BeautifulSoup(index_path.read_text(encoding="utf-8"), "html.parser")
    index.html["lang"] = "es-AR"
    if index.title:
        index.title.string = manifest["book_title"]
    metadata = index.find("meta", attrs={"name": "description"})
    if metadata:
        metadata["content"] = manifest["book_description"]
    title = index.select_one(".hero h1")
    description = index.select_one(".hero h1 + p")
    label = index.select_one(".hero p")
    start = index.select_one(".hero a")
    if title:
        title.string = manifest["book_title"]
    if description:
        description.string = manifest["book_description"]
    if label:
        label.string = "Traducción progresiva al español rioplatense"
    if start:
        start.string = "Comenzar a leer →"
        start["href"] = "pages/introduction-to-biological-psychology.html"
    hero_text = index.select_one(".hero-inner > div")
    if hero_text:
        status = index.new_tag("p")
        status["class"] = "translation-status"
        status.string = manifest["status"]
        hero_text.append(status)
    search_title = index.select_one("#search-title")
    search_input = index.select_one("#book-search")
    contents_title = index.select_one("#contents-title")
    if search_title:
        search_title.string = "Buscar en el libro"
    if search_input:
        search_input["placeholder"] = "Escribí al menos dos caracteres…"
    if contents_title:
        contents_title.string = "Índice"
    footer = index.select_one("footer")
    if footer:
        replace_contents(footer, spanish_footer())
    cover = index.select_one(".hero img")
    if cover:
        cover["alt"] = "Tapa de Introducción a la psicología biológica"
    localize_interface(index)
    index_path.write_text(str(index), encoding="utf-8")

    search_path = OUTPUT_SITE / "search-index.json"
    search_index = json.loads(search_path.read_text(encoding="utf-8"))
    for entry in search_index:
        if entry["file"] in titles:
            entry["title"] = titles[entry["file"]]
            entry["text"] = translated_text[entry["file"]]
    search_path.write_text(
        json.dumps(search_index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    build_info_path = OUTPUT_SITE / "build-info.json"
    build_info = json.loads(build_info_path.read_text(encoding="utf-8"))
    build_info["translation"] = {
        "locale": "es-AR",
        "translated_pages": len(pages),
        "status": manifest["status"],
        "guide": "../libroneuro/GUIA_DE_TRADUCCION.md",
    }
    build_info_path.write_text(
        json.dumps(build_info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_SITE / ".nojekyll").touch()
    print(f"Edición en español generada en {OUTPUT_SITE}: {len(pages)} páginas traducidas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
