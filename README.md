# Introduction to Biological Psychology — copia local

Copia estática navegable de **Introduction to Biological Psychology**, editado
por la Dra. Catherine N. Hall y publicado por University of Sussex Library.

El sitio generado está en [`site/`](site/) e incluye:

- 28 páginas HTML en el orden del libro original.
- 203 imágenes y recursos multimedia descargados localmente.
- Índice lateral y navegación anterior/siguiente.
- Búsqueda local en todo el contenido.
- Diseño adaptable a dispositivos móviles e impresión.
- Atribución, DOI y licencia en todas las páginas.

## Abrir el libro

```bash
python -m http.server 8002 --directory site
```

Después, abrir <http://localhost:8002>.

## Edición progresiva en español

La traducción al español rioplatense se genera en [`site-es/`](site-es/). Por
ahora incluye los capítulos hasta la adicción; las páginas restantes se conservan
en inglés para que la navegación siga funcionando.

```bash
python build_spanish_site.py
python -m http.server 8003 --directory site-es
```

Después, abrir <http://localhost:8003>. El generador parte de `site/`, incorpora
los fragmentos de `translations/es-rioplatense/` y crea `.nojekyll` para
publicar el directorio directamente con GitHub Pages.

## Actualizar la copia

```bash
python -m pip install -r requirements.txt
python build_static_book.py
python build_spanish_site.py
```

El primer generador reemplaza `site/` con la versión publicada en ese momento.
El segundo reemplaza `site-es/`. Los datos de la descarga quedan registrados en
`site/build-info.json`.

## Fuente y licencia

Fuente:
[Introduction to Biological Psychology](https://openpress.sussex.ac.uk/introductiontobiologicalpsychology/),
University of Sussex Library, 2023.
DOI: [10.20919/ZDGF9829](https://doi.org/10.20919/ZDGF9829).

El libro se distribuye bajo
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), excepto donde
se indique otra licencia. Esta copia es para uso no comercial y conserva las
atribuciones específicas de los materiales incorporados.

La traducción es una adaptación no oficial y no implica el aval de la editora
ni de University of Sussex Library.
