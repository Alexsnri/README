"""Muda el sitio publicado de Quincy a una dirección nueva sin perder visitas ni Google.

Lo usa el robot de publicación (.github/workflows/quincy-pages.yml) cuando existe la variable QUINCY_SITIO_NUEVO.
1. Copia el sitio armado (<sitio>/quincy) a <salida>, cambiando la dirección vieja por la nueva en todos los archivos de texto.
   Si la dirección nueva es un dominio propio (no termina en github.io), escribe el archivo CNAME.
2. En el sitio viejo cambia cada página por una redirección a la misma página en la dirección nueva
   (con canonical, y conservando ?ref= y #). Los archivos de verificación de Google se quedan igual.

Uso:  python3 quincy/scripts/agentes/mudanza.py _site https://quincy-mx.github.io/ _nuevo
"""
import html
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

VIEJO = "https://alexsnri.github.io/README/quincy/"
TEXTO = {".html", ".js", ".css", ".xml", ".txt", ".json", ".webmanifest", ".md", ".ics", ".svg"}

STUB = """<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quincy se mudó</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({js} + location.search + location.hash);</script>
</head>
<body style="font-family:system-ui,sans-serif;background:#07121a;color:#eaf3f4;padding:24px">
<p>Quincy ahora vive en <a style="color:#ffb547" href="{url}">{url}</a></p>
</body>
</html>
"""


def stub(url):
    return STUB.format(url=html.escape(url), js='"' + url.replace("\\", "").replace('"', "") + '"')


def main(sitio, nuevo, salida):
    if not nuevo.startswith("https://") or not nuevo.endswith("/"):
        sys.exit("La dirección nueva debe empezar con https:// y terminar en /")
    sitio, salida = Path(sitio), Path(salida)
    viejo_dir = sitio / "quincy"
    if salida.exists():
        shutil.rmtree(salida)
    shutil.copytree(viejo_dir, salida)

    for f in salida.rglob("*"):
        if f.is_file() and f.suffix in TEXTO:
            t = f.read_text(encoding="utf-8", errors="surrogateescape")
            if VIEJO in t:
                f.write_text(t.replace(VIEJO, nuevo), encoding="utf-8", errors="surrogateescape")
    host = urlparse(nuevo).hostname
    if not host.endswith(".github.io"):
        (salida / "CNAME").write_text(host + "\n", encoding="utf-8")
    (salida / ".nojekyll").touch()

    n = 0
    for f in viejo_dir.rglob("*.html"):
        if f.name.startswith("google"):
            continue
        rel = f.relative_to(viejo_dir).as_posix()
        rel = rel[: -len("index.html")] if rel.endswith("index.html") else rel
        f.write_text(stub(nuevo + rel), encoding="utf-8")
        n += 1
    (sitio / "index.html").write_text(stub(nuevo), encoding="utf-8")
    sm = viejo_dir / "sitemap.xml"
    if sm.exists():
        sm.unlink()
    print(f"Sitio nuevo en {salida} para {nuevo}; {n} páginas viejas ahora redirigen.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
