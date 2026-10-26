# Resultados del backtest y análisis del reto $5,000 → $1,000,000

**Datos:** velas diarias de enero 2005 a octubre 2026 (21.8 años) de 13 mercados disponibles en Exness.
Incluyen spread y comisión estimados. Las señales se calculan al cierre y se ejecutan al día siguiente.
Empieza con $5,000.

## Sistema completo (con aprendizaje)

| Riesgo/trade | Riesgo abierto máx. | Capital final | Rend. anual | Peor caída | Sharpe | ¿Llega a $1M? |
|---|---|---|---|---|---|---|
| 0.5% | 6% | $42,379 | 10.3% | −22% | 0.74 | No |
| 1% | 10% | $78,416 | 13.5% | −28% | 0.62 | No |
| 2% | 15% | $246,163 | 19.6% | −43% | 0.64 | No |
| **3% (modo Reto)** | **20%** | **$1,741,768** | **30.8%** | **−47%** | **0.74** | **Sí, en marzo 2024 (19 años)** |
| 5% | 30% | $3,715,762 | 35.5% | −68% | 0.70 | Sí, en abril 2021 (16 años) |

Con 0.5% de riesgo: 2,963 trades, 45% ganadores, factor de beneficio 1.39. Ganaron las tres estrategias:
Donchian +0.21R por trade en promedio, Momentum +0.12R y RSI(2) +0.11R.

Rendimiento con 0.5% de riesgo por año: 15 de 21 años cerraron positivos. El peor fue 2011 (−4.2%) y el
mejor 2017 (+41%). Primera mitad del periodo: 8.9% anual; segunda mitad: 12.1% anual. El sistema no se
deterioró con el tiempo, lo cual es buena señal de que no está sobreajustado.

## Monte Carlo: ¿qué tan probable es llegar a $1M en 10 años?

4,000 simulaciones con los trades reales del backtest en orden aleatorio, unos 136 trades por año:

| Riesgo/trade | Capital mediano a 10 años | Prob. de llegar a $1M | Prob. de caer ≥ 50% en el camino |
|---|---|---|---|
| 0.5% | $12,493 | 0% | 0% |
| 1% | $29,820 | 0% | 0% |
| 2% | $147,893 | 2.5% | 1.2% |
| 3% | $587,098 | 37.9% | 17.9% |
| 5% | $6,056,993 | 83.9% | 85.0% |
| 8% | $53,565,115 | 92.7% | 100% |

El Monte Carlo trata los trades como independientes, así que es **optimista**: en la vida real los trades
se agrupan en rachas y las caídas son mayores, como muestra el backtest completo de arriba.

## Conclusión

- El sistema tiene ventaja real y consistente: es rentable en 21 años y en ambas mitades del periodo.
- Convertir $5,000 en $1,000,000 es multiplicar por 200. Ningún sistema serio lo hace en uno o dos años
  sin una probabilidad altísima de quemar la cuenta. Con el modo Reto (3%), históricamente tomó alrededor de
  19 años, con una caída de casi la mitad en el camino. A 10 años, la probabilidad es cercana a 1 de 3.
- Subir a 5% u 8% acelera la meta en el papel, pero casi garantiza caídas de más del 50%. En demo no
  cuesta nada probarlo; con dinero real es como se quiebran las cuentas.
- El rendimiento pasado no garantiza el futuro. Los CFDs con apalancamiento pueden hacerte perder todo el
  capital. Deja que la demo corra varios meses antes de pensar en dinero real.
