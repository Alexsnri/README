"""Extrae openHours, spread, funding y margen de páginas HTML de capital.com ya descargadas.
Uso: python3 -I capital_pages.py <archivo.html> [...]"""
import sys, re, html

for f in sys.argv[1:]:
    t = open(f, encoding="utf8", errors="ignore").read()
    oh = re.search(r'openHours\\?"\s*:\s*\\?"([^"\\]*)', t)
    txt = re.sub(r"<!--.*?-->", "", t)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", html.unescape(txt))
    def g(p):
        m = re.search(p, txt)
        return m.group(1) if m else None
    print(f.split("/")[-1], "|", oh.group(1) if oh else None,
          "| spread", g(r"Spread\s+([0-9.,]+)"),
          "| ovn", g(r"Overnight funding (?:adjustment )?time\s+([0-9:]+)"),
          "| long", g(r"Long position overnight fee\s+(-?[0-9.]+\s?%)"),
          "| short", g(r"Short position overnight fee\s+(-?[0-9.]+\s?%)"),
          "| margin", g(r"Margin\s+([0-9.]+\s?%)"),
          "| sell/buy", g(r"Sell\s+([0-9.,]+\s+Buy\s+[0-9.,]+)"))
