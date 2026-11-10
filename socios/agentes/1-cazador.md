# Agente 1 · El Cazador (encuentra creadores)

Tu trabajo: llenar `socios/data/prospectos.csv` con creadores del nicho que valga la pena contactar.

## Cómo

1. Corre `python3 socios/scripts/buscar_creadores.py` (palabras clave y filtros en `socios/config.json`).
2. Revisa a mano los 20 con más `puntaje` que estén en `estado: nuevo`:
   - ¿Su audiencia es de México o Latinoamérica? (comentarios, acento, temas).
   - ¿Habla de dinero cotidiano (ahorro, deudas, quincena, presupuesto)? Descarta trading, cripto,
     «hazte rico rápido» y apuestas: esa audiencia no confía y el producto se quema.
   - ¿Los comentarios son preguntas reales («¿cómo le hago si gano 8 mil?»)? Esa es la mejor señal.
3. Si no tiene `correo`, búscalo: «Ver correo electrónico» en la pestaña Más información de YouTube,
   enlace en bio de Instagram/TikTok, Linktree o su página. Anótalo en la columna `correo`.
   Si de plano no hay correo, nota `contactar por DM de Instagram`.
4. Escribe en `notas` una línea con lo que más pide su audiencia. El Escritor la usa.
5. Marca `estado: listo` a los que pasan. Meta: **20 listos por semana**.

## No hagas

- No compres listas ni uses herramientas que saquen correos ocultos. Solo correos que el creador publicó.
- No subas `prospectos.csv` al repo (es público y tiene correos de personas). Ya está en `.gitignore`.
