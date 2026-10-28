"""Revisa el sitio publicado de Quincy y dice qué está mal. No cambia nada.

Revisa cada página del sitemap: que responda 200, que tenga título, descripción y canonical,
que cargue core.js (analítica) y que los enlaces internos no estén rotos. También revisa
robots.txt, sitemap.xml, manifest, service worker y los archivos de verificación de Google.

Uso:  python3 quincy/scripts/agentes/salud_sitio.py [--json]
Sale con código 1 si hay errores.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SITE = "https://quincy-mx.github.io/"
EXTRA = ["robots.txt", "sitemap.xml", "manifest.webmanifest", "sw.js", "js/core.js",
         "google6d98ea961984eb65.html", "google832c58bf0a929f35.html"]


def get(url):
    t = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "quincy-salud/1.0", "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace"), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, "", time.time() - t
    except Exception as e:  # sin red, DNS, timeout
        return 0, str(e), time.time() - t


def main():
    errors, warnings, pages = [], [], []
    st, sm, _ = get(SITE + "sitemap.xml")
    urls = re.findall(r"<loc>(.*?)</loc>", sm) if st == 200 else []
    if not urls:
        errors.append(f"sitemap.xml no se pudo leer (HTTP {st})")
    for path in EXTRA:
        code, _, _ = get(SITE + path)
        if code != 200:
            errors.append(f"{path}: HTTP {code}")
    seen_links = set()
    for u in urls:
        code, body, secs = get(u)
        info = {"url": u, "http": code, "segundos": round(secs, 2)}
        pages.append(info)
        if code != 200:
            errors.append(f"{u}: HTTP {code}")
            continue
        title = re.search(r"<title>(.*?)</title>", body, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', body)
        canon = re.search(r'<link rel="canonical" href="([^"]*)"', body)
        info.update(titulo=title.group(1).strip() if title else None, descripcion=len(desc.group(1)) if desc else 0)
        if not title:
            errors.append(f"{u}: sin <title>")
        elif len(title.group(1)) > 65:
            warnings.append(f"{u}: título de {len(title.group(1))} caracteres (Google corta ~60)")
        if not desc:
            warnings.append(f"{u}: sin meta description")
        elif not 70 <= len(desc.group(1)) <= 165:
            warnings.append(f"{u}: description de {len(desc.group(1))} caracteres (ideal 120-160)")
        if not canon:
            warnings.append(f"{u}: sin canonical")
        if "js/core.js" not in body and u.endswith(("/", ".html")) and "plan.html" not in u:
            warnings.append(f"{u}: no carga core.js (no se mide con Cloudflare)")
        if secs > 3:
            warnings.append(f"{u}: tardó {secs:.1f} s")
        for href in re.findall(r'href="([^"#]+)"', body):
            full = urllib.parse.urljoin(u, href)
            if full.startswith(SITE) and full not in seen_links:
                seen_links.add(full)
    for link in sorted(seen_links - set(urls)):
        if link.endswith((".css", ".webmanifest")) or "?" in link:
            continue
        code, _, _ = get(link)
        if code != 200:
            errors.append(f"Enlace roto: {link} (HTTP {code})")
    result = {"paginas": pages, "errores": errors, "avisos": warnings, "enlaces_revisados": len(seen_links)}
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(f"Páginas en el sitemap: {len(urls)} · enlaces internos revisados: {len(seen_links)}")
        for p in pages:
            print(f"  {p['http']}  {p['segundos']:>5}s  {p['url']}")
        print(f"\nErrores ({len(errors)}):" + "".join(f"\n  - {e}" for e in errors))
        print(f"Avisos ({len(warnings)}):" + "".join(f"\n  - {w}" for w in warnings))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
