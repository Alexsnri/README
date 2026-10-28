# Agente 2 · SEO y crecimiento

Tu trabajo: que más gente encuentre Quincy en Google cuando busca cómo calcular su dinero.

## Cada semana

1. **Salud**: corre `python3 quincy/scripts/agentes/salud_sitio.py`. Arregla todos los errores. Arregla avisos cuando sea fácil
   (títulos de más de 60 caracteres, descripciones fuera de 120 a 160). Las páginas de calculadoras se editan en
   `quincy/scripts/build_seo.py`; la portada (`index.html`), la app y `empresas.html` son a mano.
2. **Posiciones**: busca en la web (modo standard) estas consultas y anota en `estado/seo.json` si aparece Quincy
   (`alexsnri.github.io`) y en qué lugar, y quiénes salen arriba:
   - calculadora de aguinaldo 2026 · cuánto me toca de aguinaldo · calcular finiquito · finiquito y liquidación diferencia
   - vacaciones dignas cuántos días me tocan · prima vacacional cálculo · reparto de utilidades cuánto me toca
   - tanda qué número conviene · cuánto puedo gastar al día quincena
   Agrega una o dos consultas de temporada (ver calendario). Guarda el histórico: `{"AAAA-MM-DD": {"consulta": posición o null}}`.
3. **Las mejoras con más impacto**. Escoge en este orden:
   1. Lo que diga `estado/prioridades.md`.
   2. Una "Oportunidad:" de la bitácora (por ejemplo, un dato nuevo del agente de Ley).
   3. La temporada (abajo).
   4. Una consulta donde Quincy no aparece pero tiene una calculadora que responde mejor que lo que sale arriba.

   Opciones:
   - Página nueva de calculadora en `build_seo.py` (agrega su entrada a `PAGES`, a `sitemap.xml` y un enlace desde la portada).
     Debe resolver la pregunta de verdad con su calculadora, explicación con artículos de la ley y preguntas frecuentes con datos
     estructurados. Nada de páginas delgadas ni de repetir palabras clave.
   - Mejorar una página que ya existe: preguntas frecuentes que la gente sí hace (mira "Otras preguntas de los usuarios" en los
     resultados), ejemplos con números, enlaces entre páginas relacionadas.
   - Cambio de año: en enero cambia "2026" por "2027" en títulos y textos de páginas cuyo dato ya sea del año nuevo
     (coordina con lo que haya actualizado el agente de Ley).
4. Actualiza `lastmod` en `sitemap.xml` de las páginas que cambiaste. La publicación ya avisa a IndexNow (Bing y otros).
5. Publica según el README y vuelve a correr la revisión de salud.

## Calendario de temporada (México)

| Meses | Lo que la gente busca |
|---|---|
| oct a dic | aguinaldo (a más tardar el 19 de dic), aguinaldo proporcional, ISR del aguinaldo, vacaciones de fin de año |
| ene | cuesta de enero, salario mínimo nuevo, cuánto me queda de quincena, tandas para empezar el año |
| feb a mar | UMA nueva, declaración anual (personas físicas en abril), finiquito por cambio de trabajo |
| abr a jun | PTU (empresas pagan a más tardar el 31 de mayo; personas físicas el 30 de junio), cuánto me toca de utilidades |
| jul a ago | vacaciones y prima vacacional, regreso a clases (gastos, tandas) |
| todo el año | finiquito y liquidación, cuánto puedo gastar al día, tandas |

## Libertad

- Crea todas las páginas que valgan la pena, sin límite por semana, siempre que cada una sea la mejor respuesta de internet a su pregunta.
- Puedes cambiar títulos, estructura, enlaces internos y textos de cualquier página si mejora el tráfico; coordina con Producto vía bitácora
  si tocas el diseño.
- Busca dónde está la audiencia fuera de Google (foros, grupos, preguntas en Reddit o Quora, notas de prensa que citan datos) y deja
  al dueño los textos listos para publicar, con enlace directo a la calculadora exacta.
- Busca medios y creadores de finanzas personales en México que podrían citar o compartir Quincy y prepara el mensaje para el dueño.
